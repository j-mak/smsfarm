from pip.download import PipSession
from pip.req import parse_requirements

from setuptools import setup, find_packages

links = []
requires = []

requirements = parse_requirements('requirements.txt', session=PipSession())

for item in requirements:
    # we want to handle package names and also repo urls
    if getattr(item, 'url', None):
        links.append(str(item.url))
    if getattr(item, 'link', None):
        links.append(str(item.link))
    if item.req:
        requires.append(str(item.req))

setup(
    name='smsfarm',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/j-mak/smsfarm',
    license="MIT License",
    author='Jozef "sunny" Mak',
    author_email='sunny@jozefmak.eu',
    description='Python client for smsfarm.sk',
    long_description="Python client for smsfarm.sk",
    install_requires=requires,
    keywords=[
        'smsfarm',
        'sms-client'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    dependency_links=links,
    zip_safe=False,
)
