# Warp WireGuard Config Generator

Генератор конфігураційних файлів для Cloudflare Warp VPN.

## Вимоги

- Python 3.7+
- WireGuard tools (`wg`, `wg-quick`)
- Інтернет-з'єднання

### Встановлення WireGuard

```bash
# Debian/Ubuntu
sudo apt install wireguard

# Void Linux
sudo xbps-install -S wireguard-tools

# Windows
# Завантажити з https://www.wireguard.com/install/
```

## Встановлення залежностей

```bash
pip install -r requirements.txt
```

## Використання

```bash
python generatewrp.py
```

Скрипт попросить ввести ім'я для конфігурації (наприклад, `phone` або `pc`).

Файл буде збережено як `warp_<ім'я>.conf`.

## Запуск VPN

### Linux

```bash
sudo wg-quick up ./warp_phone.conf    # Увімкнути
sudo wg-quick down ./warp_phone.conf  # Вимкнути
```

### Windows

1. Відкрийте WireGuard
2. Натисніть "Add Tunnel" -> "Add empty tunnel..."
3. Вставте вміст `.conf` файлу
4. Натисніть "Activate"

### macOS

```bash
brew install --cask wireguard
```

Імпортуйте конфіг та натисніть "Activate".

## Можливі проблеми

- Якщо API Cloudflare не відповідає — перевірте інтернет-з'єднання
- Якщо `wg` не знайдено — встановіть WireGuard tools
- Endpoint автоматично виправляється (якщо API повертає формат `x.x.x.x:0:2408`)
