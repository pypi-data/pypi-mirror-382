import os
from heapq import nlargest

from loguru import logger


def select_free_gpu(n: int = 1) -> list[int] | None:
    r"""
    Get torch computation device automatically

    Parameters
    ----------
    n
        Number of GPUs to request

    Returns
    -------
    n_devices
        list of devices index
    """
    import pynvml

    assert n > 0
    try:
        pynvml.nvmlInit()
        devices = os.environ.get("CUDA_VISIBLE_DEVICES", None)
        devices = (
            range(pynvml.nvmlDeviceGetCount())
            if devices is None
            else [int(d.strip()) for d in devices.split(",") if d != ""]
        )
        free_mems = {
            i: pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(i)).free
            for i in devices
        }
        n_devices = nlargest(n, free_mems, free_mems.get)
        if len(n_devices) == 0:
            raise pynvml.NVMLError("GPU disabled.")
        logger.info(f"Using GPU {n_devices} as computation device.")
        # os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(map(str, n_devices))
        return n_devices
    except pynvml.NVMLError:  # pragma: no cover
        logger.warning("No GPU available.")
        return None


def is_rapids_ready() -> bool:
    try:
        import cupy
        import rmm

        RSC_FLAG = cupy.cuda.is_available() and rmm.is_initialized()
    except:  # noqa
        RSC_FLAG = False
        logger.warning("Rapids not available, use Scanpy")
    return RSC_FLAG


def manage_gpu(gpu_id: int, memory_strategy: str | None = None):
    r"""
    Manage Rapids GPU index and memory strategy
    """
    import cupy
    import rmm
    from rmm.allocators.cupy import rmm_cupy_allocator

    assert memory_strategy in ["large", "fast", "auto", None]
    if memory_strategy is not None:
        if memory_strategy == "large":
            managed_memory, pool_allocator = True, False
        elif memory_strategy == "fast":
            managed_memory, pool_allocator = False, True
        rmm.reinitialize(
            managed_memory=managed_memory,
            pool_allocator=pool_allocator,
            devices=gpu_id,
        )
    else:
        rmm.reinitialize(devices=gpu_id)
    cupy.cuda.set_allocator(rmm_cupy_allocator)
    cupy.cuda.Device(gpu_id).use()
    logger.info(f"Using GPU {gpu_id} and {memory_strategy} memory strategy.")
