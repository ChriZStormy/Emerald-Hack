"""
Módulo para publicar actualizaciones en la página de Facebook usando Graph API.
"""

import requests
from typing import Dict, Any

# Importamos las variables genéricas desde el módulo de settings
from notifications.facebook.settings import YOUR_PAGE_ID, YOUR_ACCESS_TOKEN


def publicar_resumen_semanal(page_id: str, access_token: str, datos_completos: Dict[str, Any]) -> bool:
    """
    Construye un string formateado con los datos del resumen semanal de mercado
    y lo envía al endpoint /feed de la API de Graph de Facebook.
    
    Args:
        page_id (str): El ID de la página de Facebook.
        access_token (str): El token de acceso a la API con permisos de página.
        datos_completos (Dict[str, Any]): Diccionario con la información del mercado.
            Debe contener las claves: 'Análisis de Competidores', 'Tendencias de Búsqueda',
            y 'Sentimiento de Mercado'.
            
    Returns:
        bool: True si la publicación fue exitosa, False en caso contrario.
    """
    
    # Extraemos las secciones requeridas manejando posibles faltantes
    analisis_competidores = datos_completos.get('Análisis de Competidores', 'No hay datos disponibles.')
    tendencias_busqueda = datos_completos.get('Tendencias de Búsqueda', 'No hay datos disponibles.')
    sentimiento_mercado = datos_completos.get('Sentimiento de Mercado', 'No hay datos disponibles.')

    # Construimos el formato del mensaje con emojis
    mensaje_formateado = (
        "📈 *RESUMEN SEMANAL DE MERCADO* 📈\n\n"
        "👥 *Análisis de Competidores*:\n"
        f"{analisis_competidores}\n\n"
        "🔍 *Tendencias de Búsqueda*:\n"
        f"{tendencias_busqueda}\n\n"
        "🧠 *Sentimiento de Mercado*:\n"
        f"{sentimiento_mercado}\n\n"
        "🚀 #Mercado #Tendencias #ResumenSemanal"
    )

    # Endpoint de la API
    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    
    # Parámetros (A Facebook Graph API le podemos pasar json params, data formdata, o query params)
    payload = {
        'message': mensaje_formateado,
        'access_token': access_token
    }

    try:
        # Petición POST a la API de Facebook
        response = requests.post(url, data=payload, timeout=15)
        
        # Levanta una excepción si la respuesta contiene un código de error HTTP (4xx o 5xx)
        response.raise_for_status()

        # Si llegamos aquí, la solicitud fue exitosa (200 OK)
        data = response.json()
        print(f"✅ Estado publicado exitosamente. ID del post: {data.get('id')}")
        return True

    except requests.exceptions.HTTPError as http_err:
        print(f"❌ Error HTTP de la API de Facebook: {http_err}")
        try:
            # Intento de mostrar más detalles del error (como "token expired", "insufficient permissions")
            error_details = response.json().get('error', {})
            print(f"Detalles del error FB: {error_details.get('message')} (Código: {error_details.get('code')})")
        except ValueError:
            pass
            
    except requests.exceptions.Timeout:
        print("❌ Error: Se agotó el tiempo de espera al conectar con Facebook.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de Conexión. Por favor revisa tu acceso a internet.")
        
    except Exception as err:
        print(f"❌ Ocurrió un error inesperado al intentar publicar en Facebook: {err}")
        
    return False


if __name__ == "__main__":
    # Datos simulados (mock)
    mock_datos_completos = {
        'Análisis de Competidores': 'La competencia X incrementó su presencia en un 15% este mes, lanzando 2 nuevos productos al mercado.',
        'Tendencias de Búsqueda': 'El término "Automatización con IA" subió al top de búsquedas, mostrando un interés del 60% en nuestra demografía clave.',
        'Sentimiento de Mercado': 'El sentimiento general es alcista, con un 75% favorable a nuevas inversiones tecnológicas.'
    }

    # Llamada de prueba usando los placeholders de settings.py
    exito = publicar_resumen_semanal(YOUR_PAGE_ID, YOUR_ACCESS_TOKEN, mock_datos_completos)
    
    if not exito:
        print("⚠️ La publicación falló. Probablemente se necesite configurar un Access Token válido en settings.py.")
