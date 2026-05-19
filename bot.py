#!/usr/bin/env python3
"""Feishu Bridge — WebSocket mode, forwards messages to any CLI AI."""

import io, os, sys, asyncio, subprocess, signal
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from lark_oapi.channel import (
    FeishuChannel, InboundMessage, ChannelConfig, PolicyConfig,
)
from lark_oapi.channel import OutboundText
from lark_oapi.core.enum import LogLevel

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
CLI_BIN = os.getenv("CLI_BIN") or os.getenv("CRUSH_BIN") or "crush"
CLI_TIMEOUT = int(os.getenv("CLI_TIMEOUT") or os.getenv("CRUSH_TIMEOUT") or "300")
CLI_CWD = os.getenv("CLI_CWD") or os.getenv("CRUSH_CWD") or ""
MAX_OUTPUT = int(os.getenv("MAX_OUTPUT") or os.getenv("CRUSH_MAX_OUTPUT") or "8000")
ALLOWED_USERS = set(
    uid.strip()
    for uid in os.getenv("ALLOWED_USERS", "").split(",")
    if uid.strip()
)

# Shared thread pool for non-blocking CLI calls.
_pool = ThreadPoolExecutor(max_workers=4)

# ---------------------------------------------------------------------------
# CLI runner
# ---------------------------------------------------------------------------


def run_cli(prompt: str) -> str:
    """Run the AI CLI in non-interactive mode and return its output."""
    try:
        proc = subprocess.run(
            [CLI_BIN, "run", prompt],
            capture_output=True,
            timeout=CLI_TIMEOUT,
            cwd=CLI_CWD or None,
            encoding="utf-8",
            errors="replace",
        )
        out = proc.stdout or ""
        if proc.stderr:
            out += "\n" + proc.stderr
        return out.strip()[:MAX_OUT] or "(empty response)"
    except subprocess.TimeoutExpired:
        return "(timeout)"
    except FileNotFoundError:
        return f"(error: CLI binary '{CLI_BIN}' not found)"
    except Exception as e:
        return f"(error: {e})"


# ---------------------------------------------------------------------------
# Message handler
# ---------------------------------------------------------------------------


async def on_message(msg: InboundMessage):
    text = (msg.content_text or "").strip()
    if not text:
        return

    sender = msg.sender.open_id
    print(f"[{datetime.now():%H:%M:%S}] {sender}: {text[:80]}", flush=True)

    # Access control
    if ALLOWED_USERS and sender not in ALLOWED_USERS:
        await channel.send(
            msg.chat_id,
            OutboundText(text="Sorry, you are not allowed to use this bot."),
            opts={"reply_to": msg.message_id},
        )
        return

    # Let the user know we're working on it.
    await channel.send(
        msg.chat_id,
        OutboundText(text="⏳ thinking..."),
        opts={"reply_to": msg.message_id},
    )

    # Run the CLI off the event loop.
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_pool, run_cli, text)

    await channel.send(
        msg.chat_id,
        OutboundText(text=result),
        opts={"reply_to": msg.message_id},
    )
    print(f"[{datetime.now():%H:%M:%S}] replied", flush=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main():
    global channel

    cfg = ChannelConfig(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        log_level=LogLevel.INFO,
        policy=PolicyConfig(
            require_mention=False,
            dm_policy="open",
            group_policy="open",
        ),
    )
    channel = FeishuChannel(config=cfg)
    channel.on("message", on_message)

    await channel.connect_until_ready()
    print("=== READY ===", flush=True)

    # Keep alive.
    stop = asyncio.get_running_loop().create_future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_running_loop().add_signal_handler(
                sig, lambda: stop.set_result(None)
            )
        except NotImplementedError:
            # Windows: signals not supported on the loop.
            pass

    try:
        await stop
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        _pool.shutdown(wait=False)
        print("shutdown.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
