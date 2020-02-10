import functools
import ujson
from confluent_kafka import Consumer, KafkaError
from ..base import _wrap


def AsyncKafka(servers, group, topics, json=False, wrap=False, interval=1):
    '''Connect to kafka server and yield back results

    Args:
        servers (list): kafka bootstrap servers
        group (str): kafka group id
        topics (list): list of kafka topics to connect to
        json (bool): load input data as json
        wrap (bool): wrap result in a list
        interval (int): kafka poll interval
    '''
    c = Consumer({
        'bootstrap.servers': servers,
        'group.id': group,
        'default.topic.config': {
            'auto.offset.reset': 'smallest'
        }
    })

    if not isinstance(topics, list):
        topics = [topics]
    c.subscribe(topics)

    async def _listen(consumer, json, wrap, interval):
        while True:
            msg = consumer.poll(interval)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            msg = msg.value().decode('utf-8')

            if not msg:
                break
            if json:
                msg = ujson.loads(msg)
            if wrap:
                msg = [msg]
            yield msg

    return _wrap(_listen, dict(consumer=c, json=json, wrap=wrap, interval=interval), name='Kafka')


@functools.wraps(AsyncKafka)
def Kafka(*args, **kwargs):
    return AsyncKafka(*args, **kwargs)
