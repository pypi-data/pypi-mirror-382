# -*- coding: utf-8 -*-
from typing import Any, List, NamedTuple
from enum import Enum, auto
from abc import ABC, abstractmethod
from threading import Thread
from time import sleep
from queue import Queue


class MsgType(Enum):
    """消息体类型"""
    END = auto()
    NORMAL = auto()


class Msg(NamedTuple):
    """消息体"""
    type: MsgType
    data: Any


class Pub(ABC, Thread):
    """线程发布者抽象类"""
    _queue: Queue
    _sub_num: int = 1
    _options: Any = None

    def __init__(self, queue: Queue, sub_num: int = 1, options: Any = None) -> None:
        super().__init__()
        self._queue = queue
        self._sub_num = sub_num
        self._options = options

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """实现线程发布的抽象函数"""
        pass


class Sub(ABC, Thread):
    """线程订阅者抽象类"""
    _queue: Queue
    _options: Any = None

    def __init__(self, queue: Queue, options: Any = None) -> None:
        super().__init__()
        self._queue = queue
        self._options = options

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """实现线程订阅的抽象函数"""
        pass


class PubSubs:
    """一个发布者多个订阅者"""
    _queue: Queue
    _pub: Pub
    _subs: List[Sub]

    def __init__(
        self,
        pub_cls: Pub,
        sub_cls: Sub,
        sub_num: int = 2,
        queue_size: int = 0,
        pub_options: Any = None,
        sub_options: Any = None
    ) -> None:
        self._queue = Queue(queue_size)
        self._pub = pub_cls(self._queue, sub_num, pub_options)
        self._subs = list(sub_cls(self._queue, sub_options) for _ in range(sub_num))

    def start(self) -> None:
        for i, sub in enumerate(self._subs):
            sub.start()
        self._pub.start()

    def join(self) -> None:
        self._pub.join()
        for i, sub in enumerate(self._subs):
            sub.join()


class DumyPub(Pub):
    def __init__(self, queue: Queue, sub_num: int = 1, options: Any = None) -> None:
        super().__init__(queue, sub_num, options)

    def run(self) -> None:
        print('dumpy tpub running')
        sleep(1)
        for _ in range(self._sub_num):
            self._queue.put(Msg(type=MsgType.END, data=None))


class DumySub(Sub):
    def __init__(self, queue: Queue, options: Any = None) -> None:
        super().__init__(queue, options)

    def run(self) -> None:
        while True:
            print('dumpy spub running')
            if self._queue.empty():
                sleep(0.1)
                continue
            msg: Msg = self._queue.get()
            print(msg)
            if msg.type == MsgType.END:
                break
            sleep(0.1)

        print('dumpy spub end')


if __name__ == '__main__':
    pubsubs = PubSubs(pub_cls=DumyPub, sub_cls=DumySub)
    pubsubs.start()
    pubsubs.join()
