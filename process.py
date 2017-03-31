from multiprocessing import Pool
import datetime
import time
import os

def cc(a):
    while True:
        print(a)
        print(os.getpid())
        print(datetime.datetime.now())
        time.sleep(6)
if __name__ == "__main__":
    p = Pool(processes=8)
    for i in range(10):
        a = 'mmm'
        p.apply_async(cc, args=(a,))
    p.close()
    p.join()




