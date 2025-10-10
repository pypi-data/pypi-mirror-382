import tqdm
import math

BLOCK_WRITE_SIZE = 4096

class ListBuffer():
    """Use lists as a storage"""
    def __init__(self):
        self.__io = []

    def clear(self):
        old_val = self.value()
        self.__init__()
        return old_val

    def value(self):
        return "".join(self.__io)

    def write(self, symbol):
        self.__io.append(symbol)

def event_writer(prv_file, df, name, serialization_f):
    num_rows = df.shape[0]
    lbuffer = ListBuffer()
    for b in tqdm.tqdm(range(math.floor(num_rows / BLOCK_WRITE_SIZE)+1), desc="{} ({:.2E} events)".format(name, num_rows*2), unit="blocks"):
        limit = min(BLOCK_WRITE_SIZE, num_rows - b*BLOCK_WRITE_SIZE)
        for index in range(limit):
            row = df.iloc[index + b*BLOCK_WRITE_SIZE]
            lbuffer.write(serialization_f(row))
        prv_file.write(lbuffer.value())
        lbuffer.clear()