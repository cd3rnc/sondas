import subprocess
import requests
import random
import json
from datetime import datetime
from qos import *
from insert_into_mongodb import insert_json_to_mongo
from scapy.all import rdpcap


#print("esperando 30 minutos")
#time.sleep(30*60)

def tiktok_test():
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = int(datetime.now().timestamp())
    print("----------------ejecucion ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"----------------")
    print("---------------obteniendo links de streaming actuales ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-----------")
    links = extract_tiktok_url()
    print("--------------links obtenidos ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"----------")
    print(links)
    print("--------------eligiendo url aleatoria....---------")
    url = random.choice(links)
    print("-------------url seleccionada: ",url)
    print("--------- realizando pruebas de resolucion de DNS y mas ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"--------")
    # Obtener el tiempo de ejecución de curl
    curl_timming = get_curl_timings(url)
    print("-------- resolucion DNS y mas obtenido-------", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"--------")
    # Extraer la mejor resolución de la URL
    resolution = 'origin'
    print("---------resolucion maxima: ",resolution)
    print("---------identificando interfaz de red a monitorear-----------------")
    interface = "eth0"
    print("----------interfaz seleccionada: ",interface)
    print("-----------ejecuntando prueba de streaming, con URL: ", url, "a una resolucion de :",resolution, "monitoreando la interfaz :",interface)
    perform_streaming_test(url, resolution, interface)

    pcap_file = "test.pcap"

    qos_data = generate_qos_json(pcap_file, url, resolution,machine,public_ip)

    # Combinar los datos de timing de curl y QoS
    curl_timming_dict = json.loads(curl_timming)
    concatenated_dict = {
        "datetime": current_datetime,
        "timestamp": timestamp,
        **curl_timming_dict,
        **qos_data
    }
    print(concatenated_dict)

    # Insertar los datos en MongoDB
    insert_json_to_mongo(concatenated_dict)


def youtube_test_2():
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = int(datetime.now().timestamp())
    

   
    print("----------------ejecucion", current_datetime, "----------------")

    print("---------------obteniendo links de streaming actuales", current_datetime, "-----------")
    links = extract_youtube_live_url()

    if not links:
        print("Error: No se encontraron enlaces de streaming.")
        return

    # Eliminar duplicados y limpiar URLs
    links = list(set(link.strip() for link in links if link.startswith("http")))

    print("--------------links obtenidos--------------")
    print(links)
    print("--------------eligiendo url aleatoria....---------")

    if not links:
        print("No hay URLs válidas para probar.")
        return

    intentos = 0
    max_intentos = len(links) * 2  # Evitar bucles infinitos
    url = None
    resolution = None

    while intentos < max_intentos:
        url = random.choice(links)
        resolution = streaming_resolution(url)

        if resolution and resolution[-1]:  # Si devuelve algo válido
            print("-------------URL seleccionada:", url)
            break  # Salimos del bucle en lugar de hacer return

        print("URL no compatible con streamlink, eligiendo otra URL...")
        intentos += 1

    if not url or not resolution:
        print("No se encontró ninguna URL compatible después de varios intentos.")
        return  # Aquí sí terminamos la función si no hay URL válida
    resolution=resolution[-1]
    # Continuar con las pruebas
    print("--------- realizando pruebas de resolucion de DNS y más", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "--------")
    curl_timming = get_curl_timings(url)
    print("-------- resolucion DNS y más obtenido-------", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "--------")

    print("---------resolucion máxima:", resolution)
    print("---------identificando interfaz de red a monitorear-----------------")
    interface = "eth0"
    print("----------interfaz seleccionada:", interface)
    print("-----------ejecutando prueba de streaming, con URL:", url, "a una resolución de:", resolution, "monitoreando la interfaz:", interface)
    perform_streaming_test(url, resolution, interface)

    pcap_file = "test.pcap"

    qos_data = generate_qos_json(pcap_file, url, resolution,machine,public_ip)

    # Combinar los datos de timing de curl y QoS
    curl_timming_dict = json.loads(curl_timming)
    concatenated_dict = {
        "datetime": current_datetime,
        "timestamp": timestamp,
        **curl_timming_dict,
        **qos_data
    }
    print(concatenated_dict)

    # Insertar los datos en MongoDB
    insert_json_to_mongo(concatenated_dict)


def twitch_test():
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = int(datetime.now().timestamp())
    print("----------------ejecucion ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"----------------")
    print("---------------obteniendo links de streaming actuales ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-----------")
    links = extract_twitch_url()
    print("--------------links obtenidos ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"----------")
    print(links)
    print("--------------eligiendo url aleatoria....---------")
    url = random.choice(links)
    print("-------------url seleccionada: ",url)
    print("--------- realizando pruebas de resolucion de DNS y mas ",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"--------")
    # Obtener el tiempo de ejecución de curl
    curl_timming = get_curl_timings(url)
    print("-------- resolucion DNS y mas obtenido-------", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"--------")
    # Extraer la mejor resolución de la URL
    #resolution = 'origin'
    resolution = streaming_resolution(url)[-1]
    print("---------resolucion maxima: ",resolution)
    print("---------identificando interfaz de red a monitorear-----------------")
    interface = "eth0"
    print("----------interfaz seleccionada: ",interface)
    print("-----------ejecuntando prueba de streaming, con URL: ", url, "a una resolucion de :",resolution, "monitoreando la interfaz :",interface)
    perform_streaming_test(url, resolution, interface)

    pcap_file = "test.pcap"

    qos_data = generate_qos_json(pcap_file, url, resolution,machine,public_ip)

    # Combinar los datos de timing de curl y QoS
    curl_timming_dict = json.loads(curl_timming)
    concatenated_dict = {
        "datetime": current_datetime,
        "timestamp": timestamp,
        **curl_timming_dict,
        **qos_data
    }
    print(concatenated_dict)

    # Insertar los datos en MongoDB
    insert_json_to_mongo(concatenated_dict)

machine = subprocess.check_output("hostname", shell=True, text=True).strip()
public_ip = requests.get("https://api.ipify.org").text

def generate_qos_json(pcap_file, url, resolution,machine,public_ip):
    paquetes = rdpcap(pcap_file)
    time_intervals, throughput = calculate_throughput(paquetes, interval=1.0)
    stall_times = detect_stall_times(time_intervals, throughput)

    qos_data = {
            "machine": machine,
            "public_ip": public_ip,
            "url": url,
        "resolution": resolution,
        "buffer_ratio": calculate_zero_throughput_ratio(throughput),
    }
    return qos_data

if __name__ == "__main__":
    twitch_test()
    youtube_test_2()
    tiktok_test()

