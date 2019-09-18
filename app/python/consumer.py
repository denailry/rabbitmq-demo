import pika
import time
import sys
import json
import pprint

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

ALTERNATE_EXCHANGE_NAME = 'unrouted'
DEFAULT_RABBITMQ_USER = 'guest'
DEFAULT_RABBITMQ_PASSWORD = 'guest'

CONSUMPTION_COUNT = 0

class Consumer:
  def __init__(self, config):
    self.host = config["host"]
    self.exchange_name = config["exchange_name"]
    self.exchange_type = config["exchange_type"]
    self.queue_name = config["queue_name"]
    self.routing_key = config["routing_key"]
    self.exclusive = config["exclusive"]

    if ("user" in config) and ("password" in config):
      credentials = pika.PlainCredentials(config["user"], config["password"])
    else:
      credentials = pika.PlainCredentials(DEFAULT_RABBITMQ_USER, DEFAULT_RABBITMQ_PASSWORD)

    params = pika.ConnectionParameters(
      host=self.host,
      credentials=credentials
    )
    self.connection = pika.BlockingConnection(params)
    self.channel = self.connection.channel()

    self.channel.queue_declare(
      queue=self.queue_name, 
      exclusive=self.exclusive
    )

    if self.exchange_name != '':
      self.exchange_args = {"alternate-exchange": ALTERNATE_EXCHANGE_NAME}
      self.channel.exchange_declare(
        exchange=self.exchange_name, 
        exchange_type=self.exchange_type, 
        arguments=self.exchange_args
      )

      self.channel.queue_bind(
        exchange=self.exchange_name, 
        queue=self.queue_name, 
        routing_key=self.routing_key
      )

  def start(self, callback):
    self.channel.basic_consume(
      queue=self.queue_name, 
      on_message_callback=callback, 
      auto_ack=True,
      exclusive=self.exclusive
    )
    self.channel.start_consuming()

  def close(self):
    self.connection.close()

def callback(channel, method, properties, body):
    global CONSUMPTION_COUNT

    CONSUMPTION_COUNT += 1

    print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
    print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)

    print('received', str(CONSUMPTION_COUNT))
    print("message: %r" % body)

def load_config(config_file):
  with open(config_file, 'r') as f:
    result = json.load(f)
    f.close()

  return result

def start_consuming(consumer):
  print()
  print('received 0')
  print("message: %r" % 'none')

  try:
    consumer.start(callback)
  except KeyboardInterrupt:
    consumer.close()

if __name__ == '__main__':
  if len(sys.argv) > 1:
    config = load_config(sys.argv[1])
  else:
    print('please specify config file')
    sys.exit(1)

  print('Running CONSUMER with configuration:')
  print()
  pprint.pprint(config)
  print()
  print('====================================')

  start_consuming(Consumer(config))
