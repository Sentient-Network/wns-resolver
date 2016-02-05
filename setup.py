__author__ = 'mdavid'

from setuptools import setup

install_requires = [
    'dnspython>=1.12.0',
    'requests>=2.5.1'
]

test_requires = [
    'mock>=1.0.1'
]

setup(
    name='wnsresolver',
    version='0.0.8',
    packages=['wnsresolver'],
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite = 'tests',
    url='https://github.com/netkicorp/wns-resolver',
    download_url='https://github.com/netkicorp/wns-resolver/tarball/0.0.7',
    platforms=['any'],
    license='BSD',
    author='mdavid',
    author_email='opensource@netki.com',
    description='Wallet Name Resolver Library'
)

print('Requirement Unbound is not available via pip. Please see README.md for installation information')