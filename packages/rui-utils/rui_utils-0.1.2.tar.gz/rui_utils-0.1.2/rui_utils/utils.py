import pickle
import time
from pathlib import Path

import numpy as np
from loguru import logger
from omegaconf import OmegaConf


def save_dict(dic: dict | OmegaConf, path: str) -> None:
    r"""
    Save the dict to as pkl/yaml format
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if ".pkl" in str(path):
        with open(path, "wb") as f:
            pickle.dump(dic, f)
    elif ".yaml" in str(path) or ".yml" in str(path):
        if isinstance(dic, dict):
            dic = OmegaConf.create(dic)
        dic.to_yaml(path)


def GetRunTime(func):
    r"""
    Decorator to get the run time of a function
    """

    def call_func(*args, **kwargs):
        begin_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        Run_time = end_time - begin_time
        logger.debug(f"{func.__name__} run time: {Run_time:.2f}s")
        return ret

    return call_func


def l2norm(mat: np.ndarray) -> np.ndarray:
    r"""
    L2 norm of numpy array
    """
    stats = np.sqrt(np.sum(mat**2, axis=1, keepdims=True)) + 1e-9
    mat = mat / stats
    return mat
