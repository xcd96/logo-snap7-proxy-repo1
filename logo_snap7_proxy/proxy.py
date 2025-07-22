import snap7
import paho.mqtt.client as mqtt

LOGO_IP = "192.168.0.250"
MQTT_BROKER = "192.168.0.11"
LOGO_PORT = 102

client = snap7.client.Client()

try:
    client.connect(LOGO_IP, 0, 1)
    print("✅ Proxy gestartet und mit LOGO! verbunden")
except Exception as e:
    print(f"❌ Fehler bei Verbindung zur LOGO!: {e}")

def set_output(q_num, value):
    try:
        byte_index = (q_num - 1) // 8
        bit_index = (q_num - 1) % 8
        data = bytearray(client.read_area(snap7.types.Areas.PA, 0, byte_index, 1))
        if value:
            data[0] |= (1 << bit_index)
        else:
            data[0] &= ~(1 << bit_index)
        client.write_area(snap7.types.Areas.PA, 0, byte_index, data)
        print(f"✅ Ausgang Q{q_num} auf {value} gesetzt")
    except Exception as e:
        print(f"❌ Fehler beim Setzen von Q{q_num}: {e}")

def on_connect(client_mqtt, userdata, flags, rc):
    if rc == 0:
        print("✅ Verbindung zum MQTT-Broker erfolgreich")
        client_mqtt.subscribe("logo/+/set")
    else:
        print(f"❌ MQTT Connect Fehler: {rc}")

def on_message(client_mqtt, userdata, msg):
    print(f"📩 MQTT Nachricht: {msg.topic} => {msg.payload}")
    try:
        if msg.topic.startswith("logo/") and msg.topic.endswith("/set"):
            q_str = msg.topic.split("/")[1]
            if q_str.startswith("q"):
                q_num = int(q_str[1:])
                if 1 <= q_num <= 9:
                    value = int(msg.payload)
                    set_output(q_num, value)
    except Exception as e:
        print(f"❌ Fehler beim Verarbeiten: {e}")

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set("logo_proxy", "supergeheim")  # 🔔 DAS IST DER FEHLENDE TEIL!
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER)
except Exception as e:
    print(f"❌ Fehler bei MQTT-Verbindung: {e}")

mqtt_client.loop_forever()
