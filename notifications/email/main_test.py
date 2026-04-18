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

def main():
    logger.info("Iniciando prueba del Dispatcher (desde carpeta notifications)...")

    # 1. Objeto JSON simulado
    user_json = """
    {
        "email": "roberleonlan@gmail.com",
        "frecuencia": "semanal",
        "flags": ["competencia", "tendencias"]
    }
    """
    
    try:
        user_config = json.loads(user_json)
    except json.JSONDecodeError as err:
        logger.error(f"El JSON del usuario vino mal formado: {err}")
        return

    destinations = [
        EmailDestination(),
        InstagramDestination() 
    ]
    
    dispatcher = NotificationDispatcher(destinations=destinations)

    logger.info("=== EMPEZANDO A PROCESAR EL USER CONFIG ===")
    dispatcher.process_request(user_config)
    logger.info("=== EJECUCIÓN FINALIZADA ===")


if __name__ == "__main__":
    main()
