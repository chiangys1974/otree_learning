import numpy as np


def talents():
    return np.random.randint(0, 100, 3)

if __name__ == '__main__':
    print(talents())

print('1')