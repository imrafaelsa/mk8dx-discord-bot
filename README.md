# MK8DX Rank Bot

Um bot simples para Discord que gerencia rankeamento (MMR) de jogadores de Mario Kart 8 Deluxe em um servidor VPS.

## Funcionalidades
- `/registrar`: Cria o perfil com 1000 MMR.
- `/perfil`: Exibe stats (MMR, Rank, Vitórias, Derrotas, Winrate).
- `/top`: Mostra o Top 10.
- `/criar_copa`: Abre um lobby para os jogadores entrarem com um botão interativo.
- `/finalizar_copa [ID]`: Abre um menu para a sala votar em quem foi o vencedor. A maioria aprova e atualiza o MMR automaticamente (Cálculo Elo).

## Setup
1. Clone o repositório ou copie os arquivos para seu VPS.
2. Crie o ambiente virtual e instale dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install discord.py python-dotenv
   ```
3. Copie o arquivo `.env.example` para `.env` e adicione o token do seu bot do Discord.
   ```bash
   cp .env.example .env
   nano .env
   ```
4. Execute o bot:
   ```bash
   python3 main.py
   ```

*Nota:* Certifique-se de que o bot tem as permissões adequadas no Discord Developer Portal (criar slash commands e ler/enviar mensagens).
