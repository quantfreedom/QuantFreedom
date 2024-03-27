from multiprocessing import Process
import os
import math
import time

num_processes = os.cpu_count()
num_loops = 100000000


def calc(cor_num: int):
    start = num_loops * cor_num
    end = num_loops * (cor_num + 1)

    print(f"Process {cor_num} is calculating from {start} to {end}\n")
    for i in range(int(start), int(end)):
    # for i in range(0, 70000000):
        math.sqrt(i)


if __name__ == "__main__":
    start = time.perf_counter()

    processes = []
    for i in range(num_processes):
        print("Registering process %d" % i)
        # processes.append(Process(target=calc(cor_num=i)))
        processes.append(Process(target=calc, args=(i,)))

    for process in processes:
        print("Starting process %s" % process)
        process.start()

    for process in processes:
        print("Joining process %s" % process)
        process.join()

    end = time.perf_counter()

    print(f"Time taken: {end - start} seconds")
