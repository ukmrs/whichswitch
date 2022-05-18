#!/usr/bin/env python3

from pathlib import Path
import sys
import itertools
from collections import namedtuple
from pprint import pprint
from functools import total_ordering
from sklearn.model_selection import train_test_split
import pandas as pd
from datetime import datetime
from string import ascii_lowercase
import random


RIBODATA = Path("../ribodata/")
WINDOW = 10
AMOUNT = 3
SEED = 8880

Seqstat = namedtuple("Seqstat", ["len", "max", "min", "avg"])


@total_ordering
class Riboclass:
    counter = 1

    def __init__(self, file):
        self.label = Riboclass.counter
        Riboclass.counter += 1
        self.file = file
        self.name = file.stem.split(".")[0]
        self.seqs = get_seqs(file)
        self.stats = get_stats(self.seqs)

    def __repr__(self):
        return f"{self.name} ({self.label}): {self.stats}"

    def __len__(self):
        return self.stats.len

    def __eq__(self, other):
        return len(self) == len(other)

    def __lt__(self, other):
        return len(self) < len(other)

    def tsvify(self):
        ln, mx, mn, avg = self.stats
        return f"{self.name}\t{self.label}\t{ln}\t{mx}\t{mn}\t{avg}"


def get_seqs(file):
    with open(file, "r") as f:
        return [line.rstrip() for line in f.readlines()[1::2]]


def get_stats(seqs):
    mx = float("-inf")
    mn = float("inf")
    total = 0
    for seq in seqs:
        lenseq = len(seq)
        mx = max(lenseq, mx)
        mn = min(lenseq, mn)
        total += lenseq

    assert total != 0

    avg = total / len(seqs)
    return Seqstat(len=len(seqs), max=mx, min=mn, avg=avg)


def prepare_df(riboswitches):
    seq = []
    label = []
    for ribo in riboswitches:
        seq.extend((apply_window(seq, WINDOW) for seq in ribo.seqs))
        label.extend((ribo.label for _ in range(len(ribo))))

    df = pd.DataFrame({"label": label, "seq": seq})

    return df


def apply_window(seq, win):
    x = 0 if len(seq) % win == 0 else 1
    return " ".join([seq[i * win : i * win + win] for i in range(len(seq) // win + x)])


def write_vorpal_file(df, filename):
    with open(filename, "w") as f:
        for _, (label, seq) in df.iterrows():
            f.write(f"{label} | {seq}\n")


def write_vorpal_test(df, filename):
    with open(filename, "w") as f, open(f"{filename}_ans", "w") as ans:
        for _, (label, seq) in df.iterrows():
            f.write(f"| {seq}\n")
            ans.write(f"{label}\n")


def main():

    date_time = datetime.now()
    date_time_readable = date_time.strftime("%d/%m/%Y, %H:%M:%S")
    prefix = Path(date_time.strftime("wsrun_%d%m%Y%H%M%S"))

    prefix.mkdir()

    ribos = [Riboclass(file) for file in RIBODATA.iterdir()]
    ribos.sort(reverse=True)

    for i, ribo in enumerate(ribos, start=1):
        ribo.label = i

    riboclass_amount = 3
    df = prepare_df(ribos[:riboclass_amount])

    train, test = train_test_split(df, test_size=0.2, random_state=SEED)

    write_vorpal_file(train, prefix / "trainset")
    write_vorpal_test(test, prefix / "testset")

    with open(prefix / "run_info", "w") as f:
        f.write(f"{date_time}\nwindow: {WINDOW}\nRIBOS:\n")
        for ribo in ribos[:riboclass_amount]:
            f.write(f"{ribo.tsvify()}\n")

    print(prefix)


if __name__ == "__main__":
    main()
