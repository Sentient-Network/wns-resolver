__author__ = 'mdavid'

import iptools
import os
import re
import requests
import socket
from base64 import b64decode
from dns import rdatatype
from flask import request
from unbound import ub_ctx, RR_TYPE_TXT, RR_CLASS_IN
from urlparse import urlparse


class WalletNameLookupError(Exception):
    pass

class WalletNameLookupInsecureError(Exception):
    pass

class WalletNameCurrencyUnavailableError(Exception):
    pass

class WalletNameNamecoinUnavailable(Exception):
    pass

class WalletNameUnavailableError(Exception):
    pass

class WalletNameResolutionError(Exception):
    pass

class WalletNameResolver:

    def __init__(self, resolv_conf='/etc/resolv.conf', dnssec_root_key='/usr/local/etc/unbound/root.key', nc_host=None, nc_port=8336, nc_rpcuser=None, nc_rpcpassword=None, nc_tmpdir=None):

        self.resolv_conf = resolv_conf
        self.dnssec_root_key = dnssec_root_key
        self.nc_host = nc_host
        self.nc_port = nc_port
        self.nc_user = nc_rpcuser
        self.nc_password = nc_rpcpassword
        self.nc_tmpdir = nc_tmpdir

    def set_namecoin_options(self, host=None, port=8336, user=None, password=None, tmpdir=None):

        self.nc_host = host
        self.nc_port = port
        self.nc_user = user
        self.nc_password = password
        self.nc_tmpdir = tmpdir

    def resolve_available_currencies(self, name):

        if not name:
            raise AttributeError('resolve_wallet_name requires both name and currency')

        if name.endswith('.bit'):
            # Namecoin Resolution Required
            try:
                from bcresolver import NamecoinResolver
                resolver = NamecoinResolver(
                    resolv_conf=self.resolv_conf,
                    dnssec_root_key=self.dnssec_root_key,
                    host=self.nc_host,
                    user=self.nc_user,
                    password=self.nc_password,
                    port=self.nc_port,
                    temp_dir=self.nc_tmpdir
                )
            except ImportError:
                raise WalletNameNamecoinUnavailable('Namecoin Lookup Required the bcresolver module.')
        else:
            # Default ICANN Resolution
            resolver = self

        # Resolve Top-Level Available Currencies
        currency_list_str = resolver.resolve('_wallet.%s' % name, 'TXT')
        if not currency_list_str:
            return []
        return currency_list_str.split()


    def resolve_wallet_name(self, name, currency):

        if not name or not currency:
            raise AttributeError('resolve_wallet_name requires both name and currency')

        if name.endswith('.bit'):
            # Namecoin Resolution Required
            try:
                from bcresolver import NamecoinResolver
                resolver = NamecoinResolver(
                    resolv_conf=self.resolv_conf,
                    dnssec_root_key=self.dnssec_root_key,
                    host=self.nc_host,
                    user=self.nc_user,
                    password=self.nc_password,
                    port=self.nc_port,
                    temp_dir=self.nc_tmpdir
                )
            except ImportError:
                raise WalletNameNamecoinUnavailable('Namecoin Lookup Required the bcresolver module.')
        else:
            # Default ICANN Resolution
            resolver = self

        # Resolve Top-Level Available Currencies
        currency_list_str = resolver.resolve('_wallet.%s' % name, 'TXT')
        if not currency_list_str:
            raise WalletNameUnavailableError

        if not [x for x in currency_list_str.split() if x == currency]:
            raise WalletNameCurrencyUnavailableError

        return resolver.resolve('_%s._wallet.%s' % (currency, name), 'TXT')

    def resolve(self, name, qtype):

        ctx = ub_ctx()
        ctx.resolvconf(self.resolv_conf)

        if not os.path.isfile(self.dnssec_root_key):
            raise Exception('Trust anchor is missing or inaccessible')
        else:
            ctx.add_ta_file(self.dnssec_root_key)

        status, result = ctx.resolve(name, rdatatype.from_text(qtype), RR_CLASS_IN)
        if status != 0:
            raise WalletNameLookupError

        if not result.secure or result.bogus:
            raise WalletNameLookupInsecureError
        elif not result.havedata:
            return None
        else:
            # We got data
            txt = result.data.as_domain_list()

            # Reference implementation for serving BIP32 and BIP70 requests
            try:
                # BIP32/BIP70 URL will be base64 encoded. Some wallet addresses fail decode.
                # If it fails, assume wallet address or unknown and return
                b64txt = b64decode(txt[0])
            except:
                return txt[0]

            # Fully qualified bitcoin URI, return as is
            if b64txt.startswith('bitcoin:'):
                return b64txt
            elif re.match(r'^https?:\/\/', b64txt):
                try:
                    # Identify localhost or link_local/multicast/private IPs and return without issuing a GET.
                    lookup_url, return_data = WalletNameResolver.get_endpoint_host(b64txt)

                    if return_data:
                        return return_data

                    # Try the URL. Returning response.text and expect a Bitcoin URI as delivered from Addressimo.
                    response = requests.get(lookup_url, headers={'X-Forwarded-For': '%s' % request.access_route[0]})
                    return response.text
                except Exception:
                    # Return base64 decoded value if we cannot perform a GET on the URL to allow requester to handle.
                    return b64txt
            else:
                # If you made it this far, assume wallet address and return
                return txt[0]

    @staticmethod
    def get_endpoint_host(b64txt):
        url = urlparse(b64txt)

        if url.hostname == 'localhost':
            return None, b64txt

        if not url.hostname:
            return None, b64txt

        no_route_ip_range_list = iptools.IpRangeList(
            iptools.ipv4.LOCALHOST,
            iptools.ipv4.PRIVATE_NETWORK_10,
            iptools.ipv4.PRIVATE_NETWORK_172_16,
            iptools.ipv4.PRIVATE_NETWORK_192_168,
            iptools.ipv4.LINK_LOCAL,
            iptools.ipv4.MULTICAST,
            iptools.ipv6.LOCALHOST,
            iptools.ipv6.PRIVATE_NETWORK,
            iptools.ipv6.LINK_LOCAL,
            iptools.ipv6.MULTICAST
        )

        if not iptools.ipv4.validate_ip(url.hostname) and not iptools.ipv6.validate_ip(url.hostname):
            # This will catch hostnames, determine if reachable, and return as a URL to fetch or raw value to return.
            try:
                socket.gethostbyname(url.hostname)
                return url.geturl(), None
            except socket.gaierror:
                return None, b64txt

        elif url.hostname in no_route_ip_range_list:
            return None, b64txt

        return url.geturl(), None


if __name__ == '__main__':

    wn_resolver = WalletNameResolver()
    wn_resolver.set_namecoin_options(
        host='localhost',
        user='rpcuser',
        password='rpcpassword'
    )
    result = wn_resolver.resolve_wallet_name('bip70.netki.xyz', 'btc')
    print result
