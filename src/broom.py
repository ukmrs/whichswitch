#!/usr/bin/env python3

from pathlib import Path
import sys
import random
import itertools
from collections import namedtuple
from pprint import pprint
from functools import total_ordering
from sklearn.model_selection import train_test_split
import pandas as pd
from datetime import datetime
from typing import Optional
import argparse
import uuid


RIBODATA = Path("../ribodata/")
Seqstat = namedtuple("Seqstat", ["len", "max", "min", "avg"])


@total_ordering
class Riboclass:
    counter = 1
    header = "id\trf\tname\tlength\tmax\tmin\tavg\n"

    def __init__(self, file):
        self.id = Riboclass.counter
        Riboclass.counter += 1
        self.file = file
        self.rf = file.stem.split(".")[0]
        self.name: Optional[str] = None
        self.seqs = get_seqs(file)
        self.stats = get_stats(self.seqs)

    def __repr__(self):
        return f"{self.name} ({self.id}): {self.stats}"

    def __len__(self):
        return self.stats.len

    def __eq__(self, other):
        return len(self) == len(other)

    def __lt__(self, other):
        return len(self) < len(other)

    def tsvify(self):
        ln, mx, mn, avg = self.stats
        return f"{self.id}\t{self.rf}\t{self.name}\t{ln}\t{mx}\t{mn}\t{avg}"


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


def prepare_df(riboswitches, window):
    seq = []
    label = []
    for ribo in riboswitches:
        seq.extend((apply_window(seq, window) for seq in ribo.seqs))
        label.extend((ribo.id for _ in range(len(ribo))))

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


def make_run_dir(now):
    prefix = Path(now.strftime("wsrun_%d%m%Y%H%M%S"))

    try:
        prefix.mkdir()
        return prefix
    except FileExistsError:
        pass

    id = uuid.uuid4().hex
    prefix = Path(f"wsrun_{id}")
    print(f"moving to uuid instead: {id}", file=sys.stderr)
    prefix.mkdir()
    return prefix


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-w", "--window", type=int,
    )

    parser.add_argument(
        "-r", "--ribos", type=int,
    )

    parser.add_argument(
        "-s", "--seed",
    )

    return parser.parse_args()


def main():
    args = get_args()

    date_time = datetime.now()
    date_time_readable = date_time.strftime("%d/%m/%Y, %H:%M:%S")

    prefix = make_run_dir(date_time)

    ribos = [Riboclass(f) for f in RIBODATA.iterdir() if f.suffix == ".fa"]
    ribos.sort(reverse=True)

    assert len(ribos) >= args.ribos, "there aren't that many riboswitches files"

    with open(RIBODATA / "ribolist.info", "r") as info:
        gen = (line.rstrip().split("\t") for line in info.readlines())
        ribotable = {k: v for k, v in gen}
        for i, ribo in enumerate(ribos, start=1):
            ribo.id = i
            ribo.name = ribotable[ribo.rf]

    df = prepare_df(ribos[: args.ribos], args.window)

    try:
        seed = int(args.seed)
    except ValueError:
        seed = random.randint(0, 0xFFFFFFFF)

    train, test = train_test_split(df, test_size=0.25, random_state=seed)

    write_vorpal_file(train, prefix / "trainset")
    write_vorpal_test(test, prefix / "testset")

    with open(prefix / "run_info", "w") as f:
        f.write(
                f"date={date_time_readable}\nwindow={args.window}"
                f"\nribos={args.ribos}\nseed={seed}\n###\n"
        )
        f.write(Riboclass.header)
        for ribo in ribos[: args.ribos]:
            f.write(f"{ribo.tsvify()}\n")

    print(prefix)


if __name__ == "__main__":
    main()
