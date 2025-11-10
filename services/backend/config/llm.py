import base64
import logging
from huggingface_hub import InferenceClient
from config import HUGGINGFACE_API_TOKEN

logger = logging.getLogger(__name__)


def _encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode image bytes to base64 data URL."""

    b64_string = base64.b64encode(image_bytes).decode('utf-8')
    return f'data:image/png;base64,{b64_string}'


def compare_screenshots(
    previous_screenshot_bytes: bytes,
    current_screenshot_bytes: bytes,
    website_url: str,
) -> str | None:
    """Compare two screenshots using Hugging Face's vision model to identify changes."""

    client = InferenceClient(token=HUGGINGFACE_API_TOKEN)

    previous_b64 = _encode_image_to_base64(previous_screenshot_bytes)
    current_b64 = _encode_image_to_base64(current_screenshot_bytes)

    prompt = (
        f'Compare these two screenshots of {website_url}. '
        f'The first image is the previous state, the second is the current state. '
        f'Describe what changed between them in a concise summary. '
        f'Focus on visual changes, content updates, '
        f'layout modifications, or new elements. '
        f'If there are no significant changes, say so.'
    )

    try:
        response = client.chat_completion(
            model='meta-llama/Llama-3.2-11B-Vision-Instruct',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {'type': 'image_url', 'image_url': {'url': previous_b64}},
                        {'type': 'image_url', 'image_url': {'url': current_b64}},
                    ],
                }
            ],
            max_tokens=500,
        )

        if not response.choices or len(response.choices) == 0:
            logger.error(f'No response choices for {website_url}')
            return None

        summary = response.choices[0].message.content
        logger.info(f'Generated change summary for {website_url}')
        return summary

    except Exception as e:
        logger.error(f'Failed to compare screenshots for {website_url}: {str(e)}')
        return None
