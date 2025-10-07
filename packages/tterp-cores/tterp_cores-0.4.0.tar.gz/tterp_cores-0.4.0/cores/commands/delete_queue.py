from cores.component.rabbitmq import RabbitMQClient


async def example_usage():
    await RabbitMQClient.init()
    client = RabbitMQClient.get_instance()
    # Wait for input to delete a queue
    queue_name = input("Nhập tên queue bạn muốn xóa: ")
    client.close_all_connections(queue_name)
    client.delete_queue(queue_name)


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
