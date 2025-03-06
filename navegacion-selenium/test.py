#!/usr/bin/python3
from random import randint
from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from pyvirtualdisplay import Display
from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from dotenv import load_dotenv
import socket, json, requests, io, os, sys

# Carga de variables de entorno
load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWD')

# Validación de las variables de entorno
if not db_host or not db_user or not db_pass:
    print("❌ Error: Faltan variables de entorno para la conexión a MongoDB.")
    sys.exit(1)

# Construcción de la URI de MongoDB
mongo_uri = f"mongodb+srv://{db_user}:{db_pass}@{db_host}/?retryWrites=true&w=majority"

# Conexión a la base de datos
try:
    client = MongoClient(mongo_uri)
    db = client.get_database()  # Obtiene la base de datos por defecto
    collection = db["sitiosWeb"]
    print("✅ Conexión a MongoDB establecida correctamente.")
except ConfigurationError:
    print("❌ Error: URI de conexión a MongoDB inválida. Verifica el nombre del host.")
    sys.exit(1)

# Formato normalizado de fecha
hoy = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

# Nombre del servidor (sonda) que ejecutará el script
server_name = socket.gethostname()

# URL de donde se obtendrán los sitios web a revisar
url = 'https://raw.githubusercontent.com/cfuentea/raspberry-pi-chromium-webdriver/master/sitios.txt'

# Parámetros de visualización para Selenium
display = Display(visible=0, size=(1280, 760))
display.start()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--mute-audio')

# Inicialización del driver de Selenium
try:
    driver = webdriver.Chrome(options=chrome_options)
    print("✅ Selenium WebDriver iniciado correctamente.")
except WebDriverException as e:
    print(f"❌ Error al iniciar Selenium WebDriver: {str(e)}")
    sys.exit(1)

# Función para medir el rendimiento de carga de un sitio web
def prueba_medicion(driver, web, server_name, hoy):
    try:
        web = web.strip()
        driver.get(web)
        navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
        responseStart = driver.execute_script("return window.performance.timing.responseStart")
        domComplete = driver.execute_script("return window.performance.timing.domComplete")

        backendPerformance_calc = (responseStart - navigationStart) / 1000
        frontendPerformance_calc = (domComplete - responseStart) / 1000

        data_dict = {
            "server_name": server_name,
            "timestamp": hoy,
            "url": web,
            "t_backend_seg": backendPerformance_calc,
            "t_frontend_seg": frontendPerformance_calc
        }
        driver.implicitly_wait(10)
        return data_dict
    except WebDriverException as e:
        print(f"❌ Error al acceder a {web}: {str(e)}")
        return None

# Espera aleatoria para evitar parecer un bot
sleep(randint(5, 30))

# Obtención de la lista de sitios web
sitios_web = []
try:
    response = requests.get(url)
    response.raise_for_status()
    sitios_web = io.StringIO(response.text)
    print("✅ Lista de sitios web obtenida desde el repositorio.")
except requests.RequestException as e:
    print(f"⚠️ Advertencia: No se pudo obtener la lista de sitios web en línea ({str(e)}). Intentando leer archivo local.")
    if os.path.exists('/tmp/sitios.txt'):
        with open('/tmp/sitios.txt', 'r') as archivo:
            sitios_web = archivo.readlines()
        print("✅ Lista de sitios web cargada desde /tmp/sitios.txt.")
    else:
        print("❌ Error: No se pudo obtener la lista de sitios web ni en línea ni desde el archivo local.")
        sys.exit(1)

# Iteración sobre los sitios web y medición
for web in sitios_web:
    try:
        data_dict = prueba_medicion(driver, web, server_name, hoy)
        if data_dict:
            collection.insert_one(data_dict)
            print(f"✅ Datos insertados en MongoDB para {web.strip()}")
        else:
            print(f"⚠️ No se insertaron datos para {web.strip()}.")
    except WebDriverException as e:
        print(f"❌ Error al cargar la página {web.strip()}: {e}")

# Cierre de recursos
driver.quit()
display.stop()
client.close()
print("✅ Script finalizado correctamente.")

