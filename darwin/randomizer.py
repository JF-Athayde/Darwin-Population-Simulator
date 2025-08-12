from math import tanh
from random import uniform
from darwin.utility import map_to_range, show_matriz
from tqdm import tqdm

def get_real_probability(cont, less_probability):
    if cont == 0:
        return less_probability

    prob_continue_all = 1
    for i in range(cont):
        prob_continue_all *= (1 - i * less_probability)
    
    prob_stop = cont * less_probability
    return prob_continue_all * prob_stop

def generate_random_number(less_probability):
    probability = 1
    check = True
    cont = 0

    while check:
        if not probability > uniform(0, 1):
            break

        cont += 1
        probability -= less_probability
    
    real_probability = get_real_probability(cont, less_probability)

    return cont, real_probability

def generate_normalized_number(bounds, less_probability):
    a, _ = generate_random_number(less_probability)
    a_normilized = map_to_range(a, 0, 1/less_probability, bounds[0], bounds[1])
    return a_normilized
