import threading
import time


def foo():
    d = threading.local()
    d.foo = 0

    while d.foo < 10:
        d.foo += 1
        time.sleep(1)
        print(d.foo)


t1 = threading.Thread(target=foo)
t1.start()

time.sleep(2)

t2 = threading.Thread(target=foo)
t2.start()