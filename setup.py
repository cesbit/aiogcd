import setuptools
from distutils.core import setup, Extension

VERSION = '0.9.1'

setup(
    name='aiogcd',
    packages=['aiogcd'],
    version=VERSION,
    description='Async Google Cloud Datastore API',
    author='Jeroen van der Heijden',
    author_email='jeroen@transceptor.technology',
    url='https://github.com/transceptor-technology/aiogcd',
    download_url='https://'
        'github.com/transceptor-technology/'
        'aiogcd/tarball/{}'.format(VERSION),
    keywords=['gcd', 'datastore', 'connector'],
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