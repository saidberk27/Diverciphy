import requests

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException as e:
        return f"Hata oluştu: {e}"

    print(f"Your Public IP: {get_public_ip()}")