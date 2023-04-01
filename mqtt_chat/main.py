import openai
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

# MQTT configuration
BROKER_ADDRESS = os.getenv("BROKER_ADDRESS")
MQTT_TOPIC_INPUT = "chat/input"
MQTT_TOPIC_OUTPUT = "chat/output"

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC_INPUT)

def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))

    user_message = msg.payload.decode("utf-8")
    assistant_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ],
    )
    response_text = assistant_response.choices[0].message["content"]
    print("Assistant: " + response_text)
    client.publish(MQTT_TOPIC_OUTPUT, response_text)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS, 1883, 60)

client.loop_forever()
