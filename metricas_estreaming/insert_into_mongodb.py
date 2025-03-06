import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

def insert_json_to_mongo(data):
    """
    Inserta un JSON en la base de datos MongoDB.
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener credenciales desde .env
    db_username = os.getenv("MONGO_USER")
    db_password = os.getenv("MONGO_PW")
    uri = os.getenv("MONGO_URI").replace("<db_username>", db_username).replace("<db_password>", db_password)
    
    # Conectar a MongoDB
    client = MongoClient(uri)
    db = client["streaming"]  # Base de datos
    collection = db["buffer-ratio"]  # Colección
    
    # Insertar el JSON
    result = collection.insert_one(data)
    
    print(f"Documento insertado con ID: {result.inserted_id}")
    
    # Cerrar la conexión
    client.close()

#qos_example = {'jitter': 69.6045265182817, 'zero_throughput_ratio': 0.4146341463414634, 'retransmission_rate': 28.258227555075425}
#insert_json_to_mongo(qos_example)

