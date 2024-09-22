from confluent_kafka import Consumer, KafkaError
import json
from my_goals.models import Goal 
import os

class KafkaConsumer:
    def __init__(self):
        self.consumer = Consumer({
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
            'group.id': 'goal-consumer-group',  # Consumer group ID
            'auto.offset.reset': 'earliest',  # Start reading from the beginning
            'session.timeout.ms': 30000,
            'heartbeat.interval.ms': 3000,
        })
        self.consumer.subscribe(['retrieved-goals-topic'])  # Subscribe to the topic

    def consume_messages(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    print("rrrrrrNone: ")
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print("errorrrrr: ")
                        # End of partition event
                        continue
                    else:
                        print(f'Error: {msg.error()}')
                        continue

                message = msg.value().decode('utf-8')  # Decode the Kafka message
                print(f"Received message: {message}")
                # Process the message
                return self.process_message(message)

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def process_message(self, message):
        print("Received message: " + message)
        goals_data = json.loads(message)  # Load the JSON as a list of dictionaries
    
        goals = []  # List to hold the goal instances (not saved to the database)

        for goal_data in goals_data:  # Iterate through each goal
            # Create a Goal instance in memory
            goal = {
                'title': goal_data['title'],
                'description': goal_data['description'],
                'created_date': goal_data['createdDate'],
                'completed_date': goal_data['completedDate'],
                'section_name': goal_data.get('section_name', ''),
                'subtasks': []  # List to hold subtasks
            }
            print(f'Goal created: {goal["title"]}')

            # Iterate through the subtasks and create SubTask instances in memory
            for subtask_data in goal_data.get('subtasks', []):  # Safely get subtasks
                subtask = {
                    'title': subtask_data['title'],
                    'description': subtask_data['description'],
                    'completed': subtask_data.get('completed', False),
                    'created_date': subtask_data['createdDate'],
                    'completed_date': subtask_data.get('completedDate', None),
                    'deadline': subtask_data.get('deadline', None)
                }
                goal['subtasks'].append(subtask)  # Add subtask to the goal's subtasks
                print(f'Subtask created: {subtask["title"]} for Goal: {goal["title"]}')

            goals.append(goal)  # Add goal to the goals list

        # You can now use the goals list as needed
        print(goals)  # Example: print the in-memory structure
        return goals

# Usage
if __name__ == "__main__":
    kafka_consumer = KafkaConsumer()
    kafka_consumer.consume_messages()
