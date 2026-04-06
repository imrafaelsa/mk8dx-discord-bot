# 🏎️ MK8DX Rank Bot

Um bot para Discord focado em gerenciar o rankeamento competitivo (MMR e Elo) de jogadores de Mario Kart 8 Deluxe. Ele permite a criação de campeonatos (copas) no formato de lobbies interativos, cálculo distribuído de estatísticas (Vitórias, Derrotas, Winrate e Rank) e um sistema democrático de votação para definir os vencedores de cada sala.

Ideal para comunidades competitivas do Discord que precisam de um sistema de MMR automatizado e fácil de usar!

---

## ✨ Funcionalidades e Comandos (Slash Commands)

Todos os comandos do bot interagem de forma moderna e fluída utilizando as **Slash Commands** (`/`) do Discord.

- `🏆 /registrar`
  - Cria um novo perfil no banco de dados. O jogador começa com **1000 de MMR**. É o primeiro passo obrigatório para todos.
  
- `📊 /perfil [@usuario]`
  - Exibe os as suas estatísticas (ou as de outro membro mencionado).
  - Mostra os detalhes do **Rank Atual**, **Quantidade de MMR**, **Vitórias**, **Derrotas** e o **Winrate (%)**.
  
- `🏅 /top`
  - Mostra o pódio! Um placar com os **10 melhores jogadores** ranqueados do servidor.

- `🏁 /criar_copa`
  - Este é o ponto de partida de uma partida. O bot irá gerar uma mensagem com um **botão interativo** para que outros jogadores entrem no seu lobby.
  - Apenas o criador da copa (Host) tem o poder de clicar em **"Iniciar Copa"**.
  - Após iniciada, a mensagem é atualizada e a sala de jogo está oficializada e os testes iniciam. O bot providenciará o ID do Lobby a ser usado no final da corrida.

- `🗳️ /finalizar_copa <ID_DO_LOBBY>`
  - Ao fim das corridas, o host ou qualquer participante deve rodar este comando passando o ID gerado na criação da sala.
  - Uma votação interativa inicia: todos os integrantes da copa devem selecionar quem foi o vencedor global da copa usando o menu "drop-down".
  - Quando a **maioria** (mais de 50%) concordar sobre o vencedor, a votação finaliza automaticamente.
  - **Cálculo de Elo Mágico:** O perdedor médio perde pontos baseados na diferença de elo, e o Vencedor ganha esse MMR. Tudo de forma simultânea e documentada no canal.

---

## 🎮 Tutorial de Uso: Do Início ao Fim de uma Copa

Para entender como a dinâmica do bot funciona na prática em seu servidor, siga o guia:

1. **Inscrição:** Todos os participantes na chamada devem usar `/registrar` uma única vez na vida.
2. **Setup do Lobby:** O líder do jogo cria a sala rodando `/criar_copa`. 
3. **Entrada na Sala:** A mensagem gerada vai ter um botão verde **"Entrar na Copa"**. Pelo menos 2 jogadores precisam apertá-lo para prosseguir.
4. **Largada:** O Líder vai clicar em **"Iniciar Copa"**. Nesse momento o bot trava o lobby e informa no chat o **ID da copa** (Ex: `112233445566778899`). Usem esse ID depois.
5. **Joguem!:** Joguem sua copa no Mario Kart (normalmente de 4 a 12 corridas dependendo da sua regra do servidor).
6. **Prestação de Contas:** No final do jogo, rodar `/finalizar_copa 112233445566778899`. Todos abrem o menu suspenso que foi gerado no chat e votam em quem fez mais pontos.
7. **Resultado Fechado:** Assim que a sala entrar em um consenso, o bot declara os vencedores e faz o balanço cambial do MMR. Em caso de fraude na votação, um admin tem o log para banir. Confie apenas na votação justa!

---

## ⚙️ Instalação / Setup (Para Administradores e Hosts VPS)

O bot foi criado puramente usando Python. Siga os passos para rodá-lo (seja local ou no seu Cloud Service / VPS).

### Pré-requisitos
- **Python 3.8+** (Recomenda-se 3.10+)
- Um **aplicativo de Bot** criado no [Discord Developer Portal](https://discord.com/developers/applications).
  - Crie uma aplicação.
  - Vá em **Bot** > Adicione um Bot. Copie o **Token**.
  - Marque os **Privileged Gateway Intents** (Pelo menos a `Message Content Intent`).
  - Convide ele pro seu servidor gerando a URL na aba **OAuth2** (escopos: `bot`, `applications.commands`).

### Passo a passo

1. **Baixe os arquivos / Clone o repositório:**
   ```bash
   git clone https://github.com/SeuUsuario/mk8dx-bot.git
   cd mk8dx-bot
   ```

2. **Crie e Ative um Ambiente Virtual (VENV):** 
   *Isso evita conflitos no Linux/Windows*.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   # No Windows: venv\Scripts\activate
   ```

3. **Instale os pacotes e dependências necessárias:**
   ```bash
   pip install discord.py python-dotenv
   ```

4. **Configure a Chave Secreta (.env):**
   Copie o arquivo de exemplo pra gerar o arquivo real `.env`.
   ```bash
   cp .env.example .env
   ```
   Abra o `.env` no seu editor, e coloque o número secreto do Token do Bot gerado acima nele.
   ```env
   DISCORD_TOKEN=SeuTokenDiscord
   ```

5. **Ligue o Bot!**
   Execute o script principal. (Lembre-se: O bot deve estar online quando chamá-lo).
   ```bash
   python3 main.py
   ```
   *Se você for rodar 24/7 no VPS, considere usar [PM2](https://pm2.keymetrics.io/), Screen, ou Transformar em um Serviço systemd no Linux, assim ele reinicia se o servidor cair!*

---

**Construído com carrinho, cascos azuis e:**
- `discord.py` para integração com API do discord e Slash Commands.
- `sqlite3` para persistir dados sem a dor de cabeça de um MySQL remoto.
- `Calculadora de Elo Progressiva` - Quanto mais forte for com quem você lutar e perder, menos você perde. E vice versa!
