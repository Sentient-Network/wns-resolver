__author__ = 'mdavid'

from wnsresolver import *

if __name__ == '__main__':

    wallet_name = 'wallet.justinnewton.me'
    currency = 'btc'
    retries = 3
    resolved_address = None

    resolver = WalletNameResolver(
        resolv_conf='/etc/resolv.conf',
        dnssec_root_key='/usr/local/etc/unbound/root.key'
    )

    for _ in range(retries):
        try:
            # Resolve the Bitcoin wallet address for wallet.justinnewnton.me
            resolved_address = resolver.resolve_wallet_name(wallet_name, currency)
            print 'Wallet Name [%s] resolved address %s [CURRENCY: %s]' % (wallet_name, resolved_address, currency)

        except WalletNameLookupError:
            print('Wallet Name [%s] resolution failed, retrying.' % wallet_name)
            continue

        except WalletNameUnavailableError:
            print('Wallet Name [%s] is setup incorrectly' % wallet_name)

        except WalletNameCurrencyUnavailableError:
            print('Wallet Name [%s] DOES NOT have an entry for currency %s' % (wallet_name, currency))

        except WalletNameLookupInsecureError:
            print('Wallet Name [%s] resolution DNSSEC Resolution is insecure (chain of trust incomplete)')

        except WalletNameNamecoinUnavailable:
            print('Wallet Name [%s] requires the bcresolver module be installed to complete. Please see https://github.com/netkicorp/blockchain-resolver for more information.')

        break

    if not resolved_address:
        print('Unable to resolve Wallet Name [%s]' % wallet_name)
