# Feishu Bridge

A lightweight WebSocket bridge connecting **Feishu (Lark) IM** to any CLI-based AI assistant.

```
Feishu user → WebSocket → bot.py → crush run "question" → reply back
```

## Features

- **WebSocket mode** — connects via Feishu's WebSocket API, no public URL needed (no ngrok required)
- **Access control** — restrict bot usage to specific Feishu users
- **Threaded execution** — CLI calls run off the event loop so the bot stays responsive

## Prerequisites

- Python 3.10+
- A Feishu app with bot capability enabled (see [Feishu Open Platform](https://open.feishu.cn/))

## Setup

### 1. Create a Feishu app

1. Go to [Feishu Open Platform](https://open.feishu.cn/) → Create an enterprise app
2. Get **App ID** and **App Secret** from the "Credentials" page
3. Enable **Bot** capability
4. Subscribe to event `im.message.receive_v1`

No webhook URL is needed in WebSocket mode.

### 2. Configure the bridge

```bash
git clone <this-repo>
cd feishu-bridge
pip install -r requirements.txt
```

```bash
cp .env.example .env
# Edit .env and fill in your FEISHU_APP_ID and FEISHU_APP_SECRET
```

### 3. Run

```bash
python bot.py
```

You should see:
```
=== READY ===
```

Now message your bot on Feishu — the bot will forward the message to the configured CLI and reply with the result.

## Configuration

All settings go in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `FEISHU_APP_ID` | — | Feishu app ID |
| `FEISHU_APP_SECRET` | — | Feishu app secret |
| `CLI_BIN` | `crush` | AI CLI binary to call |
| `CLI_TIMEOUT` | `300` | Timeout in seconds for each CLI call |
| `CLI_CWD` | — | Working directory for CLI (empty = inherit) |
| `MAX_OUTPUT` | `8000` | Max characters to send back to Feishu |
| `ALLOWED_USERS` | — | Comma-separated Feishu `open_id`s (empty = anyone) |

The bridge calls `{CLI_BIN} run "{message}"` in non-interactive mode.

## License

MIT
