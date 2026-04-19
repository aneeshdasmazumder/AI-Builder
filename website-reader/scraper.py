from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

REMOVABLE_TAGS = ("script", "style", "noscript", "svg", "iframe")


def _normalize_url(url: str) -> str:
    normalized = url.strip()
    if not normalized:
        raise ValueError("URL cannot be empty.")

    parsed = urlparse(normalized)
    if not parsed.scheme:
        normalized = f"https://{normalized}"

    return normalized


def _fetch(url: str, timeout: int) -> requests.Response:
    try:
        response = requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch website content from {url}: {exc}") from exc


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(REMOVABLE_TAGS):
        element.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines()]
    chunks = [line for line in lines if line]

    if title and (not chunks or chunks[0] != title):
        chunks.insert(0, title)

    if not chunks:
        raise ValueError("The page was fetched, but no readable text content was found.")

    return "\n".join(chunks)


def fetch_website_contents(url: str, timeout: int = 15) -> str:
    """Fetch a page and return readable text content."""
    normalized_url = _normalize_url(url)
    response = _fetch(normalized_url, timeout)
    return _extract_text(response.text)
