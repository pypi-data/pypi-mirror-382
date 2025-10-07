import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData
from joblib import Parallel, delayed
from loguru import logger

from .gpu import is_rapids_ready, manage_gpu, select_free_gpu


def harmony_pytorch(emb: np.ndarray, obs: pd.DataFrame, batch_key: str, seed: int) -> np.ndarray:
    r"""
    Run `harmony` in pytorch version

    Parameters
    ----------
    emb
        Embedding matrix (such as PCA)
    obs
        `obs` of AnnData
    batch_key
        Batch information column in `obs`
    seed
        Random seed
    """
    import torch

    try:
        from harmony import harmonize
    except ImportError:
        raise ImportError("Please install `harmony-pytorch` package first.")
    GPU_FLAG = True if torch.cuda.is_available() and emb.shape[0] > 2e3 else False
    if GPU_FLAG:
        logger.warning("Use GPU for harmony")
    return harmonize(
        emb,
        obs,
        batch_key=batch_key,
        random_state=seed,
        max_iter_harmony=30,
        use_gpu=GPU_FLAG,
    )


def gex_embedding(
    adata: AnnData,
    method: str = "pca",
    filter: bool = False,
    min_gene: int = 100,
    min_cell: int = 30,
    batch_key: str | None = None,
    call_hvg: bool = True,
    n_top_genes: int = 2000,
    hvg_by_batch: bool = False,
    hvg_only: bool = False,
    save_log: bool = False,
    n_comps: int = 50,
    seed: int = 0,
    viz: bool = True,
    disable_rapids: bool = False,
    rapids_after_scale: bool = True,
    approx: bool = False,
    resolution: float | list[float] = 0.5,
    expect_cell_types_num: int = None,
    retry_num: int = 5,
    harmony_version: str = "torch",
    emb_only: bool = False,
    gpu_id: str | int = "auto",
    memory_strategy: str | None = None,
) -> AnnData:
    r"""
    Gene expression embedding via Scanpy pipeline

    Parameters
    ----------
    adata
        AnnData object
    method
        method for embedding, `pca` or `harmony`
    filter
        If filter cells and genes, default is False
    min_gene
        Minimum number of genes for each cell
    min_cell
        Minimum number of cells for each gene
    batch_key
        Key for batch information
    call_hvg
        If call highly variable genes, default is True
    n_top_genes
        Number of top genes, default is 2000
    hvg_by_batch
        If call HVG by batch, default is False
    hvg_only
        If subset HVG of adata only, default is True
    save_log
        If save log1p data to adata.layers["log1p"] for DE genes calling, default is False
    n_comps
        Number of components for PCA, default is 50
    seed
        Random seed
    viz
        If visualize the embedding, default is True
    disable_rapids
        If forbid rapids, default is False
    rapids_after_scale
        If use rapids after scale, default is False, should set to True on large dataset
    approx
        If use approximate nearest neighbors, default is False
    resolution
        Resolution(s) for leiden clustering, default is 0.8, can be a list for multiple resolutions
    expect_cell_types_num
        Expected number of cell types, default is None
    retry_num
        Number of retries for leiden clustering to approach the expected number of cell types
    harmony_version
        Version of harmony, `torch` or `rapids`, default is `torch`
    emb_only
        If return embedding only, default is False
    gpu_id
        GPU index, default is `auto`
    memory_strategy
        Memory strategy for Rapids, `large` or `fast`, default is None

    Warning
    ----------
    Input can not be the View of anndata
    """
    logger.info("Gene expression embedding...")
    assert method.lower() in ["pca", "harmony"], f"Method {method} not supported"
    if batch_key is not None:
        method = "harmony"
        logger.info(f"Use {method} for batch correction.")

    disable_rapids = disable_rapids if is_rapids_ready() else True
    if not disable_rapids:
        import rapids_singlecell as rsc
        import rmm

        if gpu_id == "auto":
            gpu_id = select_free_gpu(1)[0]
        else:
            assert isinstance(gpu_id, int), "Invalid gpu_id"
        manage_gpu(gpu_id, memory_strategy)

    if filter:
        raw_cell, raw_genes = adata.n_obs, adata.n_vars
        sc.pp.filter_cells(adata, min_genes=min_gene)
        sc.pp.filter_genes(adata, min_cells=min_cell)
        logger.info(f"Filter {raw_cell - adata.n_obs} cells and {raw_genes - adata.n_vars} genes")

    sc_ = sc  # default backend is scanpy
    if not rapids_after_scale:
        rsc.get.anndata_to_GPU(adata)
        sc_ = rsc

    call_hvg = call_hvg and adata.n_vars > n_top_genes
    if call_hvg:
        if isinstance(n_top_genes, int):
            sc_.pp.highly_variable_genes(
                adata,
                n_top_genes=n_top_genes,
                flavor="seurat_v3",
                batch_key=batch_key if hvg_by_batch else None,
            )
        elif isinstance(n_top_genes, list):
            adata.var["highly_variable"] = False
            n_top_genes = list(set(adata.var.index).intersection(set(n_top_genes)))
            adata.var.loc[n_top_genes, "highly_variable"] = True
            logger.warning(f"{len(n_top_genes)} genes detected given lists.")
    else:
        logger.warning("All genes are seen as highly variable genes.")
        adata.var["highly_variable"] = True

    if hvg_only:
        adata = adata[:, adata.var["highly_variable"]]

    sc_.pp.normalize_total(adata, target_sum=1e4)
    sc_.pp.log1p(adata)
    # save log
    if save_log:
        adata.layers["log1p"] = adata.X.copy()

    sc_.pp.scale(adata, max_value=10)  # Use a lot GPU memory
    if rapids_after_scale and not disable_rapids:
        rsc.get.anndata_to_GPU(adata)
        sc_ = rsc

    sc_.pp.pca(adata, n_comps=n_comps)
    if method.lower() == "pca":
        adata.obsm["X_gex"] = adata.obsm["X_pca"]
    elif method.lower() == "harmony":
        if harmony_version == "rapids":
            rsc.pp.harmony_integrate(adata, key=batch_key)
            adata.obsm["X_gex"] = adata.obsm["X_pca_harmony"]
        elif harmony_version in ["pytorch", "torch"]:
            adata.obsm["X_gex"] = harmony_pytorch(adata.obsm["X_pca"], adata.obs, batch_key, seed)

    if emb_only:
        return adata.obsm["X_gex"]

    if viz:
        neighbors_kwargs = {}
        if approx and sc_ is not sc:
            neighbors_kwargs["algorithm"] = "cagra"
        sc_.pp.neighbors(adata, use_rep="X_gex", **neighbors_kwargs)

        if expect_cell_types_num is not None:
            i = 0
            res = resolution if isinstance(resolution, float) else resolution[0]
            diff = 1e7  # big number
            while i < retry_num:
                sc_.tl.leiden(adata, resolution=res)
                cls_num = adata.obs["leiden"].nunique()
                adata.obs[f"leiden_{res}"] = adata.obs["leiden"].copy()
                logger.debug(f"Leiden resolution {res}: {cls_num} clusters")
                if cls_num > expect_cell_types_num:
                    new_res = res - 0.1 * (0.8**i)
                elif cls_num < expect_cell_types_num:
                    new_res = res + 0.1 * (0.8**i)
                else:
                    break
                if abs(cls_num - expect_cell_types_num) <= diff:
                    diff = abs(cls_num - expect_cell_types_num)
                    res = new_res
                res = max(res, 0.05)
                i += 1
            adata.obs["leiden"] = adata.obs[f"leiden_{res}"].copy()
        else:
            if isinstance(resolution, float):
                resolution = [resolution]
            for res in resolution:
                sc_.tl.leiden(adata, resolution=res)
                adata.obs[f"leiden_{res}"] = adata.obs["leiden"].copy()
        sc_.tl.umap(adata)

    if sc_ is not sc:
        sc_.get.anndata_to_CPU(adata)
        rmm.reinitialize()
    return adata.copy()


