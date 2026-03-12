import time
import asyncio
import random
import string
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
vault = {}

class NoteSchema(BaseModel):
    secret: str
    seconds: int
    password_protected: Optional[bool] = False
    read_seconds: Optional[int] = None

def short_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

GITHUB_ICON = """
<a href="https://github.com/dreidrey/one-note-one-life" target="_blank" rel="noopener"
   style="position:fixed; bottom:20px; right:20px; color:#555; transition:color 0.15s;"
   onmouseover="this.style.color='#ff4d4d'" onmouseout="this.style.color='#555'">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
    </svg>
</a>
"""

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
        --font: 'Segoe UI', system-ui, sans-serif;
        --mono: 'Courier New', monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background: var(--bg);
        color: var(--text);
        font-family: var(--font);
        font-size: 0.875rem;
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
        font-size: 0.72rem;
        color: var(--text-dim);
        margin-bottom: 1.75rem;
        letter-spacing: 1px;
    }
    .label {
        font-size: 0.7rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .paper-wrap {
        position: relative;
        display: flex;
        margin-bottom: 0.75rem;
    }
    .burn-border {
        width: 3px;
        min-height: 203px;
        background: var(--border);
        border-radius: 2px;
        margin-right: 10px;
        flex-shrink: 0;
        position: relative;
        overflow: hidden;
    }
    .burn-border-fill {
        position: absolute;
        top: 0; left: 0;
        width: 100%;
        height: 100%;
        background: var(--red);
        border-radius: 2px;
        transform-origin: top;
    }
    .paper {
        flex: 1;
        background-color: #1c1c1c;
        background-image: repeating-linear-gradient(
            to bottom,
            transparent,
            transparent 28px,
            #6b2f2f 28px,
            #6b2f2f 29px
        );
        background-size: 100% 29px;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        padding-top: 6px;
        min-height: 203px;
        max-height: 203px;
        overflow: hidden;
        font-family: var(--mono);
        font-size: 0.9rem;
        color: #e8e8e8;
        white-space: pre-wrap;
        word-break: break-word;
        line-height: 29px;
    }
    .pagination {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .page-btn {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text-dim);
        border-radius: 4px;
        padding: 4px 12px;
        font-size: 0.72rem;
        letter-spacing: 1px;
        cursor: pointer;
        transition: border-color 0.15s, color 0.15s;
    }
    .page-btn:hover:not(:disabled) {{ border-color: var(--red); color: var(--red); }}
    .page-btn:disabled {{ opacity: 0.2; cursor: default; }}
    .page-indicator {{
        font-family: var(--mono);
        font-size: 0.65rem;
        color: var(--text-dim);
        letter-spacing: 1px;
    }}
    .footer-note {
        font-size: 0.72rem;
        color: var(--text-dim);
        text-align: center;
    }
    .back {
        display: inline-block;
        margin-top: 1.25rem;
        font-size: 0.72rem;
        color: var(--text-dim);
        text-decoration: none;
        letter-spacing: 1px;
    }
    .back:hover { color: var(--red); }
    #status {
        text-align: center;
        color: var(--text-dim);
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    /* Password prompt */
    .pw-group { display: flex; gap: 8px; margin-top: 0.75rem; }
    .pw-group input {
        flex: 1;
        background: var(--input-bg);
        color: #ddd;
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 10px 12px;
        outline: none;
        font-family: var(--mono);
        font-size: 0.85rem;
        transition: border-color 0.15s;
    }
    .pw-group input:focus { border-color: var(--red); }
    .pw-group button {
        background: var(--red);
        color: #fff;
        border: none;
        border-radius: 6px;
        padding: 10px 16px;
        font-family: var(--font);
        font-size: 0.85rem;
        font-weight: 700;
        cursor: pointer;
        transition: background 0.15s;
        width: auto;
        letter-spacing: 1px;
    }
    .pw-group button:hover { background: #e63c3c; }
    .pw-error {
        font-size: 0.72rem;
        color: var(--red);
        margin-top: 8px;
        text-align: center;
        display: none;
    }

    /* Timer count (shown above paper when burn timer active) */
    .timer-count-wrap {
        display: none;
        text-align: right;
        font-family: var(--mono);
        font-size: 0.7rem;
        color: var(--text-dim);
        margin-bottom: 6px;
    }
    .timer-count-wrap span { color: var(--red); }

    /* Toast */
    #toast {
        position: fixed;
        bottom: -60px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--panel);
        color: var(--text);
        border: 1px solid var(--border);
        border-left: 2px solid var(--red);
        padding: 9px 20px;
        border-radius: 4px;
        font-size: 0.75rem;
        letter-spacing: 1px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: bottom 0.35s cubic-bezier(0.68, -0.55, 0.27, 1.55);
        z-index: 1000;
        white-space: nowrap;
    }
    #toast.show { bottom: 28px; }
