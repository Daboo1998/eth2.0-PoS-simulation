import numpy as np
import csv


class Experiment:

    def __init__(self, block_interval, epochs, run_handler):
        self.run_count = -1
        self.equitabilities = []
        self.gini_cooefs = []
        self.block_intervals = []
        self.rewards = []
        self.average_stakes = []
        self.median_stakes = []
        self.sd_stakes = []
        self.block_interval = block_interval
        self.epochs = epochs
        self.run_handler = run_handler

    def run(self, runs):
        with open('all_values_per_tick_eth.csv', mode='a') as value_file:
            value_writer = csv.writer(value_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                      lineterminator='\n')
            value_writer.writerow(['run_at_time','step','GINI','EQUITABILITY', 'REWARD', 'average_stakes', 'median_stakes',  'sd_stakes'])

        while self.run_count < runs - 1:
            self.next_run()
            self.run_handler(self)

    def reset(self):
        self.run_count = 0
        self.equitabilities = []
        self.gini_cooefs = []
        self.block_intervals = []

        self.equitabilities.append([])
        self.block_intervals.append([])
        self.gini_cooefs.append([])
        self.rewards.append([])
        self.average_stakes.append([])
        self.median_stakes.append([])
        self.sd_stakes.append([])

    def save(self):
        with open('values.csv', mode='a') as value_file:
            value_writer = csv.writer(value_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
            value_writer.writerow(['run', 't','self.gini_cooefs', 'self.equitabilities',  'self.average_stakes', 'self.median_stakes',  'self.sd_stakes'])
            for r in range(len(self.gini_cooefs)):
                for t in range(len(self.gini_cooefs[0])):
                    value_writer.writerow([r,t, np.average(self.gini_cooefs[r][t]), np.average(self.equitabilities[0][t]), self.average_stakes[r][t], self.median_stakes[r][t], self.sd_stakes[r][t]])

        x = [n/self.block_interval for n in range(0, self.block_interval * self.epochs)]

        y = [np.array(lst) for lst in self.rewards]
        y = np.average(y, axis=0)
        with open('average_rewards.csv', mode='w') as value_file:
            value_writer = csv.writer(value_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
            value_writer.writerow(['x', 'y'])
            for i in range(len(x)):
                value_writer.writerow([x[i],y[i]])

        y = [np.array(lst) for lst in self.equitabilities]
        y = np.average(y, axis=0)
        with open('average_equitabilities.csv', mode='w') as value_file:
            value_writer = csv.writer(value_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
            value_writer.writerow(['x', 'y'])
            for i in range(len(x)):
                value_writer.writerow([x[i],y[i]])

        y = [np.array(lst) for lst in self.gini_cooefs]
        y = np.average(y, axis=0)
        with open('average_gini_cooefs.csv', mode='w') as value_file:
            value_writer = csv.writer(value_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
            value_writer.writerow(['x', 'y'])
            for i in range(len(x)):
                value_writer.writerow([x[i],y[i]])

    def collect(self, gini_coefficient, equitability, block_interval, reward, average_stake, median_stake, sd_stake ):
        self.gini_cooefs[self.run_count].append(gini_coefficient)
        self.equitabilities[self.run_count].append(equitability)
        self.block_intervals[self.run_count].append(block_interval)
        self.rewards[self.run_count].append(reward)
        self.average_stakes[self.run_count].append(average_stake)
        self.median_stakes[self.run_count].append(median_stake)
        self.sd_stakes[self.run_count].append(sd_stake)

    def next_run(self):
        self.run_count += 1
        self.equitabilities.append([])
        self.gini_cooefs.append([])
        self.block_intervals.append([])
        self.rewards.append([])
        self.average_stakes.append([])
        self.median_stakes.append([])
        self.sd_stakes.append([])
