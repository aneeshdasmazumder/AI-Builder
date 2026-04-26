import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from scraper import fetch_website_contents


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DEFAULT_MODEL = "gpt-4.1-mini"
MAX_WEBSITE_CHARS = 20000

load_dotenv(PROJECT_DIR / ".env", override=True)
load_dotenv(BASE_DIR / ".env", override=True)


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY was not found in .env.")
    if not api_key.isascii():
        bad_chars = [
            (index, f"U+{ord(char):04X}")
            for index, char in enumerate(api_key)
            if not char.isascii()
        ]
        raise RuntimeError(
            f"OPENAI_API_KEY contains non-ASCII characters at: {bad_chars}."
        )
    if api_key.strip() != api_key:
        raise RuntimeError("OPENAI_API_KEY has leading or trailing whitespace.")

    return OpenAI(api_key=api_key)


def build_messages(prompt, website_text):
    system_prompt = (
        "You analyze website content and respond clearly in markdown. "
        "Ignore navigation, cookie notices, and repeated boilerplate."
    )
    user_prompt = (
        f"{prompt.strip()}\n\n"
        "Website content:\n"
        f"{website_text[:MAX_WEBSITE_CHARS]}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def summarize_website(url, prompt):
    if not prompt.strip():
        prompt = "Summarize this website in a concise, useful way."

    website_text = fetch_website_contents(url)
    response = get_client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=build_messages(prompt, website_text),
    )

    return {
        "summary": response.choices[0].message.content,
        "sourceCharacters": len(website_text),
        "usedCharacters": min(len(website_text), MAX_WEBSITE_CHARS),
    }


class WebsiteReaderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            path = "/index.html"

        file_path = (FRONTEND_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(FRONTEND_DIR.resolve())):
            self.send_error(403)
            return
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404)
            return

        content_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_types.get(file_path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/summarize":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length))
            url = str(payload.get("url", "")).strip()
            prompt = str(payload.get("prompt", "")).strip()

            if not url:
                raise ValueError("Please enter a website URL.")

            result = summarize_website(url, prompt)
            self._send_json(200, {"ok": True, **result})
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    host = "127.0.0.1"
    port = int(os.getenv("WEBSITE_READER_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), WebsiteReaderHandler)
    print(f"Website Reader running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
