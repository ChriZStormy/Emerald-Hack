import sys
import os
from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import subprocess

# Agregamos la ruta del proyecto al path para importar notifications
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notifications.email.dispatcher import (
    NotificationDispatcher, 
    EmailDestination,
    FacebookDestination
)

app = Flask(__name__)

# Configurar dispatcher
email_destinations = [EmailDestination()]
fb_destinations = [FacebookDestination()]

email_dispatcher = NotificationDispatcher(destinations=email_destinations)
fb_dispatcher = NotificationDispatcher(destinations=fb_destinations)

def conectar_db():
    # conectamos con la database del root
    ruta_script = os.path.abspath(__file__)
    flask_dir = os.path.dirname(ruta_script) # Estás en Flask/
    ruta_raiz = os.path.dirname(flask_dir)    # Estás en la raíz del proyecto
    db_path = os.path.join(ruta_raiz, "DB.db")
    return sqlite3.connect(db_path)

WEEKS_DATA = [
    {
        'alimenticio': {
            'nombre': 'Insumo Alimenticio (LSTM FRESH) - Semana 1',
            'prediccion': 'Tendencia de Precios ($MXN). Modelo autoregresivo detectando fluctuación estacional.',
            'insight': '¡Hola! Es un gusto saludarte y acompañarte en la gestión de tu tortillería durante esta semana.\n\nDía 1: $22.58\nDía 2: $22.60\nDía 3: $22.59\nDía 4: $22.58\nDía 5: $22.58\nDía 6: $22.58\nDía 7: $22.56\n\nAl llegar al último día, habrás tenido un crecimiento acumulado del 0.27% en el precio respecto al inicio de la semana. Te sugiero tener un margen de 8 centavos por si las condiciones cambian.\n\nEsto pasa porque el mercado local muestra una ligera fluctuación estacional, según los reportes de comportamiento de precios recientes en la zona.\n\nAcción estratégica: Te sugiero cuidar tu flujo de efectivo diario y ajustar tus compras al detalle para mantener la estabilidad de tu margen de ganancia ante estos cambios mínimos. ¡Mucho éxito!',
            'labels': ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
            'valores': [22.58, 22.6, 22.59, 22.58, 22.58, 22.58, 22.56]
        },
        'turismo': {
            'nombre': 'Turismo Gto - Semana 1',
            'prediccion': 'Crecimiento del 20% en ocupación hotelera.',
            'insight': 'Fortalecer campañas digitales para el Festival Cervantino.',
            'labels': ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            'valores': [80, 95, 110, 130, 150, 190]
        },
        'agro': {
            'nombre': 'Agroindustria - Semana 1',
            'prediccion': 'Estabilidad en exportaciones de berries.',
            'insight': 'Invertir en sistemas de riego automatizado por sequía.',
            'labels': ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            'valores': [200, 190, 210, 205, 220, 230]
        }
    },
    {
        'alimenticio': {
            'nombre': 'Insumo Alimenticio (LSTM FRESH) - Semana 2',
            'prediccion': 'Alza moderada en costos de flete por temporada de lluvias.',
            'insight': '¡Hola! Resumen de tu segunda semana.\n\nDía 8: $22.60\nDía 9: $22.65\nDía 10: $22.70\nDía 11: $22.75\nDía 12: $22.72\nDía 13: $22.70\nDía 14: $22.68\n\nEl precio tuvo un pico a mediados de semana por interrupciones menores en logística de proveedores. \n\nAcción estratégica: Asegura inventario con anticipación para evitar compras urgentes con tarifas más altas.',
            'labels': ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
            'valores': [22.60, 22.65, 22.70, 22.75, 22.72, 22.70, 22.68]
        },
        'turismo': {
            'nombre': 'Turismo Gto - Semana 2',
            'prediccion': 'Estabilidad tras repunte inicial.',
            'insight': 'Manejar promociones directas para fidelizar clientes.',
            'labels': ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            'valores': [82, 92, 112, 135, 145, 185]
        },
        'agro': {
            'nombre': 'Agroindustria - Semana 2',
            'prediccion': 'Ligera alza en precios de fertilizante.',
            'insight': 'Buscar proveedores alternativos locales.',
            'labels': ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            'valores': [205, 195, 215, 210, 225, 235]
        }
    },
    {
        'alimenticio': {
            'nombre': 'Insumo Alimenticio (LSTM FRESH) - Semana 3',
            'prediccion': 'Estabilización de precios. Volatilidad reducida.',
            'insight': '¡Hola! Resumen de la tercera semana.\n\nDía 15: $22.65\nDía 16: $22.64\nDía 17: $22.62\nDía 18: $22.60\nDía 19: $22.58\nDía 20: $22.59\nDía 21: $22.58\n\nEl mercado ha vuelto a estabilizarse tras la leve alza de la semana pasada.\n\nAcción estratégica: Excelente momento para revisar tus márgenes y tal vez ofrecer combos especiales a clientes recurrentes para generar volumen.',
            'labels': ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
            'valores': [22.65, 22.64, 22.62, 22.60, 22.58, 22.59, 22.58]
        },
        'turismo': {
            'nombre': 'Turismo Gto - Semana 3',
            'prediccion': 'Preparación para temporada vacacional.',
            'insight': 'Asignar presupuesto inicial para pauta en redes para diciembre.',
            'labels': ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            'valores': [85, 95, 115, 140, 155, 195]
        },
        'agro': {
            'nombre': 'Agroindustria - Semana 3',
            'prediccion': 'Disminución en demanda de fresa nacional.',
            'insight': 'Enfocar recursos en exportación a Estados Unidos.',
            'labels': ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            'valores': [190, 185, 220, 225, 230, 240]
        }
    }
]

