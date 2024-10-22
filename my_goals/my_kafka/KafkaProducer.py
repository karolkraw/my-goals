import json
from confluent_kafka import Producer
import os

class KafkaProducer:
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')})  # Kafka broker URL

    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def send_message(self, topic, message):
        message_json = json.dumps(message)
        self.producer.produce(topic=topic, value=message_json, callback=self.delivery_report)
        self.producer.flush()
        
        
    