from setuptools import setup

setup(
    name="carabas2tools",
    version="1.0.0",
    description="A collection of tools to work with CARABAS-II dataset",
    url="https://github.com/gabrielluizep/carabas2tools",
    author="Gabriel Luiz Espindola Pedro",
    author_email="gabrielluizep.glep@gmail.com",
    packages=["carabas2tools"],
    package_data={},
    install_requires=["numpy", "scipy", "pandas"],
)
