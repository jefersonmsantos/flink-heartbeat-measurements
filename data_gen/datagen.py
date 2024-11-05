#!/usr/bin/env python3
import os

import datetime
import random
import uuid
import json
from faker import Faker
from faker.providers import address
from kafka import KafkaProducer
from confluent_kafka import Producer
  
class KafkaMeasurementProducer:
    
    def __init__(self, bootstrap_servers, topic, username, password):
        self.topic = topic

        self.producer = Producer({
            'bootstrap.servers' : bootstrap_servers
            ,'security.protocol' : 'SASL_SSL'
            ,'sasl.mechanisms'   : 'PLAIN'
            ,'sasl.username'     : username
            ,'sasl.password'     : password
        })

        self.fake = Faker()
        self.fake.add_provider(address)

    @staticmethod
    def serializer(message):
        return json.dumps(message).encode('utf-8')

    def generate_measurement(self):
        measurement = {
            "id": str(uuid.uuid1()),
            "state": self.fake.state_abbr(),
            "heartbeat": random.randint(60, 140),
            "timestamp": datetime.datetime.now().isoformat(),
            "occured_at": self.fake.date_time_between_dates(
                datetime_start=datetime.datetime.now() - datetime.timedelta(seconds=50),
                datetime_end=datetime.datetime.now()
            ).isoformat()
        }
        return measurement

    def send_measurement(self):
        measurement = self.generate_measurement()
        print(measurement)
        self.producer.produce(self.topic, self.serializer(measurement))
        self.producer.flush()

    def run(self):
        while True:
            self.send_measurement()

if __name__ == "__main__":
    
    kafka_config = json.loads(os.environ['KAFKA_CREDENTIALS'])

    producer = KafkaMeasurementProducer(
        bootstrap_servers=kafka_config['bootstrap_server'],
        topic=kafka_config["input_topic"],
        username =kafka_config['username'],
        password =kafka_config['password'] 
    )

    producer.run()