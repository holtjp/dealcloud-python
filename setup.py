from setuptools import setup, find_packages


setup(
    name='dealcloud',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['zeep'],
    author="DealCloud, Inc.",
    author_email="support@dealcloud.com",
    description="A Python client for the DealCloud Data Service",
    keywords="dealcloud soap client example"
)
