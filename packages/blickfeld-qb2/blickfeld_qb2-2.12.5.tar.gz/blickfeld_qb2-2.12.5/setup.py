from setuptools import find_packages, setup

setup(
    name="blickfeld_qb2",
    version="2.12.5",
    author="Blickfeld GmbH",
    author_email="opensource@blickfeld.com",
    url="https://github.com/Blickfeld/blickfeld-qb2",
    description="Python package to communicate securely with Qb2 LiDAR devices of the Blickfeld GmbH",
    packages=find_packages(),
    install_requires=[
        "numpy",
        # Betterproto dependencies
        "grpclib >= 0.4.1",
        "python-dateutil >= 2.8",
        "dataclasses >= 0.7;python_version<'3.7'"
	],
)

