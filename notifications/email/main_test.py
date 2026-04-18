import json
import logging
import os
import sys

# Agregamos la ruta del proyecto al path (subiendo 3 niveles desde notifications/email/main_test.py)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from notifications.email.dispatcher import (
    NotificationDispatcher, 
    EmailDestination,
    InstagramDestination
)

# Configuramos logging de más alto nivel para que sea visible en la consola
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    force=True
)
logger = logging.getLogger("MainTest")

import sqlite3

def main():
    logger.info("Iniciando conexión...")

    # CONFIGURACIÓN DEL PATH: 
    # Ajusta cuántos os.path.dirname necesites para llegar a la carpeta de la BD
    ruta_script = os.path.abspath(__file__)
    nivel_1 = os.path.dirname(ruta_script) # Estás en notifications/email/
    nivel_2 = os.path.dirname(nivel_1)      # Estás en notifications/
    ruta_raiz = os.path.dirname(nivel_2)
    db_path = os.path.join(ruta_raiz, "BD.db")

    destinations = [
        EmailDestination(),
        InstagramDestination() 
    ]
    dispatcher = NotificationDispatcher(destinations=destinations)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Seleccionamos tus columnas reales
            cursor.execute("SELECT Id_Usuario, nombre, correo FROM Usuario")
            usuarios = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error al leer la BD: {e}")
        return

    # Procesar la información
    for row in usuarios:
        user_id, nombre, correo = row
        
        # Ajustamos el diccionario a lo que tu tabla tiene ahora
        user_config = {
            "id": user_id,
            "nombre": nombre,
            "email": correo, # Aquí mapeamos 'correo' a la llave 'email' que espera tu dispatcher
        }
        
        logger.info(f"Enviando notificación a: {nombre} ({correo})")
        dispatcher.process_request(user_config)

if __name__ == "__main__":
    main()