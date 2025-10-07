from bergson.data import merge_shards, load_gradient_dataset
from pathlib import Path

merge_shards(Path("runs/10b-test"), out_dir=Path("runs/10b-merged"), remove_shards=False)


# Load the dataset
breakpoint()
# ds = load_gradient_dataset("runs/10b-merged")
# print(ds)

