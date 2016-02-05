__author__ = 'mdavid'

from mock import *
from unittest import TestCase
from wnsresolver import *

class TestInit(TestCase):

    def test_all_args(self):

        wns_resolver = WalletNameResolver(
            resolv_conf='resolv.conf',
            dnssec_root_key='root_key',
            nc_host = '127.0.0.1',
            nc_port = 1234,
            nc_rpcuser='rpcuser',
            nc_rpcpassword='rpcpassword',
            nc_tmpdir='/tmp'
        )

        self.assertEqual('resolv.conf', wns_resolver.resolv_conf)
        self.assertEqual('root_key', wns_resolver.dnssec_root_key)
        self.assertEqual('127.0.0.1', wns_resolver.nc_host)
        self.assertEqual(1234, wns_resolver.nc_port)
        self.assertEqual('rpcuser', wns_resolver.nc_user)
        self.assertEqual('rpcpassword', wns_resolver.nc_password)
        self.assertEqual('/tmp', wns_resolver.nc_tmpdir)

    def test_defaults(self):

        wns_resolver = WalletNameResolver()

        self.assertEqual('/etc/resolv.conf', wns_resolver.resolv_conf)
        self.assertEqual('/usr/local/etc/unbound/root.key', wns_resolver.dnssec_root_key)
        self.assertIsNone(wns_resolver.nc_host)
        self.assertEqual(8336, wns_resolver.nc_port)
        self.assertIsNone(wns_resolver.nc_user)
        self.assertIsNone(wns_resolver.nc_password)
        self.assertIsNone(wns_resolver.nc_tmpdir)


class TestNamecoinOptions(TestCase):

    def test_with_args(self):

        wns_resolver = WalletNameResolver()

        wns_resolver.set_namecoin_options(
            host='127.0.0.1',
            port=1234,
            user='rpcuser',
            password='rpcpassword',
            tmpdir='/tmp'
        )

        self.assertEqual('/etc/resolv.conf', wns_resolver.resolv_conf)
        self.assertEqual('/usr/local/etc/unbound/root.key', wns_resolver.dnssec_root_key)
        self.assertEqual('127.0.0.1', wns_resolver.nc_host)
        self.assertEqual(1234, wns_resolver.nc_port)
        self.assertEqual('rpcuser', wns_resolver.nc_user)
        self.assertEqual('rpcpassword', wns_resolver.nc_password)
        self.assertEqual('/tmp', wns_resolver.nc_tmpdir)

    def test_defaults(self):

        wns_resolver = WalletNameResolver(nc_host='127.0.0.1')
        wns_resolver.set_namecoin_options()

        self.assertEqual('/etc/resolv.conf', wns_resolver.resolv_conf)
        self.assertEqual('/usr/local/etc/unbound/root.key', wns_resolver.dnssec_root_key)
        self.assertIsNone(wns_resolver.nc_host)
        self.assertEqual(8336, wns_resolver.nc_port)
        self.assertIsNone(wns_resolver.nc_user)
        self.assertIsNone(wns_resolver.nc_password)
        self.assertIsNone(wns_resolver.nc_tmpdir)

class TestResolveAvailableCurrencies(TestCase):

    def setUp(self):

        self.patcher1 = patch('wnsresolver.WalletNameResolver.resolve')
        self.patcher2 = patch('bcresolver.NamecoinResolver')

        self.mockWnsResolver = self.patcher1.start()
        self.mockNamecoinResolver = self.patcher2.start()

        self.mockWnsResolver.side_effect = [
            'btc ltc dgc'
        ]

        self.mockNamecoinResolver.return_value.resolve.side_effect = [
            'btc ltc dgc',
        ]

    def tearDown(self):

        self.patcher1.stop()
        self.patcher2.stop()

    def test_go_right(self):

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve_available_currencies('wallet.mattdavid.xyz')

        self.assertEqual(['btc','ltc','dgc'], ret_val)
        self.assertEqual(1, self.mockWnsResolver.call_count)

    def test_go_right_email_format(self):

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve_available_currencies('wallet@mattdavid.xyz')

        self.assertEqual('_wallet.9e9285c79443cf2c0f868b0216308fb0e3ffeb45ade2c10ac67147f5.mattdavid.xyz', self.mockWnsResolver.call_args[0][0])
        self.assertEqual(['btc','ltc','dgc'], ret_val)
        self.assertEqual(1, self.mockWnsResolver.call_count)

    def test_no_name(self):

        wns_resolver = WalletNameResolver()
        self.assertRaises(AttributeError, wns_resolver.resolve_available_currencies, None)
        self.assertEqual(0, self.mockWnsResolver.call_count)

    def test_namecoin_go_right(self):

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve_available_currencies('wallet.mattdavid.bit')

        self.assertEqual(['btc','ltc','dgc'], ret_val)
        self.assertEqual(1, self.mockNamecoinResolver.call_count)
        self.assertEqual(1, self.mockNamecoinResolver.return_value.resolve.call_count)

        self.assertEqual(wns_resolver.nc_host, self.mockNamecoinResolver.call_args[1]['host'])
        self.assertEqual(wns_resolver.nc_user, self.mockNamecoinResolver.call_args[1]['user'])
        self.assertEqual(wns_resolver.nc_password, self.mockNamecoinResolver.call_args[1]['password'])
        self.assertEqual(wns_resolver.nc_port, self.mockNamecoinResolver.call_args[1]['port'])
        self.assertEqual(wns_resolver.nc_tmpdir, self.mockNamecoinResolver.call_args[1]['temp_dir'])

    def test_namecoin_import_error(self):

        self.mockNamecoinResolver.side_effect = ImportError()

        wns_resolver = WalletNameResolver()
        self.assertRaises(WalletNameNamecoinUnavailable, wns_resolver.resolve_available_currencies, 'wallet.mattdavid.bit')
        self.assertEqual(1, self.mockNamecoinResolver.call_count)


