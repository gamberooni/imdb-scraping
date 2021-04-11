import pika


credentials = pika.PlainCredentials('admin', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# create a hello queue
channel.queue_declare(queue='hello')

# specify which queue the message should go
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Fuck you!')
print(" [x] Sent 'Hello World!'")


connection.close()

