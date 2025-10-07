from setuptools import setup, find_packages
with open('README.md', 'r', encoding='utf-8') as f: readme = f.read()
setup(
    name='salada',
    version='1.0.2',
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.13.0',
        'orjson>=3.11.3',
        'ujson>=5.11.0',
        'msgpack>=1.1.1',
    ],
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=["salada", "lavalink", "discord.py", "discord"],
)
