import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from notifications.email.dispatcher import NotificationDispatcher, EmailDestination

logging.basicConfig(level=logging.INFO)

destinations = [EmailDestination()]
dispatcher = NotificationDispatcher(destinations=destinations)

usuarios = [
    {
        "email": "roberleonlan@gmail.com",
        "nombre": "Roberto Leon"
    },
    {
        "email": "ronaldoarriaga50@gmail.com",
        "nombre": "Ronaldo Arriaga"
    }
]

for user_config in usuarios:
    print(f"Enviando correo a {user_config['nombre']}...")
    dispatcher.process_request(user_config)

print("Ambos correos enviados con éxito.")
