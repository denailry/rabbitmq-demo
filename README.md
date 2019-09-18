# About
RabbitMQ is a message broker. It mainly supports Advanced Message Queuing Protocol (AMQP) 0-9-1, but it has been extended to support other protocols such as STOMP, MQTT, AMQP 1.0, HTTP and websockets. This is example of RabbitMQ client implementation for learning and exploration purpose.

# Content
- **app/{language}/consumer.{ext}** directory contains implementation of message consumer which receive message from RabbitMQ.
- **app/{language}/producer.{ext}** directory contains implementation of message producer which send message to RabbitMQ.
- **app/{language}/unrouted.{ext}** directory contains implementation of receiver for unrouted message. Basically, it is the same as consumer but hard-coded to receive unrouted message.
- **scenarios** directory contains different configurations and script to run simulation of RabbitMQ usage.

# AMQP 0-9-1 Model

RabbitMQ is a message broker. A message broker receive message from **publishers** and send the message to **consumers**. There are 2 components inside the message broker: **exchanges** and **queues**. Each messages is published to an exchange. Exchange responsibles to distribute the message to the consumers. In order to receive the message from exchange, consumers should have a queue which is bound to the exchange. Several queues can be bound to an exchange. Exchange routes the message to the bound queues depending of its type.

There are 4 types of exchange:
1. Default Exchange
2. Direct Exchange
3. Fanout Exchange
4. Topic Exchange

## Default Exchange
This type of exchange has no name. Each messages comes in will be routed to any queus which has the same name as the routing key of the message. Every queues, by default, is bound to default exchange.

## Direct Exchange
Each messages comes in will be routed to any queues whose routing key is the same as the message's routing key.

## Fanout Exchange
This type of exchange will ignore routing key. It will send each messages to all bound queues.

## Topic Exchange
Similar to direct exchange, but it can match the routing key with special pattern.

# Defined Scenarios
You can try to use RabbitMQ by using the defined scenarios in __scenarios__ directory. Firstly, make sure RabbitMQ service is already running. You can see `scenario's name` inside `scenarios` directory. To run the scenario, you can specify the desired programming language and scenario's name. 

Currently available languages are:
- **python**. You should install **pika** module first which is RabbitMQ's client for Python. It is recommeded to use virtual environment.

To run the scenario, use command below:
```
./start-scenario [language] [scenario_name]
```

For example:
```
./start-scenario python default-to-default
```