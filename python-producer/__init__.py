from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='localhost:9092')

print(producer)
for _ in range(100):
  producer.send('foobar', b'hola')

producer.flush()