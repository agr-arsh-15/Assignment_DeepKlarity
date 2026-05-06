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

def scrape_url(url: str, timeout: int = 15) -> str:
    """
    Scrape a recipe blog URL and return cleaned page text.

    Args:
        url: Full URL to scrape (must include http/https)
        timeout: Request timeout in seconds

    Returns:
        Cleaned plain text content of the page

    Raises:
        ValueError: If URL is invalid or page cannot be fetched
        Exception: For network errors
    """
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()  # Raise error for 4xx / 5xx responses
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The website took too long to respond.")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to the website. Check the URL.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e.response.status_code} — {str(e)}")

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "ads"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    return cleaned[:8000]
