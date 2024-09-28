import os
import time
import json
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
from my_goals.models import Goal

class KafkaConsumer:
    def __init__(self):
        
        
        #self.admin_client = AdminClient(self.consumer_config)
        self.admin_client = AdminClient({'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')})
        self.topic = 'retrieved-goals-topic'

        self.check_and_create_topic()
        
        self.consumer = Consumer({
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'group.id': 'test_group',
            #'group.id': 'retrieved-goals-group',
            'auto.offset.reset': 'earliest',
            #'enable.auto.commit': True,
        })
        #self.consumer.subscribe([self.topic])
              
        
    def check_and_create_topic(self):
        """
        Check if the topic exists and create it if it doesn't.
        """
        try:
            # List existing topics
            metadata = self.admin_client.list_topics(timeout=10)
            topics = metadata.topics  # Get the topics from the metadata
            
            if self.topic not in topics:
                print(f"Topic '{self.topic}' does not exist. Creating...")
                # Use 'topic' instead of 'name' as the first argument
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

        """
        Continuously poll and consume messages from the Kafka topic.
        """
        try:
            while True:
                print("berofe polling")
                msg = self.consumer.poll(1.0)
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
