import logging
import time

import psutil

from anisette import Anisette

logging.basicConfig(level=logging.DEBUG)


def test_memory():
    process = psutil.Process()

    ani = Anisette.init()
    ani.provision()

    start_time = time.time()
    for i in range(2001):
        ani.get_data()

        if i % 100 == 0:
            alloc_stats = ani._ani_provider.adi._vm.alloc_stats
            mem_usage = process.memory_info().rss / (1024 * 1024)

            print(f"{i} / {time.time() - start_time:.2f}s - {alloc_stats} / {mem_usage} MB")
