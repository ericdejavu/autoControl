from libs import *
import json

class Lucius:
    def __init__(self):
        self.hardware = Hardware()
        self.name = self.hardware.name
        self.data_gen = DataGen(self.hardware)
        self.data_gen.run()
        self.train = Train(self.name)
        self.train.run()
        self.banchmark = TestCase(self.hardware)
        self.model = UnderstandModel(self.hardware)

    def create_model(self):
        self.banchmark.run_forward_analyse()
        unique_params = self.model.find_unique()
        return unique_params

    def run(self):
        params = self.create_model()
        if params:
            with open(PREFIX + self.name + POSTFIX_CONTROL_PARAMS_FILENAME,'a+') as f:
                f.write(str(params).replace('\'','\"')+'\n')
            print '[+] build success'
        else:
            print '[-] fail to create model'
        # {"wave_thread": 10, "wave_bias": 0.03175749431862978, "wave_adjust_range": [0.7, 3]}
        # {"wave_thread": 10, "wave_bias": 0.06815953604876822, "wave_adjust_range": [0.6712106357365845, 3]}
        self.banchmark.run_backward_analyse(params)
        self.hardware.end()

lucius = Lucius()
lucius.run()
