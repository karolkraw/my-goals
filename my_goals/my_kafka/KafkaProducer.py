from confluent_kafka import Producer
import json
import os

class KafkaProducer:
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093')})  # Kafka broker URL

    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def send_message(self, topic, key, message):
        self.producer.produce(topic=topic, key=key, value=message, callback=self.delivery_report)
        self.producer.flush()  # Ensure all messages are sent
        
        
        """ def send_request(self, topic, request_payload):
        self.producer.produce(topic, key="request_goals", value=json.dumps(request_payload), callback=self.delivery_report)
        self.producer.flush()

def request_goals(user_id):
    kafka_producer = KafkaProducer()
    request_payload = {
        'request_type': 'get_goals',
        'user_id': user_id
    }
    kafka_producer.send_request('goal-request-topic', request_payload) """
        
    