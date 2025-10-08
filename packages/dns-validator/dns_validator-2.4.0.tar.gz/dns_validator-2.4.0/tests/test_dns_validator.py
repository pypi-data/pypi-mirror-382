# DNS Validator Test Cases

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dns_validator.dns_validator import DNSValidator

class TestDNSValidator(unittest.TestCase):
    """Test cases for DNS Validator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = DNSValidator(verbose=False)
        self.test_domain = "google.com"  # Reliable test domain
    
    def test_delegation_check_valid_domain(self):
        """Test delegation check with a valid domain"""
        result = self.validator.check_delegation(self.test_domain)
        
        self.assertEqual(result["domain"], self.test_domain)
        self.assertIsInstance(result["authoritative_servers"], list)
        self.assertGreater(len(result["authoritative_servers"]), 0)
        self.assertTrue(result["delegation_valid"])
    
    def test_delegation_check_invalid_domain(self):
        """Test delegation check with an invalid domain"""
        invalid_domain = "this-domain-does-not-exist-12345.com"
        result = self.validator.check_delegation(invalid_domain)
        
        self.assertEqual(result["domain"], invalid_domain)
        self.assertFalse(result["delegation_valid"])
        self.assertGreater(len(result["errors"]), 0)
    
    def test_propagation_check_valid_domain(self):
        """Test propagation check with a valid domain"""
        result = self.validator.check_propagation(self.test_domain, 'A')
        
        self.assertEqual(result["domain"], self.test_domain)
        self.assertEqual(result["record_type"], 'A')
        self.assertIsInstance(result["servers"], dict)
        self.assertGreater(len(result["servers"]), 0)
    
    def test_propagation_check_with_expected_value(self):
        """Test propagation check with expected value (should fail for wrong value)"""
        result = self.validator.check_propagation(self.test_domain, 'A', "192.168.1.1")
        
        # This should likely fail since google.com doesn't resolve to 192.168.1.1
        self.assertEqual(result["expected_value"], "192.168.1.1")
    
    def test_cloudflare_check_basic(self):
        """Test basic Cloudflare check without API token"""
        result = self.validator.check_cloudflare_settings(self.test_domain)
        
        self.assertEqual(result["domain"], self.test_domain)
        self.assertIsInstance(result["cloudflare_detected"], bool)
        self.assertIsInstance(result["records"], list)
        self.assertIsInstance(result["errors"], list)

if __name__ == '__main__':
    print("Running DNS Validator Tests...")
    print("=" * 40)
    unittest.main(verbosity=2)