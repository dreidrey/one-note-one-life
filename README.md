# One Note, One Life

Write once. Read once. Gone forever.

A self-destructing note app. Write a secret, share the link and once opened, the note is permanently deleted. No accounts, no history, no trace.

## What it does

- **Encrypted** — your note is locked before it leaves your browser. The server never sees it.
- **Lifespan** — notes expire on their own if never opened, up to 24 hours.
- **Self-destructs on read** — the moment someone opens it, it's gone.
- **Password protection** — add a password so only the right person can unlock it.
- **Burn timer** — set a countdown. When time runs out, the note wipes itself from the screen.

## Run locally

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

Open `http://localhost:8000`.