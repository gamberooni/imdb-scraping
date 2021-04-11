import sys
import pika


credentials = pika.PlainCredentials('admin', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# create a queue
channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                          delivery_mode=2, # make message persistent
                      ))
print(" [x] Sent %r" % message)

connection.close()
