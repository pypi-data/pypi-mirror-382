r"""
Trainer
"""
import time
from pathlib import Path

import ray
import torch
from loguru import logger
from omegaconf import OmegaConf
from pytorch_lightning import LightningDataModule, LightningModule, Trainer
from pytorch_lightning.callbacks import (
    Callback,
    EarlyStopping,
    LearningRateMonitor,
    ModelCheckpoint,
    TQDMProgressBar,
)
from pytorch_lightning.loggers import TensorBoardLogger
from torch.utils.data import DataLoader
from tqdm import tqdm

from ..gpu import select_free_gpu


def init_trainer(config: OmegaConf, callback: list[Callback] = None, plugins=None) -> Trainer:
    r"""
    Init pytorch lightning trainer
    """
    n_gpus = torch.cuda.device_count()
    # save dir
    model_dir = Path(config.model_dir)
    if n_gpus <= 1 or ray.is_initialized():  # CPU or ray
        devices = "auto"
    elif config.device_num == 1 and config.select_gpu:  # single GPU
        devices = select_free_gpu(1)
    else:  # DDP
        devices = config.device_num
    # callbacks
    progress_bar = TQDMProgressBar(refresh_rate=1)
    monitor_stage = "val" if config.have_val else "train"
    early_stop = EarlyStopping(
        monitor=f"{monitor_stage}/total_loss", patience=config.patient, verbose=True
    )
    model_checkpoint = ModelCheckpoint(
        dirpath=model_dir,
        monitor=f"{monitor_stage}/total_loss",
        mode="min",
        save_top_k=3,
        verbose=True,
        every_n_epochs=1,
        save_on_train_epoch_end=True,
    )
    lr_monitor = LearningRateMonitor(logging_interval="step")
    callback_list = [progress_bar, early_stop, model_checkpoint, lr_monitor]
    if callback is not None:
        callback_list.extend(callback)

    # precision
    if config.fp16:
        precision = "16-mixed" if config.device != "cpu" else "bf16-mixed"
    else:
        precision = "32-true"
    logger.debug(f"Run model with precision {precision}")
    # strategy
    if n_gpus > 1 and config.device_num > 1:
        strategy = "ddp"
        ddp_kwags = dict(
            find_unused_parameters=False, sync_batchnorm=True, use_distributed_sampler=True
        )
    else:
        strategy = "auto"
        ddp_kwags = {}
    # logger
    pl_logger = TensorBoardLogger(save_dir=model_dir, default_hp_metric=False)

    # init trainer
    return Trainer(
        accelerator=config.device,
        devices=devices,
        callbacks=callback_list,
        precision=precision,
        default_root_dir=model_dir,
        strategy=strategy,
        gradient_clip_val=config.gradient_clip_val,
        logger=pl_logger,
        log_every_n_steps=config.log_every_n_steps,
        max_epochs=config.epochs,
        check_val_every_n_epoch=config.check_val_every_n_epoch,
        plugins=plugins,
        max_steps=config.max_steps,
        detect_anomaly=config.detect_anomaly,
        num_sanity_val_steps=config.num_sanity_val_steps,
        **ddp_kwags,
    )


def fit(
    model: LightningModule,
    data: DataLoader | list[DataLoader] | LightningDataModule,
    config: OmegaConf = None,
    return_model_path: bool = False,
    show_name: str = "",
    callback: list[Callback] | None = None,
    plugins=None,
    trainer: Trainer = None,
) -> str | None:
    r"""
    Model training
    """
    trainer = init_trainer(config, callback, plugins) if trainer is None else trainer
    start_time = time.time()
    logger.info(f"Start training {show_name} model.")

    model.train()
    if isinstance(data, LightningDataModule):
        trainer.fit(model, datamodule=data)
    elif isinstance(data, list):
        if len(data) == 3:
            trainer.fit(model, train_dataloaders=data[0], val_dataloaders=data[1])
        else:
            trainer.fit(model, train_dataloaders=data[0])
    elif isinstance(data, DataLoader):
        trainer.fit(model, train_dataloaders=data)
    else:
        raise TypeError(f"Data type {type(data)} is not supported yet.")

    logger.success(f"Train finished in {time.time() - start_time:.2f}s.")
    if return_model_path:
        return trainer.checkpoint_callback.best_model_path


def inference(
    model: LightningModule,
    data: DataLoader | LightningDataModule,
    use_trainer: bool = False,
    config: OmegaConf = None,
    trainer: Trainer = None,
) -> None:
    r"""
    Model inference only
    """
    if not use_trainer:
        _manual_inference(model, data)
        return
    trainer = init_trainer(config) if trainer is None else trainer
    if isinstance(data, LightningDataModule):
        trainer.test(model, datamodule=data)
    elif isinstance(data, DataLoader):
        trainer.test(model, dataloaders=data)
    elif isinstance(data, list):
        assert len(data) > 1
        trainer.test(model, dataloaders=data[-1])
    else:
        raise TypeError(f"Type {type(data)} is not supported yet.")


def _manual_inference(
    model: LightningModule,
    data: DataLoader | LightningDataModule,
) -> None:
    r"""
    Manual inference without trainer
    """
    if isinstance(data, LightningDataModule):
        dataloader = data.test_dataloader()
    else:
        dataloader = data
    device = select_free_gpu(1)
    if device is not None:
        if ray.is_initialized():
            device = torch.device("cuda")
        else:
            device = torch.device(f"cuda:{device[0]}")
    else:
        device = torch.device("cpu")
    model = model.to(device)
    logger.debug(f"Inferring on device: {device}")
    with torch.inference_mode():
        model.eval()
        for batch in tqdm(dataloader):
            if isinstance(batch, tuple) or isinstance(batch, list):
                batch = [v.to(device) for v in batch]
            elif isinstance(batch, dict):
                batch = {k: v.to(device) for k, v in batch.items()}
            elif isinstance(batch, torch.Tensor):
                batch = batch.to(device)
            model.test_step(batch, 0)


def fit_and_inference(
    model: LightningModule,
    data: list[DataLoader] | LightningDataModule,
    config: OmegaConf,
    show_name: str = "",
    callback: list[Callback] | None = None,
    plugins=None,
) -> None:
    r"""
    Model training and inference
    """
    trainer = init_trainer(config, callback, plugins)
    fit(model, data, trainer=trainer, show_name=show_name)
    inference(model, data, trainer=trainer)
