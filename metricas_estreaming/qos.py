import scapy.all as scapy
from scapy.all import rdpcap
from scapy.all import *
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import subprocess

# Función para leer el archivo pcap y extraer los paquetes
def read_pcap(file_path):
    packets = scapy.rdpcap(file_path)
    return packets

# Función para calcular el throughput en intervalos de tiempo
def calculate_throughput(packets, interval=1.0):
    start_time = packets[0].time  # Tiempo del primer paquete
    end_time = packets[-1].time   # Tiempo del último paquete
    time_intervals = np.arange(0, end_time - start_time, interval)  # Tiempo relativo al inicio
    throughput = []

    for i in range(len(time_intervals) - 1):
        start = start_time + time_intervals[i]  # Tiempo absoluto
        end = start_time + time_intervals[i + 1]  # Tiempo absoluto
        bytes_in_interval = sum(len(p) for p in packets if start <= p.time < end)
        throughput.append(bytes_in_interval / interval)  # Bytes por segundo

    return time_intervals[:-1], throughput

# Función para detectar stall times (throughput menor a 50000 bytes/s)
def detect_stall_times(time_intervals, throughput):
    stall_times = []
    for i, thr in enumerate(throughput):
        if thr < 50000:  # Considerar throughput menor a 50000 bytes/s como stall
            stall_times.append(time_intervals[i])
    return stall_times

# Función para calcular el ratio de throughput menor a 50000 bytes/s vs total de mediciones
def calculate_zero_throughput_ratio(throughput):
    zero_count = sum(1 for thr in throughput if thr < 50000)  # Contar intervalos con throughput menor a 50 bytes/s
    total_count = len(throughput)  # Total de intervalos
    if total_count == 0:
        return 0.0  # Evitar división por cero
    return zero_count / total_count  # Ratio de throughput menor a 50 bytes/s

# Función para graficar el throughput
def plot_throughput(time_intervals, throughput, stall_times):
    plt.figure(figsize=(12, 6))
    plt.plot(time_intervals, throughput, label="Throughput (Bytes/s)")
    plt.scatter(stall_times, [0] * len(stall_times), color='red', label="Stall Times (Throughput < 50 Bytes/s)")
    plt.xlabel("Tiempo desde el inicio (s)")
    plt.ylabel("Throughput (Bytes/s)")
    plt.title("Análisis de Throughput y Stall Times (Throughput < 50 Bytes/s)")
    plt.legend()
    plt.grid()
    plt.show()


def retransimision_chart(paquetes):
    # Contadores para paquetes TCP y retransmisiones
    total_paquetes_tcp = 0
    total_retransmisiones = 0

    # Diccionario para rastrear secuencias TCP y detectar retransmisiones
    secuencias = {}

    # Intervalo de tiempo (en segundos)
    delta_tiempo = 1  # Delta de tiempo para calcular la tasa de retransmisión

    # Variables para la gráfica
    tiempos = []  # Tiempo en segundos
    tasas_retransmision = []  # Tasa de retransmisión por cada intervalo de tiempo

    # Contadores por intervalo de tiempo
    paquetes_intervalo = 0
    retransmisiones_intervalo = 0
    ultimo_tiempo = None

    # Iterar sobre cada paquete
    for paquete in paquetes:
        # Verificar si el paquete es TCP
        if TCP in paquete:
            timestamp = paquete.time  # Tiempo del paquete
            if ultimo_tiempo is None:
                ultimo_tiempo = timestamp
            
            # Verificar si el paquete está en el intervalo de tiempo actual
            if timestamp - ultimo_tiempo < delta_tiempo:
                paquetes_intervalo += 1
                tcp = paquete[TCP]
                seq = tcp.seq  # Número de secuencia TCP
                ack = tcp.ack  # Número de ACK TCP

                # Verificar si es una retransmisión
                if seq in secuencias:
                    retransmisiones_intervalo += 1
                else:
                    secuencias[seq] = True
            else:
                # Si ha pasado el intervalo, calcular tasa de retransmisión
                if paquetes_intervalo > 0:
                    tasa_retransmision = (retransmisiones_intervalo / paquetes_intervalo) * 100
                    tiempos.append(ultimo_tiempo)
                    tasas_retransmision.append(tasa_retransmision)

                # Reiniciar contadores para el siguiente intervalo de tiempo
                ultimo_tiempo = timestamp
                paquetes_intervalo = 1
                retransmisiones_intervalo = 1 if seq in secuencias else 0
                secuencias = {seq: True} if seq not in secuencias else secuencias

    # Asegurarse de agregar el último intervalo
    if paquetes_intervalo > 0:
        tasa_retransmision = (retransmisiones_intervalo / paquetes_intervalo) * 100
        tiempos.append(ultimo_tiempo)
        tasas_retransmision.append(tasa_retransmision)

    # Graficar la tasa de retransmisión a lo largo del tiempo
    plt.plot(tiempos, tasas_retransmision, label='Tasa de Retransmisión', color='blue')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Tasa de Retransmisión (%)')
    plt.title('Tasa de Retransmisión de TCP a lo largo del tiempo')
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Total paquetes TCP: {total_paquetes_tcp}")
    print(f"Total retransmisiones: {total_retransmisiones}")

