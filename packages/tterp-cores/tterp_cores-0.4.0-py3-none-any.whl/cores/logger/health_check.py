"""
Health check logging module cho infrastructure services.

Module này cung cấp health check cho:
- MySQL Database
- Redis Cache
- RabbitMQ Message Queue
- External APIs
"""

import asyncio
import time
from typing import Any

try:
    import aio_pika  # type: ignore
except Exception:  # pragma: no cover
    aio_pika = None  # type: ignore

try:
    import aiomysql  # type: ignore
except Exception:  # pragma: no cover
    aiomysql = None  # type: ignore

try:
    import aioredis  # type: ignore
except Exception:  # pragma: no cover
    aioredis = None  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from cores.logger.enhanced_logging import LogCategory, logger


class HealthCheckService:
    """Service để thực hiện health check cho các infrastructure services"""

    def __init__(self):
        self.checks = {}

    async def check_mysql(
        self, connection_string: str, timeout: float = 5.0
    ) -> dict[str, Any]:
        """Health check cho MySQL database"""
        start_time = time.time()

        try:
            if aiomysql is None:
                raise ImportError("aiomysql not installed")
            # Tạo connection pool tạm thời để test
            pool = await aiomysql.create_pool(
                host=connection_string.split("@")[1].split(":")[0]
                if "@" in connection_string
                else "localhost",
                port=3306,
                user="root",
                password="",
                db="test",
                minsize=1,
                maxsize=1,
                connect_timeout=timeout,
            )

            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()

            pool.close()
            await pool.wait_closed()

            response_time = round((time.time() - start_time) * 1000, 2)

            result_data = {
                "status": "HEALTHY",
                "response_time_ms": response_time,
                "details": {"query_result": result[0] if result else None},
            }

            logger.log_health_check("mysql", "HEALTHY", response_time, result_data)
            return result_data

        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result_data = {
                "status": "UNHEALTHY",
                "response_time_ms": response_time,
                "error": str(e),
            }

            logger.log_health_check("mysql", "UNHEALTHY", response_time, result_data)
            return result_data

    async def check_redis(
        self, redis_url: str = "redis://localhost:6379", timeout: float = 5.0
    ) -> dict[str, Any]:
        """Health check cho Redis cache"""
        start_time = time.time()

        try:
            if aioredis is None:
                raise ImportError("aioredis not installed")
            redis = aioredis.from_url(redis_url, socket_timeout=timeout)

            # Test ping
            pong = await redis.ping()

            # Test set/get
            test_key = f"health_check_{int(time.time())}"
            await redis.set(test_key, "test_value", ex=10)
            test_value = await redis.get(test_key)
            await redis.delete(test_key)

            await redis.close()

            response_time = round((time.time() - start_time) * 1000, 2)

            result_data = {
                "status": "HEALTHY",
                "response_time_ms": response_time,
                "details": {
                    "ping": pong,
                    "set_get_test": test_value.decode() if test_value else None,
                },
            }

            logger.log_health_check("redis", "HEALTHY", response_time, result_data)
            return result_data

        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result_data = {
                "status": "UNHEALTHY",
                "response_time_ms": response_time,
                "error": str(e),
            }

            logger.log_health_check("redis", "UNHEALTHY", response_time, result_data)
            return result_data

    async def check_rabbitmq(
        self, amqp_url: str = "amqp://localhost:5672", timeout: float = 5.0
    ) -> dict[str, Any]:
        """Health check cho RabbitMQ message queue"""
        start_time = time.time()

        try:
            if aio_pika is None:
                raise ImportError("aio_pika not installed")
            connection = await aio_pika.connect_robust(amqp_url, timeout=timeout)

            # Test channel creation
            channel = await connection.channel()

            # Test queue declaration (temporary)
            test_queue_name = f"health_check_{int(time.time())}"
            queue = await channel.declare_queue(test_queue_name, auto_delete=True)

            # Test publish/consume
            test_message = f"health_check_message_{int(time.time())}"
            await channel.default_exchange.publish(
                aio_pika.Message(test_message.encode()), routing_key=test_queue_name
            )

            # Get message back
            message = await queue.get(timeout=1.0)
            if message:
                await message.ack()
                received_message = message.body.decode()
            else:
                received_message = None

            await connection.close()

            response_time = round((time.time() - start_time) * 1000, 2)

            result_data = {
                "status": "HEALTHY",
                "response_time_ms": response_time,
                "details": {
                    "connection": "OK",
                    "channel": "OK",
                    "publish_consume_test": received_message == test_message,
                },
            }

            logger.log_health_check("rabbitmq", "HEALTHY", response_time, result_data)
            return result_data

        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result_data = {
                "status": "UNHEALTHY",
                "response_time_ms": response_time,
                "error": str(e),
            }

            logger.log_health_check("rabbitmq", "UNHEALTHY", response_time, result_data)
            return result_data

    async def check_sqlalchemy_session(
        self, session: AsyncSession, timeout: float = 5.0
    ) -> dict[str, Any]:
        """Health check cho SQLAlchemy async session"""
        start_time = time.time()

        try:
            # Test simple query
            result = await session.execute("SELECT 1 as health_check")
            row = await result.fetchone()

            response_time = round((time.time() - start_time) * 1000, 2)

            result_data = {
                "status": "HEALTHY",
                "response_time_ms": response_time,
                "details": {"query_result": row[0] if row else None},
            }

            logger.log_health_check("sqlalchemy", "HEALTHY", response_time, result_data)
            return result_data

        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            result_data = {
                "status": "UNHEALTHY",
                "response_time_ms": response_time,
                "error": str(e),
            }

            logger.log_health_check(
                "sqlalchemy", "UNHEALTHY", response_time, result_data
            )
            return result_data

    async def run_all_checks(self, config: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Chạy tất cả health checks"""

        logger.info(
            "Starting comprehensive health check",
            category=LogCategory.HEALTH_CHECK,
            extra_fields={"check_count": len(config)},
        )

        results = {}

        # Run checks concurrently
        tasks = []

        if "mysql" in config:
            tasks.append(
                ("mysql", self.check_mysql(config["mysql"]["connection_string"]))
            )

        if "redis" in config:
            tasks.append(("redis", self.check_redis(config["redis"]["url"])))

        if "rabbitmq" in config:
            tasks.append(("rabbitmq", self.check_rabbitmq(config["rabbitmq"]["url"])))

        # Execute all checks
        if tasks:
            completed_tasks = await asyncio.gather(
                *[task[1] for task in tasks], return_exceptions=True
            )

            for i, (service_name, _) in enumerate(tasks):
                result = completed_tasks[i]
                if isinstance(result, Exception):
                    results[service_name] = {
                        "status": "ERROR",
                        "error": str(result),
                        "response_time_ms": 0,
                    }
                else:
                    results[service_name] = result

        # Log summary
        healthy_count = sum(1 for r in results.values() if r.get("status") == "HEALTHY")
        total_count = len(results)

        logger.info(
            f"Health check completed: {healthy_count}/{total_count} services healthy",
            category=LogCategory.HEALTH_CHECK,
            extra_fields={
                "healthy_services": healthy_count,
                "total_services": total_count,
                "results": results,
            },
        )

        return results


# Global health check service instance
health_check_service = HealthCheckService()


async def startup_health_checks(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Thực hiện health checks khi startup application.

    Args:
        config: Dictionary chứa config cho các services

    Returns:
        Dictionary chứa kết quả health check
    """
    logger.info("Performing startup health checks", category=LogCategory.HEALTH_CHECK)

    try:
        results = await health_check_service.run_all_checks(config)

        # Check if any critical services are down
        critical_services = config.get("critical_services", ["mysql"])
        failed_critical = [
            service
            for service in critical_services
            if results.get(service, {}).get("status") != "HEALTHY"
        ]

        if failed_critical:
            logger.error(
                f"Critical services failed health check: {failed_critical}",
                category=LogCategory.HEALTH_CHECK,
                extra_fields={"failed_services": failed_critical},
            )
            raise RuntimeError(f"Critical services unhealthy: {failed_critical}")

        logger.info(
            "All startup health checks passed", category=LogCategory.HEALTH_CHECK
        )
        return results

    except Exception as e:
        logger.error(
            f"Startup health checks failed: {str(e)}",
            category=LogCategory.HEALTH_CHECK,
            exc_info=True,
        )
        raise


# Export public API
__all__ = ["HealthCheckService", "health_check_service", "startup_health_checks"]
