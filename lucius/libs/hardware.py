import serial.tools.list_ports
SERIAL_NAME = '/dev/ttyUSB0'

class Hardware:
    def __init__(self):
        self.serialFd = serial.Serial(SERIAL_NAME, 115200, timeout=60)
        self.name = self.refresh_name()

    def send(self,out):
        out = str(int(out))+'\r\n'
        self.serialFd.write(out)


    def read(self):
        text = self.serialFd.readline().split(',')
        result = 0
        try:
            result = int(text[0])
        except:
            result = text[0].replace('\r\n','')
        return result

    def end(self):
        self.serialFd.write('0\r\n')

    def start(self):
        self.serialFd.write('0\r\n')
        return self.read()

    def rollback_send(self,out):
        self.read()
        self.send(out)

    # 1000 -> get_name
    def refresh_name(self):
        self.serialFd.write('1000\r\n')
        text = ''
        for i in range(100):
            text = self.read()
            if type(text) == type(' '):
                break
        return text
