import uuid
import time
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

app = FastAPI()
vault = {}

class NoteSchema(BaseModel):
    secret: str
    seconds: int

BASE_STYLE = """
<style>
    :root {
        --red: #ff4d4d;
        --bg: #121212;
        --panel: #1e1e1e;
        --input-bg: #252525;
        --border: #2e2e2e;
        --text: #b0b0b0;
        --text-dim: #555;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background: var(--bg);
        color: var(--text);
        font-family: 'Segoe UI', system-ui, sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 1.5rem;
    }
    .container {
        background: var(--panel);
        padding: 2rem;
        border-radius: 10px;
        border-top: 3px solid var(--red);
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        width: 100%;
        max-width: 480px;
    }
    h1 {
        color: var(--red);
        font-size: 1.25rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 700;
        margin-bottom: 0.35rem;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-dim);
        margin-bottom: 1.75rem;
    }
    .label {
        font-size: 0.7rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    pre {
        background: var(--input-bg);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 14px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #ddd;
        white-space: pre-wrap;
        word-break: break-word;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .footer-note {
        font-size: 0.72rem;
        color: var(--text-dim);
        text-align: center;
    }
    .back {
        display: inline-block;
        margin-top: 1.25rem;
        font-size: 0.75rem;
        color: var(--text-dim);
        text-decoration: none;
        letter-spacing: 1px;
    }
    .back:hover { color: var(--red); }
    #status { text-align: center; color: var(--text-dim); font-size: 0.85rem; }
</style>
"""


@app.get("/", response_class=FileResponse)
async def read_index():
    return "index.html"


@app.post("/create")
async def create_note(item: NoteSchema):
    lifespan = min(item.seconds, 86400)
    note_id = str(uuid.uuid4())
    # Stores only the encrypted blob — server never sees plaintext
    vault[note_id] = {"content": item.secret, "expires_at": time.time() + lifespan}
    return {"id": note_id}


@app.get("/view/{note_id}", response_class=HTMLResponse)
async def view_note(note_id: str):
    note_data = vault.pop(note_id, None)

    if not note_data or time.time() > note_data["expires_at"]:
        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>One Note, One Life</title>{BASE_STYLE}</head>
<body>
<div class="container">
    <h1>One Note, One Life</h1>
    <p class="subtitle">This note no longer exists.</p>
    <p class="footer-note">It was already read, or its time ran out.</p>
    <a class="back" href="/">← Create a new note</a>
</div>
    <a href="https://github.com/dreidrey/one-note-one-life" target="_blank" rel="noopener"
       style="position:fixed; bottom:20px; right:20px; color:#555; transition:color 0.15s;"
       onmouseover="this.style.color='#ff4d4d'" onmouseout="this.style.color='#555'">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
        </svg>
    </a>
</body></html>""", status_code=404)

    encrypted = note_data["content"]

    # The encrypted blob is injected into the page.
    # The decryption key comes from the #fragment in the URL — never sent to this server.
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>One Note, One Life</title>{BASE_STYLE}</head>
<body>
<div class="container">
    <h1>One Note, One Life</h1>
    <p class="subtitle">This note was meant for you.</p>
    <div id="status">Decrypting...</div>
    <div id="noteWrap" style="display:none;">
        <div class="label">Message</div>
        <pre id="noteContent"></pre>
        <p class="footer-note">This note has been permanently deleted after reading.</p>
    </div>
</div>

<script>
    // Import key from base64url string
    async function importKey(keyStr) {{
        const raw = Uint8Array.from(
            atob(keyStr.replace(/-/g, '+').replace(/_/g, '/')),
            c => c.charCodeAt(0)
        );
        return crypto.subtle.importKey("raw", raw, {{ name: "AES-GCM" }}, false, ["decrypt"]);
    }}

    // Decrypt base64 blob (IV prepended) → plaintext string
    async function decrypt(blob, key) {{
        const combined = Uint8Array.from(atob(blob), c => c.charCodeAt(0));
        const iv = combined.slice(0, 12);
        const ciphertext = combined.slice(12);
        const plaintext = await crypto.subtle.decrypt({{ name: "AES-GCM", iv }}, key, ciphertext);
        return new TextDecoder().decode(plaintext);
    }}

    async function main() {{
        const keyStr = window.location.hash.slice(1); // everything after #
        const encrypted = {repr(encrypted)};

        if (!keyStr) {{
            document.getElementById('status').innerText = 'Missing decryption key.';
            return;
        }}

        try {{
            const key = await importKey(keyStr);
            const plaintext = await decrypt(encrypted, key);
            document.getElementById('status').style.display = 'none';
            document.getElementById('noteContent').innerText = plaintext;
            document.getElementById('noteWrap').style.display = 'block';
        }} catch (e) {{
            document.getElementById('status').innerText = 'Decryption failed — invalid or mismatched key.';
        }}
    }}

    main();
</script>
    <a href="https://github.com/dreidrey/one-note-one-life" target="_blank" rel="noopener"
       style="position:fixed; bottom:20px; right:20px; color:#555; transition:color 0.15s;"
       onmouseover="this.style.color='#ff4d4d'" onmouseout="this.style.color='#555'">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
        </svg>
    </a>
</body></html>""")


async def auto_cleanup():
    while True:
        await asyncio.sleep(60)
        now = time.time()
        expired = [id for id, data in vault.items() if now > data["expires_at"]]
        for n_id in expired:
            vault.pop(n_id, None)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_cleanup())

@app.get("/ping")
async def ping():
    return {"status": "ok"}