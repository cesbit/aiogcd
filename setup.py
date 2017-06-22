"""setup.py

Created on: May 19, 2017
   Authors: Jeroen van der Heijden <jeroen@transceptor.technology>
            jomido <https://github.com/jomido>
            egalpin <https://github.com/egalpin>

Upload to PyPI, Thx to: http://peterdowns.com/posts/first-time-with-pypi.html

python3 setup.py register -r pypitest
python3 setup.py sdist upload -r pypitest

python3 setup.py register -r pypi
python3 setup.py sdist upload -r pypi
"""

import setuptools
from distutils.core import setup, Extension

VERSION = '0.9.10'

install_requires = [
    'aiohttp==2.2.0',
    'PyJWT==1.5.0',
    'cryptography==1.9',
    'asyncio_extras==1.3.0'
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
