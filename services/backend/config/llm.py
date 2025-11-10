import base64
import logging
from openai import OpenAI
from config import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)


def get_openrouter_client() -> OpenAI:
    """Get OpenAI client configured for OpenRouter."""

    return OpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=OPENROUTER_API_KEY,
    )


def compare_screenshots(
    previous_screenshot_bytes: bytes,
    current_screenshot_bytes: bytes,
    website_url: str,
) -> str | None:
    """Compare two screenshots using Gemini 2.0 Flash and return a summary of changes."""

    client = get_openrouter_client()

    previous_b64 = base64.b64encode(previous_screenshot_bytes).decode('utf-8')
    current_b64 = base64.b64encode(current_screenshot_bytes).decode('utf-8')

    try:
        response = client.chat.completions.create(
            model='google/gemini-2.0-flash-exp:free',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': f'Compare these two screenshots of {website_url}. '
                            f'The first image is the previous version, '
                            f'the second is the current version. '
                            f'Describe what changed between them in a concise summary. '
                            f'Focus on visual changes, content updates, layout modifications, '
                            f'or new elements. If there are no significant changes, say so.',
                        },
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:image/png;base64,{previous_b64}'},
                        },
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:image/png;base64,{current_b64}'},
                        },
                    ],
                }
            ],
            max_tokens=500,
        )

        summary = response.choices[0].message.content
        logger.info(f'Generated change summary for {website_url}')
        return summary

    except Exception as e:
        logger.error(f'Failed to compare screenshots for {website_url}: {e}')
        return None
