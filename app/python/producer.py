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

class Publisher:
  def __init__(self, config):
    self.host = config["host"]
    self.exchange_name = config["exchange_name"]
    self.exchange_type = config["exchange_type"]
    self.routing_key = config["routing_key"]

    if "message" in config:
      self.message = config["message"]
    else:
      self.message = "message"

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

    if self.exchange_name != '':
      self.exchange_args = {
        "alternate-exchange": ALTERNATE_EXCHANGE_NAME
      }
      self.channel.exchange_declare(
        exchange=self.exchange_name, 
        exchange_type=self.exchange_type,
        arguments=self.exchange_args
    )

  def publish(self, message):
    self.channel.basic_publish(
      exchange=self.exchange_name, 
      routing_key=self.routing_key, 
      body=message)

  def close(self):
    self.connection.close()

def load_config(config_file):
  with open(config_file, 'r') as f:
    result = json.load(f)
    f.close()

  return result

def start_publishing(publisher, message_template):
  counter = 0

  while True:
    try:
      counter += 1
      message = message_template + ' ' + str(counter)

      publisher.publish(message)

      print(message)

      time.sleep(1)

      print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
    except KeyboardInterrupt:
      publisher.close()
      break

  print('')

if __name__ == '__main__':
  if len(sys.argv) > 1:
    config = load_config(sys.argv[1])
  else:
    print('please specify config file')
    sys.exit(1)
  
  print('Running PRODUCER with configuration:')
  print()
  pprint.pprint(config)
  print()
  print('====================================')
  print()

  if "message" in config:
    start_publishing(Publisher(config), config['message'])
  else:
    start_publishing(Publisher(config), 'message')
