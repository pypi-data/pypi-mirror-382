import pytest
import asyncio
from humanlike_automation.browsersessionmanager import BrowserSessionManager
from humanlike_automation.browserhandler import BrowserHandler
from humanlike_automation.webpagehandler import WebPageHandler

# Dummy scraper function for testing
async def dummy_scraper(web_handler, url):
    assert hasattr(web_handler, 'close')
    # Simulate some async work
    await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_initialize_and_close_session():
    manager = BrowserSessionManager(max_instances=2)
    session = await manager.initialize_session(site="https://example.com", profile="test", proxy=None, profile_folder="test_profile", stealth_mode=False)
    assert session is not None
    assert 'handler' in session
    await manager.close_session(session)
    assert session not in manager.active_sessions

@pytest.mark.asyncio
async def test_max_instances_limit():
    manager = BrowserSessionManager(max_instances=1)
    session1 = await manager.initialize_session(site="https://example.com", profile="test1", proxy=None, profile_folder="test_profile1", stealth_mode=False)
    session2 = await manager.initialize_session(site="https://example.com", profile="test2", proxy=None, profile_folder="test_profile2", stealth_mode=False)
    assert session1 is not None
    assert session2 is None  # Should not allow more than max_instances
    await manager.close_session(session1)

@pytest.mark.asyncio
async def test_stealth_mode_session():
    manager = BrowserSessionManager(max_instances=1)
    session = await manager.initialize_session(site="https://example.com", profile="stealth", proxy=None, profile_folder="stealth_profile", stealth_mode=True)
    assert session is not None
    await manager.close_session(session)

@pytest.mark.asyncio
async def test_restart_session():
    manager = BrowserSessionManager(max_instances=1)
    session = await manager.initialize_session(site="https://example.com", profile="restart", proxy=None, profile_folder="restart_profile", stealth_mode=False)
    assert session is not None
    restarted = await manager.restart_session(session)
    assert restarted is not None
    await manager.close_session(restarted)

@pytest.mark.asyncio
async def test_process_url_and_queue():
    manager = BrowserSessionManager(max_instances=2)
    urls = [f"https://example.com/page{i}" for i in range(3)]
    await manager.run_scraping_tasks(urls, dummy_scraper, site="https://example.com", profile="queue", profile_folder="queue_profile")

@pytest.mark.asyncio
async def test_invalid_url_handling():
    manager = BrowserSessionManager(max_instances=1)
    # Simulate an invalid URL (should not raise, just log error)
    session = await manager.initialize_session(site="invalid-url", profile="bad", proxy=None, profile_folder="bad_profile", stealth_mode=False)
    # Depending on implementation, session may be None or may fail later
    assert session is None or 'handler' in session

@pytest.mark.asyncio
async def test_proxy_session():
    manager = BrowserSessionManager(max_instances=1)
    # Use a dummy proxy string for test
    session = await manager.initialize_session(site="https://example.com", profile="proxy", proxy="http://127.0.0.1:8080", profile_folder="proxy_profile", stealth_mode=False)
    assert session is not None
    await manager.close_session(session)
