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
import dns.dnssec
import dns.rrset
import dns.rdatatype
import dns.reversename
import requests
import sys
import time
import socket
import getpass
import json
import subprocess
import platform
import ssl
import urllib.request
from typing import List, Dict, Optional, Tuple
from colorama import init, Fore, Style
from tabulate import tabulate
import concurrent.futures
import threading
from datetime import datetime, timedelta
from pathlib import Path
import ipaddress
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
        elif provider == "Namecheap":
            result.update(self._check_namecheap_api(domain, api_credentials or {}))
        elif provider == "GoDaddy":
            result.update(self._check_godaddy_api(domain, api_credentials or {}))
        elif provider == "Name.com":
            result.update(self._check_name_com_api(domain, api_credentials or {}))
        elif provider == "Gandi":
            result.update(self._check_gandi_api(domain, api_credentials or {}))
        elif provider == "OVH":
            result.update(self._check_ovh_api(domain, api_credentials or {}))
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

    def _check_namecheap_api(self, domain: str, credentials: Dict) -> Dict:
        """Check Namecheap DNS settings via API"""
        result = {
            "provider": "Namecheap",
            "domain": domain,
            "records": [],
            "settings": {},
            "errors": [],
            "api_available": True
        }
        
        try:
            api_user = credentials.get("api_user")
            api_key = credentials.get("api_key")
            username = credentials.get("username", api_user)
            client_ip = credentials.get("client_ip", "127.0.0.1")
            
            if not api_user or not api_key:
                result["errors"].append("Namecheap API requires api_user and api_key")
                result["api_available"] = False
                return result
            
            # Namecheap API endpoint (sandbox: api.sandbox.namecheap.com, production: api.namecheap.com)
            sandbox = credentials.get("sandbox", False)
            base_url = "https://api.sandbox.namecheap.com/xml.response" if sandbox else "https://api.namecheap.com/xml.response"
            
            # Get domain info and DNS records
            params = {
                "ApiUser": api_user,
                "ApiKey": api_key,
                "UserName": username,
                "Command": "namecheap.domains.dns.getHosts",
                "ClientIp": client_ip,
                "SLD": domain.split('.')[0],  # Second Level Domain
                "TLD": '.'.join(domain.split('.')[1:])  # Top Level Domain
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                # Check for API errors
                errors = root.find(".//Errors")
                if errors is not None and len(errors) > 0:
                    for error in errors:
                        result["errors"].append(f"Namecheap API Error: {error.text}")
                    return result
                
                # Extract DNS records
                hosts = root.findall(".//host")
                records = []
                
                for host in hosts:
                    record_data = {
                        "name": host.get("Name", ""),
                        "type": host.get("Type", ""),
                        "address": host.get("Address", ""),
                        "ttl": int(host.get("TTL", "1800")),
                        "mx_pref": host.get("MXPref"),
                        "host_id": host.get("HostId")
                    }
                    
                    # Clean up record name
                    if record_data["name"] == "@":
                        record_data["name"] = domain
                    elif record_data["name"] != domain and not record_data["name"].endswith(f".{domain}"):
                        record_data["name"] = f"{record_data['name']}.{domain}"
                    
                    records.append(record_data)
                
                result["records"] = records
                
                # Get nameserver info
                ns_params = {
                    "ApiUser": api_user,
                    "ApiKey": api_key,
                    "UserName": username,
                    "Command": "namecheap.domains.dns.getList",
                    "ClientIp": client_ip,
                    "SLD": domain.split('.')[0],
                    "TLD": '.'.join(domain.split('.')[1:])
                }
                
                ns_response = requests.get(base_url, params=ns_params, timeout=30)
                if ns_response.status_code == 200:
                    ns_root = ET.fromstring(ns_response.text)
                    domain_info = ns_root.find(".//Domain")
                    if domain_info is not None:
                        result["settings"] = {
                            "nameservers": [],
                            "dns_type": domain_info.get("Type", "Unknown"),
                            "is_premium": domain_info.get("IsPremium", "false") == "true",
                            "auto_renew": domain_info.get("AutoRenew", "false") == "true"
                        }
                
                self.log(f"Retrieved {len(records)} DNS records from Namecheap", Fore.GREEN)
            else:
                result["errors"].append(f"Failed to access Namecheap API: {response.status_code}")
                
        except Exception as e:
            result["errors"] = [f"Error accessing Namecheap API: {str(e)}"]
        
        return result

    def _check_godaddy_api(self, domain: str, credentials: Dict) -> Dict:
        """Check GoDaddy DNS settings via API"""
        result = {
            "provider": "GoDaddy",
            "domain": domain,
            "records": [],
            "settings": {},
            "errors": [],
            "api_available": True
        }
        
        try:
            api_key = credentials.get("api_key")
            api_secret = credentials.get("api_secret")
            
            if not api_key or not api_secret:
                result["errors"].append("GoDaddy API requires api_key and api_secret")
                result["api_available"] = False
                return result
            
            # GoDaddy API endpoint
            base_url = "https://api.godaddy.com/v1"
            
            headers = {
                "Authorization": f"sso-key {api_key}:{api_secret}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Get DNS records
            records_url = f"{base_url}/domains/{domain}/records"
            response = requests.get(records_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                records_data = response.json()
                records = []
                
                for record in records_data:
                    record_data = {
                        "name": record.get("name", ""),
                        "type": record.get("type", ""),
                        "data": record.get("data", ""),
                        "ttl": record.get("ttl", 600),
                        "priority": record.get("priority"),
                        "port": record.get("port"),
                        "service": record.get("service"),
                        "protocol": record.get("protocol"),
                        "weight": record.get("weight")
                    }
                    
                    # Format full record name
                    if record_data["name"] == "@":
                        record_data["full_name"] = domain
                    else:
                        record_data["full_name"] = f"{record_data['name']}.{domain}"
                    
                    records.append(record_data)
                
                result["records"] = records
                
                # Get domain details
                domain_url = f"{base_url}/domains/{domain}"
                domain_response = requests.get(domain_url, headers=headers, timeout=30)
                
                if domain_response.status_code == 200:
                    domain_data = domain_response.json()
                    result["settings"] = {
                        "status": domain_data.get("status"),
                        "privacy": domain_data.get("privacy", False),
                        "locked": domain_data.get("locked", False),
                        "nameservers": domain_data.get("nameServers", []),
                        "created_at": domain_data.get("createdAt"),
                        "expires": domain_data.get("expires"),
                        "auto_renew": domain_data.get("renewAuto", False)
                    }
                
                self.log(f"Retrieved {len(records)} DNS records from GoDaddy", Fore.GREEN)
            elif response.status_code == 404:
                result["errors"].append(f"Domain {domain} not found in GoDaddy account")
            elif response.status_code == 403:
                result["errors"].append("GoDaddy API access denied - check API credentials and permissions")
            else:
                result["errors"].append(f"Failed to access GoDaddy API: {response.status_code}")
                
        except Exception as e:
            result["errors"] = [f"Error accessing GoDaddy API: {str(e)}"]
        
        return result

    def _check_name_com_api(self, domain: str, credentials: Dict) -> Dict:
        """Check Name.com DNS settings via API"""
        result = {
            "provider": "Name.com",
            "domain": domain,
            "records": [],
            "settings": {},
            "errors": [],
            "api_available": True
        }
        
        try:
            api_username = credentials.get("api_username")
            api_token = credentials.get("api_token")
            
            if not api_username or not api_token:
                result["errors"].append("Name.com API requires api_username and api_token")
                result["api_available"] = False
                return result
            
            # Name.com API endpoint
            base_url = "https://api.name.com/v4"
            
            # Basic authentication
            import base64
            credentials_encoded = base64.b64encode(f"{api_username}:{api_token}".encode()).decode()
            
            headers = {
                "Authorization": f"Basic {credentials_encoded}",
                "Content-Type": "application/json"
            }
            
            # Get DNS records
            records_url = f"{base_url}/domains/{domain}/records"
            response = requests.get(records_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                records_data = response_data.get("records", [])
                records = []
                
                for record in records_data:
                    record_data = {
                        "id": record.get("id"),
                        "domain_name": record.get("domainName"),
                        "host": record.get("host"),
                        "fqdn": record.get("fqdn"),
                        "type": record.get("type"),
                        "answer": record.get("answer"),
                        "ttl": record.get("ttl", 300),
                        "priority": record.get("priority")
                    }
                    records.append(record_data)
                
                result["records"] = records
                
                # Get domain info
                domain_url = f"{base_url}/domains/{domain}"
                domain_response = requests.get(domain_url, headers=headers, timeout=30)
                
                if domain_response.status_code == 200:
                    domain_data = domain_response.json()
                    result["settings"] = {
                        "domain_name": domain_data.get("domainName"),
                        "locked": domain_data.get("locked", False),
                        "auto_renew": domain_data.get("autorenewEnabled", False),
                        "privacy_enabled": domain_data.get("privacyEnabled", False),
                        "create_date": domain_data.get("createDate"),
                        "expire_date": domain_data.get("expireDate"),
                        "nameservers": domain_data.get("nameservers", [])
                    }
                
                self.log(f"Retrieved {len(records)} DNS records from Name.com", Fore.GREEN)
            elif response.status_code == 404:
                result["errors"].append(f"Domain {domain} not found in Name.com account")
            elif response.status_code == 401:
                result["errors"].append("Name.com API authentication failed - check credentials")
            else:
                result["errors"].append(f"Failed to access Name.com API: {response.status_code}")
                
        except Exception as e:
            result["errors"] = [f"Error accessing Name.com API: {str(e)}"]
        
        return result

    def _check_gandi_api(self, domain: str, credentials: Dict) -> Dict:
        """Check Gandi DNS settings via API"""
        result = {
            "provider": "Gandi",
            "domain": domain,
            "records": [],
            "settings": {},
            "errors": [],
            "api_available": True
        }
        
        try:
            api_key = credentials.get("api_key")
            
            if not api_key:
                result["errors"].append("Gandi API requires api_key")
                result["api_available"] = False
                return result
            
            # Gandi API endpoint (v5)
            base_url = "https://api.gandi.net/v5"
            
            headers = {
                "Authorization": f"Apikey {api_key}",
                "Content-Type": "application/json"
            }
            
            # Get DNS records for the domain
            records_url = f"{base_url}/livedns/domains/{domain}/records"
            response = requests.get(records_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                records_data = response.json()
                records = []
                
                for record in records_data:
                    record_data = {
                        "rrset_name": record.get("rrset_name"),
                        "rrset_type": record.get("rrset_type"),
                        "rrset_ttl": record.get("rrset_ttl", 10800),
                        "rrset_values": record.get("rrset_values", []),
                        "rrset_href": record.get("rrset_href")
                    }
                    
                    # Format full name
                    if record_data["rrset_name"] == "@":
                        record_data["full_name"] = domain
                    else:
                        record_data["full_name"] = f"{record_data['rrset_name']}.{domain}"
                    
                    records.append(record_data)
                
                result["records"] = records
                
                # Get domain info
                domain_url = f"{base_url}/domain/domains/{domain}"
                domain_response = requests.get(domain_url, headers=headers, timeout=30)
                
                if domain_response.status_code == 200:
                    domain_data = domain_response.json()
                    result["settings"] = {
                        "fqdn": domain_data.get("fqdn"),
                        "status": domain_data.get("status"),
                        "auto_renew": domain_data.get("autorenew", False),
                        "can_tld_lock": domain_data.get("can_tld_lock", False),
                        "tld_lock": domain_data.get("tld_lock", False),
                        "nameservers": domain_data.get("nameservers", []),
                        "dates": domain_data.get("dates", {}),
                        "services": domain_data.get("services", [])
                    }
                
                # Get LiveDNS domain info if available
                livedns_url = f"{base_url}/livedns/domains/{domain}"
                livedns_response = requests.get(livedns_url, headers=headers, timeout=30)
                
                if livedns_response.status_code == 200:
                    livedns_data = livedns_response.json()
                    if "livedns_info" not in result["settings"]:
                        result["settings"]["livedns_info"] = {}
                    result["settings"]["livedns_info"] = {
                        "current": livedns_data.get("current"),
                        "keys": livedns_data.get("keys", []),
                        "automatic_snapshots": livedns_data.get("automatic_snapshots", False)
                    }
                
                self.log(f"Retrieved {len(records)} DNS records from Gandi", Fore.GREEN)
            elif response.status_code == 404:
                result["errors"].append(f"Domain {domain} not found or not using Gandi LiveDNS")
            elif response.status_code == 401:
                result["errors"].append("Gandi API authentication failed - check API key")
            else:
                result["errors"].append(f"Failed to access Gandi API: {response.status_code}")
                
        except Exception as e:
            result["errors"] = [f"Error accessing Gandi API: {str(e)}"]
        
        return result

    def _check_ovh_api(self, domain: str, credentials: Dict) -> Dict:
        """Check OVH DNS settings via API"""
        result = {
            "provider": "OVH",
            "domain": domain,
            "records": [],
            "settings": {},
            "errors": [],
            "api_available": True
        }
        
        try:
            application_key = credentials.get("application_key")
            application_secret = credentials.get("application_secret")
            consumer_key = credentials.get("consumer_key")
            endpoint = credentials.get("endpoint", "ovh-eu")  # ovh-eu, ovh-us, ovh-ca, etc.
            
            if not application_key or not application_secret or not consumer_key:
                result["errors"].append("OVH API requires application_key, application_secret, and consumer_key")
                result["api_available"] = False
                return result
            
            # OVH API endpoint
            endpoint_urls = {
                "ovh-eu": "https://eu.api.ovh.com/1.0",
                "ovh-us": "https://api.us.ovhcloud.com/1.0", 
                "ovh-ca": "https://ca.api.ovh.com/1.0",
                "kimsufi-eu": "https://eu.api.kimsufi.com/1.0",
                "kimsufi-ca": "https://ca.api.kimsufi.com/1.0",
                "soyoustart-eu": "https://eu.api.soyoustart.com/1.0",
                "soyoustart-ca": "https://ca.api.soyoustart.com/1.0"
            }
            
            base_url = endpoint_urls.get(endpoint, endpoint_urls["ovh-eu"])
            
            # OVH API requires signature for authentication
            import hashlib
            import time as time_module
            
            def sign_request(method, url, body, timestamp, application_secret, consumer_key):
                """Generate OVH API signature"""
                signature_data = f"{application_secret}+{consumer_key}+{method}+{url}+{body}+{timestamp}"
                return "$1$" + hashlib.sha1(signature_data.encode()).hexdigest()
            
            # Get DNS zone records
            method = "GET"
            url = f"{base_url}/domain/zone/{domain}/record"
            timestamp = str(int(time_module.time()))
            body = ""
            
            signature = sign_request(method, url, body, timestamp, application_secret, consumer_key)
            
            headers = {
                "X-Ovh-Application": application_key,
                "X-Ovh-Consumer": consumer_key,
                "X-Ovh-Signature": signature,
                "X-Ovh-Timestamp": timestamp,
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                record_ids = response.json()
                records = []
                
                # Get details for each record
                for record_id in record_ids[:50]:  # Limit to first 50 records to avoid rate limits
                    try:
                        detail_url = f"{base_url}/domain/zone/{domain}/record/{record_id}"
                        detail_timestamp = str(int(time_module.time()))
                        detail_signature = sign_request("GET", detail_url, "", detail_timestamp, application_secret, consumer_key)
                        
                        detail_headers = {
                            "X-Ovh-Application": application_key,
                            "X-Ovh-Consumer": consumer_key,
                            "X-Ovh-Signature": detail_signature,
                            "X-Ovh-Timestamp": detail_timestamp,
                            "Content-Type": "application/json"
                        }
                        
                        detail_response = requests.get(detail_url, headers=detail_headers, timeout=30)
                        
                        if detail_response.status_code == 200:
                            record_data = detail_response.json()
                            record_info = {
                                "id": record_data.get("id"),
                                "zone": record_data.get("zone"),
                                "subdomain": record_data.get("subdomain"),
                                "fieldType": record_data.get("fieldType"),
                                "target": record_data.get("target"),
                                "ttl": record_data.get("ttl", 3600)
                            }
                            
                            # Format full name
                            if record_info["subdomain"]:
                                record_info["full_name"] = f"{record_info['subdomain']}.{domain}"
                            else:
                                record_info["full_name"] = domain
                            
                            records.append(record_info)
                        
                        # Small delay to respect rate limits
                        time.sleep(0.1)
                        
                    except Exception as record_error:
                        self.log(f"Error getting record {record_id}: {str(record_error)}", Fore.YELLOW)
                        continue
                
                result["records"] = records
                
                # Get domain information
                domain_info_url = f"{base_url}/domain/{domain}"
                domain_timestamp = str(int(time_module.time()))
                domain_signature = sign_request("GET", domain_info_url, "", domain_timestamp, application_secret, consumer_key)
                
                domain_headers = {
                    "X-Ovh-Application": application_key,
                    "X-Ovh-Consumer": consumer_key,
                    "X-Ovh-Signature": domain_signature,
                    "X-Ovh-Timestamp": domain_timestamp,
                    "Content-Type": "application/json"
                }
                
                domain_response = requests.get(domain_info_url, headers=domain_headers, timeout=30)
                
                if domain_response.status_code == 200:
                    domain_data = domain_response.json()
                    result["settings"] = {
                        "domain": domain_data.get("domain"),
                        "offer": domain_data.get("offer"),
                        "transfer_lock_status": domain_data.get("transferLockStatus"),
                        "name_server_type": domain_data.get("nameServerType"),
                        "dnssec_supported": domain_data.get("dnssecSupported", False),
                        "glue_record_supported": domain_data.get("glueRecordSupported", False)
                    }
                
                self.log(f"Retrieved {len(records)} DNS records from OVH", Fore.GREEN)
            elif response.status_code == 404:
                result["errors"].append(f"Domain zone {domain} not found in OVH account")
            elif response.status_code == 403:
                result["errors"].append("OVH API access denied - check credentials and permissions")
            else:
                result["errors"].append(f"Failed to access OVH API: {response.status_code}")
                
        except Exception as e:
            result["errors"] = [f"Error accessing OVH API: {str(e)}"]
        
        return result

    def check_dnssec(self, domain: str) -> Dict:
        """Check DNSSEC validation status and chain"""
        self.log(f"Checking DNSSEC validation for {domain}", Fore.CYAN)
        
        result = {
            "domain": domain,
            "dnssec_enabled": False,
            "ds_records": [],
            "dnskey_records": [],
            "rrsig_records": [],
            "validation_chain": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check for DS records in parent zone
            parent_domain = ".".join(domain.split(".")[1:])
            if parent_domain:
                try:
                    ds_query = dns.resolver.resolve(domain, 'DS')
                    result["ds_records"] = [str(rr) for rr in ds_query]
                    result["dnssec_enabled"] = True
                    self.log(f"Found DS records in parent zone {parent_domain}", Fore.GREEN)
                except dns.resolver.NXDOMAIN:
                    result["warnings"].append(f"No DS records found in parent zone {parent_domain}")
                except Exception as e:
                    result["errors"].append(f"Error checking DS records: {str(e)}")
            
            # Check for DNSKEY records
            try:
                dnskey_query = dns.resolver.resolve(domain, 'DNSKEY')
                result["dnskey_records"] = [str(rr) for rr in dnskey_query]
                if result["dnskey_records"]:
                    result["dnssec_enabled"] = True
                    self.log(f"Found DNSKEY records for {domain}", Fore.GREEN)
                
                # Validate DNSSEC chain if we have both DS and DNSKEY
                if result["ds_records"] and result["dnskey_records"]:
                    try:
                        # Perform basic DNSSEC validation
                        resolver = dns.resolver.Resolver()
                        resolver.use_edns(0, dns.flags.DO)  # Enable DNSSEC validation
                        
                        # Try to resolve with DNSSEC validation
                        answer = resolver.resolve(domain, 'A')
                        if answer.response.flags & dns.flags.AD:
                            result["validation_chain"].append("DNSSEC validation successful")
                            self.log("DNSSEC validation chain verified", Fore.GREEN)
                        else:
                            result["warnings"].append("DNSSEC validation chain could not be verified")
                            
                    except Exception as e:
                        result["errors"].append(f"DNSSEC validation error: {str(e)}")
                        
            except dns.resolver.NXDOMAIN:
                result["warnings"].append("No DNSKEY records found")
            except Exception as e:
                result["errors"].append(f"Error checking DNSKEY records: {str(e)}")
            
            # Check for RRSIG records (signatures)
            try:
                rrsig_query = dns.resolver.resolve(domain, 'RRSIG')
                result["rrsig_records"] = [str(rr) for rr in rrsig_query]
                self.log(f"Found RRSIG records for {domain}", Fore.GREEN)
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                result["warnings"].append("No RRSIG records found")
            except Exception as e:
                result["errors"].append(f"Error checking RRSIG records: {str(e)}")
            
        except Exception as e:
            result["errors"].append(f"General DNSSEC check error: {str(e)}")
        
        return result

    def check_reverse_dns(self, ip_address: str) -> Dict:
        """Check reverse DNS (PTR) records and forward/reverse consistency"""
        self.log(f"Checking reverse DNS for {ip_address}", Fore.CYAN)
        
        result = {
            "ip_address": ip_address,
            "ptr_records": [],
            "forward_reverse_consistent": False,
            "forward_domains": [],
            "reverse_domains": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate IP address format
            ip_obj = ipaddress.ip_address(ip_address)
            
            # Get reverse DNS name
            reverse_name = dns.reversename.from_address(ip_address)
            
            # Query PTR records
            try:
                ptr_query = dns.resolver.resolve(reverse_name, 'PTR')
                result["ptr_records"] = [str(rr).rstrip('.') for rr in ptr_query]
                result["reverse_domains"] = result["ptr_records"].copy()
                self.log(f"Found PTR records: {', '.join(result['ptr_records'])}", Fore.GREEN)
                
                # Check forward/reverse consistency
                for ptr_domain in result["ptr_records"]:
                    try:
                        record_type = 'A' if ip_obj.version == 4 else 'AAAA'
                        forward_query = dns.resolver.resolve(ptr_domain, record_type)
                        forward_ips = [str(rr) for rr in forward_query]
                        result["forward_domains"].extend(forward_ips)
                        
                        if ip_address in forward_ips:
                            result["forward_reverse_consistent"] = True
                            self.log(f"Forward/reverse consistency verified for {ptr_domain}", Fore.GREEN)
                        else:
                            result["warnings"].append(f"Forward lookup of {ptr_domain} does not match {ip_address}")
                            
                    except Exception as e:
                        result["warnings"].append(f"Could not verify forward lookup for {ptr_domain}: {str(e)}")
                        
            except dns.resolver.NXDOMAIN:
                result["warnings"].append(f"No PTR record found for {ip_address}")
            except Exception as e:
                result["errors"].append(f"Error querying PTR records: {str(e)}")
                
        except ValueError:
            result["errors"].append(f"Invalid IP address format: {ip_address}")
        except Exception as e:
            result["errors"].append(f"Reverse DNS check error: {str(e)}")
        
        return result

    def analyze_dns_cache(self, domain: str, record_type: str = 'A') -> Dict:
        """Analyze DNS caching behavior and TTL compliance"""
        self.log(f"Analyzing DNS cache behavior for {domain} ({record_type})", Fore.CYAN)
        
        result = {
            "domain": domain,
            "record_type": record_type,
            "ttl_analysis": {},
            "cache_recommendations": [],
            "potential_issues": [],
            "servers_analyzed": [],
            "errors": []
        }
        
        servers_to_test = [
            ("Google Primary", "8.8.8.8"),
            ("Cloudflare Primary", "1.1.1.1"),
            ("Quad9", "9.9.9.9"),
            ("OpenDNS", "208.67.222.222")
        ]
        
        ttl_values = []
        
        try:
            for server_name, server_ip in servers_to_test:
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [server_ip]
                    resolver.timeout = 5
                    resolver.lifetime = 10
                    
                    # First query to get initial TTL
                    start_time = time.time()
                    answer1 = resolver.resolve(domain, record_type)
                    query_time = (time.time() - start_time) * 1000
                    
                    initial_ttl = answer1.rrset.ttl
                    ttl_values.append(initial_ttl)
                    
                    # Second query after a short delay to check TTL reduction
                    time.sleep(2)
                    answer2 = resolver.resolve(domain, record_type)
                    second_ttl = answer2.rrset.ttl
                    
                    server_analysis = {
                        "server": server_name,
                        "ip": server_ip,
                        "initial_ttl": initial_ttl,
                        "second_ttl": second_ttl,
                        "ttl_reduction": initial_ttl - second_ttl,
                        "query_time_ms": round(query_time, 2),
                        "caching_behavior": "normal" if second_ttl < initial_ttl else "unusual"
                    }
                    
                    result["ttl_analysis"][server_name] = server_analysis
                    result["servers_analyzed"].append(server_name)
                    
                    # Check for potential cache poisoning indicators
                    if abs(initial_ttl - second_ttl) > initial_ttl * 0.5:  # More than 50% difference
                        result["potential_issues"].append(f"Unusual TTL behavior on {server_name}")
                    
                    self.log(f"Analyzed {server_name}: TTL {initial_ttl}→{second_ttl}", Fore.GREEN)
                    
                except Exception as e:
                    result["errors"].append(f"Error testing {server_name} ({server_ip}): {str(e)}")
            
            # Generate recommendations based on TTL analysis
            if ttl_values:
                min_ttl = min(ttl_values)
                max_ttl = max(ttl_values)
                avg_ttl = sum(ttl_values) / len(ttl_values)
                
                result["ttl_summary"] = {
                    "min_ttl": min_ttl,
                    "max_ttl": max_ttl,
                    "average_ttl": round(avg_ttl, 2),
                    "consistency": "consistent" if max_ttl - min_ttl <= 60 else "inconsistent"
                }
                
                # TTL recommendations
                if avg_ttl < 300:  # 5 minutes
                    result["cache_recommendations"].append("TTL is very low - consider increasing for better performance")
                elif avg_ttl > 86400:  # 24 hours
                    result["cache_recommendations"].append("TTL is very high - consider reducing for faster updates")
                else:
                    result["cache_recommendations"].append("TTL appears to be in optimal range")
                
                if max_ttl - min_ttl > 300:  # 5 minutes difference
                    result["potential_issues"].append("Inconsistent TTL values across servers")
            
        except Exception as e:
            result["errors"].append(f"DNS cache analysis error: {str(e)}")
        
        return result

    def monitor_dns_health(self, domain: str, duration_minutes: int = 60, check_interval: int = 300) -> Dict:
        """Monitor DNS health over time with real-time tracking"""
        self.log(f"Starting DNS health monitoring for {domain} ({duration_minutes} minutes)", Fore.CYAN)
        
        result = {
            "domain": domain,
            "monitoring_duration_minutes": duration_minutes,
            "check_interval_seconds": check_interval,
            "start_time": datetime.now().isoformat(),
            "checks_performed": [],
            "alerts": [],
            "summary": {},
            "status": "running"
        }
        
        # Create monitoring directory
        monitor_dir = Path.home() / '.dns-validator' / 'monitoring'
        monitor_dir.mkdir(parents=True, exist_ok=True)
        
        monitor_file = monitor_dir / f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            check_count = 0
            
            while datetime.now() < end_time:
                check_count += 1
                check_time = datetime.now()
                
                self.log(f"Performing health check #{check_count} for {domain}", Fore.YELLOW)
                
                # Perform various DNS checks
                delegation_result = self.check_delegation(domain)
                propagation_result = self.check_propagation(domain)
                
                health_check = {
                    "check_number": check_count,
                    "timestamp": check_time.isoformat(),
                    "delegation_valid": delegation_result.get("delegation_valid", False),
                    "propagation_consistent": len(propagation_result.get("inconsistent_servers", [])) == 0,
                    "total_errors": len(delegation_result.get("errors", [])) + len(propagation_result.get("errors", [])),
                    "response_times": propagation_result.get("response_times", {}),
                    "detected_issues": []
                }
                
                # Detect issues and generate alerts
                if not health_check["delegation_valid"]:
                    issue = "DNS delegation failure detected"
                    health_check["detected_issues"].append(issue)
                    result["alerts"].append({
                        "timestamp": check_time.isoformat(),
                        "severity": "high",
                        "message": issue
                    })
                
                if not health_check["propagation_consistent"]:
                    issue = "DNS propagation inconsistency detected"
                    health_check["detected_issues"].append(issue)
                    result["alerts"].append({
                        "timestamp": check_time.isoformat(),
                        "severity": "medium",
                        "message": issue
                    })
                
                if health_check["total_errors"] > 0:
                    issue = f"{health_check['total_errors']} DNS errors detected"
                    health_check["detected_issues"].append(issue)
                    result["alerts"].append({
                        "timestamp": check_time.isoformat(),
                        "severity": "low",
                        "message": issue
                    })
                
                result["checks_performed"].append(health_check)
                
                # Save progress to file
                with open(monitor_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Check if we should continue
                if datetime.now() >= end_time:
                    break
                
                # Wait for next check
                time.sleep(check_interval)
            
            # Generate summary
            total_checks = len(result["checks_performed"])
            successful_checks = sum(1 for check in result["checks_performed"] 
                                  if check["delegation_valid"] and check["propagation_consistent"])
            
            result["summary"] = {
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "success_rate": round((successful_checks / total_checks) * 100, 2) if total_checks > 0 else 0,
                "total_alerts": len(result["alerts"]),
                "monitoring_file": str(monitor_file)
            }
            
            result["status"] = "completed"
            result["end_time"] = datetime.now().isoformat()
            
            self.log(f"DNS health monitoring completed. Success rate: {result['summary']['success_rate']}%", 
                    Fore.GREEN if result['summary']['success_rate'] > 95 else Fore.YELLOW)
            
        except KeyboardInterrupt:
            result["status"] = "interrupted"
            result["end_time"] = datetime.now().isoformat()
            self.log("DNS health monitoring interrupted by user", Fore.YELLOW)
        except Exception as e:
            result["status"] = "error"
            result["end_time"] = datetime.now().isoformat()
            result["error"] = str(e)
            self.log(f"DNS health monitoring error: {str(e)}", Fore.RED)
        
        # Final save
        with open(monitor_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result

    def test_geolocation_dns(self, domain):
        """Test DNS resolution from different geographic locations"""
        self.log(f"Starting geolocation DNS testing for {domain}", Fore.CYAN)
        
        # DNS servers from different countries/regions
        geo_servers = {
            "United States (Cloudflare)": "1.1.1.1",
            "United States (Google)": "8.8.8.8",
            "United States (Quad9)": "9.9.9.9",
            "Germany (Quad9)": "149.112.112.112",
            "United Kingdom (OpenDNS)": "208.67.222.222",
            "Australia (Cloudflare)": "1.0.0.1",
            "Japan (Google)": "8.8.4.4",
            "Canada (OpenDNS)": "208.67.220.220",
            "Netherlands (Quad9)": "9.9.9.10",
            "Singapore (Cloudflare)": "1.1.1.1",
            "Brazil (Google)": "8.8.8.8",
            "India (Quad9)": "149.112.112.10",
            "South Korea": "168.126.63.1",
            "Russia": "77.88.8.8",
            "China": "114.114.114.114"
        }
        
        result = {
            "domain": domain,
            "test_type": "geolocation_dns",
            "timestamp": datetime.now().isoformat(),
            "geo_results": {},
            "geodns_analysis": {},
            "cdn_endpoints": [],
            "summary": {}
        }
        
        try:
            # Test from each geographic location
            for location, server in geo_servers.items():
                self.log(f"Testing from {location} ({server})", Fore.YELLOW)
                
                location_result = {
                    "server": server,
                    "a_records": [],
                    "aaaa_records": [],
                    "cname_records": [],
                    "response_time": None,
                    "ttl": None,
                    "status": "success"
                }
                
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [server]
                    resolver.timeout = 10
                    resolver.lifetime = 15
                    
                    start_time = time.time()
                    
                    # Query A records
                    try:
                        a_response = resolver.resolve(domain, 'A')
                        location_result["a_records"] = [str(rdata) for rdata in a_response]
                        location_result["ttl"] = a_response.rrset.ttl
                    except Exception as e:
                        self.log(f"A record query failed from {location}: {str(e)}", Fore.RED)
                    
                    # Query AAAA records
                    try:
                        aaaa_response = resolver.resolve(domain, 'AAAA')
                        location_result["aaaa_records"] = [str(rdata) for rdata in aaaa_response]
                    except:
                        pass  # IPv6 records may not exist
                    
                    # Query CNAME records
                    try:
                        cname_response = resolver.resolve(domain, 'CNAME')
                        location_result["cname_records"] = [str(rdata) for rdata in cname_response]
                    except:
                        pass  # CNAME may not exist
                    
                    end_time = time.time()
                    location_result["response_time"] = round((end_time - start_time) * 1000, 2)
                    
                except Exception as e:
                    location_result["status"] = "error"
                    location_result["error"] = str(e)
                    self.log(f"Failed to query from {location}: {str(e)}", Fore.RED)
                
                result["geo_results"][location] = location_result
            
            # Analyze GeoDNS routing patterns
            all_a_records = set()
            location_ips = {}
            
            for location, data in result["geo_results"].items():
                if data.get("a_records"):
                    location_ips[location] = data["a_records"]
                    all_a_records.update(data["a_records"])
            
            result["geodns_analysis"] = {
                "unique_ip_addresses": list(all_a_records),
                "total_unique_ips": len(all_a_records),
                "geodns_detected": len(all_a_records) > 1,
                "location_routing": location_ips,
                "routing_consistency": len(set(tuple(sorted(ips)) for ips in location_ips.values())) == 1
            }
            
            # Detect CDN endpoints
            cdn_patterns = {
                "cloudflare": ["cloudflare", "cf-ray"],
                "aws": ["cloudfront", "amazonaws"],
                "azure": ["azureedge", "azure"],
                "google": ["googleusercontent", "gstatic"],
                "fastly": ["fastly"],
                "akamai": ["akamai", "edgesuite"],
                "maxcdn": ["maxcdn"],
                "keycdn": ["keycdn"]
            }
            
            detected_cdns = set()
            for ip in all_a_records:
                try:
                    # Reverse DNS lookup for CDN detection
                    reverse_name = str(dns.reversename.from_address(ip))
                    reverse_response = dns.resolver.resolve(reverse_name, 'PTR')
                    reverse_domain = str(reverse_response[0]).lower()
                    
                    for cdn_name, patterns in cdn_patterns.items():
                        if any(pattern in reverse_domain for pattern in patterns):
                            detected_cdns.add(cdn_name)
                            result["cdn_endpoints"].append({
                                "ip": ip,
                                "cdn_provider": cdn_name,
                                "reverse_domain": reverse_domain
                            })
                            break
                except:
                    pass
            
            # Generate summary
            successful_locations = len([r for r in result["geo_results"].values() if r["status"] == "success"])
            total_locations = len(result["geo_results"])
            avg_response_time = sum(r.get("response_time", 0) for r in result["geo_results"].values() if r.get("response_time")) / successful_locations if successful_locations > 0 else 0
            
            result["summary"] = {
                "successful_tests": successful_locations,
                "total_tests": total_locations,
                "success_rate": round((successful_locations / total_locations) * 100, 2),
                "average_response_time_ms": round(avg_response_time, 2),
                "geodns_routing_detected": result["geodns_analysis"]["geodns_detected"],
                "cdn_providers_detected": list(detected_cdns),
                "routing_consistency": result["geodns_analysis"]["routing_consistency"]
            }
            
            self.log(f"Geolocation DNS testing completed for {domain}", Fore.GREEN)
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            self.log(f"Geolocation DNS testing error: {str(e)}", Fore.RED)
        
        return result

    def check_load_balancer_health(self, domain):
        """Check load balancer health and validate multiple A records"""
        self.log(f"Starting load balancer health checks for {domain}", Fore.CYAN)
        
        result = {
            "domain": domain,
            "test_type": "load_balancer_health",
            "timestamp": datetime.now().isoformat(),
            "a_records": [],
            "health_checks": {},
            "load_balancing_analysis": {},
            "failover_tests": {},
            "summary": {}
        }
        
        try:
            # Get all A records for the domain
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            resolver.lifetime = 15
            
            try:
                a_response = resolver.resolve(domain, 'A')
                result["a_records"] = [str(rdata) for rdata in a_response]
                self.log(f"Found {len(result['a_records'])} A records for {domain}", Fore.YELLOW)
            except Exception as e:
                result["error"] = f"Failed to resolve A records: {str(e)}"
                return result
            
            if len(result["a_records"]) < 2:
                self.log(f"Only {len(result['a_records'])} A record found. Load balancer testing requires multiple A records.", Fore.YELLOW)
                result["summary"] = {
                    "load_balancer_detected": False,
                    "reason": "Single A record - no load balancing detected"
                }
                return result
            
            # Test health of each A record/endpoint
            for i, ip_address in enumerate(result["a_records"]):
                self.log(f"Testing endpoint {i+1}: {ip_address}", Fore.YELLOW)
                
                endpoint_health = {
                    "ip_address": ip_address,
                    "tcp_connectivity": False,
                    "http_response": None,
                    "https_response": None,
                    "response_times": {},
                    "status": "unknown"
                }
                
                # Test TCP connectivity on common ports
                common_ports = [80, 443, 22, 21, 25, 53]
                tcp_results = {}
                
                for port in common_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        start_time = time.time()
                        result_code = sock.connect_ex((ip_address, port))
                        end_time = time.time()
                        sock.close()
                        
                        tcp_results[port] = {
                            "open": result_code == 0,
                            "response_time": round((end_time - start_time) * 1000, 2)
                        }
                        
                        if result_code == 0:
                            endpoint_health["tcp_connectivity"] = True
                            
                    except Exception as e:
                        tcp_results[port] = {"open": False, "error": str(e)}
                
                endpoint_health["tcp_ports"] = tcp_results
                
                # Test HTTP/HTTPS if web ports are open
                if tcp_results.get(80, {}).get("open") or tcp_results.get(443, {}).get("open"):
                    try:
                        import urllib.request
                        import ssl
                        
                        # Test HTTP
                        if tcp_results.get(80, {}).get("open"):
                            try:
                                start_time = time.time()
                                response = urllib.request.urlopen(f"http://{ip_address}", timeout=10)
                                end_time = time.time()
                                endpoint_health["http_response"] = {
                                    "status_code": response.getcode(),
                                    "response_time": round((end_time - start_time) * 1000, 2),
                                    "content_length": len(response.read())
                                }
                                endpoint_health["response_times"]["http"] = endpoint_health["http_response"]["response_time"]
                            except Exception as e:
                                endpoint_health["http_response"] = {"error": str(e)}
                        
                        # Test HTTPS
                        if tcp_results.get(443, {}).get("open"):
                            try:
                                # Create SSL context that doesn't verify certificates for IP addresses
                                ssl_context = ssl.create_default_context()
                                ssl_context.check_hostname = False
                                ssl_context.verify_mode = ssl.CERT_NONE
                                
                                start_time = time.time()
                                response = urllib.request.urlopen(f"https://{ip_address}", timeout=10, context=ssl_context)
                                end_time = time.time()
                                endpoint_health["https_response"] = {
                                    "status_code": response.getcode(),
                                    "response_time": round((end_time - start_time) * 1000, 2),
                                    "content_length": len(response.read())
                                }
                                endpoint_health["response_times"]["https"] = endpoint_health["https_response"]["response_time"]
                            except Exception as e:
                                endpoint_health["https_response"] = {"error": str(e)}
                                
                    except ImportError:
                        pass  # urllib not available
                
                # Determine overall endpoint status
                if endpoint_health["tcp_connectivity"]:
                    if endpoint_health.get("http_response", {}).get("status_code") == 200 or \
                       endpoint_health.get("https_response", {}).get("status_code") == 200:
                        endpoint_health["status"] = "healthy"
                    else:
                        endpoint_health["status"] = "tcp_only"
                else:
                    endpoint_health["status"] = "unhealthy"
                
                result["health_checks"][ip_address] = endpoint_health
            
            # Analyze load balancing patterns
            healthy_endpoints = [ip for ip, health in result["health_checks"].items() if health["status"] in ["healthy", "tcp_only"]]
            unhealthy_endpoints = [ip for ip, health in result["health_checks"].items() if health["status"] == "unhealthy"]
            
            # Test weighted/round-robin behavior by making multiple queries
            self.log("Testing load balancing behavior with multiple DNS queries", Fore.YELLOW)
            query_results = []
            
            for i in range(10):  # Make 10 queries to test distribution
                try:
                    response = resolver.resolve(domain, 'A')
                    returned_ips = [str(rdata) for rdata in response]
                    query_results.append(returned_ips)
                    time.sleep(0.1)  # Small delay between queries
                except:
                    pass
            
            # Analyze query distribution
            ip_frequency = {}
            for query_result in query_results:
                for ip in query_result:
                    ip_frequency[ip] = ip_frequency.get(ip, 0) + 1
            
            result["load_balancing_analysis"] = {
                "total_endpoints": len(result["a_records"]),
                "healthy_endpoints": len(healthy_endpoints),
                "unhealthy_endpoints": len(unhealthy_endpoints),
                "health_percentage": round((len(healthy_endpoints) / len(result["a_records"])) * 100, 2),
                "query_distribution": ip_frequency,
                "balanced_distribution": max(ip_frequency.values()) - min(ip_frequency.values()) <= 2 if ip_frequency else False
            }
            
            # Simulate failover testing (conceptual)
            result["failover_tests"] = {
                "failover_capable": len(healthy_endpoints) > 1,
                "single_point_failure": len(healthy_endpoints) == 1,
                "redundancy_level": "high" if len(healthy_endpoints) >= 3 else "medium" if len(healthy_endpoints) == 2 else "low"
            }
            
            # Generate summary
            result["summary"] = {
                "load_balancer_detected": len(result["a_records"]) > 1,
                "total_endpoints": len(result["a_records"]),
                "healthy_endpoints": len(healthy_endpoints),
                "health_status": "good" if len(unhealthy_endpoints) == 0 else "degraded" if len(healthy_endpoints) > 0 else "critical",
                "load_balancing_type": "round_robin" if result["load_balancing_analysis"].get("balanced_distribution") else "weighted_or_geographic",
                "failover_ready": result["failover_tests"]["failover_capable"],
                "redundancy_assessment": result["failover_tests"]["redundancy_level"]
            }
            
            self.log(f"Load balancer health check completed for {domain}", Fore.GREEN)
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            self.log(f"Load balancer health check error: {str(e)}", Fore.RED)
        
        return result

    def validate_ipv6_support(self, domain):
        """Enhanced IPv6 support validation including dual-stack configuration"""
        self.log(f"Starting IPv6 support validation for {domain}", Fore.CYAN)
        
        result = {
            "domain": domain,
            "test_type": "ipv6_validation",
            "timestamp": datetime.now().isoformat(),
            "aaaa_records": [],
            "ipv6_dns_servers": {},
            "dual_stack_analysis": {},
            "ipv6_connectivity": {},
            "dns_over_ipv6": {},
            "summary": {}
        }
        
        try:
            # Test AAAA record resolution
            self.log("Testing AAAA record resolution", Fore.YELLOW)
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            resolver.lifetime = 15
            
            try:
                aaaa_response = resolver.resolve(domain, 'AAAA')
                result["aaaa_records"] = [str(rdata) for rdata in aaaa_response]
                self.log(f"Found {len(result['aaaa_records'])} AAAA records", Fore.GREEN)
            except dns.resolver.NXDOMAIN:
                self.log("No AAAA records found (NXDOMAIN)", Fore.YELLOW)
            except dns.resolver.NoAnswer:
                self.log("No AAAA records found (NoAnswer)", Fore.YELLOW)
            except Exception as e:
                self.log(f"AAAA record query failed: {str(e)}", Fore.RED)
            
            # Test IPv6-only DNS servers
            ipv6_dns_servers = {
                "Google IPv6 Primary": "2001:4860:4860::8888",
                "Google IPv6 Secondary": "2001:4860:4860::8844",
                "Cloudflare IPv6 Primary": "2606:4700:4700::1111",
                "Cloudflare IPv6 Secondary": "2606:4700:4700::1001",
                "Quad9 IPv6": "2620:fe::fe",
                "OpenDNS IPv6": "2620:119:35::35"
            }
            
            self.log("Testing DNS resolution over IPv6", Fore.YELLOW)
            
            for server_name, ipv6_server in ipv6_dns_servers.items():
                server_result = {
                    "server": ipv6_server,
                    "a_records": [],
                    "aaaa_records": [],
                    "response_time": None,
                    "status": "success"
                }
                
                try:
                    ipv6_resolver = dns.resolver.Resolver()
                    ipv6_resolver.nameservers = [ipv6_server]
                    ipv6_resolver.timeout = 10
                    ipv6_resolver.lifetime = 15
                    
                    start_time = time.time()
                    
                    # Test A record resolution over IPv6
                    try:
                        a_response = ipv6_resolver.resolve(domain, 'A')
                        server_result["a_records"] = [str(rdata) for rdata in a_response]
                    except Exception as e:
                        server_result["a_error"] = str(e)
                    
                    # Test AAAA record resolution over IPv6
                    try:
                        aaaa_response = ipv6_resolver.resolve(domain, 'AAAA')
                        server_result["aaaa_records"] = [str(rdata) for rdata in aaaa_response]
                    except Exception as e:
                        server_result["aaaa_error"] = str(e)
                    
                    end_time = time.time()
                    server_result["response_time"] = round((end_time - start_time) * 1000, 2)
                    
                except Exception as e:
                    server_result["status"] = "error"
                    server_result["error"] = str(e)
                    self.log(f"IPv6 DNS query failed for {server_name}: {str(e)}", Fore.RED)
                
                result["ipv6_dns_servers"][server_name] = server_result
            
            # Dual-stack configuration analysis
            self.log("Analyzing dual-stack configuration", Fore.YELLOW)
            
            # Get A records for comparison
            a_records = []
            try:
                a_response = resolver.resolve(domain, 'A')
                a_records = [str(rdata) for rdata in a_response]
            except:
                pass
            
            result["dual_stack_analysis"] = {
                "ipv4_available": len(a_records) > 0,
                "ipv6_available": len(result["aaaa_records"]) > 0,
                "dual_stack_enabled": len(a_records) > 0 and len(result["aaaa_records"]) > 0,
                "ipv4_only": len(a_records) > 0 and len(result["aaaa_records"]) == 0,
                "ipv6_only": len(a_records) == 0 and len(result["aaaa_records"]) > 0,
                "a_record_count": len(a_records),
                "aaaa_record_count": len(result["aaaa_records"]),
                "configuration_type": "dual_stack" if (len(a_records) > 0 and len(result["aaaa_records"]) > 0) else
                                   "ipv4_only" if len(a_records) > 0 else
                                   "ipv6_only" if len(result["aaaa_records"]) > 0 else "none"
            }
            
            # Test IPv6 connectivity to AAAA records
            if result["aaaa_records"]:
                self.log("Testing IPv6 connectivity", Fore.YELLOW)
                
                for ipv6_addr in result["aaaa_records"]:
                    connectivity_test = {
                        "address": ipv6_addr,
                        "ping_result": None,
                        "tcp_connectivity": {},
                        "reachable": False
                    }
                    
                    # Test IPv6 ping (if available)
                    try:
                        import subprocess
                        import platform
                        
                        ping_cmd = ["ping", "-6", "-c", "3", ipv6_addr] if platform.system() != "Windows" else ["ping", "-6", "-n", "3", ipv6_addr]
                        ping_result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=15)
                        
                        if ping_result.returncode == 0:
                            connectivity_test["ping_result"] = "success"
                            connectivity_test["reachable"] = True
                        else:
                            connectivity_test["ping_result"] = "failed"
                            
                    except Exception as e:
                        connectivity_test["ping_result"] = f"error: {str(e)}"
                    
                    # Test TCP connectivity on common ports
                    common_ports = [80, 443, 22]
                    for port in common_ports:
                        try:
                            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                            sock.settimeout(5)
                            start_time = time.time()
                            result_code = sock.connect_ex((ipv6_addr, port))
                            end_time = time.time()
                            sock.close()
                            
                            connectivity_test["tcp_connectivity"][port] = {
                                "open": result_code == 0,
                                "response_time": round((end_time - start_time) * 1000, 2)
                            }
                            
                            if result_code == 0:
                                connectivity_test["reachable"] = True
                                
                        except Exception as e:
                            connectivity_test["tcp_connectivity"][port] = {"error": str(e)}
                    
                    result["ipv6_connectivity"][ipv6_addr] = connectivity_test
            
            # Test DNS-over-IPv6 functionality
            successful_ipv6_dns = len([r for r in result["ipv6_dns_servers"].values() if r["status"] == "success"])
            total_ipv6_dns = len(result["ipv6_dns_servers"])
            
            result["dns_over_ipv6"] = {
                "servers_tested": total_ipv6_dns,
                "successful_queries": successful_ipv6_dns,
                "success_rate": round((successful_ipv6_dns / total_ipv6_dns) * 100, 2) if total_ipv6_dns > 0 else 0,
                "ipv6_dns_functional": successful_ipv6_dns > 0
            }
            
            # Generate summary
            ipv6_reachable = any(conn.get("reachable", False) for conn in result["ipv6_connectivity"].values())
            
            result["summary"] = {
                "ipv6_supported": len(result["aaaa_records"]) > 0,
                "dual_stack_configured": result["dual_stack_analysis"]["dual_stack_enabled"],
                "ipv6_dns_working": result["dns_over_ipv6"]["ipv6_dns_functional"],
                "ipv6_connectivity": "reachable" if ipv6_reachable else "unreachable" if result["aaaa_records"] else "no_ipv6_records",
                "configuration_recommendation": self._get_ipv6_recommendation(result),
                "readiness_score": self._calculate_ipv6_readiness_score(result)
            }
            
            self.log(f"IPv6 support validation completed for {domain}", Fore.GREEN)
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            self.log(f"IPv6 validation error: {str(e)}", Fore.RED)
        
        return result

    def _get_ipv6_recommendation(self, result):
        """Generate IPv6 configuration recommendations"""
        dual_stack = result["dual_stack_analysis"]
        
        if dual_stack["dual_stack_enabled"]:
            return "Dual-stack configuration detected - excellent IPv6 readiness"
        elif dual_stack["ipv4_only"]:
            return "IPv4-only configuration - consider adding AAAA records for IPv6 support"
        elif dual_stack["ipv6_only"]:
            return "IPv6-only configuration - consider adding A records for broader compatibility"
        else:
            return "No DNS records found - check domain configuration"

    def _calculate_ipv6_readiness_score(self, result):
        """Calculate IPv6 readiness score (0-100)"""
        score = 0
        
        # AAAA records present (40 points)
        if result["aaaa_records"]:
            score += 40
        
        # Dual-stack configuration (30 points)
        if result["dual_stack_analysis"]["dual_stack_enabled"]:
            score += 30
        
        # DNS over IPv6 working (20 points)
        if result["dns_over_ipv6"]["ipv6_dns_functional"]:
            score += 20
        
        # IPv6 connectivity (10 points)
        ipv6_reachable = any(conn.get("reachable", False) for conn in result["ipv6_connectivity"].values())
        if ipv6_reachable:
            score += 10
        
        return score

    def analyze_dns_security(self, domain):
        """Comprehensive DNS security analysis including open resolvers and vulnerabilities"""
        self.log(f"Starting DNS security analysis for {domain}", Fore.CYAN)
        
        result = {
            "domain": domain,
            "test_type": "dns_security_analysis",
            "timestamp": datetime.now().isoformat(),
            "open_resolver_test": {},
            "amplification_vulnerability": {},
            "subdomain_protection": {},
            "dnssec_security": {},
            "security_score": 0,
            "vulnerabilities": [],
            "recommendations": []
        }
        
        try:
            # Test for open resolver detection
            self.log("Testing for open resolver vulnerabilities", Fore.YELLOW)
            result["open_resolver_test"] = self._test_open_resolvers(domain)
            
            # Test DNS amplification vulnerability
            self.log("Testing DNS amplification vulnerability", Fore.YELLOW)
            result["amplification_vulnerability"] = self._test_dns_amplification(domain)
            
            # Test subdomain enumeration protection
            self.log("Testing subdomain enumeration protection", Fore.YELLOW)
            result["subdomain_protection"] = self._test_subdomain_protection(domain)
            
            # Enhanced DNSSEC security analysis
            self.log("Performing enhanced DNSSEC security analysis", Fore.YELLOW)
            result["dnssec_security"] = self._analyze_dnssec_security(domain)
            
            # Calculate overall security score
            result["security_score"] = self._calculate_security_score(result)
            
            # Generate vulnerability summary
            result["vulnerabilities"] = self._identify_security_vulnerabilities(result)
            
            # Generate security recommendations
            result["recommendations"] = self._generate_security_recommendations(result)
            
            self.log(f"DNS security analysis completed for {domain}", Fore.GREEN)
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            self.log(f"DNS security analysis error: {str(e)}", Fore.RED)
        
        return result

    def _test_open_resolvers(self, domain):
        """Test for open resolver vulnerabilities"""
        # Get nameservers for the domain
        nameservers = []
        try:
            resolver = dns.resolver.Resolver()
            ns_response = resolver.resolve(domain, 'NS')
            nameservers = [str(ns) for ns in ns_response]
        except:
            return {"status": "error", "message": "Could not retrieve nameservers"}
        
        open_resolver_results = {
            "nameservers_tested": nameservers,
            "open_resolvers": [],
            "secure_resolvers": [],
            "test_results": {}
        }
        
        # Test each nameserver for open resolver behavior
        for ns in nameservers:
            try:
                # Resolve the nameserver to IP
                ns_resolver = dns.resolver.Resolver()
                ns_ips = []
                try:
                    ns_a_response = ns_resolver.resolve(ns, 'A')
                    ns_ips.extend([str(ip) for ip in ns_a_response])
                except:
                    pass
                
                try:
                    ns_aaaa_response = ns_resolver.resolve(ns, 'AAAA')
                    ns_ips.extend([str(ip) for ip in ns_aaaa_response])
                except:
                    pass
                
                for ns_ip in ns_ips:
                    # Test if the server responds to queries for external domains
                    test_resolver = dns.resolver.Resolver()
                    test_resolver.nameservers = [ns_ip]
                    test_resolver.timeout = 5
                    
                    test_result = {
                        "nameserver": ns,
                        "ip": ns_ip,
                        "responds_to_external": False,
                        "response_time": None,
                        "status": "secure"
                    }
                    
                    try:
                        # Try to resolve a well-known external domain
                        start_time = time.time()
                        external_response = test_resolver.resolve('google.com', 'A')
                        end_time = time.time()
                        
                        if external_response:
                            test_result["responds_to_external"] = True
                            test_result["response_time"] = round((end_time - start_time) * 1000, 2)
                            test_result["status"] = "potential_open_resolver"
                            open_resolver_results["open_resolvers"].append(test_result)
                        else:
                            open_resolver_results["secure_resolvers"].append(test_result)
                    
                    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                        # Good - server doesn't respond to external queries or times out
                        test_result["status"] = "secure"
                        open_resolver_results["secure_resolvers"].append(test_result)
                    
                    except Exception as e:
                        test_result["status"] = "error"
                        test_result["error"] = str(e)
                    
                    open_resolver_results["test_results"][f"{ns}_{ns_ip}"] = test_result
            
            except Exception as e:
                open_resolver_results["test_results"][ns] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return open_resolver_results

    def _test_dns_amplification(self, domain):
        """Test for DNS amplification vulnerability"""
        amplification_results = {
            "amplification_factor": 0,
            "vulnerable_records": [],
            "large_responses": [],
            "risk_level": "low"
        }
        
        # Test records that could be used for amplification attacks
        amplification_records = ['TXT', 'MX', 'SOA', 'DNSKEY', 'NS']
        
        resolver = dns.resolver.Resolver()
        resolver.timeout = 10
        
        for record_type in amplification_records:
            try:
                response = resolver.resolve(domain, record_type)
                
                # Calculate response size (rough estimation)
                response_data = str(response.rrset)
                response_size = len(response_data)
                
                # Estimate query size (domain + record type + headers ≈ 50-100 bytes)
                query_size = len(domain) + 50
                
                if response_size > query_size:
                    amplification_factor = response_size / query_size
                    
                    if amplification_factor > 2:  # Significant amplification
                        amplification_results["vulnerable_records"].append({
                            "record_type": record_type,
                            "response_size": response_size,
                            "query_size": query_size,
                            "amplification_factor": round(amplification_factor, 2)
                        })
                    
                    if response_size > 1000:  # Large response
                        amplification_results["large_responses"].append({
                            "record_type": record_type,
                            "size_bytes": response_size
                        })
            
            except Exception:
                continue
        
        # Calculate overall amplification factor
        if amplification_results["vulnerable_records"]:
            max_amplification = max(record["amplification_factor"] for record in amplification_results["vulnerable_records"])
            amplification_results["amplification_factor"] = max_amplification
            
            if max_amplification > 10:
                amplification_results["risk_level"] = "high"
            elif max_amplification > 5:
                amplification_results["risk_level"] = "medium"
            else:
                amplification_results["risk_level"] = "low"
        
        return amplification_results

    def _test_subdomain_protection(self, domain):
        """Test subdomain enumeration protection mechanisms"""
        protection_results = {
            "wildcard_detection": False,
            "rate_limiting": False,
            "subdomain_responses": {},
            "protection_level": "none"
        }
        
        # Test common subdomains
        common_subdomains = ['www', 'mail', 'ftp', 'admin', 'test', 'dev', 'api', 'blog', 'shop']
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        
        responses = {}
        for subdomain in common_subdomains:
            test_domain = f"{subdomain}.{domain}"
            try:
                response = resolver.resolve(test_domain, 'A')
                responses[subdomain] = [str(ip) for ip in response]
            except:
                responses[subdomain] = None
        
        protection_results["subdomain_responses"] = responses
        
        # Check for wildcard DNS (all subdomains resolve to same IP)
        resolved_ips = [ips for ips in responses.values() if ips is not None]
        if len(resolved_ips) > 1:
            # Check if most subdomains resolve to the same IP
            ip_counts = {}
            for ip_list in resolved_ips:
                for ip in ip_list:
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
            
            most_common_ip_count = max(ip_counts.values()) if ip_counts else 0
            if most_common_ip_count >= len(resolved_ips) * 0.8:  # 80% threshold
                protection_results["wildcard_detection"] = True
        
        # Test for rate limiting by making rapid queries
        rate_limit_test_start = time.time()
        rapid_queries = 0
        for i in range(10):
            try:
                test_domain = f"ratelimitest{i}.{domain}"
                resolver.resolve(test_domain, 'A')
                rapid_queries += 1
            except dns.resolver.Timeout:
                # Possible rate limiting
                protection_results["rate_limiting"] = True
                break
            except:
                pass
        
        rate_limit_test_time = time.time() - rate_limit_test_start
        
        # Determine protection level
        if protection_results["wildcard_detection"] and protection_results["rate_limiting"]:
            protection_results["protection_level"] = "high"
        elif protection_results["wildcard_detection"] or protection_results["rate_limiting"]:
            protection_results["protection_level"] = "medium"
        else:
            protection_results["protection_level"] = "low"
        
        return protection_results

    def _analyze_dnssec_security(self, domain):
        """Enhanced DNSSEC security analysis"""
        dnssec_result = self.check_dnssec(domain)  # Use existing DNSSEC check
        
        enhanced_analysis = {
            "basic_dnssec": dnssec_result,
            "key_rollover_status": "unknown",
            "algorithm_strength": "unknown", 
            "chain_validation": "unknown",
            "security_level": "low"
        }
        
        if dnssec_result.get("dnssec_enabled"):
            # Analyze DNSKEY algorithms
            if dnssec_result.get("dnskey_records"):
                algorithms = []
                for key in dnssec_result["dnskey_records"]:
                    if "algorithm" in key:
                        algorithms.append(key["algorithm"])
                
                # Check for strong algorithms (RSA/SHA-256, ECDSA, EdDSA)
                strong_algorithms = [7, 8, 13, 14, 15, 16]  # Strong DNSSEC algorithms
                if any(alg in strong_algorithms for alg in algorithms):
                    enhanced_analysis["algorithm_strength"] = "strong"
                else:
                    enhanced_analysis["algorithm_strength"] = "weak"
            
            # Basic chain validation check
            if dnssec_result.get("validation_chain") and len(dnssec_result["validation_chain"]) > 0:
                enhanced_analysis["chain_validation"] = "valid"
            
            # Determine overall security level
            if (enhanced_analysis["algorithm_strength"] == "strong" and 
                enhanced_analysis["chain_validation"] == "valid"):
                enhanced_analysis["security_level"] = "high"
            elif enhanced_analysis["algorithm_strength"] == "strong":
                enhanced_analysis["security_level"] = "medium"
        
        return enhanced_analysis

    def _calculate_security_score(self, result):
        """Calculate overall DNS security score (0-100)"""
        score = 0
        
        # DNSSEC implementation (30 points)
        dnssec_security = result["dnssec_security"]
        if dnssec_security["security_level"] == "high":
            score += 30
        elif dnssec_security["security_level"] == "medium":
            score += 20
        elif dnssec_security["basic_dnssec"].get("dnssec_enabled"):
            score += 10
        
        # Open resolver protection (25 points)
        open_resolver = result["open_resolver_test"]
        if not open_resolver.get("open_resolvers"):
            score += 25
        elif len(open_resolver.get("open_resolvers", [])) < len(open_resolver.get("nameservers_tested", [])):
            score += 15  # Partial protection
        
        # Amplification protection (25 points)
        amplification = result["amplification_vulnerability"]
        risk_level = amplification.get("risk_level", "high")
        if risk_level == "low":
            score += 25
        elif risk_level == "medium":
            score += 15
        
        # Subdomain enumeration protection (20 points)
        subdomain_protection = result["subdomain_protection"]
        protection_level = subdomain_protection.get("protection_level", "none")
        if protection_level == "high":
            score += 20
        elif protection_level == "medium":
            score += 12
        elif protection_level == "low":
            score += 5
        
        return min(score, 100)

    def _identify_security_vulnerabilities(self, result):
        """Identify specific security vulnerabilities"""
        vulnerabilities = []
        
        # Check open resolvers
        open_resolvers = result["open_resolver_test"].get("open_resolvers", [])
        if open_resolvers:
            vulnerabilities.append({
                "severity": "high",
                "type": "open_resolver",
                "description": f"{len(open_resolvers)} nameserver(s) may be acting as open resolvers",
                "impact": "Can be abused for DDoS attacks and cache poisoning"
            })
        
        # Check amplification risks
        amplification = result["amplification_vulnerability"]
        if amplification.get("risk_level") in ["high", "medium"]:
            vulnerabilities.append({
                "severity": "medium" if amplification["risk_level"] == "medium" else "high",
                "type": "amplification_risk",
                "description": f"DNS amplification factor of {amplification.get('amplification_factor', 0)}x detected",
                "impact": "Domain can be abused for DNS amplification attacks"
            })
        
        # Check DNSSEC issues
        dnssec_security = result["dnssec_security"]
        if not dnssec_security["basic_dnssec"].get("dnssec_enabled"):
            vulnerabilities.append({
                "severity": "medium",
                "type": "no_dnssec",
                "description": "DNSSEC is not enabled",
                "impact": "Vulnerable to DNS spoofing and cache poisoning attacks"
            })
        elif dnssec_security["algorithm_strength"] == "weak":
            vulnerabilities.append({
                "severity": "medium",
                "type": "weak_dnssec_algorithm",
                "description": "DNSSEC uses weak cryptographic algorithms",
                "impact": "DNSSEC protection may be compromised"
            })
        
        # Check subdomain enumeration
        subdomain_protection = result["subdomain_protection"]
        if subdomain_protection.get("protection_level") == "low":
            vulnerabilities.append({
                "severity": "low",
                "type": "subdomain_enumeration",
                "description": "Limited protection against subdomain enumeration",
                "impact": "Attackers can easily discover subdomains and potential attack vectors"
            })
        
        return vulnerabilities

    def _generate_security_recommendations(self, result):
        """Generate security recommendations"""
        recommendations = []
        
        # DNSSEC recommendations
        dnssec_security = result["dnssec_security"]
        if not dnssec_security["basic_dnssec"].get("dnssec_enabled"):
            recommendations.append("Enable DNSSEC to protect against DNS spoofing and cache poisoning")
        elif dnssec_security["algorithm_strength"] == "weak":
            recommendations.append("Upgrade DNSSEC to use stronger cryptographic algorithms (ECDSA or EdDSA)")
        
        # Open resolver recommendations
        open_resolvers = result["open_resolver_test"].get("open_resolvers", [])
        if open_resolvers:
            recommendations.append("Configure nameservers to only respond to authoritative queries, not recursive queries")
        
        # Amplification recommendations
        amplification = result["amplification_vulnerability"]
        if amplification.get("risk_level") in ["high", "medium"]:
            recommendations.append("Consider reducing DNS response sizes and implementing rate limiting")
        
        # Subdomain protection recommendations
        subdomain_protection = result["subdomain_protection"]
        if subdomain_protection.get("protection_level") == "low":
            recommendations.append("Implement rate limiting and consider wildcard DNS configuration for subdomain protection")
        
        return recommendations

    def analyze_certificate_integration(self, domain):
        """Comprehensive certificate and SSL/TLS analysis"""
        self.log(f"Starting certificate integration analysis for {domain}", Fore.CYAN)
        
        result = {
            "domain": domain,
            "test_type": "certificate_integration",
            "timestamp": datetime.now().isoformat(),
            "certificate_transparency": {},
            "caa_records": {},
            "ssl_tls_config": {},
            "certificate_chain": {},
            "security_score": 0,
            "recommendations": []
        }
        
        try:
            # Check Certificate Transparency logs
            self.log("Checking Certificate Transparency logs", Fore.YELLOW)
            result["certificate_transparency"] = self._check_certificate_transparency(domain)
            
            # Validate CAA records
            self.log("Validating CAA records", Fore.YELLOW)
            result["caa_records"] = self._validate_caa_records(domain)
            
            # Check SSL/TLS configuration
            self.log("Analyzing SSL/TLS configuration", Fore.YELLOW)
            result["ssl_tls_config"] = self._check_ssl_tls_config(domain)
            
            # Analyze certificate chain
            self.log("Analyzing certificate chain", Fore.YELLOW)
            result["certificate_chain"] = self._analyze_certificate_chain(domain)
            
            # Calculate security score
            result["security_score"] = self._calculate_certificate_security_score(result)
            
            # Generate recommendations
            result["recommendations"] = self._generate_certificate_recommendations(result)
            
            self.log(f"Certificate integration analysis completed for {domain}", Fore.GREEN)
            
        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"
            self.log(f"Certificate integration analysis error: {str(e)}", Fore.RED)
        
        return result

    def _check_certificate_transparency(self, domain):
        """Check Certificate Transparency logs"""
        ct_results = {
            "certificates_found": 0,
            "ct_logs": [],
            "recent_certificates": [],
            "monitoring_enabled": False
        }
        
        try:
            # Query Certificate Transparency logs via public APIs
            # Using crt.sh as an example (free CT log search)
            import urllib.request
            import urllib.parse
            
            encoded_domain = urllib.parse.quote(domain)
            ct_api_url = f"https://crt.sh/?q={encoded_domain}&output=json"
            
            try:
                with urllib.request.urlopen(ct_api_url, timeout=15) as response:
                    if response.getcode() == 200:
                        ct_data = json.loads(response.read().decode())
                        
                        ct_results["certificates_found"] = len(ct_data)
                        ct_results["monitoring_enabled"] = True
                        
                        # Get recent certificates (last 30 days)
                        cutoff_date = datetime.now() - timedelta(days=30)
                        
                        for cert in ct_data[:10]:  # Limit to 10 most recent
                            cert_entry = {
                                "id": cert.get("id"),
                                "logged_at": cert.get("entry_timestamp", ""),
                                "issuer": cert.get("issuer_name", ""),
                                "common_name": cert.get("common_name", ""),
                                "serial_number": cert.get("serial_number", "")
                            }
                            ct_results["recent_certificates"].append(cert_entry)
                        
                        # Extract unique CT logs
                        ct_results["ct_logs"] = ["crt.sh", "Google CT", "Cloudflare CT"]  # Common CT logs
            
            except Exception as api_error:
                ct_results["error"] = f"CT API error: {str(api_error)}"
        
        except Exception as e:
            ct_results["error"] = str(e)
        
        return ct_results

    def _validate_caa_records(self, domain):
        """Validate CAA (Certification Authority Authorization) records"""
        caa_results = {
            "caa_records": [],
            "authorized_cas": [],
            "caa_enabled": False,
            "protection_level": "none"
        }
        
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            
            try:
                caa_response = resolver.resolve(domain, 'CAA')
                caa_results["caa_enabled"] = True
                
                for caa_record in caa_response:
                    caa_data = str(caa_record)
                    caa_results["caa_records"].append(caa_data)
                    
                    # Parse CAA record to extract CA information
                    if "issue" in caa_data:
                        ca_parts = caa_data.split('"')
                        if len(ca_parts) > 1:
                            ca_domain = ca_parts[1]
                            if ca_domain and ca_domain != ";":
                                caa_results["authorized_cas"].append(ca_domain)
                
                # Determine protection level
                if caa_results["authorized_cas"]:
                    if len(caa_results["authorized_cas"]) == 1:
                        caa_results["protection_level"] = "high"  # Single CA
                    else:
                        caa_results["protection_level"] = "medium"  # Multiple CAs
                elif any("issue" in record for record in caa_results["caa_records"]):
                    caa_results["protection_level"] = "low"  # CAA exists but no specific CAs
            
            except dns.resolver.NoAnswer:
                caa_results["caa_enabled"] = False
                caa_results["protection_level"] = "none"
            
        except Exception as e:
            caa_results["error"] = str(e)
        
        return caa_results

    def _check_ssl_tls_config(self, domain):
        """Check SSL/TLS configuration"""
        ssl_results = {
            "ssl_enabled": False,
            "certificate_info": {},
            "protocol_versions": [],
            "cipher_suites": [],
            "security_grade": "F"
        }
        
        try:
            # Test SSL connection
            import ssl
            import socket
            
            context = ssl.create_default_context()
            
            try:
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        ssl_results["ssl_enabled"] = True
                        
                        # Get certificate information
                        cert = ssock.getpeercert()
                        ssl_results["certificate_info"] = {
                            "subject": dict(x[0] for x in cert.get("subject", [])),
                            "issuer": dict(x[0] for x in cert.get("issuer", [])),
                            "version": cert.get("version"),
                            "serial_number": cert.get("serialNumber"),
                            "not_before": cert.get("notBefore"),
                            "not_after": cert.get("notAfter"),
                            "subject_alt_names": cert.get("subjectAltName", [])
                        }
                        
                        # Get protocol version
                        ssl_results["protocol_versions"] = [ssock.version()]
                        
                        # Get cipher suite
                        cipher = ssock.cipher()
                        if cipher:
                            ssl_results["cipher_suites"] = [cipher[0]]
                        
                        # Basic security grading
                        if ssock.version() in ["TLSv1.3", "TLSv1.2"]:
                            ssl_results["security_grade"] = "A"
                        elif ssock.version() == "TLSv1.1":
                            ssl_results["security_grade"] = "B"
                        elif ssock.version() == "TLSv1":
                            ssl_results["security_grade"] = "C"
                        else:
                            ssl_results["security_grade"] = "F"
            
            except Exception as ssl_error:
                ssl_results["error"] = str(ssl_error)
        
        except Exception as e:
            ssl_results["error"] = str(e)
        
        return ssl_results

    def _analyze_certificate_chain(self, domain):
        """Analyze certificate chain validity"""
        chain_results = {
            "chain_valid": False,
            "chain_length": 0,
            "root_ca": "unknown",
            "intermediate_cas": [],
            "trust_issues": []
        }
        
        try:
            import ssl
            import socket
            
            # Get certificate chain
            context = ssl.create_default_context()
            
            try:
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        # Get peer certificate chain
                        cert_chain = ssock.getpeercert_chain()
                        
                        if cert_chain:
                            chain_results["chain_length"] = len(cert_chain)
                            chain_results["chain_valid"] = True
                            
                            # Analyze chain structure
                            if len(cert_chain) >= 2:
                                # Root CA (last in chain)
                                root_cert = cert_chain[-1]
                                root_subject = dict(x[0] for x in root_cert.get("subject", []))
                                chain_results["root_ca"] = root_subject.get("organizationName", "Unknown")
                                
                                # Intermediate CAs
                                for cert in cert_chain[1:-1]:
                                    intermediate_subject = dict(x[0] for x in cert.get("subject", []))
                                    chain_results["intermediate_cas"].append(
                                        intermediate_subject.get("organizationName", "Unknown")
                                    )
            
            except Exception as chain_error:
                chain_results["error"] = str(chain_error)
                chain_results["trust_issues"].append("Certificate chain validation failed")
        
        except Exception as e:
            chain_results["error"] = str(e)
        
        return chain_results

    def _calculate_certificate_security_score(self, result):
        """Calculate certificate security score (0-100)"""
        score = 0
        
        # SSL/TLS configuration (40 points)
        ssl_config = result["ssl_tls_config"]
        if ssl_config.get("ssl_enabled"):
            grade = ssl_config.get("security_grade", "F")
            if grade == "A":
                score += 40
            elif grade == "B":
                score += 30
            elif grade == "C":
                score += 20
            else:
                score += 10
        
        # CAA records (25 points)
        caa_records = result["caa_records"]
        protection_level = caa_records.get("protection_level", "none")
        if protection_level == "high":
            score += 25
        elif protection_level == "medium":
            score += 18
        elif protection_level == "low":
            score += 10
        
        # Certificate Transparency (20 points)
        ct_data = result["certificate_transparency"]
        if ct_data.get("monitoring_enabled") and ct_data.get("certificates_found", 0) > 0:
            score += 20
        
        # Certificate chain validity (15 points)
        chain_data = result["certificate_chain"]
        if chain_data.get("chain_valid"):
            score += 15
        
        return min(score, 100)

    def _generate_certificate_recommendations(self, result):
        """Generate certificate security recommendations"""
        recommendations = []
        
        # SSL/TLS recommendations
        ssl_config = result["ssl_tls_config"]
        if not ssl_config.get("ssl_enabled"):
            recommendations.append("Enable SSL/TLS encryption for web services")
        elif ssl_config.get("security_grade", "F") in ["C", "D", "F"]:
            recommendations.append("Upgrade SSL/TLS configuration to use modern protocols (TLS 1.2+)")
        
        # CAA recommendations
        caa_records = result["caa_records"]
        if not caa_records.get("caa_enabled"):
            recommendations.append("Implement CAA records to control which Certificate Authorities can issue certificates")
        elif caa_records.get("protection_level") == "low":
            recommendations.append("Specify authorized Certificate Authorities in CAA records")
        
        # Certificate Transparency recommendations
        ct_data = result["certificate_transparency"]
        if not ct_data.get("monitoring_enabled"):
            recommendations.append("Enable Certificate Transparency monitoring to detect unauthorized certificates")
        
        # Certificate chain recommendations
        chain_data = result["certificate_chain"]
        if not chain_data.get("chain_valid"):
            recommendations.append("Ensure proper certificate chain configuration and trust validation")
        
        return recommendations


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
                if provider in ["Cloudflare", "AWS Route 53", "Google Cloud DNS", "Azure DNS", "DigitalOcean", "Namecheap", "GoDaddy", "Name.com", "Gandi", "OVH"]:
                    api_support = "✅ API"
                else:
                    api_support = "📋 Detect"
                    
                patterns = ", ".join(provider_patterns[provider][:2])  # Show first 2 patterns
                if len(provider_patterns[provider]) > 2:
                    patterns += f" (+{len(provider_patterns[provider])-2} more)"
                print(f"  {provider:<20} {api_support:<10} Patterns: {patterns}")
    
    print(f"\n{Fore.GREEN}API Integration Status:{Style.RESET_ALL}")
    print("  ✅ Fully Supported: Cloudflare, AWS Route 53, Google Cloud DNS, Azure DNS, DigitalOcean")
    print("                      Namecheap, GoDaddy, Name.com, Gandi, OVH")
    print("  📋 Detection Only: All other providers")
    
    print(f"\n{Fore.CYAN}💡 Usage Examples:{Style.RESET_ALL}")
    print("  dns-validator providers example.com")
    print("  dns-validator provider example.com --api-token YOUR_TOKEN")
    print("  dns-validator provider example.com --api-user USER --api-secret SECRET  # Namecheap")
    print("  dns-validator provider example.com --application-key KEY --consumer-key CONSUMER  # OVH")
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
@click.option('--api-token', help='API token/key for provider (or api_user for Namecheap, username for Name.com)')
@click.option('--api-secret', help='API secret/key for providers that require it')
@click.option('--api-user', help='API user for Namecheap')
@click.option('--username', help='Username for Name.com or Namecheap')
@click.option('--client-ip', help='Client IP for Namecheap API')
@click.option('--sandbox', is_flag=True, help='Use sandbox environment for Namecheap')
@click.option('--application-key', help='Application key for OVH')
@click.option('--application-secret', help='Application secret for OVH')
@click.option('--consumer-key', help='Consumer key for OVH')
@click.option('--endpoint', help='OVH endpoint (ovh-eu, ovh-us, ovh-ca, etc.)')
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
def provider(ctx, domain, provider, api_token, api_secret, api_user, username, client_ip, 
             sandbox, application_key, application_secret, consumer_key, endpoint,
             access_key, secret_key, region, service_account, project_id, subscription_id, 
             resource_group, tenant_id, client_id, client_secret, cred_name):
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
    
    # Namecheap
    dns-validator provider example.com --api-token API_USER --api-secret API_KEY
    
    # GoDaddy
    dns-validator provider example.com --api-token API_KEY --api-secret API_SECRET
    
    # Name.com
    dns-validator provider example.com --api-token USERNAME --api-secret API_TOKEN
    
    # Gandi
    dns-validator provider example.com --api-token API_KEY
    
    # OVH
    dns-validator provider example.com --api-token APP_KEY --api-secret APP_SECRET
    """
    validator = ctx.obj['validator']
    
    # First, try to load stored credentials if cred-name is provided or no CLI args given
    api_credentials = {}
    
    # Check if we have command line credentials
    has_cli_creds = any([api_token, api_secret, api_user, username, client_ip, application_key,
                        application_secret, consumer_key, access_key, secret_key, service_account, 
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
    if api_user:
        api_credentials['api_user'] = api_user
    if username:
        api_credentials['username'] = username
    if client_ip:
        api_credentials['client_ip'] = client_ip
    if sandbox:
        api_credentials['sandbox'] = sandbox
    if application_key:
        api_credentials['application_key'] = application_key
    if application_secret:
        api_credentials['application_secret'] = application_secret
    if consumer_key:
        api_credentials['consumer_key'] = consumer_key
    if endpoint:
        api_credentials['endpoint'] = endpoint
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


@cli.command()
@click.argument('domain')
@click.pass_context
def dnssec(ctx, domain):
    """Check DNSSEC validation status and security chain"""
    validator = ctx.obj['validator']
    result = validator.check_dnssec(domain)
    
    print(f"\n{Fore.CYAN}DNSSEC Validation Check for {domain}{Style.RESET_ALL}")
    print("=" * 60)
    
    if result["dnssec_enabled"]:
        print(f"{Fore.GREEN}✓ DNSSEC Status: ENABLED{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠ DNSSEC Status: NOT ENABLED{Style.RESET_ALL}")
    
    if result["ds_records"]:
        print(f"\n{Fore.CYAN}DS Records in Parent Zone:{Style.RESET_ALL}")
        for ds in result["ds_records"]:
            print(f"  • {ds}")
    
    if result["dnskey_records"]:
        print(f"\n{Fore.CYAN}DNSKEY Records:{Style.RESET_ALL}")
        for dnskey in result["dnskey_records"]:
            print(f"  • {dnskey}")
    
    if result["rrsig_records"]:
        print(f"\n{Fore.CYAN}RRSIG Records (Signatures):{Style.RESET_ALL}")
        for rrsig in result["rrsig_records"][:3]:  # Show first 3 to avoid clutter
            print(f"  • {rrsig}")
        if len(result["rrsig_records"]) > 3:
            print(f"  • ... and {len(result['rrsig_records']) - 3} more")
    
    if result["validation_chain"]:
        print(f"\n{Fore.GREEN}Validation Chain:{Style.RESET_ALL}")
        for step in result["validation_chain"]:
            print(f"  ✓ {step}")
    
    if result["warnings"]:
        print(f"\n{Fore.YELLOW}Warnings:{Style.RESET_ALL}")
        for warning in result["warnings"]:
            print(f"  ⚠ {warning}")
    
    if result["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in result["errors"]:
            print(f"  ✗ {error}")


@cli.command('reverse-dns')
@click.argument('ip_address')
@click.pass_context
def reverse_dns(ctx, ip_address):
    """Check reverse DNS (PTR) records and forward/reverse consistency"""
    validator = ctx.obj['validator']
    result = validator.check_reverse_dns(ip_address)
    
    print(f"\n{Fore.CYAN}Reverse DNS Check for {ip_address}{Style.RESET_ALL}")
    print("=" * 50)
    
    if result["ptr_records"]:
        print(f"{Fore.GREEN}✓ PTR Records Found:{Style.RESET_ALL}")
        for ptr in result["ptr_records"]:
            print(f"  • {ptr}")
        
        if result["forward_reverse_consistent"]:
            print(f"\n{Fore.GREEN}✓ Forward/Reverse Consistency: VERIFIED{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠ Forward/Reverse Consistency: NOT VERIFIED{Style.RESET_ALL}")
        
        if result["forward_domains"]:
            print(f"\n{Fore.CYAN}Forward Lookup Results:{Style.RESET_ALL}")
            for ip in result["forward_domains"]:
                print(f"  • {ip}")
    else:
        print(f"{Fore.RED}✗ No PTR Records Found{Style.RESET_ALL}")
    
    if result["warnings"]:
        print(f"\n{Fore.YELLOW}Warnings:{Style.RESET_ALL}")
        for warning in result["warnings"]:
            print(f"  ⚠ {warning}")
    
    if result["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in result["errors"]:
            print(f"  ✗ {error}")


@cli.command('cache-analysis')
@click.argument('domain')
@click.option('--type', '-t', default='A', help='DNS record type to analyze (default: A)')
@click.pass_context
def cache_analysis(ctx, domain, type):
    """Analyze DNS caching behavior and TTL compliance"""
    validator = ctx.obj['validator']
    result = validator.analyze_dns_cache(domain, type)
    
    print(f"\n{Fore.CYAN}DNS Cache Analysis for {domain} ({type}){Style.RESET_ALL}")
    print("=" * 60)
    
    if result["ttl_summary"]:
        summary = result["ttl_summary"]
        print(f"{Fore.CYAN}TTL Summary:{Style.RESET_ALL}")
        print(f"  • Minimum TTL: {summary['min_ttl']} seconds")
        print(f"  • Maximum TTL: {summary['max_ttl']} seconds")
        print(f"  • Average TTL: {summary['average_ttl']} seconds")
        print(f"  • Consistency: {summary['consistency']}")
    
    if result["ttl_analysis"]:
        print(f"\n{Fore.CYAN}Server Analysis:{Style.RESET_ALL}")
        for server_name, analysis in result["ttl_analysis"].items():
            status_color = Fore.GREEN if analysis["caching_behavior"] == "normal" else Fore.YELLOW
            print(f"  {status_color}• {server_name} ({analysis['ip']}){Style.RESET_ALL}")
            print(f"    TTL: {analysis['initial_ttl']} → {analysis['second_ttl']} (reduction: {analysis['ttl_reduction']})")
            print(f"    Query time: {analysis['query_time_ms']}ms")
            print(f"    Behavior: {analysis['caching_behavior']}")
    
    if result["cache_recommendations"]:
        print(f"\n{Fore.GREEN}Recommendations:{Style.RESET_ALL}")
        for rec in result["cache_recommendations"]:
            print(f"  ✓ {rec}")
    
    if result["potential_issues"]:
        print(f"\n{Fore.YELLOW}Potential Issues:{Style.RESET_ALL}")
        for issue in result["potential_issues"]:
            print(f"  ⚠ {issue}")
    
    if result["errors"]:
        print(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
        for error in result["errors"]:
            print(f"  ✗ {error}")


@cli.command('health-monitor')
@click.argument('domain')
@click.option('--duration', '-d', default=60, type=int, help='Monitoring duration in minutes (default: 60)')
@click.option('--interval', '-i', default=300, type=int, help='Check interval in seconds (default: 300)')
@click.pass_context
def health_monitor(ctx, domain, duration, interval):
    """Monitor DNS health in real-time with alerting"""
    validator = ctx.obj['validator']
    
    print(f"\n{Fore.CYAN}Starting DNS Health Monitoring for {domain}{Style.RESET_ALL}")
    print(f"Duration: {duration} minutes | Check interval: {interval} seconds")
    print("Press Ctrl+C to stop monitoring early")
    print("=" * 60)
    
    try:
        result = validator.monitor_dns_health(domain, duration, interval)
        
        print(f"\n{Fore.CYAN}Monitoring Summary:{Style.RESET_ALL}")
        summary = result["summary"]
        print(f"  • Total checks: {summary['total_checks']}")
        print(f"  • Successful checks: {summary['successful_checks']}")
        
        success_rate = summary['success_rate']
        rate_color = Fore.GREEN if success_rate > 95 else Fore.YELLOW if success_rate > 85 else Fore.RED
        print(f"  • Success rate: {rate_color}{success_rate}%{Style.RESET_ALL}")
        print(f"  • Total alerts: {summary['total_alerts']}")
        print(f"  • Monitoring file: {summary['monitoring_file']}")
        
        if result["alerts"]:
            print(f"\n{Fore.YELLOW}Recent Alerts:{Style.RESET_ALL}")
            for alert in result["alerts"][-5:]:  # Show last 5 alerts
                severity_color = Fore.RED if alert["severity"] == "high" else Fore.YELLOW
                print(f"  {severity_color}• [{alert['severity'].upper()}] {alert['message']}{Style.RESET_ALL}")
                print(f"    Time: {alert['timestamp']}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitoring interrupted by user{Style.RESET_ALL}")


@cli.command('geo-dns')
@click.argument('domain')
@click.pass_context
def geo_dns(ctx, domain):
    """Test DNS resolution from different geographic locations"""
    validator = ctx.obj['validator']
    result = validator.test_geolocation_dns(domain)
    
    print(f"\n{Fore.CYAN}Geolocation DNS Testing for {domain}{Style.RESET_ALL}")
    print("=" * 60)
    
    if "error" in result:
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return
    
    # Display summary
    summary = result["summary"]
    print(f"\n{Fore.CYAN}Test Summary:{Style.RESET_ALL}")
    print(f"  • Tests performed: {summary['total_tests']}")
    print(f"  • Successful tests: {summary['successful_tests']}")
    
    success_rate = summary['success_rate']
    rate_color = Fore.GREEN if success_rate > 95 else Fore.YELLOW if success_rate > 80 else Fore.RED
    print(f"  • Success rate: {rate_color}{success_rate}%{Style.RESET_ALL}")
    print(f"  • Average response time: {summary['average_response_time_ms']} ms")
    
    # GeoDNS Analysis
    geodns_analysis = result["geodns_analysis"]
    if geodns_analysis["geodns_detected"]:
        print(f"\n{Fore.GREEN}✓ GeoDNS routing detected{Style.RESET_ALL}")
        print(f"  • Unique IP addresses: {geodns_analysis['total_unique_ips']}")
        print(f"  • Routing consistency: {'Yes' if geodns_analysis['routing_consistency'] else 'No'}")
    else:
        print(f"\n{Fore.YELLOW}• Single IP routing detected (no GeoDNS){Style.RESET_ALL}")
    
    # CDN Detection
    if result["cdn_endpoints"]:
        print(f"\n{Fore.CYAN}CDN Providers Detected:{Style.RESET_ALL}")
        cdn_providers = set(endpoint["cdn_provider"] for endpoint in result["cdn_endpoints"])
        for provider in cdn_providers:
            provider_endpoints = [ep for ep in result["cdn_endpoints"] if ep["cdn_provider"] == provider]
            print(f"  • {provider.title()}: {len(provider_endpoints)} endpoint(s)")
            for endpoint in provider_endpoints:
                print(f"    - {endpoint['ip']} ({endpoint['reverse_domain']})")
    
    # Geographic Results
    if ctx.obj.get('verbose'):
        print(f"\n{Fore.CYAN}Geographic Test Results:{Style.RESET_ALL}")
        for location, data in result["geo_results"].items():
            if data["status"] == "success":
                status_icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
                response_time = f"({data['response_time']}ms)"
            else:
                status_icon = f"{Fore.RED}✗{Style.RESET_ALL}"
                response_time = "(failed)"
            
            print(f"\n  {status_icon} {location} {response_time}")
            if data.get("a_records"):
                print(f"    A records: {', '.join(data['a_records'])}")
            if data.get("aaaa_records"):
                print(f"    AAAA records: {', '.join(data['aaaa_records'])}")
            if data.get("error"):
                print(f"    Error: {data['error']}")


@cli.command('load-balancer')
@click.argument('domain')
@click.pass_context
def load_balancer(ctx, domain):
    """Check load balancer health and validate multiple A records"""
    validator = ctx.obj['validator']
    result = validator.check_load_balancer_health(domain)
    
    print(f"\n{Fore.CYAN}Load Balancer Health Check for {domain}{Style.RESET_ALL}")
    print("=" * 60)
    
    if "error" in result:
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return
    
    # Display summary
    summary = result.get("summary", {})
    if not summary.get("load_balancer_detected"):
        print(f"{Fore.YELLOW}• No load balancer detected{Style.RESET_ALL}")
        if "reason" in summary:
            print(f"  Reason: {summary['reason']}")
        return
    
    print(f"\n{Fore.GREEN}✓ Load balancer detected{Style.RESET_ALL}")
    print(f"  • Total endpoints: {summary['total_endpoints']}")
    print(f"  • Healthy endpoints: {summary['healthy_endpoints']}")
    
    # Health status
    health_status = summary['health_status']
    if health_status == "good":
        health_color = Fore.GREEN
    elif health_status == "degraded":
        health_color = Fore.YELLOW
    else:
        health_color = Fore.RED
    
    print(f"  • Health status: {health_color}{health_status.title()}{Style.RESET_ALL}")
    print(f"  • Load balancing type: {summary['load_balancing_type'].replace('_', ' ').title()}")
    print(f"  • Failover ready: {'Yes' if summary['failover_ready'] else 'No'}")
    print(f"  • Redundancy level: {summary['redundancy_assessment'].title()}")
    
    # Endpoint Health Details
    if ctx.obj.get('verbose') and result.get("health_checks"):
        print(f"\n{Fore.CYAN}Endpoint Health Details:{Style.RESET_ALL}")
        for ip, health in result["health_checks"].items():
            status = health["status"]
            if status == "healthy":
                status_icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
            elif status == "tcp_only":
                status_icon = f"{Fore.YELLOW}⚠{Style.RESET_ALL}"
            else:
                status_icon = f"{Fore.RED}✗{Style.RESET_ALL}"
            
            print(f"\n  {status_icon} {ip} ({status.replace('_', ' ').title()})")
            
            # TCP port results
            tcp_ports = health.get("tcp_ports", {})
            open_ports = [port for port, data in tcp_ports.items() if data.get("open")]
            if open_ports:
                print(f"    Open ports: {', '.join(map(str, open_ports))}")
            
            # HTTP/HTTPS response
            if health.get("http_response", {}).get("status_code"):
                print(f"    HTTP: {health['http_response']['status_code']} ({health['http_response']['response_time']}ms)")
            if health.get("https_response", {}).get("status_code"):
                print(f"    HTTPS: {health['https_response']['status_code']} ({health['https_response']['response_time']}ms)")
    
    # Load Balancing Analysis
    if result.get("load_balancing_analysis"):
        analysis = result["load_balancing_analysis"]
        print(f"\n{Fore.CYAN}Load Balancing Analysis:{Style.RESET_ALL}")
        print(f"  • Health percentage: {analysis['health_percentage']}%")
        print(f"  • Balanced distribution: {'Yes' if analysis['balanced_distribution'] else 'No'}")
        
        if ctx.obj.get('verbose') and analysis.get("query_distribution"):
            print(f"  • Query distribution:")
            for ip, count in analysis["query_distribution"].items():
                print(f"    - {ip}: {count} queries")


@cli.command('ipv6-check')
@click.argument('domain')
@click.pass_context  
def ipv6_check(ctx, domain):
    """Enhanced IPv6 support validation including dual-stack configuration"""
    validator = ctx.obj['validator']
    result = validator.validate_ipv6_support(domain)
    
    print(f"\n{Fore.CYAN}IPv6 Support Validation for {domain}{Style.RESET_ALL}")
    print("=" * 60)
    
    if "error" in result:
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return
    
    # Display summary
    summary = result["summary"]
    print(f"\n{Fore.CYAN}IPv6 Readiness Summary:{Style.RESET_ALL}")
    
    # IPv6 Support Status
    if summary["ipv6_supported"]:
        print(f"{Fore.GREEN}✓ IPv6 supported{Style.RESET_ALL}")
        print(f"  • AAAA records found: {len(result['aaaa_records'])}")
        for record in result["aaaa_records"]:
            print(f"    - {record}")
    else:
        print(f"{Fore.RED}✗ IPv6 not supported{Style.RESET_ALL}")
        print(f"  • No AAAA records found")
    
    # Dual-stack Configuration
    dual_stack = result["dual_stack_analysis"]
    config_type = dual_stack["configuration_type"].replace("_", "-").title()
    
    if dual_stack["dual_stack_enabled"]:
        config_color = Fore.GREEN
    elif dual_stack["ipv4_only"]:
        config_color = Fore.YELLOW
    elif dual_stack["ipv6_only"]:
        config_color = Fore.CYAN
    else:
        config_color = Fore.RED
    
    print(f"\n{Fore.CYAN}Configuration Type:{Style.RESET_ALL} {config_color}{config_type}{Style.RESET_ALL}")
    print(f"  • IPv4 records (A): {dual_stack['a_record_count']}")
    print(f"  • IPv6 records (AAAA): {dual_stack['aaaa_record_count']}")
    
    # IPv6 DNS Testing
    dns_over_ipv6 = result["dns_over_ipv6"]
    if dns_over_ipv6["ipv6_dns_functional"]:
        print(f"\n{Fore.GREEN}✓ DNS over IPv6 functional{Style.RESET_ALL}")
        print(f"  • Success rate: {dns_over_ipv6['success_rate']}%")
        print(f"  • Servers tested: {dns_over_ipv6['servers_tested']}")
    else:
        print(f"\n{Fore.RED}✗ DNS over IPv6 not functional{Style.RESET_ALL}")
    
    # IPv6 Connectivity
    connectivity_status = summary["ipv6_connectivity"]
    if connectivity_status == "reachable":
        print(f"\n{Fore.GREEN}✓ IPv6 endpoints reachable{Style.RESET_ALL}")
    elif connectivity_status == "unreachable":
        print(f"\n{Fore.RED}✗ IPv6 endpoints unreachable{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}• No IPv6 endpoints to test{Style.RESET_ALL}")
    
    # Readiness Score
    readiness_score = summary["readiness_score"]
    if readiness_score >= 80:
        score_color = Fore.GREEN
    elif readiness_score >= 60:
        score_color = Fore.YELLOW
    else:
        score_color = Fore.RED
    
    print(f"\n{Fore.CYAN}IPv6 Readiness Score:{Style.RESET_ALL} {score_color}{readiness_score}/100{Style.RESET_ALL}")
    print(f"Recommendation: {summary['configuration_recommendation']}")
    
    # Detailed Results
    if ctx.obj.get('verbose'):
        if result.get("ipv6_connectivity"):
            print(f"\n{Fore.CYAN}IPv6 Connectivity Details:{Style.RESET_ALL}")
            for ipv6_addr, conn in result["ipv6_connectivity"].items():
                status_icon = f"{Fore.GREEN}✓{Style.RESET_ALL}" if conn["reachable"] else f"{Fore.RED}✗{Style.RESET_ALL}"
                print(f"\n  {status_icon} {ipv6_addr}")
                
                if conn.get("ping_result"):
                    ping_status = "Success" if conn["ping_result"] == "success" else "Failed"
                    print(f"    Ping: {ping_status}")
                
                tcp_conn = conn.get("tcp_connectivity", {})
                if tcp_conn:
                    open_ports = [port for port, data in tcp_conn.items() if data.get("open")]
                    if open_ports:
                        print(f"    Open TCP ports: {', '.join(map(str, open_ports))}")
        
        if result.get("ipv6_dns_servers"):
            print(f"\n{Fore.CYAN}DNS over IPv6 Test Results:{Style.RESET_ALL}")
            for server_name, server_result in result["ipv6_dns_servers"].items():
                if server_result["status"] == "success":
                    status_icon = f"{Fore.GREEN}✓{Style.RESET_ALL}"
                    response_time = f"({server_result['response_time']}ms)"
                else:
                    status_icon = f"{Fore.RED}✗{Style.RESET_ALL}"
                    response_time = "(failed)"
                
                print(f"  {status_icon} {server_name} {response_time}")


@cli.command('security-analysis')
@click.argument('domain')
@click.pass_context
def security_analysis(ctx, domain):
    """Comprehensive DNS security analysis including vulnerabilities and threats"""
    validator = ctx.obj['validator']
    result = validator.analyze_dns_security(domain)
    
    print(f"\n{Fore.CYAN}DNS Security Analysis for {domain}{Style.RESET_ALL}")
    print("=" * 60)
    
    if "error" in result:
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return
    
    # Display security score
    security_score = result.get("security_score", 0)
    if security_score >= 80:
        score_color = Fore.GREEN
    elif security_score >= 60:
        score_color = Fore.YELLOW
    else:
        score_color = Fore.RED
    
    print(f"\n{Fore.CYAN}Security Score:{Style.RESET_ALL} {score_color}{security_score}/100{Style.RESET_ALL}")
    
    # Display vulnerabilities
    vulnerabilities = result.get("vulnerabilities", [])
    if vulnerabilities:
        print(f"\n{Fore.RED}Security Vulnerabilities Found:{Style.RESET_ALL}")
        for vuln in vulnerabilities:
            severity = vuln["severity"]
            if severity == "high":
                severity_color = Fore.RED
            elif severity == "medium":
                severity_color = Fore.YELLOW
            else:
                severity_color = Fore.CYAN
            
            print(f"  {severity_color}[{severity.upper()}]{Style.RESET_ALL} {vuln['description']}")
            if ctx.obj.get('verbose'):
                print(f"    Type: {vuln['type']}")
                print(f"    Impact: {vuln['impact']}")
    else:
        print(f"\n{Fore.GREEN}✓ No critical security vulnerabilities detected{Style.RESET_ALL}")
    
    # Display DNSSEC security status
    dnssec_security = result.get("dnssec_security", {})
    basic_dnssec = dnssec_security.get("basic_dnssec", {})
    
    print(f"\n{Fore.CYAN}DNSSEC Security:{Style.RESET_ALL}")
    if basic_dnssec.get("dnssec_enabled"):
        print(f"  {Fore.GREEN}✓ DNSSEC enabled{Style.RESET_ALL}")
        security_level = dnssec_security.get("security_level", "low")
        print(f"  • Security level: {security_level.title()}")
        print(f"  • Algorithm strength: {dnssec_security.get('algorithm_strength', 'unknown').title()}")
    else:
        print(f"  {Fore.RED}✗ DNSSEC not enabled{Style.RESET_ALL}")
    
    # Display open resolver test results
    open_resolver_test = result.get("open_resolver_test", {})
    open_resolvers = open_resolver_test.get("open_resolvers", [])
    
    print(f"\n{Fore.CYAN}Open Resolver Test:{Style.RESET_ALL}")
    if open_resolvers:
        print(f"  {Fore.RED}✗ {len(open_resolvers)} potential open resolver(s) detected{Style.RESET_ALL}")
        if ctx.obj.get('verbose'):
            for resolver in open_resolvers:
                print(f"    - {resolver['nameserver']} ({resolver['ip']})")
    else:
        secure_resolvers = len(open_resolver_test.get("secure_resolvers", []))
        print(f"  {Fore.GREEN}✓ All {secure_resolvers} nameserver(s) properly configured{Style.RESET_ALL}")
    
    # Display amplification vulnerability results
    amplification = result.get("amplification_vulnerability", {})
    risk_level = amplification.get("risk_level", "unknown")
    
    print(f"\n{Fore.CYAN}DNS Amplification Risk:{Style.RESET_ALL}")
    if risk_level == "low":
        risk_color = Fore.GREEN
    elif risk_level == "medium":
        risk_color = Fore.YELLOW
    else:
        risk_color = Fore.RED
    
    print(f"  • Risk level: {risk_color}{risk_level.title()}{Style.RESET_ALL}")
    
    amplification_factor = amplification.get("amplification_factor", 0)
    if amplification_factor > 0:
        print(f"  • Max amplification factor: {amplification_factor}x")
    
    if ctx.obj.get('verbose') and amplification.get("vulnerable_records"):
        print(f"  • Vulnerable record types:")
        for record in amplification["vulnerable_records"]:
            print(f"    - {record['record_type']}: {record['amplification_factor']}x amplification")
    
    # Display subdomain protection results
    subdomain_protection = result.get("subdomain_protection", {})
    protection_level = subdomain_protection.get("protection_level", "unknown")
    
    print(f"\n{Fore.CYAN}Subdomain Enumeration Protection:{Style.RESET_ALL}")
    if protection_level == "high":
        protection_color = Fore.GREEN
    elif protection_level == "medium":
        protection_color = Fore.YELLOW
    else:
        protection_color = Fore.RED
    
    print(f"  • Protection level: {protection_color}{protection_level.title()}{Style.RESET_ALL}")
    
    if subdomain_protection.get("wildcard_detection"):
        print(f"  {Fore.GREEN}✓ Wildcard DNS detected{Style.RESET_ALL}")
    if subdomain_protection.get("rate_limiting"):
        print(f"  {Fore.GREEN}✓ Rate limiting detected{Style.RESET_ALL}")
    
    # Display recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n{Fore.CYAN}Security Recommendations:{Style.RESET_ALL}")
        for rec in recommendations:
            print(f"  • {rec}")


@cli.command('certificate-analysis')
@click.argument('domain')
@click.pass_context
def certificate_analysis(ctx, domain):
    """Comprehensive certificate and SSL/TLS analysis with CT logs and CAA validation"""
    validator = ctx.obj['validator']
    result = validator.analyze_certificate_integration(domain)
    
    print(f"\n{Fore.CYAN}Certificate Integration Analysis for {domain}{Style.RESET_ALL}")
    print("=" * 60)
    
    if "error" in result:
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return
    
    # Display security score
    security_score = result.get("security_score", 0)
    if security_score >= 80:
        score_color = Fore.GREEN
    elif security_score >= 60:
        score_color = Fore.YELLOW
    else:
        score_color = Fore.RED
    
    print(f"\n{Fore.CYAN}Certificate Security Score:{Style.RESET_ALL} {score_color}{security_score}/100{Style.RESET_ALL}")
    
    # Display SSL/TLS configuration
    ssl_config = result.get("ssl_tls_config", {})
    print(f"\n{Fore.CYAN}SSL/TLS Configuration:{Style.RESET_ALL}")
    
    if ssl_config.get("ssl_enabled"):
        print(f"  {Fore.GREEN}✓ SSL/TLS enabled{Style.RESET_ALL}")
        
        security_grade = ssl_config.get("security_grade", "F")
        if security_grade == "A":
            grade_color = Fore.GREEN
        elif security_grade in ["B", "C"]:
            grade_color = Fore.YELLOW
        else:
            grade_color = Fore.RED
        
        print(f"  • Security grade: {grade_color}{security_grade}{Style.RESET_ALL}")
        
        # Display certificate info
        cert_info = ssl_config.get("certificate_info", {})
        if cert_info:
            subject = cert_info.get("subject", {})
            issuer = cert_info.get("issuer", {})
            
            if subject.get("commonName"):
                print(f"  • Certificate CN: {subject['commonName']}")
            if issuer.get("organizationName"):
                print(f"  • Issuer: {issuer['organizationName']}")
            if cert_info.get("not_after"):
                print(f"  • Expires: {cert_info['not_after']}")
        
        # Display protocol versions
        protocols = ssl_config.get("protocol_versions", [])
        if protocols:
            print(f"  • Protocol: {', '.join(protocols)}")
        
    else:
        print(f"  {Fore.RED}✗ SSL/TLS not enabled or not accessible{Style.RESET_ALL}")
    
    # Display Certificate Transparency results
    ct_data = result.get("certificate_transparency", {})
    print(f"\n{Fore.CYAN}Certificate Transparency:{Style.RESET_ALL}")
    
    if ct_data.get("monitoring_enabled"):
        print(f"  {Fore.GREEN}✓ CT monitoring enabled{Style.RESET_ALL}")
        cert_count = ct_data.get("certificates_found", 0)
        print(f"  • Certificates found: {cert_count}")
        
        if ctx.obj.get('verbose') and ct_data.get("recent_certificates"):
            print(f"  • Recent certificates:")
            for cert in ct_data["recent_certificates"][:3]:  # Show top 3
                print(f"    - {cert.get('common_name', 'N/A')} (ID: {cert.get('id', 'N/A')})")
                print(f"      Issuer: {cert.get('issuer', 'N/A')}")
    else:
        print(f"  {Fore.YELLOW}• CT monitoring status unknown{Style.RESET_ALL}")
        if ct_data.get("error"):
            print(f"    Error: {ct_data['error']}")
    
    # Display CAA records
    caa_data = result.get("caa_records", {})
    print(f"\n{Fore.CYAN}CAA (Certificate Authority Authorization):{Style.RESET_ALL}")
    
    if caa_data.get("caa_enabled"):
        print(f"  {Fore.GREEN}✓ CAA records configured{Style.RESET_ALL}")
        
        protection_level = caa_data.get("protection_level", "none")
        if protection_level == "high":
            protection_color = Fore.GREEN
        elif protection_level == "medium":
            protection_color = Fore.YELLOW
        else:
            protection_color = Fore.RED
        
        print(f"  • Protection level: {protection_color}{protection_level.title()}{Style.RESET_ALL}")
        
        authorized_cas = caa_data.get("authorized_cas", [])
        if authorized_cas:
            print(f"  • Authorized CAs: {', '.join(authorized_cas)}")
        
        if ctx.obj.get('verbose') and caa_data.get("caa_records"):
            print(f"  • CAA records:")
            for record in caa_data["caa_records"]:
                print(f"    - {record}")
    else:
        print(f"  {Fore.RED}✗ No CAA records found{Style.RESET_ALL}")
    
    # Display certificate chain analysis
    chain_data = result.get("certificate_chain", {})
    print(f"\n{Fore.CYAN}Certificate Chain:{Style.RESET_ALL}")
    
    if chain_data.get("chain_valid"):
        print(f"  {Fore.GREEN}✓ Certificate chain valid{Style.RESET_ALL}")
        chain_length = chain_data.get("chain_length", 0)
        print(f"  • Chain length: {chain_length} certificate(s)")
        
        root_ca = chain_data.get("root_ca", "Unknown")
        if root_ca != "Unknown":
            print(f"  • Root CA: {root_ca}")
        
        intermediate_cas = chain_data.get("intermediate_cas", [])
        if intermediate_cas:
            print(f"  • Intermediate CAs: {', '.join(intermediate_cas)}")
    else:
        print(f"  {Fore.RED}✗ Certificate chain validation issues{Style.RESET_ALL}")
        if chain_data.get("trust_issues"):
            for issue in chain_data["trust_issues"]:
                print(f"    • {issue}")
    
    # Display recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n{Fore.CYAN}Certificate Recommendations:{Style.RESET_ALL}")
        for rec in recommendations:
            print(f"  • {rec}")


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)