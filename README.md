# WNS Resolver

Netki Wallet Name Resolver Library

# General

The Netki Wallet Name Resolver library allows you to quickly integrate the Wallet Name standard into your digital
currency platform. Using the Wallet Name Service allows you to avoid difficult Bitcoin, Dogecoin, Litecoin, etc. wallet addresses
and instead use a much more memorable naming scheme that runs on top of DNS using DNSSEC to keep the Chain-of-Trust unbroken.

The Netki Wallet Name Resolver library has evolved to handle base64 encoded endpoint URLs serving a raw BIP32 generated 
wallet address or bitcoin URI pointing to a BIP70 payment request URL. When encountering such URLs after resolving a Wallet Name, the library will retrieve the URL 
and return the response. As part of our reference implementation for BIP32 and BIP70 requests, the response is expected 
in the BIP72 format as returned from [Addressimo](https://github.com/netkicorp/addressimo) - https://github.com/netkicorp/addressimo

# Requirements

## Python Modules
- [dnspython](http://www.dnspython.org) - http://www.dnspython.org
- [pyUnbound](https://www.unbound.net/documentation/pyunbound/) - https://www.unbound.net/documentation/pyunbound/

**NOTE:** pyUnbound is **NOT** available via pip. Please follow the instructions below to install and setup PyUnbound

# PyUnbound Setup
This version of **wns-resolver** has been tested with Unbound v1.4.22. ([https://unbound.net/downloads/unbound-1.4.22.tar.gz](https://unbound.net/downloads/unbound-1.4.22.tar.gz))

## Install via Repository

**unbound-python** is available via installation by yum and is available in the [EPEL](https://fedoraproject.org/wiki/EPEL) repository.

    [user@host ~]$ yum install -y unbound-python
    
This will install unbound-python, compat-libevent, and unbound-libs packages.

## Manual Download, Installation and Setup 

When ./configure-ing unbound, make sure to use the **--with-pyunbound** flag. This will make pyunbound available after make and make install

Please refer to [https://www.unbound.net/documentation/pyunbound/install.html](https://www.unbound.net/documentation/pyunbound/install.html) for Unbound installation help.

Use the [unbound-anchor](https://www.unbound.net/documentation/unbound-anchor.html) tool to setup the ICANN-supplied DNSSEC Root Trust Anchor.

Make sure to set the **PYTHON_VERSION** environment variable if you have multiple *Python* versions installed, otherwise
the module will be installed for the default system *Python* version.

    [user@host ~]$ export set PYTHON_VERSION=2.7
    [user@host ~]$ wget https://unbound.net/downloads/unbound-1.4.22.tar.gz
    [user@host ~]$ tar -xzf unbound-1.4.22-py.tar.gz
    [user@host ~]$ cd unbound-1.4.22
    [user@host ~]$ ./configure --with-pyunbound
    [user@host ~]$ make
    [user@host ~]$ make install

# Usage

**wnsresolver** provides the wnsresolver.WalletNameResolver class which has the resolve_wallet_name(name, currency) function available. 
This can be used to resolve any Wallet Name. If our [bcresolver](https://github.com/netkicorp/blockchain-resolver) module is also installed, the WalletNameResolver will handle
both ICANN and Namecoin Blockchain-based domains.

## Success Example (Wallet Name)

    >>> from wnsresolver import WalletNameResolver
    >>> wns_resolver = WalletNameResolver()
    >>> wns_resolver.resolve('wallet.justinnewton.me', 'btc')
    1P5faasXEt4BVgMaQjVo6TmvFXdGgZ8FF9

## Success Example (BIP70 bitcoin URI)

    >>> from wnsresolver import WalletNameResolver
    >>> wns_resolver = WalletNameResolver()
    >>> wns_resolver.resolve_wallet_name('bip70.netki.xyz', 'btc')
    'bitcoin:1FHz8bpEE5qUZ9XhfjzAbCCwo5bT1HMNAc?amount=100&r=https%3A%2F%2Faddressimo.netki.com%2Fresolve%2F8cea7807e11e4c3898e0a2ee54feedc6%3Fbip70%3Dtrue%26amount%3D100'

## Success Example (BIP32 bitcoin URI)

    >>> from wnsresolver import WalletNameResolver
    >>> wns_resolver = WalletNameResolver()
    >>> wns_resolver.resolve_wallet_name('bip32.netki.xyz', 'btc')
    'bitcoin:1FHz8bpEE5qUZ9XhfjzAbCCwo5bT1HMNAc'

## Wallet Name Not Found

    >>> from wnsresolver import WalletNameResolver
    >>> wns_resolver = WalletNameResolver()
    >>> wns_resolver.resolve_wallet_name('really-notfound.justinnewton.me','btc')
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "/Users/mdavid/PycharmProjects/wns-resolver/wnsresolver/__init__.py", line 67, in resolve_wallet_name
        raise WalletNameUnavailableError
    WalletNameUnavailableError
    
## Additional Examples

Additional examples are available in the examples/ directory


