from setuptools import setup, find_packages

setup(
    name='salada',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.13.0',
        'orjson>=3.11.3',
        'ujson>=5.11.0',
        'msgpack>=1.1.1',
    ]
)
