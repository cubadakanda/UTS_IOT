
import paho.mqtt.client as mqtt
import json
import mysql.connector
from datetime import datetime
import time


try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="iot_db"
    )
    cursor = db.cursor()
    print("✅ (SUBS) Berhasil terhubung ke database MySQL 'iot_db'")
except mysql.connector.Error as err:
    print(f"❌ (SUBS) Gagal terhubung ke MySQL: {err}")
    exit(1)

# --- Logika MQTT ---
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("✅ (SUBS) Terhubung ke broker MQTT!")
        client.subscribe("Sensor_Iot")
        print("Subscribed ke topik 'Sensor_Iot'")
    else:
        print(f"❌ (SUBS) Gagal terhubung ke broker, kode: {reason_code}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        suhu = float(data.get("suhu", 0))
        humidity = float(data.get("humidity", 0))
        lux = float(data.get("lux", 0))
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = "INSERT INTO data_sensor (suhu, humidity, lux, timestamp) VALUES (%s, %s, %s, %s)"
        val = (suhu, humidity, lux, ts)
        
        cursor.execute(sql, val)
        db.commit()

        print(f"(SUBS) Disimpan ke DB: suhu={suhu}, humidity={humidity}, lux={lux}")
    
    except Exception as e:
        print(f"(SUBS) Error parsing atau menyimpan data: {e}")

# --- Inisialisasi MQTT Client ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "PythonSubscriber_uts")
client.on_connect = on_connect
client.on_message = on_message

print("(SUBS) Menghubungkan ke broker...")
client.connect("broker.hivemq.com", 1883, 60) 

print("(SUBS) Menjalankan listener MQTT...")
client.loop_forever()