import tensorflow as tf
from const_str import *
from hardware import Hardware
import json,os

class Train:
    # 4x5x1
    def __init__(self, name = ''):
        self.name = name
        self.w1 = tf.Variable(tf.random_normal([4,5],stddev=1,seed=1))
        self.w2 = tf.Variable(tf.random_normal([5,1],stddev=1,seed=1))

        self.X = tf.placeholder(tf.float32, shape=(None,4), name='x-input')
        self.Y_ = tf.placeholder(tf.float32, shape=(None,1), name='y-input')

        self.a = tf.matmul(self.X, self.w1)
        self.Y = tf.matmul(self.a, self.w2)

        self.cross_entropy = -tf.reduce_mean(self.Y_ * tf.log(tf.clip_by_value(self.Y, 1e-10, 1.0)))
        self.train_step = tf.train.AdamOptimizer(0.001).minimize(self.cross_entropy)

        self.BATCH = 500

        self.data_X = []
        self.data_Y = []

    def readfile(self, filename):
        dts = []
        with open(filename) as f:
            lines = f.readlines()
            for i,line in enumerate(lines):
                if i == len(lines)-1:
                    break
                datas = [float(data) for data in line.split(',')]
                dts.append(float(line.split(',')[4]))
                next_datas = [float(data) for data in lines[i+1].split(',')]
                self.data_X.append(datas[1:])
                self.data_Y.append([next_datas[0]])
        with open(PREFIX + self.name + POSTFIX_DT_FILENAME, 'wb') as f:
            f.write(str(sum(dts) / len(dts)))

    def run(self):
        self.readfile(PREFIX + self.name + POSTFIX_MODEL_TRAINING_DATA_FILENAME)
        print len(self.data_X)

        STEP = ( len(self.data_X) - 1 ) / self.BATCH
        precent = STEP * .1

        with tf.Session() as sess:
            init = tf.initialize_all_variables()
            sess.run(init)
            sess.run(self.w1)
            sess.run(self.w2)
            result = 100
            while result > 5e-3:
                for i in range(STEP + 1):
                    start = (i * self.BATCH) % len(self.data_X)
                    end = min(start + self.BATCH,len(self.data_X))
                    sess.run(self.train_step, feed_dict={self.X:self.data_X[start:end],self.Y_:self.data_Y[start:end]})
                    if i % int(precent) == 0:
                        result = sess.run(self.cross_entropy, feed_dict={self.X:self.data_X,self.Y_:self.data_Y})
                        print '[train] process at', i * 100. / STEP, '% :', result
                train_w1, train_w2 = [list(i) for i in list(sess.run(self.w1))], [list(i) for i in list(sess.run(self.w2))]
                weights_str = str({"w1":train_w1,"w2":train_w2}).replace('\'','\"')
                with open(PREFIX + self.name + '_tmp'+ POSTFIX_WEIGHT_FILENAME, 'wb') as f:
                    f.write(weights_str+'\n')
            weights_str = str({"w1":train_w1,"w2":train_w2}).replace('\'','\"')
            print weights_str
            lines = ''
            if os.path.exists(PREFIX + self.name + POSTFIX_WEIGHT_FILENAME):
                with open(PREFIX + self.name + POSTFIX_WEIGHT_FILENAME) as f:
                    lines = '\n'.join(f.readlines())
            with open(PREFIX + self.name + POSTFIX_WEIGHT_FILENAME, 'wb') as f:
                f.write(weights_str+'\n')
                f.write(lines)

# hardware = Hardware()
# train = Train(hardware.name)
# train.run()
