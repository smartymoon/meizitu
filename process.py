from multiprocessing import Process,Pool
import datetime
import time
import os

def cc():
    while True:
        print(os.getpid())
        print(datetime.datetime.now())
        time.sleep(6)
if __name__ == "__main__":
    p = Pool(processes=8)
    for i in range(10):
        p.apply_async(cc)
    p.close()
    p.join()




