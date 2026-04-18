import requests
import json

def test_facebook_post():
    # Page Token extraido programmaticamente del endpoint /me/accounts
    page_token = "EAAUZBsFTA8vsBRHOmoKGAgbCxedAFjvh60WW0PKtTQLQ10pDha85I49s8W7aLcBpixcsmdNQ2luntpcSNG62pdnNo8GYLd6YGlybgZCF4FrMRshZAYw3DiEr42XP2ufdG3r32jAUOzZCVHkuzBWjIvs35MWH8kHu4NpiLHPRoMS7aQX20fQXbEl0ziBI9Hy2JibWYYVZBxaAvyDspbUQP4O5HQHOdp4XWPBY436sZD"
    api_version = "v25.0"
    page_id = "1028910470313878"
    url = f"https://graph.facebook.com/{api_version}/{page_id}/feed"
    
    print("Iniciando prueba de publicacion generica a la pagina de Facebook Intel Pymes...")

    payload = {
        "message": "¡Hola mundo desde nuestro script de prueba Hackathon! 🌟\n\nEste es un mensaje genérico generado para verificar la integración con la Graph API de Meta (v25.0).\n\n#IntelPymes #PruebaIntegracion",
        "access_token": page_token
    }

    try:
        response = requests.post(url, data=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Exito! Post creado exitosamente.")
            print(f"Post ID: {data.get('id')}")
        else:
            print(f"Falla en la peticion a la API. Codigo de estado: {response.status_code}")
            print(f" Detalles del error: {json.dumps(response.json(), indent=2)}")
            
    except requests.exceptions.RequestException as e:
        print(f"Advertencia: Ocurrio una excepcion durante la conexion a Facebook: {e}")

if __name__ == "__main__":
    test_facebook_post()
