from pyrogram import Client
from bot.config import settings
from bot.core.agents import generate_random_user_agent, get_random_android_device
from bot.utils import logger
from bot.utils.file_manager import save_to_json


async def register_sessions() -> None:
    API_ID = settings.API_ID
    API_HASH = settings.API_HASH

    if not API_ID or not API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    session_name = input('\nEnter the session name (press Enter to exit): ')

    if not session_name:
        return None

    # Ambil input proxy dari pengguna
    raw_proxy = input("Input the proxy in the format type://user:pass:ip:port (press Enter to use without proxy): ")
    device_model = get_random_android_device(session_name)  # Ambil device model secara konsisten untuk session ini

    # Tambahkan app_version dan system_version di sini
    app_version = "11.2.2"  # Versi aplikasi yang ingin digunakan
    system_version = "Android 13.0"  # Versi sistem operasi
    
    session = await get_tg_client(
        session_name=session_name,
        proxy=raw_proxy,
        device_model=device_model,
        app_version=app_version,
        system_version=system_version
    )
    
    async with session:
        user_data = await session.get_me()

    user_agent = generate_random_user_agent(device_type='android', browser_type='chrome', device_model=device_model)
    
    # Simpan semua data ke dalam JSON
    save_to_json(f'sessions/accounts.json',
                 dict_={
                    "session_name": session_name,
                    "user_agent": user_agent,
                    "device_model": device_model,  # Menyimpan device model
                    "proxy": raw_proxy if raw_proxy else None
                 })
    logger.success(f'Session added successfully @{user_data.username} | {user_data.first_name} {user_data.last_name}')


async def get_tg_client(session_name: str, proxy: str | None, device_model: str, app_version: str, system_version: str) -> Client:
    if not session_name:
        raise FileNotFoundError(f"Not found session {session_name}")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    proxy_dict = {
        "scheme": proxy.split(":")[0],
        "username": proxy.split(":")[1].split("//")[1],
        "password": proxy.split(":")[2],
        "hostname": proxy.split(":")[3],
        "port": int(proxy.split(":")[4])
    } if proxy else None

    tg_client = Client(
        name=session_name,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        workdir="sessions/",
        device_model=device_model,
        system_version=system_version,  # Gunakan versi sistem operasi yang diteruskan
        app_version=app_version,  # Gunakan versi aplikasi yang diteruskan
        plugins=dict(root="bot/plugins"),
        proxy=proxy_dict
    )

    return tg_client
