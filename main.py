import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

import database
from elo import get_rank_name, calculate_elo

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Initialize Database
database.setup_database()

class MK8DXBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())
        
    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

bot = MK8DXBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.tree.command(name="registrar", description="Registre-se no sistema de rankeamento.")
async def registrar(interaction: discord.Interaction):
    discord_id = str(interaction.user.id)
    success = database.register_user(discord_id)
    if success:
        await interaction.response.send_message(f"✅ {interaction.user.mention} registrado com sucesso! Você começou com 1000 MMR.", ephemeral=False)
    else:
        await interaction.response.send_message("❌ Você já está registrado no sistema.", ephemeral=True)

@bot.tree.command(name="perfil", description="Veja seu perfil ou de outro jogador.")
async def perfil(interaction: discord.Interaction, membro: discord.Member = None):
    target = membro or interaction.user
    discord_id = str(target.id)
    user_data = database.get_user_profile(discord_id)
    
    if not user_data:
        await interaction.response.send_message(f"❌ {target.mention} não está registrado. Use `/registrar`.", ephemeral=True)
        return
        
    wins, losses, mmr = user_data['wins'], user_data['losses'], user_data['mmr']
    total_games = wins + losses
    winrate = (wins / total_games * 100) if total_games > 0 else 0.0
    rank_name = get_rank_name(mmr)

    embed = discord.Embed(title=f"Perfil de {target.display_name}", color=discord.Color.blue())
    embed.add_field(name="Rank", value=rank_name, inline=False)
    embed.add_field(name="MMR", value=str(mmr), inline=True)
    embed.add_field(name="Vitórias", value=str(wins), inline=True)
    embed.add_field(name="Derrotas", value=str(losses), inline=True)
    embed.add_field(name="Winrate", value=f"{winrate:.1f}%", inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="top", description="Mostra os 10 melhores jogadores.")
async def top(interaction: discord.Interaction):
    top_players = database.get_top_players(10)
    if not top_players:
        await interaction.response.send_message("Nenhum jogador registrado ainda.", ephemeral=True)
        return
        
    description = ""
    for i, p in enumerate(top_players):
        description += f"**{i+1}º** <@{p['discord_id']}> - {get_rank_name(p['mmr'])} ({p['mmr']} MMR)\n"
        
    embed = discord.Embed(title="Top 10 Jogadores", description=description, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

# --- Lobby System ---
active_lobbies = {}

class LobbyView(discord.ui.View):
    def __init__(self, host: discord.Member):
        super().__init__(timeout=None)
        self.host = host
        self.players = [host]

    @discord.ui.button(label="Entrar na Copa", style=discord.ButtonStyle.green, custom_id="join_lobby")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("Você já está na copa!", ephemeral=True)
            return
            
        user_data = database.get_user_profile(str(interaction.user.id))
        if not user_data:
            await interaction.response.send_message("Você precisa se registrar antes de jogar! Use `/registrar`.", ephemeral=True)
            return

        self.players.append(interaction.user)
        players_mentions = "\n".join([p.mention for p in self.players])
        embed = interaction.message.embeds[0]
        embed.set_field_at(0, name=f"Jogadores ({len(self.players)}/12)", value=players_mentions)
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.defer()

    @discord.ui.button(label="Iniciar Copa", style=discord.ButtonStyle.primary, custom_id="start_lobby")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            await interaction.response.send_message("Apenas o criador da copa pode iniciá-la.", ephemeral=True)
            return
            
        if len(self.players) < 2:
            await interaction.response.send_message("É necessário pelo menos 2 jogadores para iniciar.", ephemeral=True)
            return

        lobby_id = str(interaction.message.id)
        active_lobbies[lobby_id] = self.players
        
        for item in self.children:
            item.disabled = True
            
        embed = interaction.message.embeds[0]
        embed.title = "Copa em Andamento! 🏁"
        embed.color = discord.Color.red()
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"A copa começou! Host: {self.host.mention}. Usem `/finalizar_copa {lobby_id}` quando terminarem.")

