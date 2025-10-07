with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

from setuptools import setup, find_packages

setup(name='salada', version='1.1.0', packages=find_packages(), long_description=long_description, long_description_content_type='text/markdown', author='ToddyTheNoobDud',
url='https://github.com/ToddyTheNoobDud/Salad')