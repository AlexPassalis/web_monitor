import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import utils


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_reuses_existing_connected_browser():
    """
    Test that get_browser reuses existing browser when it's connected and from same loop
    """
    mock_browser = MagicMock()
    mock_browser.is_connected.return_value = True

    utils.browser_data = {
        'p': MagicMock(),
        'browser': mock_browser,
        'loop_id': id(asyncio.get_running_loop()),
    }

    browser = await utils.get_browser()

    assert browser == mock_browser
    assert utils.browser_data['browser'] == mock_browser


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_recreates_when_loop_id_mismatch():
    """
    Test that get_browser creates new instance when loop ID doesn't match
    """
    mock_browser = MagicMock()
    mock_browser.is_connected.return_value = True

    mock_browser_new = MagicMock()
    mock_browser_new.is_connected.return_value = True

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser_new

    utils.browser_data = {
        'p': MagicMock(),
        'browser': mock_browser,
        'loop_id': 12345,
    }

    with patch('config.utils.playwright.async_api.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=mock_playwright)
        browser = await utils.get_browser()

    assert browser == mock_browser_new
    assert utils.browser_data['browser'] == mock_browser_new


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_reconnects_when_disconnected():
    """
    Test that get_browser creates new instance when existing browser is disconnected
    """
    mock_browser_disconnected = MagicMock()
    mock_browser_disconnected.is_connected.return_value = False

    mock_browser_new = MagicMock()
    mock_browser_new.is_connected.return_value = True

    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser_new

    utils.browser_data = {
        'p': MagicMock(),
        'browser': mock_browser_disconnected,
        'loop_id': id(asyncio.get_running_loop()),
    }

    with patch('config.utils.playwright.async_api.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=mock_playwright)
        browser = await utils.get_browser()

    assert browser == mock_browser_new
    assert utils.browser_data['browser'] == mock_browser_new


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_browser_cleanup_closes_browser():
    """
    Test that browser_cleanup closes browser and stops playwright
    """
    mock_browser = AsyncMock()
    mock_playwright = AsyncMock()

    current_loop = asyncio.get_running_loop()
    utils.browser_data = {
        'p': mock_playwright,
        'browser': mock_browser,
        'loop_id': id(current_loop),
    }

    await utils.browser_cleanup()

    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert utils.browser_data is None


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_browser_cleanup_handles_exception():
    """
    Test that browser_cleanup sets browser_data to None even when close fails
    """
    mock_browser = AsyncMock()
    mock_browser.close.side_effect = Exception('Close failed')
    mock_playwright = AsyncMock()

    current_loop = asyncio.get_running_loop()
    utils.browser_data = {
        'p': mock_playwright,
        'browser': mock_browser,
        'loop_id': id(current_loop),
    }

    with pytest.raises(Exception, match='Close failed'):
        await utils.browser_cleanup()

    assert utils.browser_data is None


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_reuses_async_lock():
    """
    Test that get_browser reuses existing async lock when called multiple times in same loop
    """
    mock_browser = MagicMock()
    mock_browser.is_connected.return_value = True

    utils.browser_data = {
        'p': MagicMock(),
        'browser': mock_browser,
        'loop_id': id(asyncio.get_running_loop()),
    }

    browser_1 = await utils.get_browser()
    browser_2 = await utils.get_browser()

    assert browser_1 == mock_browser
    assert browser_2 == mock_browser


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_browser_cleanup_skips_when_loop_id_mismatch():
    """
    Test that browser_cleanup doesn't clean up browser from different loop
    """
    mock_browser = AsyncMock()
    mock_playwright = AsyncMock()

    utils.browser_data = {
        'p': mock_playwright,
        'browser': mock_browser,
        'loop_id': 99999,
    }

    await utils.browser_cleanup()

    mock_browser.close.assert_not_called()
    mock_playwright.stop.assert_not_called()
    assert utils.browser_data is not None
