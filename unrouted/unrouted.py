import pika
import time
import sys

ALTERNATE_EXCHANGE_NAME = 'unrouted'
DEFAULT_QUEUE_NAME = 'unrouted-queue'

class Consumer:
  def __init__(self, host):
    self.host = host
    self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    self.channel = self.connection.channel()
    self.channel.exchange_declare(exchange=ALTERNATE_EXCHANGE_NAME, exchange_type='fanout')

    self.channel.queue_declare(queue=DEFAULT_QUEUE_NAME, exclusive=True)
    self.channel.queue_bind(exchange=ALTERNATE_EXCHANGE_NAME, queue=DEFAULT_QUEUE_NAME)

  def start(self, callback):
    self.channel.basic_consume(queue=DEFAULT_QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    self.channel.start_consuming()

  def close(self):
    self.connection.close()

def callback(channel, method, properties, body):
    print("[x] %r" % body)

if __name__ == '__main__':
  host = 'localhost'
  if len(sys.argv) > 1:
    host = sys.argv[1]

  con = Consumer(host)

  print('UNROUTED receiver is running')
  print('============================')
  print()

  try:
    con.start(callback)
  except KeyboardInterrupt:
    con.close()
