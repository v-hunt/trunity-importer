from setuptools import setup, find_packages


setup(
    name='trunity_importer',
    version='0.2',
    packages=find_packages(),
    scripts=['trunity_importer/bin/trunity-importer'],
    install_requires=[
        'lxml',
        'beautifulsoup4',
        'trunity-3-client>=0.6.1',
      ],
    url='',
    license='MIT',
    author='hunting',
    author_email='VicHunting@yandex.ua',
    description='Library for importing content from various sources to Trunity 3 LMS.'
)
