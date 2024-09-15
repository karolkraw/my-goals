from confluent_kafka import Producer
import json

class KafkaProducer:
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': 'localhost:9092'})  # Kafka broker URL

    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def send_message(self, topic, message):
        self.producer.produce(topic, key="task_completed", value=json.dumps(message), callback=self.delivery_report)
        self.producer.flush()  # Ensure all messages are sent