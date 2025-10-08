#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.11"
# dependencies = [
#     "numpy",
# ]
# ///

from multiprocessing import Pool, current_process
from multiprocessing.shared_memory import SharedMemory
import math
import numpy as np
import numpy.typing as npt

class SharedArray:
    _shm: SharedMemory
    _shape: tuple[int, ...]
    _dtype: str
    _array: npt.NDArray

    def __init__(self, shape: tuple[int, ...], dtype: str):
        size = math.prod(shape) * np.dtype(dtype).itemsize
        self._shm = SharedMemory(create=True, size=size)
        self._shape = shape
        self._dtype = dtype
        self._array = np.ndarray(shape, dtype, buffer=self._shm.buf)

    def __array__(self):
        return self._array

    def __getitem__(self, key):
        return self._array.__getitem__(key)

    def __setitem__(self, key, value):
        return self._array.__setitem__(key, value)

    def __len__(self):
        return self._array.__len__()

    @property
    def shape(self):
        return self._shape

    def __str__(self):
        return self._array.__str__()

    def __getstate__(self):
        return {
            '_shm': self._shm,
            '_shape': self._shape,
            '_dtype': self._dtype
        }

    def __setstate__(self, state):
        self._shm = state['_shm']
        self._shape = state['_shape']
        self._dtype = state['_dtype']
        self._array = np.ndarray(
            self._shape,
            dtype=self._dtype,
            buffer=self._shm.buf
        )

    def __del__(self):
        self._shm.close()

    def delete(self):
        self._shm.unlink()

def worker(arr):
    process = current_process()
    pid = process.pid or -1
    arr[pid % len(arr)] = pid


def main():
    arr = SharedArray((4,), dtype='i8')
    arr[:] = [1, 2, 3, 4]
    with Pool(processes=4) as pool:
        pool.map(worker, [arr, arr, arr, arr])
    print(arr)
    arr.delete()


if __name__ == "__main__":
    main()
