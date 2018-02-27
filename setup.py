from setuptools import setup


def readme():
    with open('README.md') as file:
        return file.read()


setup(
    name='smsfarm',
    version='0.1.0',
    packages=['smsfarm'],
    url='https://github.com/j-mak/smsfarm',
    license="MIT License",
    author='Jozef "sunny" Mak',
    author_email='sunny@jozefmak.eu',
    description='Python client for smsfarm.sk',
    long_description=readme(),
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
    ]
)
