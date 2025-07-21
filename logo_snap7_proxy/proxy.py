import snap7
import paho.mqtt.client as mqtt
import time

LOGO_IP = "192.168.0.250"
MQTT_BROKER = "homeassistant.local"
MQTT_PORT = 1883

OUTPUTS = {
    'Q1': (0, 0),
    'Q2': (0, 1),
    'Q3': (0, 2),
    'Q4': (0, 3),
    'Q5': (0, 4),
    'Q6': (0, 5),
    'Q7': (0, 6),
    'Q8': (0, 7),
    'Q9': (1, 0)
}

client = snap7.client.Client()
client.connect(LOGO_IP, 0, 1)

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("MQTT verbunden mit Code " + str(rc))
    for output in OUTPUTS:
        topic = f"logo/set/{output}"
        mqtt_client.subscribe(topic)

def on_message(client, userdata, msg):
    output = msg.topic.split('/')[-1]
    payload = msg.payload.decode().lower()
    if output in OUTPUTS:
        byte_idx, bit = OUTPUTS[output]
        current_bytes = client.read_area(snap7.types.Areas.PA, 0, 0, 2)
        current_state = list(current_bytes)
        if payload == 'on':
            current_state[byte_idx] |= (1 << bit)
        elif payload == 'off':
            current_state[byte_idx] &= ~(1 << bit)
        else:
            print(f"Ungültiger Befehl: {payload}")
            return
        client.write_area(snap7.types.Areas.PA, 0, 0, bytes(current_state))
        print(f"Setze {output} auf {payload}")

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("LOGO MQTT Proxy läuft...")

try:
    while True:
        state = client.read_area(snap7.types.Areas.PA, 0, 0, 2)
        for output, (byte_idx, bit) in OUTPUTS.items():
            status = 'ON' if state[byte_idx] & (1 << bit) else 'OFF'
            mqtt_client.publish(f"logo/status/{output}", status, retain=True)
        mqtt_client.loop(timeout=1.0)
        time.sleep(5)
except KeyboardInterrupt:
    print("Beendet")
finally:
    client.disconnect()
    mqtt_client.disconnect()
