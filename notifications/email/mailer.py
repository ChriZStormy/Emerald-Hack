import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def enviar_reporte_html(destinatario, contenido_data):
    # Configuración del servidor (Ejemplo con Gmail)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "intel.pymes@gmail.com"
    SENDER_PASSWORD = "spxg dtof nscq szjh" # Contraseña de aplicación


    # Crear el mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Resumen Semanal: Inteligencia de Mercado - {contenido_data['negocio']}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = destinatario

    # Estructura HTML básica con diseño decente (Inline CSS)
    html_template = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">Reporte de Competencia</h2>
            <p>Hola, aquí tienes lo más relevante de la semana para <strong>{contenido_data['negocio']}</strong>:</p>
            
            <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #e67e22;">🔥 Tendencias en Guanajuato</h3>
                <ul>
                    {"".join([f"<li>{item}</li>" for item in contenido_data['tendencias']])}
                </ul>
            </div>

            <div style="background: #eaf2f8; padding: 15px; border-radius: 5px;">
                <h3 style="margin-top: 0; color: #2980b9;">📊 Análisis de Competencia</h3>
                <p>{contenido_data['analisis_ia']}</p>
            </div>

            <p style="font-size: 12px; color: #7f8c8d; margin-top: 30px;">
                Recibes este correo porque configuraste notificaciones semanales.
            </p>
        </div>
    </body>
    </html>
    """

    parte_html = MIMEText(html_template, 'html')
    msg.attach(parte_html)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error al enviar: {e}")
        return False