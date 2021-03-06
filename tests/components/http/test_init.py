"""The tests for the Home Assistant HTTP component."""
import logging
import unittest

from homeassistant.setup import async_setup_component

import homeassistant.components.http as http


class TestView(http.HomeAssistantView):
    """Test the HTTP views."""

    name = 'test'
    url = '/hello'

    async def get(self, request):
        """Return a get request."""
        return 'hello'


async def test_registering_view_while_running(hass, aiohttp_client,
                                              aiohttp_unused_port):
    """Test that we can register a view while the server is running."""
    await async_setup_component(
        hass, http.DOMAIN, {
            http.DOMAIN: {
                http.CONF_SERVER_PORT: aiohttp_unused_port(),
            }
        }
    )

    await hass.async_start()
    # This raises a RuntimeError if app is frozen
    hass.http.register_view(TestView)


class TestApiConfig(unittest.TestCase):
    """Test API configuration methods."""

    def test_api_base_url_with_domain(hass):
        """Test setting API URL with domain."""
        api_config = http.ApiConfig('example.com')
        assert api_config.base_url == 'http://example.com:8123'

    def test_api_base_url_with_ip(hass):
        """Test setting API URL with IP."""
        api_config = http.ApiConfig('1.1.1.1')
        assert api_config.base_url == 'http://1.1.1.1:8123'

    def test_api_base_url_with_ip_and_port(hass):
        """Test setting API URL with IP and port."""
        api_config = http.ApiConfig('1.1.1.1', 8124)
        assert api_config.base_url == 'http://1.1.1.1:8124'

    def test_api_base_url_with_protocol(hass):
        """Test setting API URL with protocol."""
        api_config = http.ApiConfig('https://example.com')
        assert api_config.base_url == 'https://example.com:8123'

    def test_api_base_url_with_protocol_and_port(hass):
        """Test setting API URL with protocol and port."""
        api_config = http.ApiConfig('https://example.com', 433)
        assert api_config.base_url == 'https://example.com:433'

    def test_api_base_url_with_ssl_enable(hass):
        """Test setting API URL with use_ssl enabled."""
        api_config = http.ApiConfig('example.com', use_ssl=True)
        assert api_config.base_url == 'https://example.com:8123'

    def test_api_base_url_with_ssl_enable_and_port(hass):
        """Test setting API URL with use_ssl enabled and port."""
        api_config = http.ApiConfig('1.1.1.1', use_ssl=True, port=8888)
        assert api_config.base_url == 'https://1.1.1.1:8888'

    def test_api_base_url_with_protocol_and_ssl_enable(hass):
        """Test setting API URL with specific protocol and use_ssl enabled."""
        api_config = http.ApiConfig('http://example.com', use_ssl=True)
        assert api_config.base_url == 'http://example.com:8123'


async def test_api_base_url_with_domain(hass):
    """Test setting API URL."""
    result = await async_setup_component(hass, 'http', {
        'http': {
            'base_url': 'example.com'
        }
    })
    assert result
    assert hass.config.api.base_url == 'http://example.com'


async def test_api_base_url_with_ip(hass):
    """Test setting api url."""
    result = await async_setup_component(hass, 'http', {
        'http': {
            'server_host': '1.1.1.1'
        }
    })
    assert result
    assert hass.config.api.base_url == 'http://1.1.1.1:8123'


async def test_api_base_url_with_ip_port(hass):
    """Test setting api url."""
    result = await async_setup_component(hass, 'http', {
        'http': {
            'base_url': '1.1.1.1:8124'
        }
    })
    assert result
    assert hass.config.api.base_url == 'http://1.1.1.1:8124'


async def test_api_no_base_url(hass):
    """Test setting api url."""
    result = await async_setup_component(hass, 'http', {
        'http': {
        }
    })
    assert result
    assert hass.config.api.base_url == 'http://127.0.0.1:8123'


async def test_not_log_password(hass, aiohttp_client, caplog):
    """Test access with password doesn't get logged."""
    assert await async_setup_component(hass, 'api', {
        'http': {
            http.CONF_API_PASSWORD: 'some-pass'
        }
    })
    client = await aiohttp_client(hass.http.app)
    logging.getLogger('aiohttp.access').setLevel(logging.INFO)

    resp = await client.get('/api/', params={
        'api_password': 'some-pass'
    })

    assert resp.status == 200
    logs = caplog.text

    # Ensure we don't log API passwords
    assert '/api/' in logs
    assert 'some-pass' not in logs


async def test_proxy_config(hass):
    """Test use_x_forwarded_for must config together with trusted_proxies."""
    assert await async_setup_component(hass, 'http', {
        'http': {
            http.CONF_USE_X_FORWARDED_FOR: True,
            http.CONF_TRUSTED_PROXIES: ['127.0.0.1']
        }
    }) is True


async def test_proxy_config_only_use_xff(hass):
    """Test use_x_forwarded_for must config together with trusted_proxies."""
    assert await async_setup_component(hass, 'http', {
        'http': {
            http.CONF_USE_X_FORWARDED_FOR: True
        }
    }) is not True


async def test_proxy_config_only_trust_proxies(hass):
    """Test use_x_forwarded_for must config together with trusted_proxies."""
    assert await async_setup_component(hass, 'http', {
        'http': {
            http.CONF_TRUSTED_PROXIES: ['127.0.0.1']
        }
    }) is not True
