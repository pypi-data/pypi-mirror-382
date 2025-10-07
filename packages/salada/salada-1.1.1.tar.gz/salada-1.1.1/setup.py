from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / 'README.md'
with open(readme_path, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='salada',
    version='1.1.1',
    author='ToddyTheNoobDud',
    description='Lightning-fast async Lavalink client for discord.py',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ToddyTheNoobDud/Salad',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    install_requires=[
        'aiohttp>=3.8.0',
        'discord.py>=2.0.0',
    ],
    extras_require={
        'fast': ['orjson', 'ujson', 'msgpack', 'aiofiles'],
    },
)