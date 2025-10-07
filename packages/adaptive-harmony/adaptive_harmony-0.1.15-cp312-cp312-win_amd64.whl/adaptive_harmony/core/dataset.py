from adaptive_harmony import StringThread
from typing import Callable, Sequence
from datasets import load_dataset
import numpy as np


class DataSet[T]:
    def __init__(self, threads: Sequence[T], allow_looping: bool = False):
        self.threads = threads
        self.allow_looping = allow_looping
        # This will be used to shuffle the dataset when we cross the epoch boundary, initially it is just the indices of the threads
        # to respect the given order in the first epoch
        self.access_indices = np.random.permutation(np.arange(len(threads)))
        self.idx = 0

    def __iter__(self) -> "DataSet":
        return self

    def __len__(self) -> int:
        return len(self.threads)

    def __next__(self) -> T:

        if not self.allow_looping and self.idx == len(self.threads):
            raise StopIteration()
        elif self.allow_looping and self.idx == len(self.access_indices):
            self.access_indices = np.concatenate([self.access_indices, np.random.permutation(len(self.threads))])

        sample_idx = self.access_indices[self.idx]
        ret = self.threads[sample_idx]
        self.idx += 1
        return ret

    def __getitem__(self, x):
        return self.threads.__getitem__(x)

    def completion_percentage(self) -> float:
        """If dataset is looping, this can return a value greater than 1.0. Handle in recipe."""
        return self.idx / len(self.threads)

    def reset(self):
        self.idx = 0


def convert_sample_dict(
    turns_key: str | None = "messages", role_key="role", content_key="content", trim_final_assistant_turns=False
):
    def f(dialogue: dict) -> StringThread:
        if turns_key is not None:
            dialogue = dialogue[turns_key]
        turns = [(turn[role_key], turn[content_key]) for turn in dialogue]

        if trim_final_assistant_turns:
            while len(turns) > 0 and turns[-1][0] == "assistant":
                turns = turns[:-1]

        return StringThread(turns)

    return f


def load_from_hf(repo: str, split: str, convert_sample_fn: Callable[..., StringThread]) -> list[StringThread]:
    dataset = load_dataset(repo, split=split, keep_in_memory=True)
    dataset = dataset.select(range(len(dataset)))  # type: ignore
    return [convert_sample_fn(x) for x in dataset]
