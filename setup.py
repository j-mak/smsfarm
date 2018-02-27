from setuptools import setup


def readme():
    with open('README.md') as file:
        return file.read()


def license_file():
    with open('LICENSE.md') as file:
        return file.read()


setup(
    name='smsfarm',
    version='0.1.0',
    packages=['smsfarm'],
    url='https://github.com/j-mak/smsfarm',
    license=license_file(),
    author='Jozef "sunny" Mak',
    author_email='sunny@jozefmak.eu',
    description='Python client for smsfarm.sk',
    long_description=readme(),
    keywords=[
        'smsfarm',
        'sms-client'
    ],
    classifiers=[

    ]
)
