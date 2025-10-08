from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dns-validator",
    version="2.0.1",
    author="Matisse Urquhart",
    author_email="me@maturqu.com",
    description="A comprehensive DNS validation tool with delegation, propagation, and provider settings checks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HereLiesHugo/dns-validator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "dnspython>=2.3.0",
        "requests>=2.28.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "pycryptodome>=3.15.0",
        "cryptography>=41.0.0",
        "setuptools>=65.5.0",
        "boto3>=1.26.0",
        "google-cloud-dns>=0.34.0",
        "azure-mgmt-dns>=8.0.0",
        "azure-identity>=1.12.0",
    ],
    entry_points={
        "console_scripts": [
            "dns-validator=dns_validator.dns_validator:cli",
            "dnsval=dns_validator.dns_validator:cli",
        ],
    },
    keywords="dns validation delegation propagation cloudflare nameservers cli",
    project_urls={
        "Bug Reports": "https://github.com/HereLiesHugo/dns-validator/issues",
        "Source": "https://github.com/HereLiesHugo/dns-validator",
        "Documentation": "https://github.com/HereLiesHugo/dns-validator#readme",
    },
)
