# DNS Validator

A comprehensive cross-platform CLI tool for DNS validation, featuring delegation checks, propagation testing, and DNS provider settings analysis.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/license-%20%20GNU%20GPLv3%20-green?style=plastic)

## Features

- **DNS Delegation Check**: Verify DNS delegation and authoritative name servers
- **Propagation Check**: Test DNS propagation across multiple public DNS servers
- **Multi-Provider DNS Settings**: Detect and analyze DNS settings from 50+ providers including Cloudflare, AWS Route 53, Google Cloud DNS, Azure DNS, and more
- **🔐 Secure Credential Management**: Encrypted storage and management of API keys for multiple providers
- **Verbose CLI Output**: Detailed logging and colored output for better debugging
- **Cross-platform Compatibility**: Works on Windows, Linux, and macOS
- **Concurrent Processing**: Fast parallel DNS queries for efficient testing

## Installation

### Method 1: Direct Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/HereLiesHugo/dns-validator.git
cd dns-validator

# Install dependencies
pip install -r requirements.txt

# Make the script executable (Linux/macOS)
chmod +x dns_validator.py
```

## Usage

### Basic Commands

```bash
# Check DNS delegation
python dns_validator.py delegation example.com

# Check DNS propagation (A record)
python dns_validator.py propagation example.com

# Check propagation for specific record type
python dns_validator.py propagation example.com --type MX

# Check propagation with expected value validation
python dns_validator.py propagation example.com --expected "192.168.1.1"

# Detect DNS providers
python dns_validator.py providers example.com

# List all supported providers
python dns_validator.py list-providers

# Check provider settings (with API integration)
python dns_validator.py provider example.com --api-token your_token

# Check Cloudflare settings (legacy command)
python dns_validator.py cloudflare example.com --api-token your_cf_token

# Run all checks at once
python dns_validator.py full example.com

# Manage API credentials (NEW!)
python dns_validator.py creds add Cloudflare production --api-token YOUR_TOKEN
python dns_validator.py creds list
python dns_validator.py provider example.com --provider cloudflare --cred-name production

# Enable verbose output for any command
python dns_validator.py --verbose delegation example.com
```

### Advanced Usage Examples

```bash
# Comprehensive check with all options
python dns_validator.py full example.com \
  --type A \
  --expected "192.168.1.1" \
  --api-token your_cloudflare_token

# Check MX record propagation
python dns_validator.py propagation example.com --type MX --verbose

