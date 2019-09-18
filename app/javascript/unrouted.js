const fs = require('fs');
const amqp = require('amqplib/callback_api');

const ALTERNATE_EXCHANGE_NAME = 'unrouted'
const ALTERNATE_EXCHANGE_TYPE = 'fanout'
const DEFAULT_QUEUE_NAME = 'unrouted-queue'

class AlternateConsumer {
  constructor(config) {
    this._connection = config.connection;
    this._channel = config.channel;
  }

  consume(handler) {
    this._channel.consume(DEFAULT_QUEUE_NAME, handler);
  }

  close() {
    this._connection.close();
  }
}

function createChannel(connection) {
  return new Promise((resolve, reject) => {
    connection.createChannel(function(err, channel) {
      (err == null) ? resolve(channel) : reject(err);
    });
  });
}

function createConnection(host) {
  return new Promise((resolve, reject) => {
    amqp.connect(`amqp://${host}`, function(err, connection) {
      (err == null) ? resolve(connection) : reject(err);
    })
  });
}

async function createAlternateConsumer(host) {
  const connection = await createConnection(host);
  const channel = await createChannel(connection);

  await channel.assertQueue(DEFAULT_QUEUE_NAME, {
    exclusive: true
  });

  await channel.assertExchange(
    ALTERNATE_EXCHANGE_NAME, 
    ALTERNATE_EXCHANGE_TYPE
  );

  await channel.bindQueue(
    DEFAULT_QUEUE_NAME,
    ALTERNATE_EXCHANGE_NAME
  );

  const consumerConfig = { connection, channel };

  return new AlternateConsumer(consumerConfig);
}

async function main() {
  let host = 'localhost';
  if (process.argv.length > 1 && process.argv[2] != null) {
    host = process.argv[2];
  }

  const consumer = await createAlternateConsumer(host);
  consumer.consume(function(msg) {
    console.log(" [x] Received unrouted %s", msg.content.toString());
  });
}

main();
