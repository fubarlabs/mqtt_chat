# Chat-Enabled MQTT System

This project demonstrates how to build a chat-enabled MQTT system using OpenAI's GPT-3.5-turbo, the Paho MQTT library, python-dotenv, and Poetry.

## Prerequisites

- Python 3.7+
- Poetry
- An MQTT broker (e.g., Mosquitto)

## Installation

1. Clone this repository:
```
git clone https://github.com/ricklon/mqtt_chat.git
cd mqtt_chat
```

2. Install dependencies using Poetry:

`poetry install


3. Create a `.env` file in the project root directory with your OpenAI API key and MQTT broker address:
```
OPENAI_API_KEY=your_openai_api_key
BROKER_ADDRESS=your_mqtt_broker_address
```

Replace `your_openai_api_key` and `your_mqtt_broker_address` with your OpenAI API key and the address of your MQTT broker.

## Usage

1. Run the chat-enabled MQTT system:

`poetry run python mqtt_chat/main.py`


2. Publish user messages to the `chat/input` topic and receive assistant responses from the `chat/output` topic using an MQTT client.

## License

This project is licensed under the [MIT License](LICENSE).
