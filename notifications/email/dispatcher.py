import logging
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


def fetch_mock_data(flags: List[str]) -> Dict[str, Any]:
    """
    Función 'MockData' para obtener información relevante simulada,
    con base en los flags o temáticas de interés que activa el usuario.
    """
    logger.info(f"Consultando MockData para los flags registrados: {flags}")
    
    # Estructura de modelo de datos requerida por el template html del mailer.py
    data = {
        "negocio": "Startup S.A. de C.V.",
        "tendencias": [],
        "analisis_ia": ""
    }
    
    try:
        if "tendencias" in flags:
            data["tendencias"] = [
                "Aumento de 20% en búsquedas locales de tus servicios principales.",
                "Los consumidores muestran mayor preferencia por tiempos de respuesta sub-1hr.",
            ]
        else:
            data["tendencias"] = ["(No estas suscrito a alertas de tendencias)"]

        if "competencia" in flags:
            data["analisis_ia"] = (
                "Se ha detectado que 2 de tus competidores directos lanzaron promociones "
                "de 'Envío Gratis'. Se sugiere ajustar los copys de tus campañas actuales."
            )
        else:
            data["analisis_ia"] = "(No solicitaste el módulo competitivo en tus preferencias)"
            
    except Exception as e:
        logger.error(f"Error inesperado al generar los MockDatas: {e}", exc_info=True)
        raise DataProviderError(f"Error generando datos: {e}")
        
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


class InstagramDestination(NotificationDestination):
    """Ejemplo de cómo sería fácil incorporar Instagram u otra red."""
    def send(self, recipient: str, content: Dict[str, Any]) -> bool:
        ig_user = recipient.split("@")[0] # Mock para armar un username
        logger.info(f"[InstagramDestination] Enviando DM automático vía Instagram Graph API a @{ig_user}...")
        # Lógica de instabot o meta apis para enviar mensajes
        return True


class NotificationDispatcher:
    def __init__(self, destinations: List[NotificationDestination]):
        """Inyectar dependencias de los destinos evita acomplamiento rígido."""
        self.destinations = destinations

    def _should_send_now(self, frecuencia: str) -> bool:
        """
        Verifica en base a reglas de calendario (o cron intervals) si el
        usuario debe recibir el correo en este preciso momento de ejecución.
        """
        valid_frequencies = ["diaria", "semanal", "mensual"]
        if frecuencia not in valid_frequencies:
            logger.warning(f"Frecuencia '{frecuencia}' desconocida, se procederá a iterarlo como 'semanal'")
            frecuencia = "semanal"

        # ** SIMULACIÓN DE LÓGICA ** 
        # En producción revisaríamos timestamps, DB status o CRON Expressions. 
        # Lo damos por verdadero aquí para que siempre despache propósitos de la prueba:
        logger.info(f"Evaluador de Frecuencia: Confirmado para envío '{frecuencia}'.")
        return True

    def process_request(self, user_config: Dict[str, Any]) -> None:
        """
        Flujo principal Orquestador:
        1. Recibe la configuración del usuario (dict/json object).
        2. Analiza momento de envío.
        3. Recolecta data valiosa del Motor de IA.
        4. Transmite a todos los destinos configurados.
        """
        email = user_config.get("email")
        frecuencia = user_config.get("frecuencia", "semanal")
        flags = user_config.get("flags", [])

        if not email:
            logger.error("Payload Inválido: Falta la llave 'email' en la configuración del usuario.")
            return

        # 1. Determinamos si toca notificar.
        if not self._should_send_now(frecuencia):
            logger.info(f"Omision de procesamiento de {email}: No le corresponde el turno de frecuencia.")
            return

        try:
            # 2. Consultar servicios de Data
            content = fetch_mock_data(flags)
            
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
