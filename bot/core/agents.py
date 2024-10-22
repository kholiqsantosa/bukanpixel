import random

# Daftar 15 tipe HP Xiaomi
xiao_devices = [
    'Xiaomi Mi 9', 'Xiaomi Mi 10', 'Xiaomi Mi 11',
    'Redmi Note 8', 'Redmi Note 9', 'Redmi Note 13',
    'Redmi K20', 'Redmi K30', 'Xiaomi Poco X6 Pro',
    'Xiaomi Poco F1', 'Xiaomi Poco X3 NFC',
    'Xiaomi Mi Mix 4', 'Xiaomi Mi A3', 'Xiaomi Mi A2',
    'Xiaomi Mi 8', 'Redmi 9', 'Xiaomi Mi 10T'
]

def get_random_android_device() -> str:
    """Mengambil model perangkat Android secara acak dari daftar Xiaomi."""
    return random.choice(xiao_devices)

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