@bot.tree.command(name="criar_copa", description="Abre um lobby para os jogadores entrarem.")
async def criar_copa(interaction: discord.Interaction):
    user_data = database.get_user_profile(str(interaction.user.id))
    if not user_data:
        await interaction.response.send_message("Você precisa se registrar primeiro! Use `/registrar`.", ephemeral=True)
        return
        
    embed = discord.Embed(title="Nova Copa de MK8DX! 🏎️", description="Clique abaixo para entrar.", color=discord.Color.green())
    embed.add_field(name="Jogadores (1/12)", value=interaction.user.mention)
    
    view = LobbyView(interaction.user)
    await interaction.response.send_message(embed=embed, view=view)

# --- Votação e Finalização ---
class VoteWinnerView(discord.ui.View):
    def __init__(self, players, lobby_id):
        super().__init__(timeout=None)
        self.players = players
        self.lobby_id = lobby_id
        self.votes = {}  # voter_id -> winner_id
        self.add_item(WinnerSelect(players, self))

class WinnerSelect(discord.ui.Select):
    def __init__(self, players, parent_view):
        self.parent_view = parent_view
        options = [discord.SelectOption(label=p.display_name, value=str(p.id)) for p in players]
        super().__init__(placeholder="Selecione o vencedor...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.parent_view.players:
            await interaction.response.send_message("Você não participou desta copa.", ephemeral=True)
            return

        winner_id = self.values[0]
        self.parent_view.votes[str(interaction.user.id)] = winner_id
        
        # Check if majority voted for the same person
        votes_count = {}
        for v in self.parent_view.votes.values():
            votes_count[v] = votes_count.get(v, 0) + 1
            
        required_votes = (len(self.parent_view.players) // 2) + 1
        
        await interaction.response.send_message(f"Voto computado para <@{winner_id}>.", ephemeral=True)

        for w_id, count in votes_count.items():
            if count >= required_votes:
                await process_match_results(interaction, self.parent_view.players, w_id)
                self.parent_view.stop()
                self.disabled = True
                await interaction.message.edit(content=f"**Partida Finalizada!** O vencedor foi <@{w_id}>! 🏆", view=self.parent_view)
                return

async def process_match_results(interaction: discord.Interaction, players: list, winner_id: str):
    winner_data = database.get_user_profile(winner_id)
    losers = [p for p in players if str(p.id) != winner_id]
    
    loser_mmrs = [database.get_user_profile(str(l.id))['mmr'] for l in losers]
    avg_loser_mmr = sum(loser_mmrs) / len(loser_mmrs) if loser_mmrs else winner_data['mmr']
    
    win_gain, loss_deduct = calculate_elo(winner_data['mmr'], avg_loser_mmr)
    
    # Atualiza banco
    database.update_user_stats(winner_id, win_gain, is_win=True)
    
    loser_text = ""
    for l in losers:
        database.update_user_stats(str(l.id), loss_deduct, is_win=False) # loss_deduct is negative
        loser_text += f"<@{l.id}>: {loss_deduct} MMR\n"

    embed = discord.Embed(title="Resultados da Copa", color=discord.Color.gold())
    embed.add_field(name="Vencedor", value=f"<@{winner_id}> ganhou +{win_gain} MMR!", inline=False)
    embed.add_field(name="Perdedores", value=loser_text, inline=False)
    
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="finalizar_copa", description="Inicia a votação para o vencedor da copa.")
async def finalizar_copa(interaction: discord.Interaction, lobby_id: str):
    if lobby_id not in active_lobbies:
        await interaction.response.send_message("ID de lobby inválido ou lobby não está ativo.", ephemeral=True)
        return
        
    players = active_lobbies[lobby_id]
    if interaction.user not in players:
        await interaction.response.send_message("Você não está nesta copa.", ephemeral=True)
        return

    view = VoteWinnerView(players, lobby_id)
    await interaction.response.send_message("Selecione o vencedor da copa abaixo. A maioria dos votos define o resultado.", view=view)

if __name__ == '__main__':
    bot.run(TOKEN)
