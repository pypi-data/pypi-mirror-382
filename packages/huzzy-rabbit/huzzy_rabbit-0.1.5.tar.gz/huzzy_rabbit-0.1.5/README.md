# RabbitMQ Async Client for Python

A robust, asynchronous RabbitMQ client built with `aio_pika` for Python applications. This class provides connection management, auto-reconnection, message publishing, queue declarations, binding, and RPC support. It handles disconnections gracefully and ensures reliable message delivery.

## Features

- **Async/Await Support**: Fully asynchronous using `asyncio`.
- **Auto-Reconnection**: Built-in reconnection logic for robust operation.
- **Exchange and Queue Management**: Easy declaration and binding.
- **Message Publishing**: Persistent messages with custom headers.
- **Queue Consumption**: Simple listener setup.
- **RPC Support**: Remote procedure calls with correlation IDs.
- **Error Handling**: Catches channel/connection errors and recovers automatically.
- **Type Hints**: Full type annotation for better IDE support.

## Installation

Install the required dependencies:

```bash
pip install huzzy-rabbit
```


The class is self-contained and doesn't require additional setup beyond the dependencies.

## Quick Start

1. **Initialize the Client**:
   ```python
   from huzzy_rabbit.rabbit_mq import RabbitMQ
   
   rabbitmq = RabbitMQ()
   ```

2. **Connect to RabbitMQ**:

   ```python
   import asyncio
   
   async def main():
       await rabbitmq.connect("amqp://guest:guest@localhost/")
   
   asyncio.run(main())
   ```

3. **Publish a Message**:

   ```python
   async def publish_example():
       message_data = {"key": "value", "action": "test"}
       await rabbitmq.publish(
           message_dict=message_data,
           exchange_name="my_exchange",
           routing_key="my_routing_key"
       )
   ```

4. **Close the Connection** (when done):
   ```python
   await rabbitmq.close()
   ```

## Connection Management

### Initial Connection

Connect to your RabbitMQ server with retry logic:

```python
await rabbitmq.connect(
    connection_url="amqp://user:password@host:5672/",
    max_retries=5  # Optional: default is 3
)
```

The client uses `connect_robust` for automatic reconnection on network issues. The `reconnect_interval` is set to 5 seconds by default.

### Ensuring Connection

Before any operation, the client automatically calls `ensure_connection()` internally. You can call it manually if needed:

```python
await rabbitmq.ensure_connection()
```

This checks if the connection/channel is active and reconnects/reopens as necessary. Exchanges are re-declared after reconnection.

## Publishing Messages

Publish JSON-serializable messages to an exchange:

```python
# Declare exchange first (if not exists)
await rabbitmq.declare_exchange("my_exchange")

# Publish with default settings
message_data = {"user_id": 123, "event": "signup"}
await rabbitmq.publish(
    message_dict=message_data,
    exchange_name="my_exchange",
    routing_key="user.events",
    routing_action="process"  # Optional: adds to message headers
)

# Or use a pre-built Message object
from aio_pika import Message

custom_message = Message(b"Raw body", headers={"custom": "header"})
await rabbitmq.publish(
    message= custom_message,
    exchange_name="my_exchange",
    routing_key="user.events"
)
```

- Messages are persistent by default (`DeliveryMode.PERSISTENT`).
- Headers can include an `"action"` key for routing logic.
- If the exchange doesn't exist, declare it first using `declare_exchange`.

## Declaring Exchanges

Declare a durable direct exchange:

```python
exchange = await rabbitmq.declare_exchange("my_exchange")
```

- Type: `DIRECT` (default).
- Durable: `True` (survives broker restarts).
- Exchanges are cached in `rabbitmq.exchanges` and re-declared on reconnection.

## Queues and Binding

### Declare and Bind a Queue (Without Consumer)

```python
await rabbitmq.declare_queue(
    queue_name="my_queue",
    exchange_name="my_exchange",
    routing_key="my_routing_key"  # Optional: defaults to queue_name
)
```

This creates a durable queue and binds it to the exchange.

### Declare, Bind, and Consume (With Listener)

Set up a queue with a consumer callback:

```python
async def message_listener(message):
    async with message.process():  # Acknowledge after processing
        data = json.loads(message.body.decode())
        print(f"Received: {data}")
        # Process your message here

await rabbitmq.declare_queue_and_bind(
    queue_name="my_queue",
    exchange_name="my_exchange",
    app_listener=message_listener,
    routing_key="my_routing_key"
)
```

- The listener is an async callable that receives a `DeliveredMessage`.
- Use `message.process()` for manual acknowledgments.
- QoS prefetch is set to 1 for fair dispatching.

## Remote Procedure Calls (RPC)

For request-response patterns:

```python
async def response_listener(message):
    # Process request and send reply
    correlation_id = message.correlation_id
    # ... process logic ...
    reply_body = json.dumps({"result": "success"}).encode()
    reply = Message(reply_body, correlation_id=correlation_id)
    await reply_channel.publish(reply, routing_key=message.reply_to)

# Client side: Send RPC request
correlation_id = str(uuid.uuid4())
await rabbitmq.remote_procedure_call(
    queue_name="rpc_reply_queue",
    on_response=response_listener,  # Server-side handler
    correlation_id=correlation_id,
    message_dict={"request": "data"}
)
```

- Requires a unique `correlation_id` for matching responses.
- The `reply_to` queue is auto-declared.
- Use in producer-consumer patterns where the server consumes and replies.

## Error Handling and Reconnection

- **Automatic Recovery**: Operations like `publish` catch `ChannelClosed` and `AMQPConnectionError`, reconnect, and retry.
- **Logging**: Errors are logged using Python's `logging` module. Configure your logger for production.
- **Retries**: Connection attempts retry up to `max_retries` times with exponential backoff.
- **Thread Safety**: Designed for single-instance use in async contexts; not thread-safe.

If a disconnection occurs (e.g., broker restart), the client will:
1. Detect closed channel/connection.
2. Reconnect using robust settings.
3. Re-declare exchanges and queues.
4. Resume operations.

## Configuration

Customize via instance attributes:

```python
rabbitmq = RabbitMQ()
rabbitmq.reconnect_interval = 10  # Seconds between reconnect attempts
```

## Best Practices

- **Singleton Pattern**: Use one instance per application for shared connections.
- **Graceful Shutdown**: Always call `await rabbitmq.close()` in shutdown hooks.
- **Error Propagation**: Wrap calls in try-except for custom error handling.
- **Testing**: Mock `aio_pika` for unit tests or use a local RabbitMQ container.
- **Security**: Use SSL/TLS for production: `amqps://` URLs with certificates.

## Limitations

- Direct exchange type only (extend `declare_exchange` for others).
- No built-in message TTL or expiration.
- RPC assumes synchronous response; use timeouts for production.

## Contributing

Fork the repo, make changes, and submit a PR. Ensure tests pass and add type hints.

## License

MIT License. See LICENSE for details.

For issues or questions, open a GitHub issue.