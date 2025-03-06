import os
import socket
import json
import requests
import io
import logging
import time
from random import randint
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from pyvirtualdisplay import Display
from pymongo import MongoClient
from dotenv import load_dotenv
from plugins.base_plugin import TestPlugin

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class WebMeasurementTest(TestPlugin):
    def __init__(self):
        """Inicializa la clase y carga la configuración"""
        super().__init__()
        load_dotenv()

        # Configuración desde el archivo YAML
        self.config = self._load_config()

        self.db_host = os.getenv('DB_HOST')
        self.db_user = os.getenv('DB_USER')
        self.db_pass = os.getenv('DB_PASSWD')

        self.mongo_uri = f"mongodb+srv://{self.db_user}:{self.db_pass}@{self.db_host}/?retryWrites=true&w=majority"
        self.collection_name = self.config.get("mongo_collection", "sitiosWeb")

        self.server_name = socket.gethostname()
        self.url_list_source = self.config.get("url_list_source", "https://raw.githubusercontent.com/cfuentea/raspberry-pi-chromium-webdriver/master/sitios.txt")
        
        self.results = []
        self.client = None
        self.db = None
        self.collection = None

    def run(self):
        """Ejecuta la prueba de medición de carga web."""
        logging.info(f"Running WebMeasurementTest on {self.server_name}")
        
        # Intentar conectar a MongoDB
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.Cluster0
            self.collection = self.db[self.collection_name]
            logging.info("Connected to MongoDB successfully.")
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            return

        # Iniciar Display Virtual (para Selenium sin interfaz)
        display = Display(visible=0, size=(1280, 760))
        display.start()

        # Configuración del driver de Selenium
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--mute-audio')

        driver = webdriver.Chrome(options=chrome_options)

        # Obtener la lista de sitios web desde la URL configurada
        sitios = self._get_sites_list()

        # Iterar sobre los sitios web
        for web in sitios:
            web = web.strip()
            if not web:
                continue

            time.sleep(randint(5, 30))  # Simular comportamiento humano

            data_dict = self._measure_site(driver, web)
            if data_dict:
                self.results.append(data_dict)
                self.collection.insert_one(data_dict)

        driver.quit()
        display.stop()
        self.client.close()

    def _get_sites_list(self):
        """Obtiene la lista de sitios web desde la URL o un backup local."""
        try:
            response = requests.get(self.url_list_source)
            response.raise_for_status()
            return response.text.splitlines()
        except requests.RequestException:
            logging.warning("Error fetching site list from URL. Using local backup file.")
            try:
                with open('/tmp/sitios.txt', 'r') as archivo:
                    return archivo.readlines()
            except Exception as e:
                logging.error(f"Error reading local backup file: {e}")
                return []

    def _measure_site(self, driver, web):
        """Mide los tiempos de carga de un sitio web y retorna los datos estructurados."""
        try:
            driver.get(web)
            navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
            responseStart = driver.execute_script("return window.performance.timing.responseStart")
            domComplete = driver.execute_script("return window.performance.timing.domComplete")

            backendPerformance_calc = (responseStart - navigationStart) / 1000
            frontendPerformance_calc = (domComplete - responseStart) / 1000

            data_dict = {
                "server_name": self.server_name,
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "url": web,
                "t_backend_seg": backendPerformance_calc,
                "t_frontend_seg": frontendPerformance_calc
            }
            return data_dict
        except WebDriverException as e:
            logging.error(f"Error loading {web}: {e}")
            return None

    def get_results(self):
        """Devuelve los resultados recopilados."""
        return {f"test_{i}": result for i, result in enumerate(self.results)}

    def get_config(self):
        """Devuelve la configuración utilizada."""
        return self.config

# Instancia del plugin
plugin = WebMeasurementTest()