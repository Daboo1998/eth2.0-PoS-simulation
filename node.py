from numpy import uint64

ETH_IN_GWEI = 10**9
MAX_EFFECTIVE_BALANCE = 2**5 * ETH_IN_GWEI
EFFECTIVE_BALANCE_INCREMENT = 1 * ETH_IN_GWEI
HYSTERESIS_QUOTIENT = uint64(4)
HYSTERESIS_DOWNWARD_MULTIPLIER = uint64(1)
HYSTERESIS_UPWARD_MULTIPLIER = uint64(5)

class Node:
    def __init__(self, id: int, initial_stake: uint64):
        self.id = id
        self.stake = initial_stake
        self.initial_stake = initial_stake
        self.initial_fractional_stake = 0
        self.fractional_stake = 0
        self.effective_balance = min(initial_stake * ETH_IN_GWEI, MAX_EFFECTIVE_BALANCE) // ETH_IN_GWEI

    def set_initial_fractional_stake(self, total_stake):
        self.initial_fractional_stake = self.initial_stake / total_stake
        self.fractional_stake = self.initial_fractional_stake

    def update_fractional_stake(self, total_stake):
        self.fractional_stake = self.stake / total_stake

    def update_effective_balance(self, new_stake):
        HYSTERESIS_INCREMENT = uint64(EFFECTIVE_BALANCE_INCREMENT // HYSTERESIS_QUOTIENT)
        DOWNWARD_THRESHOLD = HYSTERESIS_INCREMENT * HYSTERESIS_DOWNWARD_MULTIPLIER
        UPWARD_THRESHOLD = HYSTERESIS_INCREMENT * HYSTERESIS_UPWARD_MULTIPLIER

        if (
                new_stake + DOWNWARD_THRESHOLD < self.effective_balance
                or self.effective_balance + UPWARD_THRESHOLD < new_stake
        ):
            self.effective_balance = min(new_stake - new_stake % EFFECTIVE_BALANCE_INCREMENT, MAX_EFFECTIVE_BALANCE)





