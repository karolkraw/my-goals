import os
import time
import json
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from my_goals.models import Goal

class KafkaConsumer:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'group.id': 'retrieved-goals-group',
            'auto.offset.reset': 'earliest',
        })
        
        self.admin_client = AdminClient({'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')})
        self.topic = 'retrieved-goals-topic'
        self.check_and_create_topic()
        
    def check_and_create_topic(self):
        try:
            metadata = self.admin_client.list_topics(timeout=10)
            topics = metadata.topics
            
            if self.topic not in topics:
                print(f"Topic '{self.topic}' does not exist. Creating...")
                new_topic = NewTopic(topic=self.topic, num_partitions=1, replication_factor=1)
                self.admin_client.create_topics([new_topic])
                print(f"Topic '{self.topic}' created successfully.")
            else:
                print(f"Topic '{self.topic}' already exists.")
        except Exception as e:
            print(f"Error in checking/creating topic: {e}")
            raise
   
    def consume_messages(self):
        self.consumer.subscribe([self.topic])

        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Error in message: {msg.error()}")
                        continue

                message_value = msg.value().decode('utf-8')
                print(f"Received message: {message_value}")
                return self.process_message(message_value)

        finally:
            self.consumer.close()

    def process_message(self, message):
        try:
            goals_data = json.loads(message)
            goals = []

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

            return goals

        except json.JSONDecodeError as e:
            print(f"Failed to decode message: {e}")
        except Exception as e:
            print(f"Error processing message: {e}")
