import subprocess
import sys
import requests
import json
import uuid
import re
import shutil
from datetime import datetime, timezone


def check_python_version():
    if sys.version_info < (3, 7):
        print("Потрібен Python 3.7 або вище.")
        sys.exit(1)


def check_wireguard_installed():
    if shutil.which("wg") is None:
        print("WireGuard tools не знайдено.")
        print("Встановіть WireGuard:")
        print("  Debian/Ubuntu: sudo apt install wireguard")
        print("  Void Linux:    sudo xbps-install -S wireguard-tools")
        print("  Windows:       https://www.wireguard.com/install/")
        sys.exit(1)


def generate_keys():
    try:
        privkey = subprocess.check_output(
            ["wg", "genkey"], stderr=subprocess.STDOUT
        ).strip().decode()
        pubkey = subprocess.run(
            ["wg", "pubkey"],
            input=privkey.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.strip().decode()
        return privkey, pubkey
    except subprocess.CalledProcessError as e:
        print(f"Помилка генерації ключів: {e.output.decode()}")
        sys.exit(1)
    except FileNotFoundError:
        print("Команда 'wg' не знайдена. Встановіть WireGuard tools.")
        sys.exit(1)


def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r"\.\.", "_", name)
    name = name.strip(". ")
    if not name:
        name = "warp"
    return name


def register_warp(pubkey):
    install_id = str(uuid.uuid4())
    data = {
        "key": pubkey,
        "install_id": install_id,
        "fcm_token": "",
        "tos": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "type": "Android",
        "locale": "en_US",
    }
    headers = {"Content-Type": "application/json"}

    urls = [
        "https://api.cloudflareclient.com/v0a2158/reg",
        "https://api.cloudflareclient.com/v0d2208/reg",
    ]

    for url in urls:
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"API {url} повернув {resp.status_code}")
        except requests.exceptions.Timeout:
            print(f"Таймаут з'єднання з {url}")
        except requests.exceptions.ConnectionError:
            print(f"Не вдалося підключитися до {url}")
        except requests.exceptions.SSLError as e:
            print(f"SSL помилка: {e}")

    print("Не вдалося зареєструватися в Cloudflare Warp.")
    print("Перевірте інтернет-з'єднання або спробуйте пізніше.")
    return None


def fix_endpoint(endpoint_v4):
    parts = endpoint_v4.split(":")
    if len(parts) == 3 and parts[1] == "0":
        return f"{parts[0]}:{parts[2]}"
    return endpoint_v4


def create_conf_file(data, privkey, filename):
    try:
        interface = data["config"]["interface"]
        peers = data["config"]["peers"][0]
    except (KeyError, IndexError) as e:
        print(f"Неочікувана структура відповіді API: {e}")
        print("Повна відповідь:")
        print(json.dumps(data, indent=2))
        return

    endpoint_v4 = peers["endpoint"]["v4"]
    endpoint_v4 = fix_endpoint(endpoint_v4)
    port = peers.get("endpoint", {}).get("v4_port", 2408)

    conf = f"""[Interface]
PrivateKey = {privkey}
Address = {interface['addresses']['v4']}/32,{interface['addresses']['v6']}/128
DNS = 1.1.1.1

[Peer]
PublicKey = {peers['public_key']}
Endpoint = {endpoint_v4}:{port}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""
    with open(filename, "w") as f:
        f.write(conf)
    print(f"Конфігурацію збережено в {filename}")


def main():
    check_python_version()
    check_wireguard_installed()

    print("=== Warp WireGuard Config Generator ===\n")

    print("Генеруємо ключі WireGuard...")
    privkey, pubkey = generate_keys()

    print("Реєстрація в Cloudflare Warp...")
    data = register_warp(pubkey)

    if data:
        name = input(
            "Введіть ім'я для конфігурації (наприклад, phone або pc): "
        ).strip()
        name = sanitize_filename(name)
        filename = f"warp_{name}.conf"
        create_conf_file(data, privkey, filename)
    else:
        print("Помилка: не вдалося отримати конфігурацію.")
        sys.exit(1)


if __name__ == "__main__":
    main()
