import urllib.parse

import httpx

POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
POLLINATIONS_MODEL = "sana"


class ImageServiceError(Exception):
    """Raised when the image provider fails or is unreachable."""


class NoImageReturnedError(Exception):
    """Raised when the provider responded but didn't return image bytes."""


class ImageService:
    """Wraps Pollinations.ai's free, keyless text-to-image API. No API
    key needed — it's a public, unauthenticated endpoint, which is why
    there's no "not configured" error case here unlike the other
    services in this app."""

    def generate_image(self, prompt: str) -> tuple[bytes, str]:
        """Returns (image_bytes, content_type) — Pollinations may return
        PNG or JPEG depending on the model, so the caller shouldn't
        assume a fixed format."""
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"{POLLINATIONS_BASE_URL}/{encoded_prompt}"

        try:
            response = httpx.get(
                url, params={"model": POLLINATIONS_MODEL, "nologo": "true"}, timeout=60
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
