import subprocess
import requests
import json
import uuid
from datetime import datetime

def generate_keys():
    privkey = subprocess.check_output(['wg', 'genkey']).strip().decode()
    pubkey = subprocess.run(['wg', 'pubkey'], input=privkey.encode(), stdout=subprocess.PIPE).stdout.strip().decode()
    return privkey, pubkey

def register_warp(pubkey):
    install_id = str(uuid.uuid4())
    data = {
        "key": pubkey,
        "install_id": install_id,
        "fcm_token": "",
        "tos": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "type": "Android",
        "locale": "en_US"
    }
    headers = {"Content-Type": "application/json"}

    url = "https://api.cloudflareclient.com/v0a2158/reg"
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        return resp.json()
    else:
        print("Ошибка регистрации:", resp.status_code, resp.text)
        return None

def create_conf_file(data, privkey, filename):
    interface = data['config']['interface']
    peers = data['config']['peers'][0]

    conf = f"""[Interface]
PrivateKey = {privkey}
Address = {interface['addresses']['v4']}/32,{interface['addresses']['v6']}/128
DNS = 1.1.1.1

[Peer]
PublicKey = {peers['public_key']}
Endpoint = {peers['endpoint']['v4']}:2408
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""
    with open(filename, "w") as f:
        f.write(conf)
    print(f"Конфигурация сохранена в {filename}")

def main():
    print("Генерируем ключи WireGuard...")
    privkey, pubkey = generate_keys()
    print("Регистрация в Cloudflare Warp...")
    data = register_warp(pubkey)
    if data:
        name = input("Введите имя для конфигурации (например, phone или pc): ").strip()
        filename = f"warp_{name}.conf"
        create_conf_file(data, privkey, filename)

if __name__ == "__main__":
    main()

