__author__ = 'mdavid'

from setuptools import setup

install_requires = [
    'dnspython>=1.12.0'
]

test_requires = [
    'mock>=1.0.1'
]

setup(
    name='wnsresolver',
    version='0.0.6',
    packages=['wnsresolver'],
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite = 'tests',
    url='https://github.com/netkicorp/wns-resolver',
    download_url='https://github.com/netkicorp/wns-resolver/tarball/0.0.6',
    platforms=['any'],
    license='BSD',
    author='mdavid',
    author_email='opensource@netki.com',
    description='Wallet Name Resolver Library'
)

print('Requirement Unbound is not available via pip. Please see README.md for installation information')