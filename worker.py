import time
import pika
import sys
import os

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)  # manual acknowledgement

def main():
    credentials = pika.PlainCredentials('admin', 'password')
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
    channel = connection.channel()

    # receive message from the hello queue
    channel.queue_declare(queue="task_queue", durable=True)

    # do not dispatch a new message to a worker until it has processed and ack the previous one
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue='task_queue',
                    on_message_callback=callback)    

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()         

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)    