from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='morwlox123',
    version='1.4.88',
    author='m0rwyak',
    author_email='itzm3gap0n@gmail.com',
    description='lox lox lox pon.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://m0rwi.ru',
    packages=find_packages(),
    install_requires=[''],
    keywords='files speedfiles ',
    project_urls={
    'GitHub': 'https://github.com/gualf5ve/morwlox123'
    },
    python_requires='>=3.6'
)