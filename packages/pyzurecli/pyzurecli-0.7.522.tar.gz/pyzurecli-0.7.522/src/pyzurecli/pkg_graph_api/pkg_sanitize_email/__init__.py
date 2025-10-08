from pathlib import Path
from typing import Optional
from loguru import logger as log
import bleach
from bs4 import BeautifulSoup

import ollama
response = ollama.chat(
    model='llama2',
    messages=[{
        'role': 'user',
        'content': 'tell me in a single sentence who invented Python?'
    }]
)
print(response)
#
# def sanitize_and_simplify_html(html: str, verbose: Optional[bool] = False) -> str:
#     """
#     Sanitize and simplify HTML for conversational rendering.
#     Keeps only bold, italics, paragraph breaks, and line breaks.
#
#     Args:
#         html (str): Raw HTML input (e.g., from Microsoft Graph API).
#         verbose (bool, optional): Enable detailed logging.
#
#     Returns:
#         str: Clean, simplified HTML safe for conversational UI.
#     """
#     # Step 1: Sanitize dangerous content
#     allowed_tags = ["b", "strong", "i", "em", "p", "br"]
#     sanitized = bleach.clean(html, tags=allowed_tags, strip=True)
#
#     # Step 2: Simplify structure with BeautifulSoup
#     soup = BeautifulSoup(sanitized, "html.parser")
#
#     # Flatten unnecessary tags into paragraphs
#     for tag in soup.find_all(True):
#         if tag.name not in allowed_tags:
#             tag.unwrap()  # remove tag but keep text
#
#     # Normalize spacing
#     body_text = soup.get_text("\n", strip=True)
#
#     # Wrap back into simple <p> paragraphs
#     formatted_html = ""
#     for block in body_text.split("\n"):
#         if block.strip():
#             formatted_html += f"<p>{block}</p>\n"
#
#     if verbose:
#         log.debug("Simplified HTML into conversational-friendly format")
#
#     return formatted_html.strip()

if __name__ == "__main__":
    test_html = Path("test.html")
    sanitized = sanitize_and_simplify_html(test_html.read_text())
    test_html.write_text(sanitized)