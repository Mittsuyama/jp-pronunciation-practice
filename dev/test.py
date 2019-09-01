import math


def rembGraph():
    a = 0.0
    for i in range(1, 100):
        b = math.exp(-(i - 1)/5)
        a += b
        if a >= 1:
            print(i, a)
            a = 0


if __name__ == "__main__":
    rembGraph()
