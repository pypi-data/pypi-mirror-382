#!/usr/bin/env python3
"""
DNS Validator CLI - A comprehensive DNS validation tool

Author: Matisse Urquhart
Contact: me@maturqu.com
License: GNU AGPL v3.0
"""

import click
import dns.resolver
import dns.zone  
import dns.query
import dns.message
import requests
import sys
import time
import socket
import getpass
from typing import List, Dict, Optional, Tuple
from colorama import init, Fore, Style
from tabulate import tabulate
import concurrent.futures
import threading
from datetime import datetime
from .api_key_manager import APIKeyManager

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class DNSValidator:
    """Main DNS validation class"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.lock = threading.Lock()
        
    def log(self, message: str, color: str = Fore.WHITE, level: str = "INFO"):
        """Thread-safe logging with color support"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with self.lock:
            if self.verbose or level in ["ERROR", "WARNING"]:
                print(f"{color}[{timestamp}] {level}: {message}{Style.RESET_ALL}")
    
    def check_delegation(self, domain: str) -> Dict:
        """Check DNS delegation for a domain"""
        self.log(f"Checking DNS delegation for {domain}", Fore.CYAN)
        
        result = {
            "domain": domain,
            "authoritative_servers": [],
            "parent_servers": [],
            "delegation_valid": False,
            "errors": []
        }
        
        try:
            # Get authoritative name servers from the domain's zone
            ns_records = dns.resolver.resolve(domain, 'NS')
            result["authoritative_servers"] = [str(ns) for ns in ns_records]
            self.log(f"Found {len(result['authoritative_servers'])} authoritative servers", Fore.GREEN)
            
            # Check parent delegation
            parent_domain = '.'.join(domain.split('.')[1:])
            if parent_domain:
                try:
                    parent_ns = dns.resolver.resolve(parent_domain, 'NS')
                    result["parent_servers"] = [str(ns) for ns in parent_ns]
                    self.log(f"Found {len(result['parent_servers'])} parent servers", Fore.GREEN)
                except Exception as e:
                    self.log(f"Could not resolve parent NS records: {e}", Fore.YELLOW, "WARNING")
            
            # Verify delegation consistency
            if result["authoritative_servers"]:
                result["delegation_valid"] = True
                self.log("DNS delegation appears valid", Fore.GREEN)
            else:
                result["errors"].append("No authoritative servers found")
                self.log("No authoritative servers found", Fore.RED, "ERROR")
                
        except dns.resolver.NXDOMAIN:
            error_msg = f"Domain {domain} does not exist"
            result["errors"].append(error_msg)
            self.log(error_msg, Fore.RED, "ERROR")
        except Exception as e:
            error_msg = f"Error checking delegation: {str(e)}"
            result["errors"].append(error_msg)
            self.log(error_msg, Fore.RED, "ERROR")
        
        return result
    
    def check_propagation(self, domain: str, record_type: str = 'A', expected_value: str = None) -> Dict:
        """Check DNS propagation across multiple public DNS servers"""
        self.log(f"Checking DNS propagation for {domain} ({record_type} record)", Fore.CYAN)
        
        # Popular public DNS servers
        dns_servers = [
            ("Google Primary", "8.8.8.8"),
            ("Google Secondary", "8.8.4.4"),
            ("Cloudflare Primary", "1.1.1.1"),
            ("Cloudflare Secondary", "1.0.0.1"),
            ("Quad9", "9.9.9.9"),
            ("OpenDNS", "208.67.222.222"),
            ("Verisign", "64.6.64.6"),
            ("Level3", "4.2.2.1")
        ]
        
        result = {
            "domain": domain,
            "record_type": record_type,
            "expected_value": expected_value,
            "servers": {},
            "propagated": True,
            "consistency": True
        }
        
        def check_server(server_info):
            name, ip = server_info
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [ip]
                resolver.timeout = 5
                resolver.lifetime = 10
                
                response = resolver.resolve(domain, record_type)
                values = [str(record) for record in response]
                
                self.log(f"{name} ({ip}): {', '.join(values)}", Fore.GREEN)
                
                return name, {
                    "ip": ip,
                    "values": values,
                    "response_time": response.response.time * 1000,  # Convert to ms
                    "status": "success"
                }
            except dns.resolver.NXDOMAIN:
                self.log(f"{name} ({ip}): NXDOMAIN", Fore.RED)
                return name, {"ip": ip, "values": [], "status": "nxdomain"}
            except Exception as e:
                self.log(f"{name} ({ip}): Error - {str(e)}", Fore.YELLOW)
                return name, {"ip": ip, "values": [], "status": "error", "error": str(e)}
        
        # Check all servers concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(check_server, server): server for server in dns_servers}
            
            for future in concurrent.futures.as_completed(futures):
                name, server_result = future.result()
                result["servers"][name] = server_result
        
        # Analyze results
        successful_responses = [s for s in result["servers"].values() if s["status"] == "success"]
        
        if not successful_responses:
            result["propagated"] = False
            self.log("DNS record not found on any server", Fore.RED, "ERROR")
        else:
            # Check consistency across servers
            all_values = [set(s["values"]) for s in successful_responses]
            if len(set(frozenset(values) for values in all_values)) > 1:
                result["consistency"] = False
                self.log("Inconsistent DNS responses detected across servers", Fore.YELLOW, "WARNING")
            
            # Check against expected value if provided
            if expected_value:
                matches = any(expected_value in s["values"] for s in successful_responses)
                if not matches:
                    result["propagated"] = False
                    self.log(f"Expected value '{expected_value}' not found", Fore.RED, "ERROR")
        
        return result
    
    def detect_dns_provider(self, domain: str) -> Dict:
        """Detect DNS provider based on nameservers"""
        self.log(f"Detecting DNS provider for {domain}", Fore.CYAN)
        
        # DNS provider patterns (expanded list)
        provider_patterns = {
            "Cloudflare": ["cloudflare.com", "ns.cloudflare.com"],
            "AWS Route 53": ["awsdns", "amazonaws.com", "amzndns"],
            "Google Cloud DNS": ["googledomains.com", "google.com", "ns-cloud"],
            "Azure DNS": ["azure-dns.com", "azure-dns.net", "azure-dns.org", "azure-dns.info"],
            "DigitalOcean": ["digitalocean.com", "ns1.digitalocean.com", "ns2.digitalocean.com", "ns3.digitalocean.com"],
            "Namecheap": ["namecheap.com", "registrar-servers.com"],
            "GoDaddy": ["domaincontrol.com", "godaddy.com"],
            "Quad9": ["quad9.net"],
            "OpenDNS": ["opendns.com", "umbrella.com"],
            "Verisign": ["verisign-grs.com"],
            "DNS Made Easy": ["dnsmadeeasy.com"],
            "Dyn": ["dynect.net", "dyn.com"],
            "Hurricane Electric": ["he.net"],
            "ClouDNS": ["cloudns.net"],
            "Porkbun": ["porkbun.com"],
            "Name.com": ["name.com"],
            "Domain.com": ["domain.com"],
            "Network Solutions": ["worldnic.com", "networksolutions.com"],
            "1&1 IONOS": ["1and1.com", "ionos.com", "ui-dns.com"],
            "Hostinger": ["hostinger.com"],
            "Bluehost": ["bluehost.com"],
            "Hover": ["hover.com"],
            "Gandi": ["gandi.net"],
            "Dynadot": ["dynadot.com"],
            "eNom": ["enom.com"],
            "Register.com": ["register.com"],
            "Tucows": ["tucows.com"],
            "FastDomain": ["fastdomain.com"],
            "Linode": ["linode.com"],
            "Vultr": ["vultr.com"],
            "OVH": ["ovh.net", "ovh.com"],
            "Hetzner": ["hetzner.com"],
            "Scaleway": ["scaleway.com"],
            "No-IP": ["no-ip.com"],
            "DuckDNS": ["duckdns.org"],
            "FreeDNS": ["afraid.org"],
            "Zonomi": ["zonomi.com"],
            "NS1": ["nsone.net"],
            "Constellix": ["constellix.com"],
            "UltraDNS": ["ultradns.com", "ultradns.net"],
            "Neustar": ["neustar.biz"],
            "Easydns": ["easydns.com"],
            "Rage4": ["r4ns.com"],
            "PowerDNS": ["powerdns.com"],
            "BuddyNS": ["buddyns.com"],
            "GeoDNS": ["geodns.com"],
            "PointDNS": ["pointhq.com"],
            "Route53 Resolver": ["resolver.dns-oarc.net"],
            "Yandex DNS": ["yandex.net"],
            "Selectel": ["selectel.ru"],
            "Reg.ru": ["reg.ru"],
            "Timeweb": ["timeweb.ru"]
        }
        
        result = {
            "domain": domain,
            "detected_providers": [],
            "nameservers": [],
            "primary_provider": "Unknown",
            "errors": []
        }
        
        try:
            ns_records = dns.resolver.resolve(domain, 'NS')
            nameservers = [str(ns).lower().rstrip('.') for ns in ns_records]
            result["nameservers"] = nameservers
            
            # Check each nameserver against provider patterns
            detected_providers = set()
            for nameserver in nameservers:
                for provider, patterns in provider_patterns.items():
                    if any(pattern in nameserver for pattern in patterns):
                        detected_providers.add(provider)
                        self.log(f"Detected {provider} nameserver: {nameserver}", Fore.GREEN)
            
            result["detected_providers"] = list(detected_providers)
            
            if detected_providers:
                # Primary provider is the first detected (most common pattern)
                result["primary_provider"] = list(detected_providers)[0]
                self.log(f"Primary DNS provider: {result['primary_provider']}", Fore.GREEN)
            else:
                self.log("No known DNS provider detected", Fore.YELLOW, "WARNING")
                
        except Exception as e:
            result["errors"].append(f"Could not resolve nameservers: {str(e)}")
            self.log(f"Error detecting provider: {str(e)}", Fore.RED, "ERROR")
        
        return result
    
    def check_provider_settings(self, domain: str, provider: str = None, api_credentials: Dict = None) -> Dict:
        """Check DNS provider settings with API integration"""
        if not provider:
            detection_result = self.detect_dns_provider(domain)
            provider = detection_result.get("primary_provider", "Unknown")
        
        self.log(f"Checking {provider} settings for {domain}", Fore.CYAN)
        
        result = {
            "domain": domain,
            "provider": provider,
            "records": [],
            "settings": {},
            "errors": [],
            "api_available": False
        }
        
        # Provider-specific API integrations
        if provider == "Cloudflare":
            if api_credentials and api_credentials.get("api_token"):
                result.update(self._check_cloudflare_api(domain, api_credentials["api_token"]))
            else:
                result["errors"].append("Cloudflare API token required")
        elif provider == "AWS Route 53":
            result.update(self._check_route53_api(domain, api_credentials or {}))
        elif provider == "Google Cloud DNS":
            result.update(self._check_google_dns_api(domain, api_credentials or {}))
        elif provider == "Azure DNS":
            result.update(self._check_azure_dns_api(domain, api_credentials or {}))
        elif provider == "DigitalOcean":
            result.update(self._check_digitalocean_api(domain, api_credentials or {}))
        else:
            result["errors"].append(f"No API integration available for {provider}")
            self.log(f"No API integration for {provider}", Fore.YELLOW, "WARNING")
        
        return result
    
    def _check_cloudflare_api(self, domain: str, api_token: str) -> Dict:
        """Check Cloudflare API settings"""
        result = {"api_available": True}
        
        try:
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            # Get zone ID
            zones_response = requests.get(
                f'https://api.cloudflare.com/client/v4/zones?name={domain}',
                headers=headers,
                timeout=10
            )
            
            if zones_response.status_code == 200:
                zones_data = zones_response.json()
                if zones_data['success'] and zones_data['result']:
                    zone_id = zones_data['result'][0]['id']
                    zone_info = zones_data['result'][0]
                    
                    result["settings"] = {
                        "status": zone_info.get('status', 'unknown'),
                        "plan": zone_info.get('plan', {}).get('name', 'unknown'),
                        "development_mode": zone_info.get('development_mode', False),
                        "security_level": zone_info.get('security_level', 'unknown'),
                        "ssl": zone_info.get('ssl', 'unknown'),
                        "ssl_universal_ssl_enabled": zone_info.get('ssl_universal_ssl_enabled', False)
                    }
                    
                    # Get DNS records
                    records_response = requests.get(
                        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
                        headers=headers,
                        timeout=10
                    )
                    
                    if records_response.status_code == 200:
                        records_data = records_response.json()
                        if records_data['success']:
                            result["records"] = records_data['result']
                            self.log(f"Retrieved {len(result['records'])} DNS records from Cloudflare", Fore.GREEN)
            else:
                result["errors"] = [f"Cloudflare API error: {zones_response.status_code}"]
                
        except Exception as e:
            result["errors"] = [f"Error accessing Cloudflare API: {str(e)}"]
        
        return result
    
    def _check_route53_api(self, domain: str, credentials: Dict) -> Dict:
        """Check AWS Route 53 API settings"""
        result = {"api_available": True, "settings": {}, "records": [], "errors": []}
        
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            # Initialize Route 53 client
            if credentials.get('access_key') and credentials.get('secret_key'):
                client = boto3.client(
                    'route53',
                    aws_access_key_id=credentials['access_key'],
                    aws_secret_access_key=credentials['secret_key'],
                    region_name=credentials.get('region', 'us-east-1')
                )
            else:
                # Try using default credentials (IAM role, profile, etc.)
                client = boto3.client('route53')
            
            # Find hosted zone for domain
            hosted_zones = client.list_hosted_zones()
            zone_id = None
            zone_info = None
            
            for zone in hosted_zones['HostedZones']:
                if zone['Name'].rstrip('.') == domain:
                    zone_id = zone['Id'].split('/')[-1]
                    zone_info = zone
                    break
            
            if not zone_id:
                result["errors"].append(f"Hosted zone for {domain} not found")
                return result
            
            # Get zone settings
            result["settings"] = {
                "zone_id": zone_id,
                "name": zone_info['Name'],
                "record_count": zone_info['ResourceRecordSetCount'],
                "config": zone_info.get('Config', {}),
                "caller_reference": zone_info.get('CallerReference', 'N/A')
            }
            
            # Get DNS records
            paginator = client.get_paginator('list_resource_record_sets')
            records = []
            
            for page in paginator.paginate(HostedZoneId=zone_id):
                for record in page['ResourceRecordSets']:
                    record_data = {
                        "name": record['Name'],
                        "type": record['Type'],
                        "ttl": record.get('TTL', 'N/A'),
                        "values": []
                    }
                    
                    if 'ResourceRecords' in record:
                        record_data["values"] = [r['Value'] for r in record['ResourceRecords']]
                    elif 'AliasTarget' in record:
                        record_data["values"] = [f"ALIAS: {record['AliasTarget']['DNSName']}"]
                        record_data["alias"] = True
                    
                    records.append(record_data)
            
            result["records"] = records
            self.log(f"Retrieved {len(records)} DNS records from Route 53", Fore.GREEN)
            
        except ImportError:
            result["api_available"] = False
            result["errors"] = ["boto3 library not installed. Install with: pip install boto3"]
        except (NoCredentialsError, ClientError) as e:
            result["errors"] = [f"AWS credentials error: {str(e)}"]
        except Exception as e:
            result["errors"] = [f"Error accessing Route 53 API: {str(e)}"]
        
        return result
    
    def _check_google_dns_api(self, domain: str, credentials: Dict) -> Dict:
        """Check Google Cloud DNS API settings"""
        result = {"api_available": True, "settings": {}, "records": [], "errors": []}
        
        try:
            from google.cloud import dns
            from google.oauth2 import service_account
            import json
            
            # Initialize client with service account
            if credentials.get('service_account'):
                if isinstance(credentials['service_account'], str):
                    # If it's a file path
                    if credentials['service_account'].endswith('.json'):
                        creds = service_account.Credentials.from_service_account_file(
                            credentials['service_account']
                        )
                    else:
                        # If it's JSON string
                        service_account_info = json.loads(credentials['service_account'])
                        creds = service_account.Credentials.from_service_account_info(
                            service_account_info
                        )
                    
                    project_id = credentials.get('project_id') or creds.project_id
                    client = dns.Client(project=project_id, credentials=creds)
                else:
                    result["errors"] = ["Invalid service account credentials"]
                    return result
            else:
                # Try using default credentials
                project_id = credentials.get('project_id')
                if not project_id:
                    result["errors"] = ["Project ID required for Google Cloud DNS"]
                    return result
                client = dns.Client(project=project_id)
            
            # Find managed zone for domain
            zones = list(client.list_zones())
            zone = None
            
            for z in zones:
                if z.dns_name.rstrip('.') == domain:
                    zone = z
                    break
            
            if not zone:
                result["errors"].append(f"Managed zone for {domain} not found")
                return result
            
            # Get zone settings
            result["settings"] = {
                "zone_name": zone.name,
                "dns_name": zone.dns_name,
                "description": zone.description or "N/A",
                "creation_time": str(zone.created),
                "name_servers": zone.name_servers
            }
            
            # Get DNS records
            records = []
            for record in zone.list_resource_record_sets():
                record_data = {
                    "name": record.name,
                    "type": record.record_type,
                    "ttl": record.ttl,
                    "values": list(record.rrdatas)
                }
                records.append(record_data)
            
            result["records"] = records
            self.log(f"Retrieved {len(records)} DNS records from Google Cloud DNS", Fore.GREEN)
            
        except ImportError:
            result["api_available"] = False
            result["errors"] = ["google-cloud-dns library not installed. Install with: pip install google-cloud-dns"]
        except Exception as e:
            result["errors"] = [f"Error accessing Google Cloud DNS API: {str(e)}"]
        
        return result
    
    def _check_azure_dns_api(self, domain: str, credentials: Dict) -> Dict:
        """Check Azure DNS API settings"""
        result = {"api_available": True, "settings": {}, "records": [], "errors": []}
        
        try:
            from azure.identity import DefaultAzureCredential, ClientSecretCredential
            from azure.mgmt.dns import DnsManagementClient
            from azure.core.exceptions import ResourceNotFoundError
            
            # Initialize credentials
            if all(k in credentials for k in ['client_id', 'client_secret', 'tenant_id']):
                credential = ClientSecretCredential(
                    tenant_id=credentials['tenant_id'],
                    client_id=credentials['client_id'],
                    client_secret=credentials['client_secret']
                )
            else:
                # Try using default credentials (managed identity, CLI, etc.)
                credential = DefaultAzureCredential()
            
            subscription_id = credentials.get('subscription_id')
            if not subscription_id:
                result["errors"] = ["Azure subscription ID required"]
                return result
            
            # Initialize DNS client
            dns_client = DnsManagementClient(credential, subscription_id)
            
            # Find resource group and zone
            resource_group = credentials.get('resource_group')
            if not resource_group:
                # Try to find the zone across all resource groups
                zones = list(dns_client.zones.list())
                zone = None
                for z in zones:
                    if z.name == domain:
                        zone = z
                        resource_group = z.id.split('/')[4]  # Extract RG from resource ID
                        break
                
                if not zone:
                    result["errors"].append(f"DNS zone for {domain} not found")
                    return result
            else:
                try:
                    zone = dns_client.zones.get(resource_group, domain)
                except ResourceNotFoundError:
                    result["errors"].append(f"DNS zone {domain} not found in resource group {resource_group}")
                    return result
            
            # Get zone settings
            result["settings"] = {
                "zone_name": zone.name,
                "resource_group": resource_group,
                "location": zone.location,
                "number_of_record_sets": zone.number_of_record_sets,
                "max_number_of_record_sets": zone.max_number_of_record_sets,
                "name_servers": zone.name_servers
            }
            
            # Get DNS records
            records = []
            record_sets = dns_client.record_sets.list_by_dns_zone(resource_group, domain)
            
            for record_set in record_sets:
                record_data = {
                    "name": record_set.name,
                    "type": record_set.type.split('/')[-1],  # Extract record type from full type
                    "ttl": record_set.ttl,
                    "values": []
                }
                
                # Extract values based on record type
                if hasattr(record_set, 'a_records') and record_set.a_records:
                    record_data["values"] = [r.ipv4_address for r in record_set.a_records]
                elif hasattr(record_set, 'aaaa_records') and record_set.aaaa_records:
                    record_data["values"] = [r.ipv6_address for r in record_set.aaaa_records]
                elif hasattr(record_set, 'cname_record') and record_set.cname_record:
                    record_data["values"] = [record_set.cname_record.cname]
                elif hasattr(record_set, 'mx_records') and record_set.mx_records:
                    record_data["values"] = [f"{r.preference} {r.exchange}" for r in record_set.mx_records]
                elif hasattr(record_set, 'ns_records') and record_set.ns_records:
                    record_data["values"] = [r.nsdname for r in record_set.ns_records]
                elif hasattr(record_set, 'txt_records') and record_set.txt_records:
                    record_data["values"] = [' '.join(r.value) for r in record_set.txt_records]
                
                records.append(record_data)
            
            result["records"] = records
            self.log(f"Retrieved {len(records)} DNS records from Azure DNS", Fore.GREEN)
            
        except ImportError:
            result["api_available"] = False
            result["errors"] = ["Azure libraries not installed. Install with: pip install azure-mgmt-dns azure-identity"]
        except Exception as e:
            result["errors"] = [f"Error accessing Azure DNS API: {str(e)}"]
        
        return result
    
    def _check_digitalocean_api(self, domain: str, credentials: Dict) -> Dict:
        """Check DigitalOcean API settings"""
        result = {"api_available": True, "settings": {}, "records": [], "errors": []}
        
        try:
            api_token = credentials.get('api_token')
            if not api_token:
                result["errors"] = ["DigitalOcean API token required"]
                return result
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            # Get domain information
            domain_response = requests.get(
                f'https://api.digitalocean.com/v2/domains/{domain}',
                headers=headers,
                timeout=10
            )
            
            if domain_response.status_code == 404:
                result["errors"].append(f"Domain {domain} not found in DigitalOcean")
                return result
            elif domain_response.status_code != 200:
                result["errors"].append(f"DigitalOcean API error: {domain_response.status_code}")
                return result
            
            domain_data = domain_response.json()['domain']
            
            # Get domain settings
            result["settings"] = {
                "name": domain_data['name'],
                "ttl": domain_data.get('ttl', 'N/A'),
                "zone_file": domain_data.get('zone_file', 'N/A')
            }
            
            # Get DNS records
            records_response = requests.get(
                f'https://api.digitalocean.com/v2/domains/{domain}/records',
                headers=headers,
                timeout=10
            )
            
            if records_response.status_code == 200:
                records_data = records_response.json()
                records = []
                
                for record in records_data['domain_records']:
                    record_data = {
                        "id": record['id'],
                        "name": record['name'],
                        "type": record['type'],
                        "ttl": record.get('ttl', 'N/A'),
                        "values": [record.get('data', '')],
                        "priority": record.get('priority')
                    }
                    
                    # Add priority for MX records
                    if record['type'] == 'MX' and record.get('priority'):
                        record_data["values"] = [f"{record['priority']} {record.get('data', '')}"]
                    
                    records.append(record_data)
                
                result["records"] = records
                self.log(f"Retrieved {len(records)} DNS records from DigitalOcean", Fore.GREEN)
            else:
                result["errors"].append(f"Failed to retrieve DNS records: {records_response.status_code}")
            
        except Exception as e:
            result["errors"] = [f"Error accessing DigitalOcean API: {str(e)}"]
        
        return result


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """DNS Validator - A comprehensive DNS validation tool"""
    ctx.ensure_object(dict)
    ctx.obj['validator'] = DNSValidator(verbose=verbose)


