import csv
import json
import requests
import io

URL = "http://storage.googleapis.com/play_public/supported_devices.csv"

def update_devices():
    print(f"Descargando lista de dispositivos desde {URL}...")
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error al descargar: {e}")
        return

    # El CSV usa codificación UTF-16 con BOM a veces, o Latin-1. Google suele usar UTF-16
    content = response.content.decode('utf-16')
    f = io.StringIO(content)
    reader = csv.DictReader(f)

    devices = {}

    # Filtrar estrictamente por Xiaomi y Samsung (incluye Poco y Redmi)
    marcas_interes = ["Xiaomi", "Samsung", "Poco", "Redmi"]

    print("Procesando modelos...")
    for row in reader:
        brand = row.get('Retailer', '')
        marketing_name = row.get('Marketing Name', '')
        device = row.get('Device', '')
        model = row.get('Model', '')

        if not model or not marketing_name:
            continue

        # Validar que pertenezca a las marcas de interés
        if not any(m.lower() in brand.lower() or m.lower() in marketing_name.lower() for m in marcas_interes):
            continue

        # Si el modelo ya existe y tiene nombre comercial, no sobreescribir con algo genérico
        if model in devices and len(devices[model]) > len(marketing_name):
            continue

        # Guardar mapeo
        devices[model] = marketing_name

        # También mapear por 'Device' si es diferente (Xiaomi usa mucho esto)
        if device and device != model:
            devices[device] = marketing_name

    print(f"Total de modelos indexados: {len(devices)}")

    # Guardar en JSON optimizado
    with open("devices.json", "w", encoding="utf-8") as j:
        json.dump(devices, j, ensure_ascii=False, indent=2)

    print("¡Archivo devices.json generado con éxito!")

if __name__ == "__main__":
    update_devices()
