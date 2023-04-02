import openai
import os
import paho.mqtt.client as mqtt
import re

from dotenv import load_dotenv

load_dotenv()

# MQTT configuration
BROKER_ADDRESS = os.getenv("BROKER_ADDRESS")
MQTT_TOPIC_INPUT = "chat/input"
MQTT_TOPIC_OUTPUT = "chat/output"
MQTT_TOPIC_BOTS = "bots"
MQTT_TOPIC_NEWBOT = "chat/input/newbot"
MQTT_TOPIC_UPDATEBOT = "chat/input/updatebot"
MQTT_TOPIC_DELETEBOT = "chat/input/deletebot"
MQTT_TOPIC_GETBOT = "chat/input/getbot"

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Dictionary to store bot information
bots = {}

def register_bot(client, bot_name, system_content):
    bots[bot_name] = {"system_content": system_content}
    client.publish(MQTT_TOPIC_BOTS, f"New bot registered: {bot_name}")

def update_bot(client, bot_name, system_content):
    if bot_name in bots:
        bots[bot_name]["system_content"] = system_content
        client.publish(MQTT_TOPIC_BOTS, f"Bot '{bot_name}' updated")
    else:
        client.publish(MQTT_TOPIC_OUTPUT, f"Bot '{bot_name}' not found")

def delete_bot(client, bot_name):
    if bot_name in bots:
        del bots[bot_name]
        client.publish(MQTT_TOPIC_BOTS, f"Bot '{bot_name}' deleted")
    else:
        client.publish(MQTT_TOPIC_OUTPUT, f"Bot '{bot_name}' not found")

def get_bot(client, bot_name):
    if bot_name in bots:
        bot_info = bots[bot_name]
        client.publish(MQTT_TOPIC_OUTPUT, f"Bot '{bot_name}': {bot_info}")
    else:
        client.publish(MQTT_TOPIC_OUTPUT, f"Bot '{bot_name}' not found")

def handle_chat_input(client, bot_name, user_message):
    if bot_name in bots:
        system_content = bots[bot_name]["system_content"]
        assistant_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_message},
            ],
        )
        response_text = assistant_response.choices[0].message["content"]
        print("Assistant: " + response_text)
        client.publish(MQTT_TOPIC_OUTPUT, response_text)
    else:
        client.publish(MQTT_TOPIC_OUTPUT, f"Bot '{bot_name}' not found")

def generate_mqtt_subscription_pattern(user_message):
    assistant_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that helps users create MQTT topic subscriptions based on their natural language input. Only respond with the part between the ' '"},
            {"role": "user", "content": user_message},
        ],
    )
    response_text = assistant_response.choices[0].message["content"]
    return response_text.strip()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC_INPUT)
    client.subscribe(MQTT_TOPIC_BOTS)
    client.subscribe(MQTT_TOPIC_NEWBOT)
    client.subscribe(MQTT_TOPIC_UPDATEBOT)
    client.subscribe(MQTT_TOPIC_DELETEBOT)
    client.subscribe(MQTT_TOPIC_GETBOT)

def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " " + str(msg.payload))

    if msg.topic == MQTT_TOPIC_INPUT:
        payload = msg.payload.decode("utf-8").split('|')
        bot_name = payload[0]
        user_message = payload[1]
        handle_chat_input(client, bot_name, user_message)
    elif msg.topic == MQTT_TOPIC_BOTS:
        bot_name = msg.payload.decode("utf-8")
        register_bot(client, bot_name, "You are a helpful assistant.")
    elif msg.topic == MQTT_TOPIC_NEWBOT:
        bot_info = msg.payload.decode("utf-8").split('|')
        bot_name = bot_info[0]
        system_content = bot_info[1]
        register_bot(client, bot_name, system_content)
    elif msg.topic == MQTT_TOPIC_UPDATEBOT:
        bot_info = msg.payload.decode("utf-8").split('|')
        bot_name = bot_info[0]
        system_content = bot_info[1]
        update_bot(client, bot_name, system_content)
    elif msg.topic == MQTT_TOPIC_DELETEBOT:
        bot_name = msg.payload.decode("utf-8")
        delete_bot(client, bot_name)
    elif msg.topic == MQTT_TOPIC_GETBOT:
        bot_name = msg.payload.decode("utf-8")
        get_bot(client, bot_name)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS, 1883, 60)

client.loop_forever()