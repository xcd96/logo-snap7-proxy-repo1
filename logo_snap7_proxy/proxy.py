import snap7
import paho.mqtt.client as mqtt

LOGO_IP = "192.168.0.250"
MQTT_BROKER = "192.168.0.11"

print("Starte Proxy...")

try:
    client = snap7.client.Client()
    client.connect(LOGO_IP, 0, 1)
    print("✅ Verbindung zur LOGO! erfolgreich")
except Exception as e:
    print(f"❌ Fehler bei Verbindung zur LOGO!: {e}")

def set_output(q_num, value):
    byte_index = (q_num - 1) // 8
    bit_index = (q_num - 1) % 8
    try:
        data = bytearray(client.read_area(snap7.types.Areas.PA, 0, byte_index, 1))
        if value:
            data[0] |= (1 << bit_index)
        else:
            data[0] &= ~(1 << bit_index)
        client.write_area(snap7.types.Areas.PA, 0, byte_index, data)
        print(f"✅ Ausgang Q{q_num} gesetzt auf {value}")
    except Exception as e:
        print(f"❌ Fehler beim Setzen von Q{q_num}: {e}")

def on_message(client_mqtt, userdata, msg):
    print(f"MQTT empfangen: {msg.topic} => {msg.payload}")
    try:
        if msg.topic.startswith("logo/q") and msg.topic.endswith("/set"):
            q_num = int(msg.topic.split("/")[1][1:])
            if 1 <= q_num <= 9:
                value = int(msg.payload)
                set_output(q_num, value)
    except Exception as e:
        print(f"❌ Fehler bei Verarbeitung von MQTT: {e}")

try:
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER)
    print("✅ Verbindung zum MQTT-Broker erfolgreich")
    mqtt_client.subscribe("logo/q+/set")
    mqtt_client.loop_forever()
except Exception as e:
    print(f"❌ Fehler beim Start von MQTT-Client: {e}")
