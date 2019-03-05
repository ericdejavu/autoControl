import time,math,random
from graph import Graph
from const_str import *
from hardware import Hardware
import json

# control value
# setting value
class UnderstandModel:
    def __init__(self, hardware, values_range = [[0,100],[0,180]]):
        if not hardware:
            exit(1)
        self.hardware = hardware
        self.name = hardware.name
        self.control_range = values_range[0]
        self.setting_range = values_range[1]
        with open(PREFIX + self.name + POSTFIX_DT_FILENAME) as f:
            self.dt = float(f.readline())


    def search_minist_start_thread(self):
        pre_r = 0
        start_value = []
        for j in range(20):
            for i in range(self.control_range[0],self.control_range[1]+1):
                r = self.hardware.read()
                if type(r) != type(1):
                    continue
                print r,pre_r,i
                if i != 0 and abs(pre_r - r) >= 2:
                    start_value.append(i)
                    break
                self.hardware.send(i)
                time.sleep(self.dt)
                pre_r = r
        mi,ma = min(start_value),max(start_value)
        start_value.remove(mi)
        start_value.remove(ma)
        return sum(start_value) / len(start_value)

    def find_unique(self):
        with open(PREFIX + self.name + POSTFIX_WEIGHT_FILENAME) as f:
            weights = json.loads(f.readline())
        with open(PREFIX + self.hardware.name + POSTFIX_OFFSET_FILENAME) as f:
            offset = float(f.readline())
        w1 ,w2 = weights['w1'], weights['w2']
        r = sum(self.setting_range) / 2
        pre_r = r
        tmp = []
        for j in range(5):
            tmp.append((w1[0][j]*r + w1[1][j]*pre_r + w1[3][j]*self.dt) * w2[j][0])
        wave_bias = (90 - sum(tmp) / offset) / sum(w1[2])
        wave_bias = wave_bias if wave_bias > 0 else -wave_bias

        wave_thread = self.search_minist_start_thread()
        wave_adjust_range = [(wave_bias + wave_thread) / 15, max(wave_thread / 3, (wave_bias + wave_thread) / 15 + 1)]

        # {'wave_thread': 10, 'wave_bias': 0.2643393843104657, 'wave_adjust_range': [0.52643393843104658, 10]}
        return {'wave_bias':wave_bias,'wave_thread':wave_thread,'wave_adjust_range':wave_adjust_range}

# hardware = Hardware()
# model = UnderstandModel(hardware)
# print model.find_unique()