# Validate CNAME record
python dns_validator.py propagation subdomain.example.com --type CNAME
```

## Command Reference

### Global Options

- `--verbose, -v`: Enable verbose output with detailed logging

### Commands

#### `delegation <domain>`
Check DNS delegation for a domain.

**Features:**
- Validates authoritative name servers
- Checks parent delegation
- Identifies delegation issues

#### `propagation <domain>`
Check DNS propagation across multiple DNS servers.

**Options:**
- `--type, -t`: DNS record type (default: A)
- `--expected, -e`: Expected value to validate against

**Features:**
- Tests 8 major public DNS servers (Google, Cloudflare, Quad9, etc.)
- Concurrent queries for fast results
- Consistency checking across servers
- Response time measurement

#### `providers <domain>`
Detect DNS providers for a domain.

**Features:**
- Identifies primary and secondary DNS providers
- Shows all detected providers
- Lists nameserver details

#### `list-providers`
List all supported DNS providers.

**Features:**
- Shows 50+ supported DNS providers organized by category
- Indicates API integration status
- Displays detection patterns

#### `provider <domain>`
Check DNS provider settings with API integration.

**Options:**
- `--provider`: Specify provider to check
- `--api-token`: API token for provider integration
- `--api-secret`: API secret for providers that require it
- `--access-key`: Access key for AWS Route 53
- `--secret-key`: Secret key for AWS Route 53
- `--service-account`: Service account file for Google Cloud DNS

**Features:**
- Auto-detects DNS provider
- API integration for detailed settings
- DNS record retrieval and analysis
- Provider-specific configuration display

#### `cloudflare <domain>`
Check Cloudflare DNS settings (legacy command).

**Options:**
- `--api-token`: Cloudflare API token for detailed information

**Features:**
- Detects Cloudflare nameserver usage
- Retrieves zone settings (with API token)
- Lists all DNS records with proxy status
- Shows security and performance settings

#### `full <domain>`
Perform all DNS checks in sequence.

**Options:**
- `--type, -t`: DNS record type for propagation check
- `--expected, -e`: Expected value for validation
- `--api-token`: Cloudflare API token

**Features:**
- Comprehensive validation report
- Summary of all issues found
- Recommended actions

#### `creds`
🔐 **Manage API credentials for DNS providers (NEW!)**

**Subcommands:**
- `add <provider> <name>`: Add new credentials with secure encryption
- `list`: Display all stored credentials (secrets masked)
- `edit <provider> <name>`: Interactively edit existing credentials
- `delete <provider> <name>`: Remove stored credentials
- `test <provider> <name> <domain>`: Test credentials with API call
- `export <file>`: Export credential structure (optional --include-secrets)
- `clear`: Remove all stored credentials

**Features:**
- 🔒 AES-256 encryption for all sensitive data
- 🏢 Multi-provider support (Cloudflare, AWS, Google Cloud, Azure, DigitalOcean)
- 👥 Multiple credential sets per provider (staging, production, etc.)
- 🔐 Interactive secure input for sensitive fields
- 💾 Secure storage in `~/.dns-validator/` directory
- 📤 Safe export/backup functionality

## DNS Servers Tested

The propagation check queries the following public DNS servers:

| Provider | Primary | Secondary |
|----------|---------|-----------|
| Google | 8.8.8.8 | 8.8.4.4 |
| Cloudflare | 1.1.1.1 | 1.0.0.1 |
| Quad9 | 9.9.9.9 | - |
| OpenDNS | 208.67.222.222 | - |
| Verisign | 64.6.64.6 | - |
| Level3 | 4.2.2.1 | - |

## Supported DNS Providers

The tool supports detection and analysis of 50+ DNS providers:

### 🌐 Major Cloud Providers
- **Cloudflare** (✅ Full API Support + 🔐 Credential Management)
- **AWS Route 53** (✅ Full API Support + 🔐 Credential Management)
- **Google Cloud DNS** (✅ Full API Support + 🔐 Credential Management)
- **Azure DNS** (✅ Full API Support + 🔐 Credential Management)
- **DigitalOcean** (✅ Full API Support + 🔐 Credential Management)

### 🚀 VPS/Cloud Hosting
- DigitalOcean, Linode, Vultr, OVH, Hetzner, Scaleway

### 🏢 Domain Registrars
- Namecheap, GoDaddy, Name.com, Domain.com, Gandi, Hover, Dynadot

### 🔒 Security/Privacy DNS
- Quad9, OpenDNS

### ⚡ Performance DNS
- DNS Made Easy, NS1, Constellix, UltraDNS

### 🆓 Free DNS Services
- No-IP, DuckDNS, FreeDNS, Hurricane Electric

And many more! Use `python dns_validator.py list-providers` to see the complete list.

## API Integration

### 🔐 Secure Credential Management (NEW!)

Store your API credentials securely with AES encryption:

```bash
# Add credentials interactively (most secure)
dns-validator creds add Cloudflare production --interactive

# Add credentials via command line
dns-validator creds add AWS staging --access-key AKIA123... --secret-key abc123...

# List stored credentials
dns-validator creds list

# Use stored credentials
dns-validator provider example.com --provider cloudflare --cred-name production

# Test credentials
dns-validator creds test Cloudflare production example.com
```

### Cloudflare
```bash
# Using stored credentials (recommended)
dns-validator creds add Cloudflare production --api-token YOUR_CF_TOKEN
dns-validator provider example.com --provider cloudflare --cred-name production

# Direct usage (less secure)
dns-validator provider example.com --api-token YOUR_CF_TOKEN
```

### AWS Route 53
```bash
# Using stored credentials (recommended)
dns-validator creds add AWS production --access-key YOUR_KEY --secret-key YOUR_SECRET --region us-east-1
dns-validator provider example.com --provider aws --cred-name production

# Direct usage
dns-validator provider example.com --access-key YOUR_KEY --secret-key YOUR_SECRET

# Using default AWS credentials
dns-validator provider example.com --provider "AWS Route 53"
```
**Prerequisites:** `pip install boto3`

### Google Cloud DNS
```bash
# Using service account file
dns-validator provider example.com --service-account /path/to/service-account.json --project-id YOUR_PROJECT
```
**Prerequisites:** `pip install google-cloud-dns`

### Azure DNS
```bash
# Using service principal
dns-validator provider example.com --subscription-id SUB_ID --tenant-id TENANT_ID --client-id CLIENT_ID --client-secret CLIENT_SECRET

