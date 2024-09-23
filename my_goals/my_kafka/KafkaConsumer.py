import os
import json
import time
from confluent_kafka import Consumer, KafkaError
from my_goals.models import Goal

class KafkaConsumer:
    def __init__(self, max_retries=5, retry_delay=5):
        """
        Initializes the Kafka consumer with retries and subscription to the topic.
        """
        self.consumer_config = {
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'group.id': 'retrieved-goals-group',
            'session.timeout.ms': 45000,  # 45 seconds
            'heartbeat.interval.ms': 10000,  # 10 seconds
            'auto.offset.reset': 'earliest',  # Start from the earliest if no committed offset is found
            'enable.auto.commit': True,

        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.topic = 'retrieved-goals-topic'
        self.create_consumer()

    def create_consumer(self):
        """
        Create the Kafka consumer and subscribe to the topic with retry logic.
        """
        retries = 0
        print("CREATE CONSUMER")
        while retries < self.max_retries:
            try:
                self.consumer = Consumer(self.consumer_config)
                self.consumer.subscribe([self.topic])
                print(f"Successfully subscribed to topic: {self.topic}")
                return
            except KafkaError as e:
                print(f"Error subscribing to topic: {e}")
                retries += 1
                print(f"Retrying ({retries}/{self.max_retries}) in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        raise Exception(f"Failed to subscribe to topic '{self.topic}' after {self.max_retries} attempts")

    def consume_messages(self):
        """
        Continuously poll and consume messages from the Kafka topic.
        """
        try:
            while True:
                print("berofe polling")
                msg = self.consumer.poll(timeout=5.0)
                print("after polling")
                if msg is None:
                    print("msg is none")
                    # No message available to process at this moment
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition reached, continue to next message
                        continue
                    else:
                        print(f"Error in message: {msg.error()}")
                        continue

                # Process the valid message
                message_value = msg.value().decode('utf-8')
                print(f"Received message: {message_value}")
                return self.process_message(message_value)

        except KeyboardInterrupt:
            print("Consumer interrupted by user.")
        finally:
            self.consumer.close()

    def process_message(self, message):
        """
        Processes the incoming message and constructs in-memory Goal objects.
        """
        try:
            print("PROCESSING A MESSAGE")
            goals_data = json.loads(message)  # Parse the JSON message
            goals = []  # List to store parsed Goal objects

            for goal_data in goals_data:
                goal = {
                    'title': goal_data['title'],
                    'description': goal_data['description'],
                    'created_date': goal_data['createdDate'],
                    'completed_date': goal_data['completedDate'],
                    'section_name': goal_data.get('section_name', ''),
                    'subtasks': []
                }
                print(f"Goal created: {goal['title']}")

                for subtask_data in goal_data.get('subtasks', []):
                    subtask = {
                        'title': subtask_data['title'],
                        'description': subtask_data['description'],
                        'completed': subtask_data.get('completed', False),
                        'created_date': subtask_data['createdDate'],
                        'completed_date': subtask_data.get('completedDate', None),
                        'deadline': subtask_data.get('deadline', None),
                    }
                    goal['subtasks'].append(subtask)
                    print(f"Subtask created: {subtask['title']} for Goal: {goal['title']}")

                goals.append(goal)

            print("Parsed goals: ", goals)  # You can replace this with saving to DB logic if needed
            return goals

        except json.JSONDecodeError as e:
            print(f"Failed to decode message: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")

# Usage example
if __name__ == "__main__":
    kafka_consumer = KafkaConsumer()
    kafka_consumer.consume_messages()
