import time
import warnings
warnings.simplefilter('ignore')

def math_is_hard(N):
    x = 0
    while x < N:
        time.sleep(1)
        yield x * x
        x += 1