# Using default Azure credentials
dns-validator provider example.com --subscription-id SUB_ID --resource-group RG_NAME
```
**Prerequisites:** `pip install azure-mgmt-dns azure-identity`

### DigitalOcean
```bash
dns-validator provider example.com --api-token YOUR_DO_TOKEN
```

For detailed setup instructions, see [CLOUD_PROVIDER_SETUP.md](CLOUD_PROVIDER_SETUP.md).

## Examples

### Check if DNS changes have propagated

```bash
# After updating A record to point to new server
python dns_validator.py propagation example.com --expected "192.168.1.100"
```

### Troubleshoot DNS delegation issues

```bash
# Check if nameservers are properly configured
python dns_validator.py delegation example.com --verbose
```

### Detect and validate DNS provider

```bash
# Detect DNS provider
python dns_validator.py providers example.com

# Store credentials securely
python dns_validator.py creds add Cloudflare production --api-token your_token

# Check provider settings with stored credentials
python dns_validator.py provider example.com --provider cloudflare --cred-name production

# Direct API usage (less secure)
python dns_validator.py provider example.com --api-token your_token

# Legacy Cloudflare check
python dns_validator.py cloudflare example.com --api-token your_token
```

### Credential Management Examples

```bash
# Add multiple environments
python dns_validator.py creds add Cloudflare staging --interactive
python dns_validator.py creds add Cloudflare production --interactive
python dns_validator.py creds add AWS dev --access-key KEY1 --secret-key SECRET1
python dns_validator.py creds add AWS prod --access-key KEY2 --secret-key SECRET2

# List all stored credentials
python dns_validator.py creds list

# Test credentials
python dns_validator.py creds test Cloudflare production example.com

# Export backup (structure only)
python dns_validator.py creds export backup.json

# Export with secrets (use with caution)
python dns_validator.py creds export full-backup.json --include-secrets

# Edit existing credentials
python dns_validator.py creds edit Cloudflare production

# Delete credentials
python dns_validator.py creds delete AWS dev

# Clear all credentials
python dns_validator.py creds clear
```

### Complete domain validation

```bash
# Run all checks with verbose output
python dns_validator.py --verbose full example.com --api-token your_token
```

## Output Colors

The tool uses colored output for better readability:

- 🟢 **Green**: Success, valid configurations
- 🔴 **Red**: Errors, failed validations
- 🟡 **Yellow**: Warnings, inconsistencies
- 🔵 **Blue**: Information, processing status
- 🟣 **Magenta**: Headers, summaries

## Troubleshooting

### Common Issues

1. **"No module named 'dns'"**: Install dnspython
   ```bash
   pip install dnspython
   ```

2. **Cloudflare API errors**: Check your API token permissions

3. **Timeout errors**: Some DNS servers may be slow; this is normal

4. **Permission denied (Linux/macOS)**: Make the script executable
   ```bash
   chmod +x dns_validator.py
   ```

### Windows PowerShell

If you encounter execution policy issues on Windows:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Requirements

- Python 3.7 or higher
- Internet connection for DNS queries
- Optional: Cloudflare API token for enhanced features

## Dependencies

- `click`: Command-line interface framework
- `dnspython`: DNS toolkit for Python
- `requests`: HTTP library for API calls
- `colorama`: Cross-platform colored terminal text
- `tabulate`: Pretty-print tabular data
- `cryptography`: Secure credential encryption (AES-256)
- `concurrent.futures`: Parallel processing
- **Optional Cloud SDKs:**
  - `boto3`: AWS Route 53 integration
  - `google-cloud-dns`: Google Cloud DNS integration
  - `azure-mgmt-dns` + `azure-identity`: Azure DNS integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/HereLiesHugo/dns-validator/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/HereLiesHugo/dns-validator/issues)
- 📖 **Documentation**: [README](https://github.com/HereLiesHugo/dns-validator#readme)

## Changelog

### v2.0.0
- 🔐 **NEW: Secure Credential Management System**
  - AES-256 encrypted storage of API keys and tokens
  - Multi-provider credential support (Cloudflare, AWS, Google Cloud, Azure, DigitalOcean)
  - Multiple credential sets per provider (staging, production, etc.)
  - Interactive secure input for sensitive data
  - Credential testing, export, and backup functionality
- 🌐 **Enhanced API Integration**
  - Full API support for AWS Route 53, Google Cloud DNS, Azure DNS, DigitalOcean
  - Improved error handling and debugging
  - Better provider detection (52+ providers supported)
- 🛡️ **Security Improvements**
  - Credentials never stored in plain text
  - Secure credential directory (~/.dns-validator/)
  - Safe export options (with/without secrets)
- 🚀 **Performance & UX**
  - Faster concurrent DNS queries
  - Better error messages and help text
  - Improved cross-platform compatibility

### v1.0.0
- Initial release
- DNS delegation checking
- DNS propagation testing across 8 public servers
- Cloudflare integration with API support
- Cross-platform compatibility
- Verbose logging and colored output
- Concurrent DNS queries for performance