def retransmision_rate(paquetes):
    # Contadores para paquetes TCP y retransmisiones
    total_paquetes_tcp = 0
    total_retransmisiones = 0

    # Diccionario para rastrear secuencias TCP y detectar retransmisiones
    secuencias = {}

    # Iterar sobre cada paquete
    for paquete in paquetes:
        # Verificar si el paquete es TCP
        if TCP in paquete:
            total_paquetes_tcp += 1
            tcp = paquete[TCP]
            seq = tcp.seq  # Número de secuencia TCP
            ack = tcp.ack  # Número de ACK TCP

            # Verificar si es una retransmisión
            if seq in secuencias:
                total_retransmisiones += 1
            else:
                secuencias[seq] = True

    # Calcular la tasa de retransmisión
    if total_paquetes_tcp > 0:
        tasa_retransmision = (total_retransmisiones / total_paquetes_tcp) * 100
        #print(f"Total paquetes TCP: {total_paquetes_tcp}")
        #print(f"Total retransmisiones: {total_retransmisiones}")
        #print(f"Tasa de retransmisión: {tasa_retransmision:.2f}%")
    else:
        print("No se encontraron paquetes TCP en la captura.")
    return tasa_retransmision

def jitter(paquetes):
    # Lista para almacenar los tiempos de llegada de los paquetes TCP
    tiempos_paquetes = []

    # Iterar sobre cada paquete
    for paquete in paquetes:
        # Verificar si el paquete es TCP
        if TCP in paquete:
            tiempos_paquetes.append(float(paquete.time))  # Convertir a float explícitamente

    # Calcular los intervalos entre los paquetes consecutivos
    intervalos = []
    for i in range(1, len(tiempos_paquetes)):
        intervalo = tiempos_paquetes[i] - tiempos_paquetes[i-1]
        intervalos.append(intervalo)

    # Calcular el jitter: desviación estándar de los intervalos
    jitter = np.std(intervalos)*1000

    # Mostrar el jitter
    #print(f"Jitter (desviación estándar de los intervalos de tiempo): {jitter:.6f} milisegundos")
    return float(jitter)


