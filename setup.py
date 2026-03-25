"""setup.py

Created on: May 19, 2017
   Authors: Jeroen van der Heijden <jeroen@cesbit.com>
            jomido <https://github.com/jomido>
            egalpin <https://github.com/egalpin>
            Koos Joosten <koos@cesbit.com>

Upload to PyPI:

python -m build
twine upload --repository pypitest dist/aiogcd-X.X.X*
twine upload --repository pypi dist/aiogcd-X.X.X*
"""

from setuptools import setup

VERSION = '1.0.2'

try:
    with open('README.md', 'r') as f:
        long_description = f.read()
except IOError:
    long_description = ''

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
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jeroen van der Heijden',
    author_email='jeroen@cesbit.com',
    url='https://github.com/cesbit/aiogcd',
    download_url='https://'
        'github.com/cesbit/'
        'aiogcd/tarball/{}'.format(VERSION),
    keywords=['gcd', 'datastore', 'connector'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development'
    ],
)
