from celery import shared_task
from .my_kafka.KafkaProducer import KafkaProducer
from .my_kafka.KafkaConsumer import KafkaConsumer
import redis
import os
import json


# Configure Redis
r = redis.StrictRedis(host=os.getenv('REDIS', 'localhost'), port=6379, db=0)


@shared_task
def retrieve_goal_history(sectionName):
    print("CCCCCCCCCCCCCCCCCC")
    producer = KafkaProducer()
    consumer = KafkaConsumer()
    
    producer.send_message('history-topic', 'history', sectionName)

    # Consume Kafka response (this method should return data)
    response_data = consumer.consume_messages()
    print("FFFFFFFFFFFFFFFFF: " + str(response_data))
    serialized_data = json.dumps(response_data)

    # Store result in Redis
    r.set(f"goal_history_{sectionName}", serialized_data)

    return serialized_data