</style>
"""


@app.get("/", response_class=FileResponse)
async def read_index():
    return "index.html"


@app.post("/create")
async def create_note(item: NoteSchema):
    lifespan = min(item.seconds, 86400)
    note_id = short_id()
    while note_id in vault:
        note_id = short_id()
    vault[note_id] = {
        "content": item.secret,
        "expires_at": time.time() + lifespan,
        "password_protected": item.password_protected,
        "read_seconds": item.read_seconds
    }
    return {"id": note_id}


@app.get("/fetch/{note_id}")
async def fetch_note(note_id: str):
    note_data = vault.get(note_id)
    if not note_data or time.time() > note_data["expires_at"]:
        return {"error": "not_found"}
    return {
        "content": note_data["content"],
        "password_protected": note_data["password_protected"],
        "read_seconds": note_data["read_seconds"]
    }


@app.delete("/consume/{note_id}")
async def consume_note(note_id: str):
    vault.pop(note_id, None)
    return {"ok": True}


@app.get("/view/{note_id}", response_class=HTMLResponse)
async def view_note(note_id: str):
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>One Note, One Life</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23ff4d4d'/><text x='50' y='72' font-size='60' text-anchor='middle' fill='white' font-family='sans-serif' font-weight='bold'>N</text></svg>">
{BASE_STYLE}</head>
<body>
<div id="toast"></div>

<div class="container">
    <h1>One Note, One Life</h1>
    <p class="subtitle">This note was meant for you.</p>
    <div id="status">Loading...</div>

    <div id="pwPrompt" style="display:none;">
        <div class="label">Password required</div>
        <div class="pw-group">
            <input type="password" id="pwInput" placeholder="Enter password...">
            <button onclick="submitPassword()">Unlock</button>
        </div>
    </div>

    <div id="noteWrap" style="display:none;">
        <div class="label">Message</div>
        <div class="timer-count-wrap" id="timerCountWrap">
            Self-destructs in <span id="timerCount">—</span>
        </div>
        <div class="paper-wrap">
            <div class="burn-border" id="burnBorder" style="display:none;">
                <div class="burn-border-fill" id="burnBorderFill"></div>
            </div>
            <div class="paper" id="noteContent"></div>
        </div>
        <div class="pagination" id="pagination" style="display:none;">
            <button class="page-btn" id="prevBtn" onclick="changePage(-1)" disabled>← Prev</button>
            <span class="page-indicator" id="pageIndicator">1 / 1</span>
            <button class="page-btn" id="nextBtn" onclick="changePage(1)">Next →</button>
        </div>
        <p class="footer-note">This note has been permanently deleted after reading.</p>
    </div>

    <div id="expiredWrap" style="display:none;">
        <p class="footer-note">This note no longer exists. It was already read, or its time ran out.</p>
        <a class="back" href="/">← Create a new note</a>
    </div>
</div>

<script>
    const NOTE_ID = "{note_id}";
    let encryptedBlob = null;
    let baseKeyRaw = null;
    let readSecondsGlobal = null;
    let toastTimer = null;

    function showToast(msg, duration) {{
        duration = duration || 3000;
        const t = document.getElementById('toast');
        if (toastTimer) {{
            clearTimeout(toastTimer);
            t.classList.remove('show');
        }}
        setTimeout(() => {{
            t.innerText = msg;
            t.classList.add('show');
            toastTimer = setTimeout(() => t.classList.remove('show'), duration);
        }}, 80);
    }}

    async function importBaseKey(keyStr) {{
        const raw = Uint8Array.from(
            atob(keyStr.replace(/-/g, '+').replace(/_/g, '/')),
            c => c.charCodeAt(0)
        );
        const key = await crypto.subtle.importKey("raw", raw, {{ name: "AES-GCM" }}, false, ["decrypt"]);
        return {{ key, raw }};
    }}

    async function deriveKey(password, rawBase) {{
        const enc = new TextEncoder();
        const keyMaterial = await crypto.subtle.importKey(
            "raw", enc.encode(password), "PBKDF2", false, ["deriveKey"]
        );
        return crypto.subtle.deriveKey(
            {{ name: "PBKDF2", salt: rawBase, iterations: 100000, hash: "SHA-256" }},
            keyMaterial,
            {{ name: "AES-GCM", length: 256 }}, false, ["decrypt"]
        );
    }}

    async function decrypt(blob, key) {{
        const combined = Uint8Array.from(atob(blob), c => c.charCodeAt(0));
        const iv = combined.slice(0, 12);
        const ciphertext = combined.slice(12);
        const plaintext = await crypto.subtle.decrypt({{ name: "AES-GCM", iv }}, key, ciphertext);
        return new TextDecoder().decode(plaintext);
    }}

    function startReadTimer(seconds) {{
        const countWrap = document.getElementById('timerCountWrap');
        const burnBorder = document.getElementById('burnBorder');
        const fill = document.getElementById('burnBorderFill');
        const count = document.getElementById('timerCount');

        countWrap.style.display = 'block';
        burnBorder.style.display = 'block';
        count.textContent = seconds + 's';

        // Drain left border from top to bottom
        requestAnimationFrame(() => {{
            requestAnimationFrame(() => {{
                fill.style.transition = 'transform ' + seconds + 's linear';
                fill.style.transform = 'scaleY(0)';
            }});
        }});

        // Warning threshold: 10s if timer > 10s, else halfway
        const warnAt = seconds > 10 ? 10 : Math.max(Math.floor(seconds / 2), 1);

        let remaining = seconds;
        const interval = setInterval(() => {{
            remaining--;
            count.textContent = remaining + 's';

            // Toast 2: mid-countdown warning
            if (remaining === warnAt) {{
                showToast('⚠️ Note burns in ' + remaining + ' second' + (remaining !== 1 ? 's' : ''));
            }}

            if (remaining <= 0) {{
                clearInterval(interval);
                // Wipe content from DOM
                document.getElementById('noteContent').innerText = '';
                document.getElementById('noteWrap').style.display = 'none';
                // Toast 3: burned — then reload
                showToast('🔥 Note has been burned.', 2500);
                setTimeout(() => window.location.reload(), 2700);
            }}
        }}, 1000);
    }}

    let pages = [];
    let currentPage = 0;
    const CHARS_PER_PAGE = 250;

    function buildPages(text) {{
        pages = [];
        for (let i = 0; i < text.length; i += CHARS_PER_PAGE) {{
            pages.push(text.slice(i, i + CHARS_PER_PAGE));
        }}
        if (pages.length === 0) pages = [''];
    }}

    function renderPage() {{
        document.getElementById('noteContent').innerText = pages[currentPage];
        document.getElementById('pageIndicator').innerText = (currentPage + 1) + ' / ' + pages.length;
        document.getElementById('prevBtn').disabled = currentPage === 0;
        document.getElementById('nextBtn').disabled = currentPage === pages.length - 1;
        if (pages.length > 1) document.getElementById('pagination').style.display = 'flex';
    }}

    function changePage(dir) {{
        currentPage = Math.max(0, Math.min(pages.length - 1, currentPage + dir));
        renderPage();
    }}

    async function showNote(plaintext, readSeconds) {{
        await fetch('/consume/' + NOTE_ID, {{ method: 'DELETE' }});
        document.getElementById('status').style.display = 'none';
        document.getElementById('pwPrompt').style.display = 'none';
        buildPages(plaintext);
        renderPage();
        document.getElementById('noteWrap').style.display = 'block';

        if (readSeconds) {{
            showToast('⏱️ This note self-destructs in ' + readSeconds + ' second' + (readSeconds !== 1 ? 's' : ''));
            startReadTimer(readSeconds);
        }}
    }}

    function showExpired() {{
        document.getElementById('status').style.display = 'none';
        document.getElementById('expiredWrap').style.display = 'block';
    }}

    async function submitPassword() {{
        const password = document.getElementById('pwInput').value;
        if (!password) return;
        try {{
            const derivedKey = await deriveKey(password, baseKeyRaw);
            const plaintext = await decrypt(encryptedBlob, derivedKey);
            await showNote(plaintext, readSecondsGlobal);
        }} catch (e) {{
            showToast('Wrong password. Try again.');
            document.getElementById('pwInput').value = '';
            document.getElementById('pwInput').focus();
        }}
    }}

    document.addEventListener('DOMContentLoaded', () => {{
        const pwInput = document.getElementById('pwInput');
        if (pwInput) pwInput.addEventListener('keydown', e => {{ if (e.key === 'Enter') submitPassword(); }});
    }});

    async function main() {{
        const keyStr = window.location.hash.slice(1);
        if (!keyStr) {{
            document.getElementById('status').innerText = 'Missing decryption key.';
            return;
        }}

        const res = await fetch('/fetch/' + NOTE_ID);
        const data = await res.json();
        if (data.error) {{ showExpired(); return; }}

        encryptedBlob = data.content;
        readSecondsGlobal = data.read_seconds;
        const {{ key, raw }} = await importBaseKey(keyStr);
        baseKeyRaw = raw;

        if (data.password_protected) {{
            document.getElementById('status').style.display = 'none';
            document.getElementById('pwPrompt').style.display = 'block';
            document.getElementById('pwInput').focus();
        }} else {{
            try {{
                const plaintext = await decrypt(encryptedBlob, key);
                await showNote(plaintext, readSecondsGlobal);
            }} catch (e) {{
                document.getElementById('status').innerText = 'Decryption failed.';
            }}
        }}
    }}

    main();
</script>
{GITHUB_ICON}
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