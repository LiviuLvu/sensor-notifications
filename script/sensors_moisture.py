import os
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID') # python-sensors

if not MQTT_HOST:
    raise RuntimeError('🚨 MQTT Host is not set')

# The callback called when the client responds to connection request
def on_connect(client, userdata, flags, reason_code, properties=None):
    print('Connected to MQTT with result code:', reason_code)
    if reason_code == 0:
          # change to a specific topic
        client.subscribe('zigbee2mqtt/0xa4c13875a846a8f4')

# Callback called when a message has been received on a topic that the client subscribes to
def on_message(client, userdata, message):
    print(f'Message received: {message.topic} {message.payload!r}')

def on_connect_fail(client, userdata, properties=None):
    print('Connection failed')
    print('Client ID:', client.callback_api_version)

def main():
    client = mqtt.Client(
        client_id=MQTT_CLIENT_ID,
        protocol=mqtt.MQTTv311,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail
    client.on_message = on_message

    # Let Paho handle reconnects
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    print('Connecting to MQTT...')
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)

     # Blocks forever, auto-reconnects internally
    client.loop_forever()

# Only run main if script is executed directly, not when imported
if __name__ == '__main__':
    main()