def jitter_chart(paquetes):

    # Intervalo de tiempo (en segundos)
    delta_tiempo = 1  # Intervalo de 1 segundo

    # Lista para almacenar los tiempos de llegada de los paquetes TCP
    tiempos_paquetes = []

    # Variables para la gráfica
    tiempos = []  # Tiempo relativo
    jitters = []  # Jitter por intervalo de 1 segundo

    # Iterar sobre cada paquete
    for paquete in paquetes:
        # Verificar si el paquete es TCP
        if TCP in paquete:
            tiempos_paquetes.append(float(paquete.time))  # Convertir a float explícitamente

    # Calcular los intervalos de tiempo y el jitter por cada intervalo de 1 segundo
    paquetes_intervalo = []
    for i in range(1, len(tiempos_paquetes)):
        # Calcular el tiempo relativo del paquete
        tiempo_relativo = tiempos_paquetes[i] - tiempos_paquetes[0]  # Tiempo relativo al primer paquete

        # Determinar si el paquete está dentro del intervalo de tiempo actual
        intervalo_actual = int(tiempo_relativo // delta_tiempo)
       
        # Añadir el paquete al intervalo correspondiente
        if len(paquetes_intervalo) <= intervalo_actual:
            paquetes_intervalo.extend([[]] * (intervalo_actual - len(paquetes_intervalo) + 1))

        paquetes_intervalo[intervalo_actual].append(tiempos_paquetes[i])

    # Calcular el jitter para cada intervalo de tiempo
    for intervalo in range(len(paquetes_intervalo)):
        if len(paquetes_intervalo[intervalo]) > 1:
            # Calcular los intervalos de tiempo entre paquetes
            intervalos = np.diff(paquetes_intervalo[intervalo])

            # Calcular el jitter (desviación estándar de los intervalos de tiempo)
            jitter = np.std(intervalos) * 1000  # Convertir a milisegundos
            tiempos.append(intervalo * delta_tiempo)
            jitters.append(jitter)

    # Graficar el jitter a lo largo del tiempo
    plt.plot(tiempos, jitters, label='Jitter', color='blue')
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Jitter (milisegundos)')
    plt.title('Jitter de TCP a lo largo del tiempo')
    plt.grid(True)
    plt.legend()
    plt.show()

def extract_twitch_url():
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--no-sandbox")
	service = Service("/usr/bin/chromedriver")
	driver = webdriver.Chrome(service=service, options=chrome_options)
	driver.get("https://www.twitch.tv/")
	time.sleep(5)
	soup = BeautifulSoup(driver.page_source, "html.parser")
	streamers = soup.find_all("a", {"data-a-target": "preview-card-image-link"})
	stream_links = ["https://www.twitch.tv" + s["href"] for s in streamers]
	driver.quit()
	return stream_links

def extract_tiktok_url():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    stream_links = []

    while not stream_links:
        driver.get("https://www.tiktok.com/live")
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        streamers = soup.find_all("a", {"class": "css-12pauqr-StyledHoverLink e1gme4pn10"})
        stream_links = ["https://www.tiktok.com" + s["href"] for s in streamers]
    
    driver.quit()
    return stream_links

def extract_youtube_live_url():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.youtube.com/live")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    streamers = soup.find_all("a", {"id": "thumbnail"})
    stream_links = ["https://www.youtube.com" + s["href"] for s in streamers if s.get("href")]
    driver.quit()
    return stream_links

def extract_twitch_url():
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--no-sandbox")
	service = Service("/usr/bin/chromedriver")
	driver = webdriver.Chrome(service=service, options=chrome_options)
	driver.get("https://www.twitch.tv/")
	time.sleep(5)
	soup = BeautifulSoup(driver.page_source, "html.parser")
	streamers = soup.find_all("a", {"data-a-target": "preview-card-image-link"})
	stream_links = ["https://www.twitch.tv" + s["href"] for s in streamers]
	driver.quit()
	return stream_links

def streaming_resolution(url):
    script_path = "execute_streaming.sh"
    result = subprocess.run(["bash", script_path, url], capture_output=True, text=True)
    #print("Output del comando (stdout):")
    #print(result.stdout)
    
    #print("\nOutput del comando (stderr):")
    #print(result.stderr)
    output_lines = result.stderr.splitlines()
    for line in output_lines:
        if "Available streams:" in line:
            streams_line = line
            break
    else:
        print("No se encontró la línea con las resoluciones disponibles.")
        return []
    resolutions = re.findall(r'\b\d+p(?:\d+)?\b', streams_line)
    
    return resolutions

def perform_streaming_download(url,resolution):
    script_path = "nohup bash execute_streaming.sh"
    subprocess.run([script_path, url, resolution], text=True)
    return True

def obtain_interfaces():
    result = subprocess.run(["ip", "-o", "link", "show"], capture_output=True, text=True)
    interfaces = [line.split(": ")[1].split()[0] for line in result.stdout.splitlines()]
    return interfaces

def perform_streaming_test(url,resolution,interface):
    #print("bash","test.sh" ,url, resolution, interface)
    result = subprocess.run(["bash","test.sh" ,url, resolution, interface], capture_output=True, text=False)
    return True


def get_curl_timings(url):
    result = subprocess.run(
        ['curl', '-w', '\nTiempos:\n-----------\nTiempo de resolución DNS: %{time_namelookup}\nTiempo de conexión TCP: %{time_connect}\nTiempo de handshake TLS: %{time_appconnect}\nTiempo hasta el primer byte: %{time_starttransfer}\nTiempo total: %{time_total}\n', '-o', '/dev/null', '-s', url],
        stdout=subprocess.PIPE,
        text=True
    )
    output = result.stdout
    timings = {}
    for line in output.split('\n'):
        if 'Tiempo de resolución DNS:' in line:
            timings['dns_resolution_time (ms)'] = round(float(line.split(':')[1].strip()) * 1000,3)
        elif 'Tiempo de conexión TCP (ms):' in line:
            timings['tcp_connection_time'] = round(float(line.split(':')[1].strip()) * 1000,3)
        elif 'Tiempo de handshake TLS:' in line:
            timings['tls_handshake_time (ms)'] = round(float(line.split(':')[1].strip()) * 1000,3)
        elif 'Tiempo hasta el primer byte:' in line:
            timings['time_to_first_byte (ms)'] = round(float(line.split(':')[1].strip()) * 1000,3)
        elif 'Tiempo total:' in line:
            timings['total_time (ms)'] = round(float(line.split(':')[1].strip()) * 1000,3)

    return json.dumps(timings, indent=4)


