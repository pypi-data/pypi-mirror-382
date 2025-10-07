import json
import matplotlib.pyplot as plt
import numpy as np

def plot_eta_over_time(log_file: str, unit: str = "seconds", save: str | None = None):
    with open(log_file) as f:
        data = json.load(f)
    key = f"eta_{unit}"
    etas = np.array([entry[key] for entry in data if key in entry])
    steps = np.arange(len(etas))

    plt.scatter(steps, etas, marker="o", alpha=0.7)
    plt.xlabel("Log entry index")
    plt.ylabel(f"ETA ({unit})")
    plt.title("ETA over log entries")
    plt.grid(alpha=0.3)
    if save:
        plt.savefig(save, bbox_inches="tight")
    else:
        plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", type=str, required=True)
    parser.add_argument("--unit", type=str, default="seconds")
    parser.add_argument("--save", type=str, default=None)
    args = parser.parse_args()
    plot_eta_over_time(args.log_file, args.unit, args.save)
