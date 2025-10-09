import threading

def synchronized(lock_name='_lock'):
    """创建一个同步装饰器，类似Java的synchronized关键字"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # 获取实例的锁对象
            lock = getattr(self, lock_name)
            # 自动获取和释放锁
            with lock:
                return func(self, *args, **kwargs)
        return wrapper
    return decorator