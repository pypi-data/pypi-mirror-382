import random
from typing import Any


class WRandom:
    """weighted random"""

    def __init__(self, choices: list[tuple[Any, int]]):
        choices = [(item, weight) for item, weight in choices if weight > 0]
        self.num_choices = len(choices)
        self.items, weights = zip(*choices)
        total_weight = sum(weights)

        # normalize weights to scale with the number of choices
        scaled_probs = [w * self.num_choices / total_weight for w in weights]

        self.probability_table = [0.0] * self.num_choices
        self.alias_table = [0] * self.num_choices

        small = []  # indices of probabilities < 1
        large = []  # indices of probabilities >= 1

        for idx, prob in enumerate(scaled_probs):
            if prob < 1.0:
                small.append(idx)
            else:
                large.append(idx)

        while small and large:
            small_idx = small.pop()
            large_idx = large.pop()

            self.probability_table[small_idx] = scaled_probs[small_idx]
            self.alias_table[small_idx] = large_idx

            scaled_probs[large_idx] = scaled_probs[large_idx] - (
                1 - scaled_probs[small_idx]
            )
            if scaled_probs[large_idx] < 1.0:
                small.append(large_idx)
            else:
                large.append(large_idx)

        # handle leftover probabilities
        for leftover_idx in large + small:
            self.probability_table[leftover_idx] = 1.0
            self.alias_table[leftover_idx] = leftover_idx

    def choice(self) -> Any:
        # choose a random index and decide based on probability table
        idx = random.randint(0, self.num_choices - 1)
        if random.random() < self.probability_table[idx]:
            return self.items[idx]
        else:
            return self.items[self.alias_table[idx]]


if __name__ == "__main__":
    choice = input("choice > ")
    match choice:
        case "wrandom":
            from collections import Counter

            # Test 1: choice returns only given items
            choices = [("a", 1), ("b", 2), ("c", 3)]
            wr = WRandom(choices)
            for _ in range(100):
                result = wr.choice()
                assert result in ["a", "b", "c"], f"Unexpected item: {result}"
            print("Test 1 passed: only returns provided items")

            # Test 2: weighted distribution roughly matches expected probabilities
            counts = Counter(wr.choice() for _ in range(100_000))
            total = sum(counts.values())
            observed_probs = {k: v / total for k, v in counts.items()}
            total_weight = sum(w for _, w in choices)
            expected_probs = {item: weight / total_weight for item, weight in choices}

            for item in expected_probs:
                assert abs(observed_probs[item] - expected_probs[item]) < 0.01, (
                    f"Probability for {item} is off"
                )
            print("Test 2 passed: weighted distribution is correct")

            # Test 3: single choice
            wr_single = WRandom([("only", 10)])
            for _ in range(10):
                assert wr_single.choice() == "only"
            print("Test 3 passed: single choice always returned")

            # Test 4: equal weights
            items = ["x", "y", "z", "w"]
            wr_equal = WRandom([(item, 1) for item in items])
            counts = Counter(wr_equal.choice() for _ in range(10_000))
            for count in counts.values():
                assert abs(count - 2500) < 200  # allow some randomness
            print("Test 4 passed: equal weights roughly uniform")

            # Test 5: zero weight item (optional, depends on your logic)
            choices_zero = [("a", 0), ("b", 1), ("c", 3)]
            wr_zero = WRandom(choices_zero)
            counts = Counter(wr_zero.choice() for _ in range(50_000))
            assert counts["a"] == 0, "Zero-weight item appeared!"
            print("Test 5 passed: zero-weight item never chosen")

            print("All tests passed!")
