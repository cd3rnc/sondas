import os
import yaml
import logging
import inspect
from abc import ABC, abstractmethod

class TestPlugin(ABC):
    def _load_config(self):
        """
        Loads the plugin configuration from a YAML file located in the same directory as the plugin module.
        The configuration file is expected to have the same base name as the module (for example, if the module is
        ping_plugin.py, then it will look for ping_plugin.yaml).
        """
        try:
            # Get the file where the current plugin class is defined.
            module_file = inspect.getfile(self.__class__)
            base_dir = os.path.dirname(module_file)
            module_basename = os.path.splitext(os.path.basename(module_file))[0]
            config_file = os.path.join(base_dir, f"{module_basename}.yaml")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                return config
            else:
                logging.warning(f"Configuration file {config_file} not found. Using empty config.")
                return {}
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            return {}

    @abstractmethod
    def run(self):
        """
        Run the test. The plugin should load and use its own configuration.
        """
        pass

    @abstractmethod
    def get_results(self):
        """
        Return the results of the test.
        """
        pass

    @abstractmethod
    def get_config(self):
        """
        Return a copy of the plugin configuration.
        """
        pass