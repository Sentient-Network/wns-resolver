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

        self.mockUnbound = self.patcher1.start()
        self.mockRequests = self.patcher2.start()
        self.mockOS = self.patcher3.start()

        self.mockResult = Mock()
        self.mockResult.secure = True
        self.mockResult.bogus = False
        self.mockResult.havedata = True
        self.mockResult.data.as_domain_list.return_value = ['Yml0Y29pbjo/cj1odHRwczovL21lcmNoYW50LmNvbS9wYXkucGhwP2glM0QyYTg2MjhmYzJmYmU=']
        self.mockUnbound.return_value.resolve.return_value = (0, self.mockResult)

        self.mockRequests.get.return_value.text = 'test response text'

    def test_go_right_startswith_bitcoin_uri(self):

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('bitcoin:?r=https://merchant.com/pay.php?h%3D2a8628fc2fbe', ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_go_right_startswith_http(self):

        # Setup Test case
        self.mockResult.data.as_domain_list.return_value = ['aHR0cHM6Ly9iaXAzMmFkZHJlc3MuY29tL2dldG1pbmU=']
        self.mockRequests.get.return_value.json.return_value = {'data': {'wallet_address': '1btcwalletaddress'}}

        wns_resolver = WalletNameResolver()
        ret_val = wns_resolver.resolve('wallet.mattdavid.xyz', 'TXT')

        # Validate response
        self.assertEqual('test response text', ret_val)

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(1, self.mockRequests.get.call_count)

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
        self.assertEqual(0, self.mockRequests.get.call_count)

    def test_wallet_name_resolution_error(self):

        # Setup Test case
        from wnsresolver import WalletNameResolutionError
        self.mockResult.data.as_domain_list.return_value = ['aHR0cHM6Ly9iaXA3MHBheW1lbnRyZXF1ZXN0LmNvbS9nZXRtaW5l']
        self.mockRequests.get.side_effect = Exception()

        wns_resolver = WalletNameResolver()
        self.assertRaises(
            WalletNameResolutionError,
            wns_resolver.resolve,
            'wallet.mattdavid.xyz',
            'TXT'
        )

        # Validate all calls
        self.assertEqual(1, self.mockUnbound.call_count)
        self.assertEqual(1, self.mockUnbound.return_value.resolve.call_count)
        self.assertEqual(1, self.mockRequests.get.call_count)
