import math

from simulation import Simulation
from experiment import Experiment
from numpy import random

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    nodes = [(100, 32.0)]

    epochs = 10
    block_interval = 210
    number_of_proposers_per_choice = 1

    steps = block_interval * epochs

    def handler(experiment):
        sim = Simulation(nodes, block_interval, number_of_proposers_per_choice)
        sim.run(steps=steps, should_print_intermediate_states=False, experiment=experiment)

    experiment = Experiment(block_interval, epochs, run_handler=handler)
    experiment.run(10)
    experiment.save()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