@cli.command()
@click.argument('domain')
@click.pass_context
def delegation(ctx, domain):
    """Check DNS delegation for a domain"""
    validator = ctx.obj['validator']
    result = validator.check_delegation(domain)
    
    print(f"\n{Fore.CYAN}DNS Delegation Check for {domain}{Style.RESET_ALL}")
    print("=" * 50)
    
    if result["delegation_valid"]:
        print(f"{Fore.GREEN}✓ Delegation Status: VALID{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Delegation Status: INVALID{Style.RESET_ALL}")
    
    if result["authoritative_servers"]:
        print(f"\n{Fore.YELLOW}Authoritative Name Servers:{Style.RESET_ALL}")
        for i, server in enumerate(result["authoritative_servers"], 1):
            print(f"  {i}. {server}")
    
    if result["parent_servers"]:
        print(f"\n{Fore.YELLOW}Parent Name Servers:{Style.RESET_ALL}")
        for i, server in enumerate(result["parent_servers"], 1):
            print(f"  {i}. {server}")
    
    if result["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in result["errors"]:
            print(f"  • {error}")
    
    print()


@cli.command()
@click.argument('domain')
@click.option('--type', '-t', default='A', help='DNS record type to check (default: A)')
@click.option('--expected', '-e', help='Expected value to validate against')
@click.pass_context
def propagation(ctx, domain, type, expected):
    """Check DNS propagation across multiple DNS servers"""
    validator = ctx.obj['validator']
    result = validator.check_propagation(domain, type.upper(), expected)
    
    print(f"\n{Fore.CYAN}DNS Propagation Check for {domain} ({type.upper()} record){Style.RESET_ALL}")
    print("=" * 60)
    
    if result["propagated"]:
        print(f"{Fore.GREEN}✓ Propagation Status: COMPLETE{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Propagation Status: INCOMPLETE{Style.RESET_ALL}")
    
    if not result["consistency"]:
        print(f"{Fore.YELLOW}⚠ Warning: Inconsistent responses detected{Style.RESET_ALL}")
    
    # Create table for results
    table_data = []
    for server_name, server_data in result["servers"].items():
        status_color = Fore.GREEN if server_data["status"] == "success" else Fore.RED
        values_str = ", ".join(server_data.get("values", [])) or "No response"
        response_time = f"{server_data.get('response_time', 0):.1f}ms" if server_data.get('response_time') else "N/A"
        
        table_data.append([
            server_name,
            server_data["ip"],
            f"{status_color}{server_data['status'].upper()}{Style.RESET_ALL}",
            values_str,
            response_time
        ])
    
    print(f"\n{Fore.YELLOW}Server Results:{Style.RESET_ALL}")
    print(tabulate(
        table_data,
        headers=["DNS Server", "IP Address", "Status", "Values", "Response Time"],
        tablefmt="grid"
    ))
    
    if expected:
        print(f"\n{Fore.YELLOW}Expected Value:{Style.RESET_ALL} {expected}")
    
    print()


@cli.command('list-providers')
@click.pass_context
def list_providers(ctx):
    """List all supported DNS providers"""
    
    # Get provider patterns from the validator class
    provider_patterns = {
        "Cloudflare": ["cloudflare.com", "ns.cloudflare.com"],
        "AWS Route 53": ["awsdns", "amazonaws.com", "amzndns"],
        "Google Cloud DNS": ["googledomains.com", "google.com", "ns-cloud"],
        "Azure DNS": ["azure-dns.com", "azure-dns.net", "azure-dns.org", "azure-dns.info"],
        "DigitalOcean": ["digitalocean.com", "ns1.digitalocean.com", "ns2.digitalocean.com", "ns3.digitalocean.com"],
        "Namecheap": ["namecheap.com", "registrar-servers.com"],
        "GoDaddy": ["domaincontrol.com", "godaddy.com"],
        "Quad9": ["quad9.net"],
        "OpenDNS": ["opendns.com", "umbrella.com"],
        "Verisign": ["verisign-grs.com"],
        "DNS Made Easy": ["dnsmadeeasy.com"],
        "Dyn": ["dynect.net", "dyn.com"],
        "Hurricane Electric": ["he.net"],
        "ClouDNS": ["cloudns.net"],
        "Porkbun": ["porkbun.com"],
        "Name.com": ["name.com"],
        "Domain.com": ["domain.com"],
        "Network Solutions": ["worldnic.com", "networksolutions.com"],
        "1&1 IONOS": ["1and1.com", "ionos.com", "ui-dns.com"],
        "Hostinger": ["hostinger.com"],
        "Bluehost": ["bluehost.com"],
        "Hover": ["hover.com"],
        "Gandi": ["gandi.net"],
        "Dynadot": ["dynadot.com"],
        "eNom": ["enom.com"],
        "Register.com": ["register.com"],
        "Tucows": ["tucows.com"],
        "FastDomain": ["fastdomain.com"],
        "Linode": ["linode.com"],
        "Vultr": ["vultr.com"],
        "OVH": ["ovh.net", "ovh.com"],
        "Hetzner": ["hetzner.com"],
        "Scaleway": ["scaleway.com"],
        "No-IP": ["no-ip.com"],
        "DuckDNS": ["duckdns.org"],
        "FreeDNS": ["afraid.org"],
        "Zonomi": ["zonomi.com"],
        "NS1": ["nsone.net"],
        "Constellix": ["constellix.com"],
        "UltraDNS": ["ultradns.com", "ultradns.net"],
        "Neustar": ["neustar.biz"],
        "Easydns": ["easydns.com"],
        "Rage4": ["r4ns.com"],
        "PowerDNS": ["powerdns.com"],
        "BuddyNS": ["buddyns.com"],
        "GeoDNS": ["geodns.com"],
        "PointDNS": ["pointhq.com"],
        "Route53 Resolver": ["resolver.dns-oarc.net"],
        "Yandex DNS": ["yandex.net"],
        "Selectel": ["selectel.ru"],
        "Reg.ru": ["reg.ru"],
        "Timeweb": ["timeweb.ru"]
    }
    
    print(f"\n{Fore.CYAN}Supported DNS Providers ({len(provider_patterns)} total){Style.RESET_ALL}")
    print("=" * 60)
    
    # Group providers by category
    categories = {
        "🌐 Major Cloud Providers": ["Cloudflare", "AWS Route 53", "Google Cloud DNS", "Azure DNS"],
        "🚀 VPS/Cloud Hosting": ["DigitalOcean", "Linode", "Vultr", "OVH", "Hetzner", "Scaleway"],
        "🏢 Domain Registrars": ["Namecheap", "GoDaddy", "Name.com", "Domain.com", "Gandi", "Hover", "Dynadot"],
        "🔒 Security/Privacy DNS": ["Quad9", "OpenDNS"],
        "⚡ Performance DNS": ["DNS Made Easy", "NS1", "Constellix", "UltraDNS"],
        "🌍 Regional Providers": ["Yandex DNS", "Selectel", "Reg.ru", "Timeweb"],
        "🆓 Free DNS Services": ["No-IP", "DuckDNS", "FreeDNS", "Hurricane Electric"],
        "🏢 Enterprise/Hosting": ["Verisign", "Dyn", "Neustar", "Network Solutions", "1&1 IONOS", "Hostinger", "Bluehost"],
        "🔧 Specialized DNS": ["ClouDNS", "Porkbun", "Zonomi", "Easydns", "Rage4", "PowerDNS", "BuddyNS", "GeoDNS", "PointDNS"]
    }
    
    for category, providers in categories.items():
        print(f"\n{Fore.YELLOW}{category}{Style.RESET_ALL}")
        for provider in providers:
            if provider in provider_patterns:
                # Updated API support status
                if provider in ["Cloudflare", "AWS Route 53", "Google Cloud DNS", "Azure DNS", "DigitalOcean"]:
                    api_support = "✅ API"
                else:
                    api_support = "📋 Detect"
                    
                patterns = ", ".join(provider_patterns[provider][:2])  # Show first 2 patterns
                if len(provider_patterns[provider]) > 2:
                    patterns += f" (+{len(provider_patterns[provider])-2} more)"
                print(f"  {provider:<20} {api_support:<10} Patterns: {patterns}")
    
    print(f"\n{Fore.GREEN}API Integration Status:{Style.RESET_ALL}")
    print("  ✅ Fully Supported: Cloudflare, AWS Route 53, Google Cloud DNS, Azure DNS, DigitalOcean")
    print("  📋 Detection Only: All other providers")
    
    print(f"\n{Fore.CYAN}💡 Usage Examples:{Style.RESET_ALL}")
    print("  dns-validator providers example.com")
    print("  dns-validator provider example.com --api-token YOUR_TOKEN")
    print()


@cli.command()
@click.argument('domain')
@click.pass_context
def providers(ctx, domain):
    """Detect and display DNS providers for a domain"""
    validator = ctx.obj['validator']
    result = validator.detect_dns_provider(domain)
    
    print(f"\n{Fore.CYAN}DNS Provider Detection for {domain}{Style.RESET_ALL}")
    print("=" * 50)
    
    if result["detected_providers"]:
        print(f"{Fore.GREEN}✓ Detected DNS Providers:{Style.RESET_ALL}")
        for i, provider in enumerate(result["detected_providers"], 1):
            primary_indicator = " (Primary)" if provider == result["primary_provider"] else ""
            print(f"  {i}. {provider}{primary_indicator}")
    else:
        print(f"{Fore.YELLOW}⚠ No known DNS providers detected{Style.RESET_ALL}")
    
    print(f"\n{Fore.YELLOW}Nameservers:{Style.RESET_ALL}")
    for i, ns in enumerate(result["nameservers"], 1):
        print(f"  {i}. {ns}")
    
    if result["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in result["errors"]:
            print(f"  • {error}")
    
    print()


@cli.command()
@click.argument('domain')
@click.option('--provider', help='Specific DNS provider to check')
@click.option('--api-token', help='API token/key for provider (Cloudflare, DigitalOcean, etc.)')
@click.option('--api-secret', help='API secret for providers that require it')
@click.option('--access-key', help='Access key for AWS Route 53')
@click.option('--secret-key', help='Secret key for AWS Route 53')
@click.option('--region', help='AWS region (default: us-east-1)')
@click.option('--service-account', help='Service account JSON file/string for Google Cloud DNS')
@click.option('--project-id', help='Google Cloud project ID')
@click.option('--subscription-id', help='Azure subscription ID')
@click.option('--resource-group', help='Azure resource group name')
@click.option('--tenant-id', help='Azure tenant ID')
@click.option('--client-id', help='Azure client ID')
@click.option('--client-secret', help='Azure client secret')
@click.option('--cred-name', help='Use stored credentials by name')
@click.pass_context
def provider(ctx, domain, provider, api_token, api_secret, access_key, secret_key, region, 
             service_account, project_id, subscription_id, resource_group, tenant_id, 
             client_id, client_secret, cred_name):
    """Check DNS provider settings with API integration
    
    Examples:
    \b
    # Using stored credentials
    dns-validator provider example.com --cred-name production
    
    # Cloudflare with command line
    dns-validator provider example.com --api-token YOUR_CF_TOKEN
    
    # AWS Route 53
    dns-validator provider example.com --access-key KEY --secret-key SECRET
    
    # Google Cloud DNS
    dns-validator provider example.com --service-account /path/to/service-account.json --project-id PROJECT
    
    # Azure DNS
    dns-validator provider example.com --subscription-id SUB_ID --resource-group RG_NAME
    
    # DigitalOcean
    dns-validator provider example.com --api-token YOUR_DO_TOKEN
    """
    validator = ctx.obj['validator']
    
    # First, try to load stored credentials if cred-name is provided or no CLI args given
    api_credentials = {}
    
    # Check if we have command line credentials
    has_cli_creds = any([api_token, api_secret, access_key, secret_key, service_account, 
                        subscription_id, tenant_id, client_id, client_secret])
    
    if cred_name or not has_cli_creds:
        try:
            key_manager = APIKeyManager()
            
            # If provider not specified, try to detect it
            if not provider:
                detection_result = validator.detect_dns_provider(domain)
                provider = detection_result.get("primary_provider", "Unknown")
                if provider == "Unknown":
                    print(f"{Fore.YELLOW}Could not detect DNS provider. Please specify with --provider{Style.RESET_ALL}")
                    return
            
            # Try to get stored credentials
            if cred_name:
                stored_creds = key_manager.get_credentials(provider, cred_name)
                if not stored_creds:
                    print(f"{Fore.RED}No stored credentials found for {provider} ({cred_name}){Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Use 'dns-validator creds add \"{provider}\" {cred_name} --interactive' to add credentials{Style.RESET_ALL}")
                    return
            else:
                # Try to get default credentials (first available)
                stored_creds = key_manager.get_credentials(provider)
                if stored_creds:
                    print(f"{Fore.CYAN}Using stored credentials for {provider}{Style.RESET_ALL}")
            
            if stored_creds:
                api_credentials.update(stored_creds)
                
        except Exception as e:
            if cred_name:
                print(f"{Fore.RED}Error loading stored credentials: {e}{Style.RESET_ALL}")
                return
            # Continue with CLI credentials if stored creds fail
    
    # Override with command line credentials if provided
    if api_token:
        api_credentials['api_token'] = api_token
    if api_secret:
        api_credentials['api_secret'] = api_secret
    if access_key:
        api_credentials['access_key'] = access_key
    if secret_key:
        api_credentials['secret_key'] = secret_key
    if region:
        api_credentials['region'] = region
    if service_account:
        api_credentials['service_account'] = service_account
    if project_id:
        api_credentials['project_id'] = project_id
    if subscription_id:
        api_credentials['subscription_id'] = subscription_id
    if resource_group:
        api_credentials['resource_group'] = resource_group
    if tenant_id:
        api_credentials['tenant_id'] = tenant_id
    if client_id:
        api_credentials['client_id'] = client_id
    if client_secret:
        api_credentials['client_secret'] = client_secret
    
    result = validator.check_provider_settings(domain, provider, api_credentials)
    
    print(f"\n{Fore.CYAN}{result['provider']} Settings Check for {domain}{Style.RESET_ALL}")
    print("=" * 60)
    
    if result["api_available"]:
        print(f"{Fore.GREEN}✓ API integration available{Style.RESET_ALL}")
        
        if result["settings"]:
            print(f"\n{Fore.YELLOW}Provider Settings:{Style.RESET_ALL}")
            for key, value in result["settings"].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        if result["records"]:
            print(f"\n{Fore.YELLOW}DNS Records ({len(result['records'])} total):{Style.RESET_ALL}")
            
            # Group records by type
            records_by_type = {}
            for record in result["records"]:
                record_type = record.get("type", "UNKNOWN")
                if record_type not in records_by_type:
                    records_by_type[record_type] = []
                records_by_type[record_type].append(record)
            
            for record_type, records in records_by_type.items():
                print(f"\n  {record_type} Records:")
                for record in records:
                    name = record.get("name", "N/A")
                    content = record.get("content", "N/A")
                    ttl = record.get("ttl", "N/A")
                    
                    # Cloudflare-specific proxy status
                    if result['provider'] == 'Cloudflare':
                        proxied = record.get("proxied", False)
                        proxy_status = " 🟠 Proxied" if proxied else " ⚪ DNS Only"
                    else:
                        proxy_status = ""
                    
                    print(f"    {name} → {content} (TTL: {ttl}){proxy_status}")
    else:
        print(f"{Fore.YELLOW}⚠ No API integration available for {result['provider']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Tip: Provide API credentials to access detailed settings{Style.RESET_ALL}")
    
    if result["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in result["errors"]:
            print(f"  • {error}")
    
    print()


@cli.command()
@click.argument('domain')
@click.option('--api-token', help='Cloudflare API token for detailed settings')
@click.pass_context
def cloudflare(ctx, domain, api_token):
    """Check Cloudflare DNS settings (legacy command - use 'provider' instead)"""
    validator = ctx.obj['validator']
    
    # Use the new provider system but force Cloudflare
    api_credentials = {'api_token': api_token} if api_token else None
    result = validator.check_provider_settings(domain, "Cloudflare", api_credentials)
    
    print(f"\n{Fore.CYAN}Cloudflare Settings Check for {domain}{Style.RESET_ALL}")
    print("=" * 50)
    
    # Check if actually using Cloudflare
    detection = validator.detect_dns_provider(domain)
    is_cloudflare = "Cloudflare" in detection.get("detected_providers", [])
    
    if is_cloudflare:
        print(f"{Fore.GREEN}✓ Cloudflare nameservers detected{Style.RESET_ALL}")
        
        if result["settings"]:
            print(f"\n{Fore.YELLOW}Zone Settings:{Style.RESET_ALL}")
            for key, value in result["settings"].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        if result["records"]:
            print(f"\n{Fore.YELLOW}DNS Records ({len(result['records'])} total):{Style.RESET_ALL}")
            
            records_by_type = {}
            for record in result["records"]:
                record_type = record.get("type", "UNKNOWN")
                if record_type not in records_by_type:
                    records_by_type[record_type] = []
                records_by_type[record_type].append(record)
            
            for record_type, records in records_by_type.items():
                print(f"\n  {record_type} Records:")
                for record in records:
                    name = record.get("name", "N/A")
                    content = record.get("content", "N/A")
                    ttl = record.get("ttl", "N/A")
                    proxied = record.get("proxied", False)
                    proxy_status = "🟠 Proxied" if proxied else "⚪ DNS Only"
                    print(f"    {name} → {content} (TTL: {ttl}) {proxy_status}")
    else:
        print(f"{Fore.YELLOW}⚠ Cloudflare nameservers not detected{Style.RESET_ALL}")
        detected_providers = detection.get("detected_providers", [])
        if detected_providers:
            print(f"{Fore.CYAN}💡 Detected providers: {', '.join(detected_providers)}{Style.RESET_ALL}")
        
        if not api_token:
            print(f"{Fore.CYAN}💡 Tip: Use --api-token to get detailed Cloudflare settings{Style.RESET_ALL}")
    
    if result["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in result["errors"]:
            print(f"  • {error}")
    
    print()


@cli.command()
@click.argument('domain')
@click.option('--type', '-t', default='A', help='DNS record type to check')
@click.option('--expected', '-e', help='Expected value to validate against')
@click.option('--api-token', help='API token for provider integration')
@click.pass_context
def full(ctx, domain, type, expected, api_token):
    """Perform all DNS checks (delegation, propagation, and provider settings)"""
    validator = ctx.obj['validator']
    
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"COMPREHENSIVE DNS VALIDATION for {domain}")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    # 1. Delegation Check
    print(f"\n{Fore.CYAN}1. DELEGATION CHECK{Style.RESET_ALL}")
    delegation_result = validator.check_delegation(domain)
    
    if delegation_result["delegation_valid"]:
        print(f"{Fore.GREEN}✓ DNS delegation is valid{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ DNS delegation issues detected{Style.RESET_ALL}")
        for error in delegation_result["errors"]:
            print(f"  • {error}")
    
    # 2. Propagation Check
    print(f"\n{Fore.CYAN}2. PROPAGATION CHECK{Style.RESET_ALL}")
    propagation_result = validator.check_propagation(domain, type.upper(), expected)
    
    if propagation_result["propagated"]:
        print(f"{Fore.GREEN}✓ DNS propagation is complete{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ DNS propagation issues detected{Style.RESET_ALL}")
    
    if not propagation_result["consistency"]:
        print(f"{Fore.YELLOW}⚠ Inconsistent responses across DNS servers{Style.RESET_ALL}")
    
    # 3. Provider Detection
    print(f"\n{Fore.CYAN}3. DNS PROVIDER DETECTION{Style.RESET_ALL}")
    provider_detection = validator.detect_dns_provider(domain)
    
    if provider_detection["detected_providers"]:
        primary_provider = provider_detection["primary_provider"]
        print(f"{Fore.GREEN}✓ Detected DNS provider: {primary_provider}{Style.RESET_ALL}")
        
        if len(provider_detection["detected_providers"]) > 1:
            other_providers = [p for p in provider_detection["detected_providers"] if p != primary_provider]
            print(f"  Additional providers: {', '.join(other_providers)}")
        
        # 4. Provider Settings Check
        print(f"\n{Fore.CYAN}4. PROVIDER SETTINGS CHECK{Style.RESET_ALL}")
        api_credentials = {'api_token': api_token} if api_token else None
        provider_result = validator.check_provider_settings(domain, primary_provider, api_credentials)
        
        if provider_result["api_available"]:
            print(f"{Fore.GREEN}✓ {primary_provider} API integration available{Style.RESET_ALL}")
            if provider_result["records"]:
                print(f"  📋 {len(provider_result['records'])} DNS records found")
        else:
            print(f"{Fore.YELLOW}⚠ No API integration available for {primary_provider}{Style.RESET_ALL}")
            if not api_token:
                print(f"{Fore.CYAN}💡 Tip: Use --api-token to access detailed settings{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ No known DNS provider detected{Style.RESET_ALL}")
        provider_result = {"errors": ["Unknown DNS provider"]}
    
    # Summary
    print(f"\n{Fore.MAGENTA}SUMMARY{Style.RESET_ALL}")
    print("=" * 20)
    
    issues = []
    if not delegation_result["delegation_valid"]:
        issues.append("DNS delegation issues")
    if not propagation_result["propagated"]:
        issues.append("DNS propagation incomplete")
    if not propagation_result["consistency"]:
        issues.append("Inconsistent DNS responses")
    if provider_result.get("errors"):
        issues.append("Provider API errors")
    
    if not issues:
        print(f"{Fore.GREEN}🎉 All DNS checks passed successfully!{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ Issues found:{Style.RESET_ALL}")
        for issue in issues:
            print(f"  • {issue}")
    
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")


# Credential Management Commands
@cli.group()
def creds():
    """Manage API credentials for DNS providers"""
    pass


@creds.command('add')
@click.argument('provider')
@click.argument('name')
@click.option('--interactive', '-i', is_flag=True, help='Interactive credential input')
@click.option('--api-token', help='API token/key')
@click.option('--api-secret', help='API secret')
@click.option('--access-key', help='Access key (AWS)')
@click.option('--secret-key', help='Secret key (AWS)')
@click.option('--region', help='Region (AWS)')
@click.option('--service-account', help='Service account file/JSON (Google Cloud)')
@click.option('--project-id', help='Project ID (Google Cloud)')
@click.option('--subscription-id', help='Subscription ID (Azure)')
@click.option('--resource-group', help='Resource group (Azure)')
@click.option('--tenant-id', help='Tenant ID (Azure)')
@click.option('--client-id', help='Client ID (Azure)')
@click.option('--client-secret', help='Client secret (Azure)')
def add_credentials(provider, name, interactive, **kwargs):
    """Add new API credentials for a provider
    
    Examples:
    \b
    # Interactive mode (recommended for security)
    dns-validator creds add Cloudflare production --interactive
    
    # Command line (less secure)
    dns-validator creds add Cloudflare production --api-token YOUR_TOKEN
    
    # Multiple credentials for same provider
    dns-validator creds add "AWS Route 53" staging --interactive
    dns-validator creds add "AWS Route 53" production --interactive
    """
    try:
        key_manager = APIKeyManager()
        credentials = {}
        
        if interactive:
            print(f"\n{Fore.CYAN}Adding credentials for {provider} ({name}){Style.RESET_ALL}")
            print("Enter credentials (press Enter to skip optional fields):")
            
            # Provider-specific interactive prompts
            if provider.lower() == 'cloudflare':
                api_token = getpass.getpass("Cloudflare API Token: ")
                if api_token:
                    credentials['api_token'] = api_token
            
            elif 'aws' in provider.lower() or 'route 53' in provider.lower():
                access_key = input("AWS Access Key ID: ")
                if access_key:
                    credentials['access_key'] = access_key
                    secret_key = getpass.getpass("AWS Secret Access Key: ")
                    if secret_key:
                        credentials['secret_key'] = secret_key
                region = input("AWS Region (default: us-east-1): ") or "us-east-1"
                credentials['region'] = region
            
            elif 'google' in provider.lower():
                service_account = input("Service Account JSON file path or JSON string: ")
                if service_account:
                    credentials['service_account'] = service_account
                project_id = input("Google Cloud Project ID: ")
                if project_id:
                    credentials['project_id'] = project_id
            
            elif 'azure' in provider.lower():
                subscription_id = input("Azure Subscription ID: ")
                if subscription_id:
                    credentials['subscription_id'] = subscription_id
                resource_group = input("Resource Group (optional): ")
                if resource_group:
                    credentials['resource_group'] = resource_group
                tenant_id = input("Tenant ID (for service principal): ")
                if tenant_id:
                    credentials['tenant_id'] = tenant_id
                    client_id = input("Client ID: ")
                    if client_id:
                        credentials['client_id'] = client_id
                        client_secret = getpass.getpass("Client Secret: ")
                        if client_secret:
                            credentials['client_secret'] = client_secret
            
            elif 'digitalocean' in provider.lower():
                api_token = getpass.getpass("DigitalOcean API Token: ")
                if api_token:
                    credentials['api_token'] = api_token
            
            else:
                # Generic prompts
                api_token = getpass.getpass("API Token/Key (if applicable): ")
                if api_token:
                    credentials['api_token'] = api_token
                api_secret = getpass.getpass("API Secret (if applicable): ")
                if api_secret:
                    credentials['api_secret'] = api_secret
        
        else:
            # Use command line arguments
            for key, value in kwargs.items():
                if value is not None:
                    credentials[key.replace('-', '_')] = value
        
        if not credentials:
            print(f"{Fore.RED}No credentials provided{Style.RESET_ALL}")
            return
        
        key_manager.add_credentials(provider, name, credentials)
        print(f"{Fore.GREEN}✓ Credentials added for {provider} ({name}){Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error adding credentials: {e}{Style.RESET_ALL}")


@creds.command('list')
@click.option('--provider', help='Filter by provider')
@click.option('--show-values', is_flag=True, help='Show credential values (use with caution)')
def list_credentials(provider, show_values):
    """List stored credentials"""
    try:
        key_manager = APIKeyManager()
        all_creds = key_manager.list_credentials(provider)
        
        if not all_creds:
            print(f"{Fore.YELLOW}No credentials stored{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Stored Credentials{Style.RESET_ALL}")
        print("=" * 50)
        
        for prov, creds in all_creds.items():
            print(f"\n{Fore.YELLOW}{prov}:{Style.RESET_ALL}")
            
            if not creds:
                print("  No credentials stored")
                continue
            
            for name, cred_data in creds.items():
                print(f"  📋 {name}")
                
                if show_values:
                    for key, value in cred_data.items():
                        if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                            display_value = value if show_values else '***HIDDEN***'
                        else:
                            display_value = value
                        print(f"    {key}: {display_value}")
                else:
                    fields = list(cred_data.keys())
                    print(f"    Fields: {', '.join(fields)}")
        
        print()
        
    except Exception as e:
        print(f"{Fore.RED}Error listing credentials: {e}{Style.RESET_ALL}")


@creds.command('delete')
@click.argument('provider')
@click.argument('name')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def delete_credentials(provider, name, confirm):
    """Delete stored credentials"""
    try:
        key_manager = APIKeyManager()
        
        if not confirm:
            response = input(f"Delete credentials for {provider} ({name})? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled")
                return
        
        if key_manager.delete_credentials(provider, name):
            print(f"{Fore.GREEN}✓ Credentials deleted for {provider} ({name}){Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Credentials not found for {provider} ({name}){Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error deleting credentials: {e}{Style.RESET_ALL}")


@creds.command('edit')
@click.argument('provider')
@click.argument('name')
@click.option('--interactive', '-i', is_flag=True, help='Interactive credential editing')
def edit_credentials(provider, name, interactive):
    """Edit existing credentials"""
    try:
        key_manager = APIKeyManager()
        existing_creds = key_manager.get_credentials(provider, name)
        
        if not existing_creds:
            print(f"{Fore.RED}Credentials not found for {provider} ({name}){Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Editing credentials for {provider} ({name}){Style.RESET_ALL}")
        print("Current fields:", ", ".join(existing_creds.keys()))
        print("Enter new values (press Enter to keep existing):")
        
        updated_creds = {}
        
        for key, current_value in existing_creds.items():
            if any(sensitive in key.lower() for sensitive in ['token', 'key', 'secret', 'password']):
                prompt = f"{key} (***HIDDEN***): "
                new_value = getpass.getpass(prompt)
            else:
                prompt = f"{key} ({current_value}): "
                new_value = input(prompt)
            
            if new_value:
                updated_creds[key] = new_value
        
        if updated_creds:
            key_manager.update_credentials(provider, name, updated_creds)
            print(f"{Fore.GREEN}✓ Credentials updated for {provider} ({name}){Style.RESET_ALL}")
        else:
            print("No changes made")
        
    except Exception as e:
        print(f"{Fore.RED}Error editing credentials: {e}{Style.RESET_ALL}")


@creds.command('export')
@click.argument('output_file')
@click.option('--include-secrets', is_flag=True, help='Include sensitive values (use with caution)')
def export_credentials(output_file, include_secrets):
    """Export credentials to a file"""
    try:
        key_manager = APIKeyManager()
        key_manager.export_config(output_file, include_secrets)
        
        if include_secrets:
            print(f"{Fore.YELLOW}⚠ Exported credentials with secrets to {output_file}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠ Keep this file secure!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Exported credential structure to {output_file}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error exporting credentials: {e}{Style.RESET_ALL}")


@creds.command('clear')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def clear_all_credentials(confirm):
    """Clear all stored credentials"""
    try:
        if not confirm:
            response = input("Clear ALL stored credentials? This cannot be undone! [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled")
                return
        
        key_manager = APIKeyManager()
        key_manager.clear_all_credentials()
        print(f"{Fore.GREEN}✓ All credentials cleared{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error clearing credentials: {e}{Style.RESET_ALL}")


@creds.command('test')
@click.argument('provider')
@click.argument('name')
@click.argument('domain')
def test_credentials(provider, name, domain):
    """Test stored credentials with a domain"""
    try:
        key_manager = APIKeyManager()
        credentials = key_manager.get_credentials(provider, name)
        
        if not credentials:
            print(f"{Fore.RED}Credentials not found for {provider} ({name}){Style.RESET_ALL}")
            return
        
        print(f"{Fore.CYAN}Testing credentials for {provider} ({name}) with {domain}{Style.RESET_ALL}")
        
        # Use the existing provider check functionality
        validator = DNSValidator(verbose=True)
        result = validator.check_provider_settings(domain, provider, credentials)
        
        if result.get("api_available") and not result.get("errors"):
            print(f"{Fore.GREEN}✓ Credentials are working!{Style.RESET_ALL}")
            if result.get("records"):
                print(f"Found {len(result['records'])} DNS records")
        else:
            print(f"{Fore.RED}✗ Credentials test failed{Style.RESET_ALL}")
            for error in result.get("errors", []):
                print(f"  • {error}")
        
    except Exception as e:
        print(f"{Fore.RED}Error testing credentials: {e}{Style.RESET_ALL}")


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)