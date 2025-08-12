def map_to_range(x, min_val, max_val, a, b):
    x_norm = (x - min_val) / (max_val - min_val)
    return a + x_norm * (b - a)

def show_matriz(matriz):
    for line in matriz:
        print(line)

def mean(vector):
    return sum(vector)/len(vector)