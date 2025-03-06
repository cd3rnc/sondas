#!/usr/bin/env python3
import os
import time
import logging
from datetime import datetime
import dns.resolver
from plugins.base_plugin import TestPlugin

# Configure basic logging in English
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class DNSTest(TestPlugin):
    def __init__(self):
        self.results = {}
        # Load configuration (e.g., from dnstest.yaml)
        self.config = self._load_config()

    def get_config(self):
        """Returns a copy of the plugin configuration."""
        return self.config.copy()

    def run(self):
        """
        Runs DNS resolution tests for all hosts defined in the configuration.
        Expected configuration keys in the YAML:
          - hosts: list of hostnames to resolve.
          - dns: list of DNS server IPs to use for resolution.
          - count: number of resolution attempts per host (default: 10)
          - timeout: timeout in seconds for each resolution attempt (default: 10)
        """
        hosts = self.config.get("hosts", [])
        dns_servers = self.config.get("dns", [])
        count = self.config.get("count", 10)
        timeout = self.config.get("timeout", 10)

        if not dns_servers:
            logging.error("No DNS servers provided in configuration.")
            return

        logging.info(f"Using DNS server(s): {dns_servers}")
        self.results = {}

        for host in hosts:
            logging.info(f"Resolving {host} using DNS server(s) {dns_servers}")
            result = self.resolve_host(host, count, dns_servers, timeout)
            result["test_name"] = self.__class__.__name__
            self.results[host] = result

    def resolve_host(self, host, count, dns_servers, timeout):
        """
        Resolves a given host 'count' times using the provided DNS servers and timeout,
        and returns a dictionary with the statistics.
        """
        resolver = dns.resolver.Resolver()
        resolver.nameservers = dns_servers

        successes = 0
        failures = 0
        times_list = []
        resolved_ips = []

        for i in range(count):
            try:
                start = time.time()
                answers = resolver.resolve(host, 'A', lifetime=timeout)
                end = time.time()
                resolution_time_ms = (end - start) * 1000  # Convert to milliseconds
                times_list.append(resolution_time_ms)
                ip = answers[0].to_text()  # Usamos la primera IP
                resolved_ips.append(ip)
                successes += 1
                logging.info(f"{host} resolved to {ip} in {resolution_time_ms:.2f} ms (attempt {i+1})")
            except Exception as e:
                logging.error(f"Error resolving {host} on attempt {i+1}: {e}")
                failures += 1

        avg_time = sum(times_list) / len(times_list) if times_list else None
        min_time = min(times_list) if times_list else None
        max_time = max(times_list) if times_list else None

        result = {
            "timestamp": datetime.now().isoformat(),
            "host": host,
            "success": successes,
            "failure": failures,
            "avg": avg_time,
            "min": min_time,
            "max": max_time,
            "resolved_ips": list(set(resolved_ips)) 
        }
        return result

    def get_results(self):
        """Returns the DNS resolution test results."""
        return self.results

# Export an instance of the plugin.
plugin = DNSTest()