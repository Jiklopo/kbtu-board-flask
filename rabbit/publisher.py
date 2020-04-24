import pika


class MetaClass(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class RabbitmqConfigure(metaclass=MetaClass):

    def __init__(self, queue='posts', host='localhost', routingKey='posts', exchange=''):
        """ Configure Rabbit Mq Server  """
        self.queue = queue
        self.host = host
        self.routingKey = routingKey
        self.exchange = exchange


class RabbitMq():

    def __init__(self, server):
        self.server = server

        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server.host))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self.server.queue)

    def publish(self, payload):
        self._channel.basic_publish(exchange=self.server.exchange,
                                    routing_key=self.server.routingKey,
                                    body=str(payload))

        print("Published Message: {}".format(payload))


class RabbitPublisher:
    def __init__(self):
        self.server = RabbitmqConfigure(queue='posts',
                                        host='localhost')
        self.rabbitmq = RabbitMq(self.server)

    def publish(self, message):
        self.rabbitmq.publish(message)
