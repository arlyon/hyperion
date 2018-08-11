from setuptools import setup, find_packages

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hyperion',
    version='1.0',
    url='https://github.com/arlyon/hyperion',
    license='MIT',
    author='arlyon',
    author_email='arlyon@me.com',
    description='CLI and rest api for postcode data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=['hyperion'],
    install_requires=[
        'Click',
        'aiohttp',
        'colorama',
        'uvloop',
        'peewee',
        'geopy',
        'lxml',
        'feedparser'
    ],
    entry_points='''
        [console_scripts]
        hyperion=hyperion.__main__:run
    ''',
)
