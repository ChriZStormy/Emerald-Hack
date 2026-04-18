import logging
import threading
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List

# Se importa la función existente del módulo 'mailer'
from .mailer import enviar_reporte_html

# Configuración estándar del logger para el módulo
logger = logging.getLogger(__name__)

class DataProviderError(Exception):
    """Excepción para errores al recuperar los datos."""
    pass

class DeliveryError(Exception):
    """Excepción para fallas en el envío al destino."""
    pass


def fetch_mock_data(nombre: str) -> Dict[str, Any]:
    """
    Función 'MockData' para obtener información relevante simulada,
    ahora utilizando el nombre del usuario o negocio.
    """
    logger.info(f"Consultando MockData para: {nombre}")
    
    # Estructura de modelo de datos requerida por el template html del mailer.py
    data = {
        "negocio": nombre,
        "tendencias": [
            "Aumento de 20% en búsquedas locales de tus servicios principales.",
            "Los consumidores muestran mayor preferencia por tiempos de respuesta sub-1hr.",
        ],
        "analisis_ia": (
            "Se ha detectado que 2 de tus competidores directos lanzaron promociones "
            "de 'Envío Gratis'. Se sugiere ajustar los copys de tus campañas actuales."
        )
    }
    
    return data


class NotificationDestination(ABC):
    """
    Patrón Strategy / Interfaz Base para cumplir con Clean Code y SOLID (Open/Closed Principle). 
    Permite escalar fácilmente distintos métodos de envío de notificaciones.
    """
    @abstractmethod
    def send(self, recipient: str, content: Dict[str, Any]) -> bool:
        pass


class EmailDestination(NotificationDestination):
    """Integración con el submódulo 'mailer.py'."""
    def send(self, recipient: str, content: Dict[str, Any]) -> bool:
        logger.info(f"[EmailDestination] Solicitando envío de correo a: {recipient}")
        try:
            success = enviar_reporte_html(recipient, content)
            if not success:
                # Disparamos error en caso de que devuelva False (para simular mejor control)
                raise DeliveryError("El servicio enviar_reporte_html devolvió False (falla SMTP/Credenciales).")
            
            logger.info("[EmailDestination] Reporte por correo enviado de manera exitosa.")
            return True
        except Exception as e:
            logger.error(f"[EmailDestination] Excepción durante el proceso de envío de email: {e}")
            raise DeliveryError(f"Email fallido: {e}")


class FacebookDestination(NotificationDestination):
    """
    Integración con Facebook Graph API (v25.0).
    Realiza una petición POST asíncrona mediante Threading para no penalizar el tiempo principal.
    """
    def __init__(self):
        # Token de página proporcionado
        self.page_token = "EAAUZBsFTA8vsBRHOmoKGAgbCxedAFjvh60WW0PKtTQLQ10pDha85I49s8W7aLcBpixcsmdNQ2luntpcSNG62pdnNo8GYLd6YGlybgZCF4FrMRshZAYw3DiEr42XP2ufdG3r32jAUOzZCVHkuzBWjIvs35MWH8kHu4NpiLHPRoMS7aQX20fQXbEl0ziBI9Hy2JibWYYVZBxaAvyDspbUQP4O5HQHOdp4XWPBY436sZD"
        self.api_version = "v25.0"
        self.page_id = "1028910470313878"
        self.url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}/feed"

    def send(self, recipient: str, content: Dict[str, Any]) -> bool:
        negocio = content.get("negocio", "Pyme")
        analisis = content.get("analisis_ia", "Reporte generado por IA.")
        
        # Texto del post formateado
        message = f"🚀 Actualización Intel Pymes para {negocio}:\n\n{analisis}\n\n#IntelPymes #IA #Resumen"
        
        logger.info("[FacebookDestination] Preparando publicación en API de Facebook...")

        def _post_to_fb():
            payload = {
                "message": message,
                "access_token": self.page_token
            }
            try:
                # El timeout previene que se quede colgado eternamente
                response = requests.post(self.url, data=payload, timeout=10)
                if response.status_code == 200:
                    post_id = response.json().get('id')
                    logger.info(f"[FacebookDestination] ¡Post publicado con éxito en el muro! ID: {post_id}")
                else:
                    logger.error(f"[FacebookDestination] Error Graph API ({response.status_code}): {response.text}")
            except Exception as e:
                logger.error(f"[FacebookDestination] Excepción crítica conectando a Facebook: {e}")

        # Se dispara el thread para que la red no bloquee el sistema (por ej: el correo se manda enseguida)
        fb_thread = threading.Thread(target=_post_to_fb)
        fb_thread.start()
        
        return True


class NotificationDispatcher:
    def __init__(self, destinations: List[NotificationDestination]):
        """Inyectar dependencias de los destinos evita acomplamiento rígido."""
        self.destinations = destinations

    def process_request(self, user_config: Dict[str, Any]) -> None:
        """
        Flujo principal Orquestador:
        1. Recibe la configuración del usuario (dict/json object).
        2. Recolecta data valiosa del Motor de IA.
        3. Transmite a todos los destinos configurados.
        """
        email = user_config.get("email")
        nombre = user_config.get("nombre", "Cliente")

        if not email:
            logger.error("Payload Inválido: Falta la llave 'email' en la configuración del usuario.")
            return

        try:
            # 2. Consultar servicios de Data
            content = fetch_mock_data(nombre)
            
            # 3. Invocar la comunicación por cada destino aplicable
            for dest in self.destinations:
                try:
                    dest.send(email, content)
                except DeliveryError as de:
                    logger.warning(f"El destino {type(dest).__name__} falló la entrega a {email}. Detalles: {de}")
                    # Manejo individualizado para que si falla una vía (email), siga usando el resto (ej. IG)
                
        except DataProviderError as e:
            logger.error(f"Fallo crpitico al fabricar la data inteligente para {email}. Abortar. ({e})")
        except Exception as e:
            logger.critical(f"Panic - Error no manejado en pipeline del Dispatcher: {e}", exc_info=True)
