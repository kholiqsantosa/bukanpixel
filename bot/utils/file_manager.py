import json
import os

from bot.utils import logger


def load_from_json(path: str):
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as file:
            try:
                # Coba muat data sebagai list
                return json.load(file)
            except json.JSONDecodeError:
                logger.error(f"File {path} is not a valid JSON. Resetting the file.")
                # Jika terjadi kesalahan, buat file baru
                return reset_json_file(path)
    else:
        # Jika file tidak ada, buat file baru dengan contoh
        return reset_json_file(path)


def reset_json_file(path: str):
    example = {
        "session_name": "name_example",
        "user_agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
        "proxy": "type://user:pass:ip:port"
    }
    with open(path, 'w', encoding='utf-8') as file:
        json.dump([example], file, ensure_ascii=False, indent=2)
    return [example]


def save_to_json(path: str, dict_):
    # Cek apakah file sudah ada
    if os.path.isfile(path):
        # Jika file sudah ada, muat data yang ada
        with open(path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    raise ValueError("Data in JSON file is not a list.")
            except (json.JSONDecodeError, ValueError):
                logger.error(f"File {path} is corrupted or not a valid JSON list. Resetting the file.")
                data = []  # Reset data jika tidak valid
    else:
        # Jika file tidak ada, buat list baru
        data = []

    # Tambahkan dict_ ke list data
    data.append(dict_)

    # Simpan kembali data ke dalam file
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
