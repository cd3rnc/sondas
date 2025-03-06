#!/usr/bin/env python3
import os
import yaml
import importlib
import argparse
import redis
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def load_global_config(config_path='config.yaml'):
    """Load the global configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading global configuration from {config_path}: {e}")
        raise

def load_plugins():
    """
    Dynamically load all plugin modules from the plugins directory.
    Each plugin module is expected to expose an instance named `plugin`.
    Returns a list of plugin instances.
    """
    plugins = []
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    for filename in os.listdir(plugins_dir):
        if filename.endswith('.py') and filename not in ('__init__.py', 'base_plugin.py'):
            module_name = filename[:-3]  # remove the '.py' extension
            try:
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, 'plugin') and isinstance(module.plugin):
                    plugins.append(module.plugin) 
                else:
                    logging.warning(f"El modulo {module_name} no fue implementado correctamente")
            except Exception as e:
                logging.error(f"Error loading plugins from {plugins_dir}: {e}")
        raise
    return plugins

def parse_arguments():
    """Parse command-line arguments for selecting plugins to run."""
    try:
        parser = argparse.ArgumentParser(description="Run selected plugins")
        parser.add_argument(
            'plugins',
            nargs='*',
            help="Names of plugins to execute (default: all)"
        )
        return parser.parse_args()
    except Exception as e:
        logging.error(f"Error parsing arguments: {e}")
        raise

def main():
    try:
        args = parse_arguments()
    except Exception:
        return

    try:
        global_config = load_global_config()
        logging.info(f"Global Configuration: {global_config}")
    except Exception:
        return

    # Configuración de Redis a partir de variables de entorno
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_queue = os.environ.get("REDIS_QUEUE", "upx_results")

    try:
        redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        # Verifica la conectividad con Redis
        redis_client.ping()
        logging.info(f"Connected to Redis at {redis_host}:6379")
    except Exception as e:
        logging.error(f"Error connecting to Redis at {redis_host}:6379: {e}")
        return

    try:
        plugins = load_plugins()
    except Exception:
        return

    if args.plugins:
        requested = [p.lower() for p in args.plugins]
        plugins = [plugin for plugin in plugins
                   if plugin.__class__.__name__.lower() in requested]
        if not plugins:
            logging.info(f"No matching plugins found for: {args.plugins}")
            return
    
    uxp = os.environ.get("UXP", "uxp")
    # Ejecutar los plugins y enviar resultados a Redis
    for plugin in plugins:
        start_time = time.time()
        logging.info(f"--- Running plugin: {plugin.__class__.__name__} ---")
        try:
            plugin.run()
            execution_time = time.time() - start_time
            logging.info(f"Execution time for {plugin.__class__.__name__}: {execution_time:.2f} seconds")
        except Exception as e:
            logging.error(f"Error running plugin {plugin.__class__.__name__}: {e}")
            continue

        try:
            results = plugin.get_results()
        except Exception as e:
            logging.error(f"Error retrieving results from plugin {plugin.__class__.__name__}: {e}")
            continue

        logging.info("Test Results:")
        for key, result in results.items():
            try:
                logging.info(f"{key}: {result}")
                # Agregar al resultado el hostname y el nombre del plugin
                result["uxp"] = uxp
                result["test_name"] = plugin.__class__.__name__
                redis_client.rpush(redis_queue, json.dumps(result))
                logging.info(f"Sent to Redis queue '{redis_queue}': {json.dumps(result)}")
            except redis.RedisError as re:
                logging.error(f"Redis error sending result for key {key}: {re}")
            except Exception as e:
                logging.error(f"Unexpected error sending result for key {key}: {e}")

if __name__ == '__main__':
    main()