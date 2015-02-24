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