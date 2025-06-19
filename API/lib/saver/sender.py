import pika
import json


def send_message_to_rabbit(rabbit=None):
    # 创建连接和通道
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # 启用发布者确认
    channel.confirm_delivery()

    # 声明持久化队列
    channel.queue_declare(queue='update_msg_queue', durable=True)

    try:
        # 发布持久化消息
        channel.basic_publish(
            exchange='',
            routing_key='update_msg_queue',
            body=json.dumps({'data': 'update resource'}),
            properties=pika.BasicProperties(
                delivery_mode=2,  # 持久化消息
            )
        )
        print(" [x] 消息确认投递成功")
    except pika.exceptions.UnroutableError:
        print(" [!] 消息丢失，未到达队列")
    except pika.exceptions.NackError:
        print(" [!] Broker明确拒绝消息")

    connection.close()
