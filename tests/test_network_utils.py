from unittest import TestCase

from utils.network_utils import host_pings, wait_for_ping

class NotTestHostPings(TestCase):

    def test_host_pings_returns_true_for_responsive_host(self):
        self.assertTrue(host_pings({}, 'localhost'))

    def test_host_pings_returns_false_for_unresponsive_host(self):
        self.assertFalse(host_pings({}, 'some_hostname_that_is_almost_certainly_not_real', 0))


class TestWaitForPing(TestCase):

    def test_wait_for_ping_returns_true_for_responsive_host(self):
        test_config: dict = { 'current_imd_ip': 'localhost' }
        self.assertTrue(wait_for_ping(test_config, True))
