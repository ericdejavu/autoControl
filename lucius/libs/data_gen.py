import math,random,time
from hardware import Hardware
from const_str import *


class DataGen:
    def __init__(self,hardware):
        if not hardware:
            exit(1)
        self.hardware = hardware
        self.name = self.hardware.name
        # if not name:
        #     self.name = self.hardware.name()
        print self.name,'r=',self.hardware.start()
        self.pre_r = 0
        self.last_r = 0

    def process_bar(self, l):
        self.RUN_CIRCLE = l
        self.precent = self.RUN_CIRCLE * .01

    # 160k
    def gen(self):
        r_set = []
        # 20k
        for j in range(10):
            for i in range(20,101,20):
                a = [i / (1 + math.exp(-x*.1)) for x in range(-100,100)]
                b = a[:]
                b.reverse()
                a += b
                r_set += a
        # 130k
        A = 50
        r_set += [A * math.sin(i * math.pi / 180) + A for i in range(20000)]
        r_set += [A * math.sin((i + random.randint(-10,10)) * math.pi / 180) + A for i in range(30000)]
        r_set += [A * math.sin((i + random.randint(-50,50)) * math.pi / 180) + A for i in range(5000)]
        r_set += [A * math.sin((i + random.randint(-80,80)) * math.pi / 180) + A for i in range(80000)]
        # 5k
        A = 10
        r_set += [A * math.sin((i + random.randint(-2,2)) * math.pi / 180) + A for i in range(5000)]
        self.process_bar(len(r_set))
        print len(r_set)
        return r_set

    def run(self):
        waves = self.gen()
        pre_r,last_r = 0,0
        start_time = time.time()
        with open(PREFIX + self.name + POSTFIX_MODEL_TRAINING_DATA_FILENAME,'a+') as f:
            for i,wave in enumerate(waves):
                t = time.time()
                if wave > 100:
                    wave = 100
                elif wave < -100:
                    wave = -100
                r = self.hardware.read()
                self.hardware.send(wave)
                dt = time.time() - t
                _str = str(r)+','+str(pre_r)+','+str(last_r)+','+str(int(wave))+','+str(dt)+'\n'
                last_r = pre_r
                pre_r = r
                f.write(_str)
                if i % self.precent == 0:
                    used_time = (time.time() - start_time) / 60.
                    process = i * 1. / self.RUN_CIRCLE
                    total_time = '?' if i == 0 else used_time / process - used_time
                    print ' [gen]',  process * 100, '% , ', total_time


# hardware = Hardware()
# data_gen = DataGen(hardware)
# data_gen.run()
