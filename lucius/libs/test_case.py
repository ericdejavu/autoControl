from hardware import Hardware
from const_str import *
from graph import Graph
import time,math,random
import tensorflow as tf
import json

class TestCase:
    def __init__(self, hardware):
        if not hardware:
            exit(1)
        self.name = hardware.name
        with open(PREFIX + self.name + POSTFIX_WEIGHT_FILENAME) as f:
            weights = json.loads(f.readline())
        w1 ,w2 = weights['w1'], weights['w2']
        self.forward = Forward(w1,w2, hardware)
        self.backward = Backward(w1,w2, hardware)

    def run_forward_analyse(self):
        return self.forward.run()

    def run_backward_analyse(self, unique_params):
        return self.backward.run(unique_params)

class Forward:
    def __init__(self,w1,w2,hardware):
        self.X = tf.placeholder(tf.float32, shape=(None,4), name='x-input')

        self.a = tf.matmul(self.X, w1)
        self.Y = tf.matmul(self.a, w2)

        self.w1, self.w2 = w1, w2

        self.hardware = hardware
        self.hardware.start()
        self.wave_set = []
        for i in range(20,101,20):
            a = [i / (1 + math.exp(-x*.2)) for x in range(-50,50)]
            b = a[:]
            b.reverse()
            a += b
            self.wave_set += a
        with open(PREFIX + self.hardware.name + POSTFIX_DT_FILENAME) as f:
            self.dt = float(f.readline())

    def run(self):
        s,l = 0,0
        pre_r,last_r = 0,0
        with tf.Session() as sess:
            init = tf.initialize_all_variables()
            sess.run(init)
            offset,x,y_p,y_r = 0,[],[],[]
            for i,wave in enumerate(self.wave_set[:int(len(self.wave_set)*.1)]):
                t = time.time()
                if wave > 100:
                    wave = 100
                elif wave < -100:
                    wave = -100
                self.hardware.send(wave)
                r = self.hardware.read()
                dt = t - time.time()
                last_r = pre_r
                pre_r = r
                pred_r = sess.run(self.Y, feed_dict={self.X:[[pre_r,last_r,wave,dt]]})[0][0]
                if r != 0:
                    print pred_r
                    offset += pred_r / r
                    l += 1
                time.sleep(self.dt)
            offset = offset / l
            print offset
            with open(PREFIX + self.hardware.name + POSTFIX_OFFSET_FILENAME,'wb') as f:
                f.write(str(offset))

            for i,wave in enumerate(self.wave_set):
                t = time.time()
                if wave > 100:
                    wave = 100
                elif wave < -100:
                    wave = -100
                self.hardware.send(wave)
                r = self.hardware.read()
                dt = t - time.time()
                last_r = pre_r
                pre_r = r
                pred_r = int(sess.run(self.Y, feed_dict={self.X:[[pre_r,last_r,wave,dt]]})[0][0] / offset)
                # x.append(i)
                # y_p.append(pred_r)
                # y_r.append(r)
                print pred_r,r
                if abs(pred_r - r) <= 1:
                    s += 1
                time.sleep(self.dt)

        print 'forward accuracy:',s / 10. ,'%'
        # graph = Graph()
        # graph.draw([[x,y_p,'b','pred'],[x,y_r,'g','real']])

        # time.sleep(1)
        # self.hardware.end()
        return s / 10


class Backward:
    def __init__(self,w1,w2,hardware):
        # [180 / (1 + math.exp(-x*.05)) for x in range(-200,200)]
        self.w1, self.w2 = w1, w2
        self.r_set = []
        for i in range(20,181,20):
            a = [i / (1 + math.exp(-x*.2)) for x in range(-50,50)]
            b = a[:]
            b.reverse()
            a += b
            self.r_set += a

        A = 90
        self.r_set += [A * math.sin(i*2 * math.pi / 180) + A for i in range(360)]
        self.r_set += [90 for i in range(300)]

        self.hardware = hardware
        self.hardware.start()
        with open(PREFIX + self.hardware.name + POSTFIX_DT_FILENAME) as f:
            self.dt = float(f.readline())

    def run(self, params):
        if not params:
            return
        sum_err = 0
        x,y_p,y_r,y_wave = [],[],[],[]
        pre_r,last_r = 0,0
        total_t = time.time()
        with open(PREFIX + self.hardware.name + POSTFIX_OFFSET_FILENAME) as f:
            offset = float(f.readline())
        with open(PREFIX + self.hardware.name + POSTFIX_DT_FILENAME) as f:
            dt = float(f.readline())
        move_pwm = params['wave_thread']
        left , right = -params['wave_adjust_range'][0], params['wave_adjust_range'][0]
        for i in range(len(self.r_set)):
            r = self.hardware.read()
            tmp = []
            for j in range(5):
                tmp.append((self.w1[0][j]*r + self.w1[1][j]*pre_r + self.w1[3][j]*dt) * self.w2[j][0])
            wave = (self.r_set[i] - sum(tmp) / offset) / sum(self.w1[2]) + params['wave_bias']
            print wave
            if right <= wave <= 3:
                wave = move_pwm
            elif left >= wave >= -3:
                wave = -move_pwm
            elif left <= wave <= right:
                wave = 0
            else:
                add = move_pwm
                wave = wave + add if wave > 0 else wave - add
            wave = int(wave)
            if wave > 100:
                wave = 100
            elif wave < -100:
                wave = -100
            self.hardware.send(wave)
            last_r = pre_r
            pre_r = r
            x.append(i)
            y_p.append(int(self.r_set[i]))
            y_r.append(r)
            y_wave.append(wave)
            print self.r_set[i],r
            time.sleep(self.dt)

        print time.time() - total_t
        graph = Graph()
        graph.draw([[x,y_p,'b','set'],[x[:-10],y_r[10:],'g','real']])

        time.sleep(1)
        self.hardware.end()


# hardware = Hardware()
# testCase = TestCase(hardware)
# testCase.run_forward_analyse()
# testCase.run_backward_analyse({"wave_thread": 10, "wave_bias": 0.03175749431862978, "wave_adjust_range": [0.7, 3]})