class TestResolveWalletName(TestCase):

    def setUp(self):

        self.patcher1 = patch('wnsresolver.WalletNameResolver.resolve')
        self.patcher2 = patch('bcresolver.NamecoinResolver')

        self.mockWnsResolver = self.patcher1.start()
        self.mockNamecoinResolver = self.patcher2.start()

        self.mockWnsResolver.side_effect = [
            'btc',
            '23456789MgDBffBffBff'
        ]

        self.mockNamecoinResolver.return_value.resolve.side_effect = [
            'btc',
            '23456789MgDBffBffBff'
        ]

    def tearDown(self):

        self.patcher1.stop()
        self.patcher2.stop()
        
    def test_go_right(self):
        
        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve_wallet_name('wallet.mattdavid.xyz', 'btc')

        self.assertEqual('23456789MgDBffBffBff', ret_val)
        self.assertEqual(2, self.mockWnsResolver.call_count)

    def test_go_right_email_format(self):

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve_wallet_name('wallet@mattdavid.xyz', 'btc')

        self.assertEqual('_wallet.9e9285c79443cf2c0f868b0216308fb0e3ffeb45ade2c10ac67147f5.mattdavid.xyz', self.mockWnsResolver.call_args_list[0][0][0])
        self.assertEqual('_btc._wallet.9e9285c79443cf2c0f868b0216308fb0e3ffeb45ade2c10ac67147f5.mattdavid.xyz', self.mockWnsResolver.call_args_list[1][0][0])
        self.assertEqual('23456789MgDBffBffBff', ret_val)
        self.assertEqual(2, self.mockWnsResolver.call_count)


    def test_no_name(self):

        wns_resolver = WalletNameResolver()
        self.assertRaises(AttributeError, wns_resolver.resolve_wallet_name, None, 'btc')
        self.assertEqual(0, self.mockWnsResolver.call_count)

    def test_no_currency(self):

        wns_resolver = WalletNameResolver()
        self.assertRaises(AttributeError, wns_resolver.resolve_wallet_name, 'wallet.mattdavid.xyz', None)
        self.assertEqual(0, self.mockWnsResolver.call_count)

    def test_no_currency_list(self):

        wns_resolver = WalletNameResolver()
        self.assertRaises(WalletNameCurrencyUnavailableError, wns_resolver.resolve_wallet_name, 'wallet.mattdavid.xyz', 'dgc')
        self.assertEqual(1, self.mockWnsResolver.call_count)

    def test_no_available_currency(self):

        self.mockWnsResolver.side_effect = None
        self.mockWnsResolver.return_value = None

        wns_resolver = WalletNameResolver()
        self.assertRaises(WalletNameUnavailableError, wns_resolver.resolve_wallet_name, 'wallet.mattdavid.xyz', 'btc')
        self.assertEqual(1, self.mockWnsResolver.call_count)

    def test_namecoin_go_right(self):

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve_wallet_name('wallet.mattdavid.bit', 'btc')

        self.assertEqual('23456789MgDBffBffBff', ret_val)
        self.assertEqual(1, self.mockNamecoinResolver.call_count)
        self.assertEqual(2, self.mockNamecoinResolver.return_value.resolve.call_count)

        self.assertEqual(wns_resolver.nc_host, self.mockNamecoinResolver.call_args[1]['host'])
        self.assertEqual(wns_resolver.nc_user, self.mockNamecoinResolver.call_args[1]['user'])
        self.assertEqual(wns_resolver.nc_password, self.mockNamecoinResolver.call_args[1]['password'])
        self.assertEqual(wns_resolver.nc_port, self.mockNamecoinResolver.call_args[1]['port'])
        self.assertEqual(wns_resolver.nc_tmpdir, self.mockNamecoinResolver.call_args[1]['temp_dir'])

    def test_namecoin_import_error(self):

        self.mockNamecoinResolver.side_effect = ImportError()

        wns_resolver = WalletNameResolver()
        self.assertRaises(WalletNameNamecoinUnavailable, wns_resolver.resolve_wallet_name, 'wallet.mattdavid.bit', 'btc')
        self.assertEqual(1, self.mockNamecoinResolver.call_count)


