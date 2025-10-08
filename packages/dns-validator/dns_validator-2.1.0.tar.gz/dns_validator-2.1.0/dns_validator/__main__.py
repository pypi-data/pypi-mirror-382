#!/usr/bin/env python3
"""
Main entry point for DNS Validator when installed as a package

Author: Matisse Urquhart
Contact: me@maturqu.com
License: GNU AGPL v3.0
"""

from dns_validator.dns_validator import cli

if __name__ == '__main__':
    cli()