def _scanpy_viz(
    adata: AnnData,
    gpu_id: int,
    rapids: bool = True,
    memory_strategy: str = None,
    approx: bool = False,
    leiden: bool = True,
    resolution: float = 0.5,
    n_neighbors: int = 15,
) -> tuple[np.ndarray, np.ndarray | None]:
    neighbor_kwargs = dict(n_neighbors=n_neighbors, use_rep="X")
    if approx == "auto":
        approx = True if adata.n_obs > 1e4 else False
    assert isinstance(approx, bool), "Invalid approx"
    if rapids:
        import rapids_singlecell as rsc

        sc_ = rsc
        manage_gpu(gpu_id, memory_strategy)
        rsc.get.anndata_to_GPU(adata)
        logger.debug("Use rapids for visualization.")
        neighbor_kwargs["algorithm"] = "cagra" if approx else "brute"
    else:
        sc_ = sc

    sc_.pp.neighbors(adata, **neighbor_kwargs)
    sc_.tl.umap(adata)
    umap = adata.obsm["X_umap"]
    if leiden:
        sc_.tl.leiden(adata, resolution=resolution)
    leiden = adata.obs["leiden"].values if leiden else None
    return umap, leiden


def scanpy_viz(
    adata: AnnData,
    keys: list[str] = ["center", "nbr"],
    gpu_id: int | list = None,
    resolution: float = 0.5,
    rapids: bool = True,
    approx: bool | str = "auto",
    memory_strategy: str | None = None,
    leiden: bool = True,
    n_neighbors: int = 15,
    parallel: bool = True,
) -> sc.AnnData:
    r"""
    Fast clustering and visualization via scanpy/rapids

    Parameters
    -----------
    adata
        AnnData object
    keys
        Keys for visualization, should match the keys in `adata.obsm[X_{key}]`
    gpu_id
        GPU index, default is None
    resolution
        Resolution for leiden clustering, default is 0.5
    rapids
        If use rapids for visualization, default is True
    approx
        If use approximate nearest neighbors, default is False
    memory_strategy
        Memory strategy for Rapids, `large` or `fast`, default is None
    leiden
        If use leiden clustering, default is True
    n_neighbors
        Number of neighbors, default is 15
    parallel
        parallel computation, default is True
    """
    kwargs = dict(
        resolution=resolution,
        rapids=rapids,
        memory_strategy=memory_strategy,
        approx=approx,
        leiden=leiden,
        n_neighbors=n_neighbors,
    )
    RSC_FLAG = is_rapids_ready()

    # make agency adata
    viz_adatas = []
    keys = [keys] if isinstance(keys, str) else keys
    for key in keys:
        if key.lower() == "x":
            viz_adatas.append(adata.copy())
        elif f"X_{key}" in adata.obsm.keys():
            viz_adatas.append(sc.AnnData(X=adata.obsm[f"X_{key}"].copy()))
        else:
            logger.warning(f"Key {key} not in adata.obsm, skip.")

    # select n gpus
    if RSC_FLAG and rapids:
        if gpu_id is None:
            gpu_ids = select_free_gpu(len(viz_adatas))
            if len(gpu_ids) < len(viz_adatas):
                gpu_ids = np.random.choice(gpu_ids, len(viz_adatas), replace=True).tolist()
        elif isinstance(gpu_id, int):
            gpu_ids = [gpu_id] * len(viz_adatas)
        elif isinstance(gpu_id, list):
            gpu_ids = gpu_id
        else:
            raise ValueError(f"Invalid gpu_id type: {type(gpu_id)}")
    else:
        gpu_ids = [None] * len(viz_adatas)
    assert len(gpu_id) == len(viz_adatas)

    # parallel computation
    if not parallel or len(viz_adatas) > 1:
        results = [
            _scanpy_viz(_adata, _gpu_id, **kwargs) for _adata, _gpu_id in zip(viz_adatas, gpu_ids)
        ]
    else:
        results = Parallel(n_jobs=len(viz_adatas))(
            delayed(_scanpy_viz)(_adata, gpu_id, **kwargs)
            for _adata, gpu_id in zip(viz_adatas, gpu_ids)
        )
    umaps, leidens = zip(*results)

    for key, umap, leiden in zip(keys, umaps, leidens):
        adata.obsm[f"X_umap_{key}"] = umap
        if leiden is not None:
            adata.obs[f"leiden_{key}"] = leiden
    if RSC_FLAG:
        import rmm

        rmm.reinitialize()
    return adata


def clip_umap(array, percent: float = 0.1):
    r"""
    Clip the outlier to the percentile range of UMAP

    Parameters
    ----------
    array
        UMAP array
    percent
        Percentile for clipping, default is 0.1
    """
    assert 0 < percent < 50
    half_percent = percent / 2
    percentile_down = np.percentile(array, half_percent, axis=0)
    percentile_up = np.percentile(array, 100 - half_percent, axis=0)
    return np.clip(array, a_min=percentile_down, a_max=percentile_up)