class TestResolve(TestCase):
    def setUp(self):
        self.patcher1 = patch('wnsresolver.ub_ctx')
        self.patcher2 = patch('wnsresolver.requests')
        self.patcher3 = patch('wnsresolver.os')
        self.patcher4 = patch('wnsresolver.request')
        self.patcher5 = patch('wnsresolver.WalletNameResolver.get_endpoint_host')

        self.mockUnbound = self.patcher1.start()
        self.mockRequests = self.patcher2.start()
        self.mockOS = self.patcher3.start()
        self.mockRequest = self.patcher4.start()
        self.mockGetEndpointHost = self.patcher5.start()

        self.mockResult = Mock()
        self.mockResult.secure = True
        self.mockResult.bogus = False
        self.mockResult.havedata = True
        self.mockResult.data.as_domain_list.return_value = ['Yml0Y29pbjo/cj1odHRwczovL21lcmNoYW50LmNvbS9wYXkucGhwP2glM0QyYTg2MjhmYzJmYmU=']
        self.mockUnbound.return_value.resolve.return_value = (0, self.mockResult)

        self.mockRequests.get.return_value.text = 'test response text'
        self.mockRequest.access_route = ['8.8.8.8']

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
        self.patcher5.stop()

    def test_go_right_startswith_bitcoin_uri(self):

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('bitcoin:?r=https://merchant.com/pay.php?h%3D2a8628fc2fbe', ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_go_right_startswith_http_get_endpoint_returns_lookup_url(self):

        # Setup Test case
        self.mockGetEndpointHost.return_value = 'lookup_url_returned', None
        self.mockResult.data.as_domain_list.return_value = ['aHR0cHM6Ly9iaXAzMmFkZHJlc3MuY29tL2dldG1pbmU=']

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('test response text', ret_val)

        # Validate GET contains b64txt and headers
        self.assertEqual('lookup_url_returned', self.mockRequests.get.call_args[0][0])
        self.assertEqual({'X-Forwarded-For': '8.8.8.8'}, self.mockRequests.get.call_args[1].get('headers'))

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(1, self.mockGetEndpointHost.call_count)
        self.assertEqual(1, self.mockRequests.get.call_count)

    def test_go_right_startswith_http_get_endpoint_returns_return_data(self):

        # Setup test case
        self.mockGetEndpointHost.return_value = None, 'myretdata'
        self.mockResult.data.as_domain_list.return_value = ['aHR0cHM6Ly9iaXAzMmFkZHJlc3MuY29tL2dldG1pbmU=']

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('myretdata', ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(1, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_go_right_b64decode_exception(self):

        # Setup Test case
        self.mockResult.data.as_domain_list.return_value = ['1MSK1PMnDZN4SLDQ6gB4c6GKRExfGD6Gb3']

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('1MSK1PMnDZN4SLDQ6gB4c6GKRExfGD6Gb3', ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_go_right_end_of_chain(self):

        # Setup Test case
        self.mockResult.data.as_domain_list.return_value = ['dGhpc2lzZ3JlYXQx']

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('dGhpc2lzZ3JlYXQx', ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_trust_anchor_missing(self):

        # Setup Test case
        self.mockOS.path.isfile.return_value = False

        wns_resolver = WalletNameResolver()
        self.assertRaisesRegexp(
            Exception,
            'Trust anchor is missing or inaccessible',
            wns_resolver.resolve,
            'wallet.mattdavid.xyz',
            'TXT'
        )

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(0, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_status_not_0(self):

        # Setup Test case
        from wnsresolver import WalletNameLookupError
        self.mockUnbound.return_value.resolve.return_value = (1, self.mockResult)

        wns_resolver = WalletNameResolver()
        self.assertRaises(
            WalletNameLookupError,
            wns_resolver.resolve,
            'wallet.mattdavid.xyz',
            'TXT'
        )

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_insecure_result(self):

        # Setup Test case
        from wnsresolver import WalletNameLookupInsecureError
        self.mockResult.secure = False

        wns_resolver = WalletNameResolver()
        self.assertRaises(
            WalletNameLookupInsecureError,
            wns_resolver.resolve,
            'wallet.mattdavid.xyz',
            'TXT'
        )

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_bogus_result(self):

        # Setup Test case
        from wnsresolver import WalletNameLookupInsecureError
        self.mockResult.bogus = True

        wns_resolver = WalletNameResolver()
        self.assertRaises(
            WalletNameLookupInsecureError,
            wns_resolver.resolve,
            'wallet.mattdavid.xyz',
            'TXT'
        )

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_havedata_false(self):

        # Setup Test case
        self.mockResult.havedata = False

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertIsNone(ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockGetEndpointHost.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_exception_during_lookup_url_get(self):

        # Setup Test case
        self.mockGetEndpointHost.return_value = 'urls', None
        self.mockResult.data.as_domain_list.return_value = ['aHR0cHM6Ly9iaXA3MHBheW1lbnRyZXF1ZXN0LmNvbS9nZXRtaW5l']
        self.mockRequests.get.side_effect = Exception()

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('https://bip70paymentrequest.com/getmine', ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(1, self.mockGetEndpointHost.call_count)
        self.assertEqual(1, self.mockRequests.get.call_count)


class TestGetEndpointHost(TestCase):
    def setUp(self):
        self.patcher1 = patch('wnsresolver.socket')
        self.mockSocket = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right_valid_hostname(self):

        wns_resolver = WalletNameResolver()
        return_url, return_data = wns_resolver.get_endpoint_host('http://www.example.com/pr/uuid')

        self.assertEqual('http://www.example.com/pr/uuid', return_url)
        self.assertIsNone(return_data)

    def test_go_right_valid_ipv4(self):

        wns_resolver = WalletNameResolver()
        return_url, return_data = wns_resolver.get_endpoint_host('https://8.8.8.8/pr/uuid')

        self.assertEqual('https://8.8.8.8/pr/uuid', return_url)
        self.assertIsNone(return_data)

    def test_go_right_valid_ipv6(self):

        wns_resolver = WalletNameResolver()
        return_url, return_data = wns_resolver.get_endpoint_host('https://[2001:4860:4860::8888]/pr/uuid')

        self.assertEqual('https://[2001:4860:4860::8888]/pr/uuid', return_url)
        self.assertIsNone(return_data)

    def test_hostname_localhost(self):

        wns_resolver = WalletNameResolver()
        return_url, return_data = wns_resolver.get_endpoint_host('https://localhost/pr/uuid')

        self.assertIsNone(return_url)
        self.assertEqual('https://localhost/pr/uuid', return_data)

    def test_hostname_is_none(self):

        wns_resolver = WalletNameResolver()
        return_url, return_data = wns_resolver.get_endpoint_host('https://')

        self.assertIsNone(return_url)
        self.assertEqual('https://', return_data)

    def test_gethostbyname_returns_socket_gaierror(self):

        import socket
        self.mockSocket.gaierror = socket.gaierror
        self.mockSocket.gethostbyname.side_effect = self.mockSocket.gaierror

        wns_resolver = WalletNameResolver()
        return_url, return_data = wns_resolver.get_endpoint_host('https://nonexistent_hostname/pr/uuid')

        self.assertIsNone(return_url)
        self.assertEqual('https://nonexistent_hostname/pr/uuid', return_data)

    def test_no_route_ip(self):

        wns_resolver = WalletNameResolver()
        return_url, return_data = wns_resolver.get_endpoint_host('https://192.168.100.1/pr/uuid')

        self.assertIsNone(return_url)
        self.assertEqual('https://192.168.100.1/pr/uuid', return_data)

class TestPreprocessName(TestCase):

    def test_no_change(self):

        wns_resolver = WalletNameResolver()
        name = wns_resolver.preprocess_name('wallet.domain.com')
        self.assertEqual('wallet.domain.com', name)

    def test_email_walletname(self):

        wns_resolver = WalletNameResolver()
        name = wns_resolver.preprocess_name('wallet@domain.com')
        self.assertEqual('9e9285c79443cf2c0f868b0216308fb0e3ffeb45ade2c10ac67147f5.domain.com', name)

    def test_email_with_multiple_at_signs(self):

        wns_resolver = WalletNameResolver()
        name = wns_resolver.preprocess_name('wallet@wallet@domain.com')
        self.assertEqual('9e9285c79443cf2c0f868b0216308fb0e3ffeb45ade2c10ac67147f5.wallet@domain.com', name)