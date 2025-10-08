import asyncio
import json
import logging
import random
from typing import Callable, Optional

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError, ChannelClosed


class RabbitMQ:
    exchanges: dict[str, AbstractExchange] = {}
    channel: Optional[AbstractChannel] = None
    connection: Optional[AbstractRobustConnection] = None
    connection_url: Optional[str] = None
    reconnect_interval = 5
    max_backoff = 60
    logger = logging.getLogger("rabbitmq")

    metrics = {
        "connect_attempts": 0,
        "publish_failures": 0,
        "rpc_timeouts": 0,
    }

    _connect_lock = asyncio.Lock()

    # ----------------------------------------------------------------------
    # CONNECTION HANDLING
    # ----------------------------------------------------------------------
    @classmethod
    async def connect(cls, connection_url: str, max_retries: int = 5) -> None:
        cls.connection_url = connection_url
        retries = 0

        while retries < max_retries:
            cls.metrics["connect_attempts"] += 1
            try:
                await cls._connect()
                cls.logger.info("✅ Connected to RabbitMQ successfully.")
                return
            except AMQPConnectionError as e:
                retries += 1
                cls.logger.warning(
                    f"[connect] Attempt {retries}/{max_retries} failed: {e}"
                )
                if retries == max_retries:
                    raise Exception("Max RabbitMQ connection retries reached")

                sleep_time = min(
                    cls.reconnect_interval * (2 ** (retries - 1)), cls.max_backoff
                )
                sleep_time += random.uniform(0, 1)  # jitter
                cls.logger.debug(f"[connect] Retrying in {sleep_time:.2f}s...")
                await asyncio.sleep(sleep_time)

    @classmethod
    async def _connect(cls) -> None:
        async with cls._connect_lock:
            if cls.connection and not cls.connection.is_closed:
                return

            await cls._close_connection_quietly()
            cls.logger.debug("[_connect] Establishing new RabbitMQ connection...")

            cls.connection = await connect_robust(
                cls.connection_url, reconnect_interval=cls.reconnect_interval
            )
            cls.channel = await cls.connection.channel()
            await cls.channel.set_qos(prefetch_count=1)

            # Re-declare exchanges
            for name in list(cls.exchanges.keys()):
                await cls.declare_exchange(name)

    @classmethod
    async def _close_connection_quietly(cls) -> None:
        try:
            if cls.channel and not cls.channel.is_closed:
                await cls.channel.close()
            if cls.connection and not cls.connection.is_closed:
                await cls.connection.close()
        except Exception as e:
            cls.logger.warning(f"[close] Error during connection cleanup: {e}")
        finally:
            cls.channel = None
            cls.connection = None

    @classmethod
    async def ensure_connection(cls) -> None:
        try:
            loop = asyncio.get_running_loop()
            if loop.is_closed:
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            cls.logger.warning(
                "[ensure_connection] No running event loop; reconnecting..."
            )
            await cls._connect()
            return

        if not cls.connection or cls.connection.is_closed:
            await cls._connect()
        elif not cls.channel or cls.channel.is_closed:
            async with cls._connect_lock:
                cls.channel = await cls.connection.channel()
                await cls.channel.set_qos(prefetch_count=1)

    # ----------------------------------------------------------------------
    # HEALTH CHECK
    # ----------------------------------------------------------------------
    @classmethod
    def ready(cls) -> bool:
        """Quick health check"""
        return bool(
            cls.connection
            and not cls.connection.is_closed
            and cls.channel
            and not cls.channel.is_closed
        )

    # ----------------------------------------------------------------------
    # PUBLISHING
    # ----------------------------------------------------------------------
    @classmethod
    async def publish(
        cls,
        message_dict: dict,
        exchange_name: str,
        routing_key: str,
        message: Optional[Message] = None,
        routing_action: Optional[str] = None,
    ) -> bool:
        await cls.ensure_connection()

        if message is None:
            body = json.dumps(message_dict).encode()
            message = Message(body, delivery_mode=DeliveryMode.PERSISTENT)

        message.headers = {
            **(message.headers or {}),
            **({"action": routing_action} if routing_action else {}),
        }

        if exchange_name not in cls.exchanges:
            if not await cls.declare_exchange(exchange_name):
                return False

        try:
            exchange = cls.exchanges[exchange_name]
            await exchange.publish(message, routing_key=routing_key)
            return True
        except (ChannelClosed, AMQPConnectionError) as e:
            cls.metrics["publish_failures"] += 1
            cls.logger.warning(f"[publish] Publish failed: {e}, reconnecting...")
            await cls.ensure_connection()
            try:
                exchange = cls.exchanges[exchange_name]
                await exchange.publish(message, routing_key=routing_key)
                return True
            except Exception as retry_e:
                cls.logger.error(f"[publish] Retry failed: {retry_e}")
                return False

    # ----------------------------------------------------------------------
    # DECLARATION
    # ----------------------------------------------------------------------
    @classmethod
    async def declare_exchange(cls, exchange_name: str) -> bool:
        try:
            await cls.ensure_connection()
            exchange = await cls.channel.declare_exchange(
                exchange_name, type=ExchangeType.DIRECT, durable=True
            )
            cls.exchanges[exchange_name] = exchange
            return True
        except Exception as e:
            cls.logger.error(f"[declare_exchange] Failed for '{exchange_name}': {e}")
            return False

    @classmethod
    async def declare_queue_and_bind(
        cls,
        queue_name: str,
        exchange_name: str,
        app_listener: Callable,
        routing_key: Optional[str] = None,
    ) -> bool:
        try:
            await cls.ensure_connection()
            queue = await cls.channel.declare_queue(queue_name, durable=True)
            if exchange_name not in cls.exchanges:
                if not await cls.declare_exchange(exchange_name):
                    return False

            exchange = cls.exchanges[exchange_name]
            routing_key = routing_key or queue_name
            await queue.bind(exchange, routing_key)
            await queue.consume(app_listener)
            return True
        except Exception as e:
            cls.logger.error(f"[declare_queue_and_bind] Failed for '{queue_name}': {e}")
            return False

    # ----------------------------------------------------------------------
    # RPC
    # ----------------------------------------------------------------------
    @classmethod
    async def remote_procedure_call(
        cls,
        queue_name: str,
        on_response: Callable,
        correlation_id: str,
        message_dict: dict,
        timeout: int = 10,
    ) -> bool:
        max_rpc_retries = 3
        for attempt in range(max_rpc_retries):
            try:
                await cls.ensure_connection()

                message_body = json.dumps(message_dict).encode()
                temp_queue = await cls.channel.declare_queue(exclusive=True)
                message = Message(
                    message_body,
                    delivery_mode=DeliveryMode.PERSISTENT,
                    correlation_id=correlation_id,
                    reply_to=temp_queue.name,
                )

                if not await cls.publish(
                    message=message,
                    routing_key=queue_name,
                    exchange_name="rpc_exchange",
                    message_dict=message_dict,
                ):
                    if attempt < max_rpc_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    return False

                future = asyncio.get_event_loop().create_future()

                async def _handle_response(msg):
                    if msg.correlation_id == correlation_id:
                        future.set_result(msg.body)
                        await msg.ack()

                await temp_queue.consume(_handle_response)

                try:
                    await asyncio.wait_for(future, timeout=timeout)
                    await temp_queue.delete()
                    return True
                except asyncio.TimeoutError:
                    cls.metrics["rpc_timeouts"] += 1
                    cls.logger.warning(
                        f"[RPC] Timeout after {timeout}s for {correlation_id}"
                    )
                    await temp_queue.delete()
                    if attempt < max_rpc_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    return False

            except (ChannelClosed, AMQPConnectionError) as e:
                cls.metrics["publish_failures"] += 1
                cls.logger.warning(
                    f"[RPC] Attempt {attempt + 1} failed ({e}); retrying..."
                )
                if attempt < max_rpc_retries - 1:
                    await cls.ensure_connection()
                    await asyncio.sleep(1)
                else:
                    return False
            except Exception as e:
                cls.logger.error(f"[RPC] Unexpected error: {e}")
                return False
        return False

    # ----------------------------------------------------------------------
    # CLEANUP
    # ----------------------------------------------------------------------
    @classmethod
    async def close(cls) -> None:
        await cls._close_connection_quietly()
