const fs = require('fs');
const amqp = require('amqplib/callback_api');

const ALTERNATE_EXCHANGE_NAME = 'unrouted'

class Producer {
  constructor(config) {
    this._connection = config.connection;
    this._channel = config.channel;
    this._exchange = config.exchange_name;
    this._routing_key = config.routing_key;
  }

  publish(message) {
    return this._channel.publish(
      this._exchange,
      this._routing_key,
      Buffer.from(message)
    );
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

async function createProducer(config) {
  const connection = await createConnection(config.host);
  const channel = await createChannel(connection);

  if (config.exchange_name != '') {
    await channel.assertExchange(
      config.exchange_name, 
      config.exchange_type,
      {
        alternateExchange: ALTERNATE_EXCHANGE_NAME
      }
    );
  }

  const producerConfig = { ...config, connection, channel };

  return new Producer(producerConfig);
}

async function startPublishingLoop(handler) {
  while (true) {
    try {
      await Promise.resolve(handler());
      await new Promise((resolve) => {
        setTimeout(() => resolve(), 1000);
      });
    } catch(err) {
      console.log(err);
    }
  }
}

async function main() {
  const config = JSON.parse(fs.readFileSync(process.argv[2]));
  const producer = await createProducer(config);
  startPublishingLoop(async () => {
    const message = 'hello';

    await producer.publish(message);

    console.log(" [x] Sent %s", message);
  });
}

if (process.argv.length > 1 && process.argv[2] != null) {
  main();
} else {
  console.log('please specify config file');
  process.exit(1);
}
