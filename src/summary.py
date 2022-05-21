#!/usr/bin/env python3
from collections import defaultdict
from pprint import pprint
from sklearn import metrics
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import argparse


def get_y_true_pred():
    with open("predictions", "r") as pred, open("testset_ans", "r") as ans:
        ypred = np.array([int(i) for i in pred.read().rstrip().split("\n")])
        ytrue = np.array([int(i) for i in ans.read().rstrip().split("\n")])
        return ytrue, ypred


def create_confusion_plot(ytrue, ypred, ribos):
    fig, ax = plt.subplots(dpi=200, figsize=(20, 14))
    cm = metrics.confusion_matrix(ytrue, ypred)
    normalized = metrics.confusion_matrix(ytrue, ypred, normalize="true")

    ax.imshow(normalized, cmap="viridis")

    ids = [i for i in range(1, ribos + 1)]

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(ids)), ids)
    ax.set_yticks(np.arange(len(ids)), ids)

    for i in range(len(ids)):
        for j in range(len(ids)):
            text = ax.text(j, i, cm[i, j], ha="center", va="center", color="grey")

    ax.set_title("confusion_matrix")
    fig.tight_layout()
    plt.savefig("confusion_matrix.png")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--window", type=int, default=6)
    parser.add_argument("-r", "--ribos", type=int, default=32)
    return parser.parse_args()


def main():
    args = get_args()
    ytrue, ypred = get_y_true_pred()

    create_confusion_plot(ytrue, ypred, args.ribos)
    report = metrics.classification_report(ytrue, ypred)
    cohen = metrics.cohen_kappa_score(ytrue, ypred)

    print(report)
    print(f"Cohen's Kappa score: {cohen}")


if __name__ == "__main__":
    main()
