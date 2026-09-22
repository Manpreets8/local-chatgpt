import re
import urllib.parse

import httpx

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
POLLINATIONS_MODEL = "sana"

# The free "sana" model defaults hard toward photorealism, especially for
# landscape/wide scenes — testing showed even negative prompts can't fully
# override that for those compositions. It does respond well to explicit
# style/material keywords for single-subject or character prompts, so we
# reinforce style only when the user's own prompt signals they want one
# (never force a look the user didn't ask for).
_STYLE_KEYWORDS = re.compile(
    r"\b(3d|three[- ]?d|pixar|cgi|cartoon|animat\w*|claymation|toy|figurine)\b",
    re.IGNORECASE,
)
_STYLE_BOOST = (
    ", 3D render, CGI, Pixar animation style, glossy toy-like materials, "
    "studio lighting, octane render, stylized illustration, not photorealistic"
)


class ImageServiceError(Exception):
    """Raised when the image provider fails or is unreachable."""


class NoImageReturnedError(Exception):
    """Raised when the provider responded but didn't return image bytes."""


class ImageService:
    """Wraps Pollinations.ai's free, keyless text-to-image API. No API
    key needed — it's a public, unauthenticated endpoint, which is why
    there's no "not configured" error case here unlike the other
    services in this app."""

    def _build_prompt(self, prompt: str) -> str:
        if _STYLE_KEYWORDS.search(prompt):
            return prompt + _STYLE_BOOST
        return prompt

    def generate_image(self, prompt: str) -> tuple[bytes, str]:
        """Returns (image_bytes, content_type) — Pollinations may return
        PNG or JPEG depending on the model, so the caller shouldn't
        assume a fixed format."""
        built_prompt = self._build_prompt(prompt)
        encoded_prompt = urllib.parse.quote(built_prompt)
        url = f"{POLLINATIONS_BASE_URL}/{encoded_prompt}"

        try:
            response = httpx.get(
                url,
                params={
                    "model": POLLINATIONS_MODEL,
                    "nologo": "true",
                    "enhance": "true",
                    "width": 1024,
                    "height": 1024,
                },
                timeout=60,
            )
        except httpx.HTTPError as exc:
            raise ImageServiceError(f"Could not reach the image service: {exc}") from exc

        if response.status_code != 200:
            raise ImageServiceError(
                f"Image service returned {response.status_code}: {response.text[:200]}"
            )

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise NoImageReturnedError("The image service didn't return an image for this prompt.")

        return response.content, content_type


image_service = ImageService()

__all__ = ["image_service", "ImageService", "ImageServiceError", "NoImageReturnedError"]
