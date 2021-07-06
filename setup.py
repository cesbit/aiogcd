"""setup.py

Created on: May 19, 2017
   Authors: Jeroen van der Heijden <jeroen@transceptor.technology>
            jomido <https://github.com/jomido>
            egalpin <https://github.com/egalpin>

Upload to PyPI:

python setup.py sdist
twine upload --repository pypitest dist/aiogcd-X.X.X.tar.gz
twine upload --repository pypi dist/aiogcd-X.X.X.tar.gz
"""

import setuptools
from distutils.core import setup, Extension

VERSION = '0.11.14'

install_requires = [
    'aiohttp>=2',
    'PyJWT>=1',
    'cryptography>=1',
    'asyncio_extras>=1'
]

setup(
    name='aiogcd',
    packages=[
        'aiogcd',
        'aiogcd.connector',
        'aiogcd.orm',
        'aiogcd.orm.properties'],
    version=VERSION,
    description='Async Google Cloud Datastore API',
    author='Jeroen van der Heijden',
    author_email='jeroen@transceptor.technology',
    url='https://github.com/transceptor-technology/aiogcd',
    download_url='https://'
        'github.com/transceptor-technology/'
        'aiogcd/tarball/{}'.format(VERSION),
    keywords=['gcd', 'datastore', 'connector'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development'
    ],
)