current_week_idx = 0

@app.route('/')
def index():
    global current_week_idx
    # Evitar índice fuera de rango
    idx = current_week_idx % len(WEEKS_DATA)
    sectores = WEEKS_DATA[idx]
    return render_template('home.html', sectores=sectores)

@app.route('/simular', methods=['POST'])
def simular():
    global current_week_idx
    current_week_idx += 1
    idx = current_week_idx % len(WEEKS_DATA)
    data_actual = WEEKS_DATA[idx]
    
    # Send messages to users for the new week
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, correo FROM Usuario")
        usuarios = cursor.fetchall()
        conn.close()
        
        alimenticio = data_actual['alimenticio']
        
        for usuario in usuarios:
            nombre, correo = usuario
            user_config = {"nombre": nombre, "email": correo}
            
            custom_content = {
                "negocio": nombre,
                "tendencias": [
                    f"Semana {idx + 1}: {alimenticio['prediccion']}"
                ],
                "analisis_ia": alimenticio['insight']
            }
            
            print(f"Enviando reporte de Semana {idx + 1} a {nombre} ({correo})")
            email_dispatcher.process_request(user_config, custom_content)
            
        # Post to Facebook once per simulation (not per user)
        fb_config = {"nombre": "Comunidad Pymes Guanajuato", "email": "admin@facebook.page"}
        fb_content = {
            "negocio": "Pymes de Guanajuato",
            "analisis_ia": f"¡Reporte semanal disponible! {alimenticio['prediccion']} - {alimenticio['insight']}"
        }
        print(f"Publicando reporte general de Semana {idx + 1} en Facebook...")
        fb_dispatcher.process_request(fb_config, fb_content)
        
    except Exception as e:
        print(f"Error en simulacion: {e}")
        
    return redirect(url_for('index'))
@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    telefono = request.form.get('telefono')
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        # Verificar si la tabla existe o crearla si no existe en el root (por si aca)
        cursor.execute('''CREATE TABLE IF NOT EXISTS Usuario (
                            Id_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT,
                            correo TEXT,
                            Numero TEXT)''')
        cursor.execute("INSERT INTO Usuario (nombre, correo, Numero) VALUES (?, ?, ?)", 
                       (nombre, correo, telefono))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Enviar notificación de bienvenida/reporte al usuario recién registrado
        user_config = {
            "id": user_id,
            "nombre": nombre,
            "email": correo
        }
        print(f"Despachando notificaciones para el nuevo usuario {nombre}...")
        email_dispatcher.process_request(user_config)
        
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)