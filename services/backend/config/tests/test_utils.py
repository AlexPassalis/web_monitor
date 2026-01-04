import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import utils


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_reuses_existing_connected_browser(reset_browser_state):
    """
    Test that get_browser reuses existing browser when it's connected
    """
    mock_browser = MagicMock()
    mock_browser.is_connected.return_value = True

    loop_id = id(asyncio.get_running_loop())
    utils.browser_data[loop_id] = {
        'p': MagicMock(),
        'browser': mock_browser,
    }

    browser = await utils.get_browser()

    assert browser == mock_browser


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_creates_new_when_not_exists(reset_browser_state):
    """
    Test that get_browser creates new browser when none exists for current loop
    """
    mock_browser_new = MagicMock()
    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser_new

    with patch('config.utils.playwright.async_api.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=mock_playwright)
        browser = await utils.get_browser()

    assert browser == mock_browser_new
    loop_id = id(asyncio.get_running_loop())
    assert utils.browser_data[loop_id]['browser'] == mock_browser_new


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_reconnects_when_disconnected(reset_browser_state):
    """
    Test that get_browser creates new instance when existing browser is disconnected
    """
    mock_browser_disconnected = MagicMock()
    mock_browser_disconnected.is_connected.return_value = False

    mock_browser_new = MagicMock()
    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser_new

    loop_id = id(asyncio.get_running_loop())
    utils.browser_data[loop_id] = {
        'p': MagicMock(),
        'browser': mock_browser_disconnected,
    }

    with patch('config.utils.playwright.async_api.async_playwright') as mock_pw:
        mock_pw.return_value.start = AsyncMock(return_value=mock_playwright)
        browser = await utils.get_browser()

    assert browser == mock_browser_new
    assert utils.browser_data[loop_id]['browser'] == mock_browser_new


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_browser_cleanup_closes_browser(reset_browser_state):
    """
    Test that browser_cleanup closes browser and stops playwright
    """
    mock_browser = AsyncMock()
    mock_playwright = AsyncMock()

    loop_id = id(asyncio.get_running_loop())
    utils.browser_data[loop_id] = {
        'p': mock_playwright,
        'browser': mock_browser,
    }

    await utils.browser_cleanup()

    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert loop_id not in utils.browser_data


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_browser_cleanup_noop_when_no_browser(reset_browser_state):
    """
    Test that browser_cleanup does nothing when no browser exists for current loop
    """
    await utils.browser_cleanup()

    loop_id = id(asyncio.get_running_loop())
    assert loop_id not in utils.browser_data


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_browser_reuses_async_lock(reset_browser_state):
    """
    Test that get_browser reuses existing async lock when called multiple times in same loop
    """
    mock_browser = MagicMock()
    mock_browser.is_connected.return_value = True

    loop_id = id(asyncio.get_running_loop())
    utils.browser_data[loop_id] = {
        'p': MagicMock(),
        'browser': mock_browser,
    }

    browser_1 = await utils.get_browser()
    lock_1 = utils.async_locks.get(loop_id)

    browser_2 = await utils.get_browser()
    lock_2 = utils.async_locks.get(loop_id)

    assert browser_1 == mock_browser
    assert browser_2 == mock_browser
    assert lock_1 is lock_2


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_browser_cleanup_removes_async_lock(reset_browser_state):
    """
    Test that browser_cleanup removes the async lock for the current loop
    """
    mock_browser = AsyncMock()
    mock_playwright = AsyncMock()

    loop_id = id(asyncio.get_running_loop())
    utils.browser_data[loop_id] = {
        'p': mock_playwright,
        'browser': mock_browser,
    }
    utils.async_locks[loop_id] = asyncio.Lock()

    await utils.browser_cleanup()

    assert loop_id not in utils.async_locks
