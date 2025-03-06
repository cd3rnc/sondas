import os
import logging
from datetime import datetime
from ping3 import ping
from plugins.base_plugin import TestPlugin

def ping_host(host, count, size, timeout):
    """
    Pings a given host a specified number of times with packets of a given size and timeout.
    
    Args:
        host (str): Hostname or IP address to ping.
        count (int): Number of packets to send.
        size (int): Packet size in bytes.
        timeout (int): Timeout for each ping request in seconds.
    
    Returns:
        dict: A dictionary containing the ping results and statistics, including timestamp.
    """
    start_time = datetime.now().isoformat()
    result = {
        "timestamp": start_time,
        "host": host,
        "success": 0,
        "failure": 0,
        "avg": None,
        "max": None,
        "min": None,
    }
    response_times = []

    for _ in range(count):
        try:
            response_time = ping(host, size=size, timeout=timeout)
            if response_time is None:
                result["failure"] += 1
            else:
                result["success"] += 1
                response_times.append(response_time)
        except Exception as e:
            logging.error(f"Error pinging {host}: {e}")
            result["failure"] += 1

    if response_times:
        result["avg"] = sum(response_times) / len(response_times)
        result["max"] = max(response_times)
        result["min"] = min(response_times)

    return result

class PingTest(TestPlugin):
    def __init__(self):
        self.results = {}
        self.plugin_name = "ping_plugin"  # Plugin name identifier.
        # Load the plugin's configuration using the base class method.
        self.config = self._load_config()

    def get_config(self):
        """
        Returns a copy of the plugin configuration.
        """
        return self.config.copy()

    def run(self):
        """
        Runs the ping tests for all hosts defined in the plugin configuration.
        Expected configuration keys in ping_plugin.yaml:
            - hosts: list of hosts to ping
            - count: number of ping packets to send (default: 10)
            - size: packet size in bytes (default: 56)
            - timeout: timeout for each ping request in seconds (default: 2)
        """
        hosts = self.config.get("hosts", [])
        count = self.config.get("count", 10)
        size = self.config.get("size", 56)
        timeout = self.config.get("timeout", 2)

        # Reset previous results.
        self.results = {}

        for host in hosts:
            logging.info(f"Pinging {host} with {count} packets, size {size}, timeout {timeout}.")
            result = ping_host(host, count, size, timeout)
        
            self.results[host] = result
            

    def get_results(self):
        """
        Returns the ping test results.
        """
        return self.results

# Export an instance of the plugin.
plugin = PingTest()