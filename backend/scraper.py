import socket
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "169.254.169.254",  # Cloud metadata endpoint
    "::1",
}


def is_safe_url(url: str) -> bool:
    """
    Validate URL to prevent Server-Side Request Forgery (SSRF).
    Blocks requests to loopback addresses, metadata IPs, and non-HTTP protocols.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname = hostname.lower()
        if hostname in BLOCKED_HOSTS:
            return False

        # Check for local IP ranges (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
        try:
            ip = socket.gethostbyname(hostname)
            if (
                ip.startswith("127.")
                or ip.startswith("10.")
                or ip.startswith("192.168.")
                or ip == "0.0.0.0"
                or ip == "169.254.169.254"
                or (ip.startswith("172.") and 16 <= int(ip.split(".")[1]) <= 31)
            ):
                return False
        except Exception:
            # If DNS resolution fails here, let requests handle it or fail safely
            pass

        return True
    except Exception:
        return False


def scrape_url(url: str, timeout: int = 15) -> str:
    """
    Scrape a recipe blog URL and return cleaned page text.

    Args:
        url: Full URL to scrape (must include http:// or https://)
        timeout: Request timeout in seconds

    Returns:
        Cleaned plain text content of the page

    Raises:
        ValueError: If URL is unsafe, invalid, or page cannot be fetched
        Exception: For network or HTTP errors
    """
    if not is_safe_url(url):
        raise ValueError("Invalid or unsafe URL. Only public HTTP/HTTPS URLs are allowed.")

    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The website took too long to respond.")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to the website. Please check the URL.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e.response.status_code} — {str(e)}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "ads"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    # Return up to 8,000 characters to optimize LLM context size
    return cleaned[:8000]
