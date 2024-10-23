import random
import json
import os

# Daftar 15 tipe HP Xiaomi
xiao_devices = [
    'Xiaomi 14T', 'Xiaomi 14T Pro', 'Xiaomi 14',
    'Xiaomi 13T', 'Redmi Note 13 5G', 'Redmi Note 13',
    'Redmi K20', 'Redmi K30', 'Xiaomi Poco X6 Pro',
    'Redmi Note 12', 'Xiaomi Poco X3 NFC',
    'Xiaomi Mi Mix 4', 'Xiaomi Mi A3', 'Xiaomi Mi A2',
    'Xiaomi Mi 8', 'Redmi 9', 'Xiaomi Mi 10T'
]

# Pastikan tidak ada spasi ganda di antara kata-kata
xiao_devices = [device.replace("  ", " ") for device in xiao_devices]

# Nama file JSON untuk menyimpan device_model berdasarkan session
DEVICE_MODEL_FILE = 'device_models.json'

def load_device_models() -> dict:
    """Memuat semua device model dari file JSON."""
    if os.path.exists(DEVICE_MODEL_FILE):
        with open(DEVICE_MODEL_FILE, 'r') as file:
            return json.load(file)
    return {}

def load_device_model(session_name: str) -> str:
    """Memuat device model dari file JSON untuk session tertentu."""
    device_models = load_device_models()
    return device_models.get(session_name, None)

def save_device_models(device_models: dict) -> None:
    """Menyimpan semua device models ke dalam file JSON."""
    with open(DEVICE_MODEL_FILE, 'w') as file:
        json.dump(device_models, file)

def save_device_model(session_name: str, device_model: str) -> None:
    """Menyimpan device model untuk session tertentu ke dalam file JSON."""
    device_models = load_device_models()  # Memuat semua device models
    device_models[session_name] = device_model  # Perbarui atau tambahkan
    save_device_models(device_models)  # Simpan kembali

def get_random_android_device(session_name: str) -> str:
    """Mengambil model perangkat Android berdasarkan session_name."""
    device_model = load_device_model(session_name)
    if device_model is None:
        # Pilih device model secara acak dan simpan
        device_model = random.choice(xiao_devices).strip()
        save_device_model(session_name, device_model)  # Simpan ke JSON
    return device_model

def generate_random_user_agent(device_type='android', browser_type='chrome', device_model=None):
    chrome_versions = list(range(110, 127))
    firefox_versions = list(range(90, 100))

    if browser_type == 'chrome':
        major_version = random.choice(chrome_versions)
        minor_version = random.randint(0, 9)
        build_version = random.randint(1000, 9999)
        patch_version = random.randint(0, 99)
        browser_version = f"{major_version}.{minor_version}.{build_version}.{patch_version}"
    elif browser_type == 'firefox':
        browser_version = random.choice(firefox_versions)

    if device_type == 'android':
        android_versions = ['13.0', '13.0', '13.0', '13.0']
        if browser_type == 'chrome':
            return (f"Mozilla/5.0 (Linux; Android {random.choice(android_versions)}; {device_model}) "
                    f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Mobile Safari/537.36")
        elif browser_type == 'firefox':
            return (f"Mozilla/5.0 (Android {random.choice(android_versions)}; Mobile; rv:{browser_version}.0) "
                    f"Gecko/{browser_version}.0 Firefox/{browser_version}.0")

    return None

