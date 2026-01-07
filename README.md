# Zigbee2mqtt
## Push notifications from sensors

## Why this project?

Needed a reliable way to monitor and get alerts based on sensors I use around the house.  
Practical, fun way to use Python to solve problems in home automation.

### Why not Home Assistant?

- Tested inside Proxmox container: difficult to pair sensors, displays duplicates, and can break after updates.
- I don't want to use a dedicated device, so that HA can work well with usb zigbee antena.

---

## Components needed for my Proxmox setup

### 1. Zigbee antenna (USB)

Already have a USB from Conbee II which works great.

Check it is recognized and available in Proxmox:

```bash
ls /dev/serial/by-id/
```

---

### 2. MQTT message broker

**What it is:**  
Central server for the Message Queuing Telemetry Transport protocol, lightweight publish-subscribe protocol designed for IoT devices with low power and bandwidth.

**Selected option:** Mosquitto  
https://mosquitto.org/

- Proxmox LXC helper:  
  https://community-scripts.github.io/ProxmoxVE/scripts?id=mqtt
- Chosen because it was available in Proxmox helpers and required fewer resources than EMQX.

**Post install steps:**  
https://github.com/community-scripts/ProxmoxVE/discussions/782

---

### 3. MQTT client

**What it is:**  
Software that enables connection to an MQTT broker.

**Selected software:** zigbee2mqtt  
https://www.zigbee2mqtt.io/

- Docker compose:  
  https://www.zigbee2mqtt.io/guide/installation/02_docker.html
- Proxmox LXC helper:  
  https://community-scripts.github.io/ProxmoxVE/scripts?id=zigbee2mqtt
- This was the only zigbee–mqtt software available in Proxmox helpers.

**Post install steps:**  
https://github.com/community-scripts/ProxmoxVE/discussions/410

---

### 4. Push notification options

- Pushover: https://pushover.net/  
- Telegram: never used  
- Email: delayed, might miss something urgent (e.g., pipe leak)

---

## Mosquitto LXC final settings

```
Container Type: Unprivileged
Container ID: 101
Hostname: mqtt

Disk: 2 GB
CPU: 1 core
RAM: 512 MiB

Bridge: vmbr0
IPv4: 192.168.2.40/24

Timezone: Europe/Bucharest
```

Access it using:  
http://192.168.2.40:1883

---

## Zigbee2mqtt LXC final settings

```
Container Type: Privileged
Container ID: 102
Hostname: zigbee2mqtt

Disk: 5 GB
CPU: 2 cores
RAM: 1024 MiB

Bridge: vmbr0
IPv4: 192.168.2.42/24

Timezone: Europe/Bucharest
```

Access it using:  
http://192.168.2.42:9442

---

## Debugging

Check logs:

```bash
journalctl -u zigbee2mqtt -n 50 --no-pager
```

Config reference:  
https://www.zigbee2mqtt.io/guide/configuration/all-settings.html#advanced

---

## Issues encountered

- Static IP not connecting to OPNsense DHCP
- SSH accidentally enabled
- Conbee II USB used in another container (Home Assistant)
- Frontend host set to `localhost` instead of `0.0.0.0`
- `permit_join` was false
- `reject_unauthorized` was true without SSL
- Wrong serial port path

---

## Final Zigbee2MQTT config

```yaml
version: 4
homeassistant:
  enabled: false
permit_join: true
frontend:
  enabled: true
  port: 9442
  host: 0.0.0.0
mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://192.168.2.40:1883
  user: youruser
  password: yourpass
  keepalive: 60
  reject_unauthorized: false
  version: 4
serial:
  port: /dev/serial/by-id/usb-dresden_elektronik_ingenieurtechnik_GmbH_ConBee_II_DE2478649-if00
  adapter: deconz
advanced:
  pan_id: GENERATE
  network_key: GENERATE
  channel: 20
```

---

## Python MQTT library

https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html

---

## Python script (MQTT client)

```python
import os
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID")

if not MQTT_HOST:
    raise RuntimeError("MQTT Host is not set")

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Connected to MQTT with result code:", reason_code)
    if reason_code == 0:
        client.subscribe("zigbee2mqtt/0xa4c13875a846a8f4")

def on_message(client, userdata, message):
    print(f"Message received: {message.topic} {message.payload!r}")

def main():
    client = mqtt.Client(
        client_id=MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv311,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    client.reconnect_delay_set(min_delay=1, max_delay=30)

    print("Connecting to MQTT...")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_forever()

if __name__ == "__main__":
    main()
```

---

## Successful log output

```
Connecting to MQTT...
Connected to MQTT with result code: Success
Message received: zigbee2mqtt/0xa4c13875a846a8f4 b'{"battery":68,"battery_low":false,"linkquality":255,"water_leak":false}'
```

---

## Mosquitto testing

Subscriber:

```bash
mosquitto_sub -h localhost -t test/topic -v
```

Publisher:

```bash
mosquitto_pub -h localhost -t test/topic -m "hello mqtt"
```

Remote test:

```bash
mosquitto_pub -h 192.168.2.XX -t test/topic -m "test from remote"
```

Logs:

```bash
tail -f /var/log/mosquitto/mosquitto.log
```

---

## TODO

- [x] Install client
- [x] Install broker
- [x] Pair sensor to zigbee2mqtt
- [x] Write script and test notification
- [ ] Containerize script
- [ ] Install push notification app and get API key
- [ ] Use script to push received message to phone
- [ ] Deploy script in Dokploy

Optional:
- Pair Home Assistant to Zigbee
