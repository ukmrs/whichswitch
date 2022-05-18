#!/usr/bin/env python3
from collections import defaultdict
from pprint import pprint


class Count:
    def __init__(self):
        self.total = 0
        self.correct = 0

    def __repr__(self):
        return f"{self.correct}/{self.total}"

    @property
    def acc(self):
        return self.correct / self.total

def get_stats():
    with open("predictions", "r") as pred, open("testset_ans", "r") as ans:
        tracker = defaultdict(Count)
        gen = (
            (p.rstrip(), a.rstrip()) for p, a in zip(pred.readlines(), ans.readlines())
        )

        for p, a in gen:
            tracker[a].total += 1
            tracker[a].correct += p == a

    return tracker


def main():
    tracker = get_stats()
    total, correct = 0, 0
    for k, v in tracker.items():
        total += v.total
        correct += v.correct
        print(f"{k}\t{v}\t{v.acc}")


    print(f"acc: {correct/total}")


if __name__ == "__main__":
    main()
