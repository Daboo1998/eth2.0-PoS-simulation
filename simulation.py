from math import sqrt
from typing import List
from numpy import median
import numpy as np
from numpy import uint64

from node import Node
from tester import Tester
import random
import csv
import time

ETH_IN_GWEI = 10**9

# From https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#integer_squareroot
def integer_squareroot(n: uint64) -> uint64:
    """
    Return the largest integer ``x`` such that ``x**2 <= n``.
    """
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


# Retrieved from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#rewards-and-penalties
# All the constants below are in Gwei (1 ETH = 1'000'000'000 Gwei)
BASE_REWARD_FACTOR = uint64(2**6)
WHISTLEBLOWER_REWARD_QUOTIENT = uint64(2**9)
PROPOSER_REWARD_QUOTIENT = uint64(2**3)
INACTIVITY_PENALTY_QUOTIENT = uint64(2**26)
MIN_SLASHING_PENALTY_QUOTIENT = uint64(2**7)
PROPORTIONAL_SLASHING_MULTIPLIER = uint64(1)


# Retrieved from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#misc
# All the constants below are in Gwei (1 ETH = 1'000'000'000 Gwei)
BASE_REWARDS_PER_EPOCH = uint64(4)

MAX_COMMITTEES_PER_SLOT = uint64(2**6)
SLOTS_PER_EPOCH = uint64(2**5)
TARGET_COMMITTEE_SIZE = uint64(2**7)


class Simulation:

    def __init__(self, stake_distribution, block_interval, number_of_proposers_per_choice):
        self.number_of_nodes = 0
        self.nodes = []
        self.number_of_proposers_per_choice = number_of_proposers_per_choice
        self.blocks = 0
        self.block_interval = block_interval
        self.initial_stakes = []

        for dist in stake_distribution:
            for i in range(0, dist[0]):
                if dist[1] < 32.0:
                    continue
                validator = Node(self.number_of_nodes, dist[1])
                self.number_of_nodes += 1
                self.nodes.append(validator)

    def get_total_stake(self):
        return uint64(sum([node.effective_balance for node in self.nodes]))

    def stakes(self):
        stakes = []
        stakes.append([node.stake for node in self.nodes])
        return stakes

    def select_proposers(self) -> List[Node]:
        self.number_of_proposers_per_choice = max(uint64(1), min(
            MAX_COMMITTEES_PER_SLOT,
            uint64(len(self.nodes) // SLOTS_PER_EPOCH // TARGET_COMMITTEE_SIZE),
        ))

        total_stake = self.get_total_stake()
        coins = random.sample(list(range(1, int(total_stake + 1))), self.number_of_proposers_per_choice)

        start_coins = 0
        end_coins = 0

        proposers = []

        for node in self.nodes:
            end_coins += node.effective_balance
            for coin in coins:
                if end_coins >= coin > start_coins:
                    proposers.append(node)
            start_coins = end_coins

        # prevent player from being chosen twice
        if len(proposers) != len(set(proposers)):
            proposers = self.select_proposers()

        return proposers

    #Slightly modified from https://github.com/ethereum/eth2.0-specs/blob/dev/specs/phase0/beacon-chain.md#helpers
    def get_base_reward(self, proposer):
        total_balance = self.get_total_stake()
        return proposer.effective_balance * ETH_IN_GWEI * BASE_REWARD_FACTOR // integer_squareroot(total_balance) // BASE_REWARDS_PER_EPOCH

    def generate_reward(self, proposer):
        return float(self.get_base_reward(proposer) // PROPOSER_REWARD_QUOTIENT) / ETH_IN_GWEI


    def run(self, steps, should_print_intermediate_states, experiment=None):
        self.print_state(0)
        run_at_time=time.time()

        for step in range(1, steps + 1):
            proposers = self.select_proposers()
            reward = 0
            rewards = []
            for proposer in proposers:
                reward = self.generate_reward(proposer)
                rewards.append(reward)
                new_stake = proposer.stake + reward
                proposer.update_effective_balance(new_stake)
                proposer.stake = new_stake


            self.print_state(step)

            experiment.collect(
                Tester.gini_coefficient(self.nodes),
                Tester.equitability(self.nodes),
                1 + step // self.block_interval,
                reward,
                self.get_total_stake()/self.number_of_nodes,
                median(self.stakes()),
                np.std(self.stakes())
            )
            with open('all_values_per_tick_eth.csv', mode='a') as value_file:
                value_writer = csv.writer(value_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
                value_writer.writerow([run_at_time, step, Tester.gini_coefficient(self.nodes), Tester.equitability(self.nodes), np.average(rewards), self.get_total_stake()/self.number_of_nodes / ETH_IN_GWEI, median(self.stakes()) / ETH_IN_GWEI,np.std(self.stakes())])

            total_stake = self.get_total_stake()

            [node.update_fractional_stake(total_stake) for node in self.nodes]

        if not should_print_intermediate_states:
            self.print_state(steps)
            pass

    def print_state(self, step):

        print(f'Step #{step}:')
        print()

        print(f'Equitability = {Tester.equitability(self.nodes)}')
        print(f"Gini coefficient = {Tester.gini_coefficient(self.nodes)}")
        print()

        for node in self.nodes:
            print(f"Node `{node.id}` has stake = {node.stake}")

        print()
        print('----------------')
