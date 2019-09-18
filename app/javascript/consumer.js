const fs = require('fs');
const amqp = require('amqplib/callback_api');

const ALTERNATE_EXCHANGE_NAME = 'unrouted'

class Consumer {
  constructor(config) {
    this._connection = config.connection;
    this._channel = config.channel;
    this._queue = config.queue_name;
    this._routing_key = config.routing_key;
  }

  consume(handler) {
    this._channel.consume(this._queue, handler);
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

async function createConsumer(config) {
  const connection = await createConnection(config.host);
  const channel = await createChannel(connection);

  await channel.assertQueue(config.queue_name, {
    exclusive: config.exclusive
  });

  if (config.exchange_name != '') {
    await channel.assertExchange(
      config.exchange_name, 
      config.exchange_type,
      {
        alternateExchange: ALTERNATE_EXCHANGE_NAME
      }
    );

    await channel.bindQueue(
      config.queue_name,
      config.exchange_name,
      config.routing_key
    );
  }

  const consumerConfig = { ...config, connection, channel };

  return new Consumer(consumerConfig);
}

async function main() {
  const config = JSON.parse(fs.readFileSync(process.argv[2]));
  const consumer = await createConsumer(config);
  consumer.consume(function(msg) {
    console.log(" [x] Received %s", msg.content.toString());
  });
}

if (process.argv.length > 1 && process.argv[2] != null) {
  main();
} else {
  console.log('please specify config file');
  process.exit(1);
}
