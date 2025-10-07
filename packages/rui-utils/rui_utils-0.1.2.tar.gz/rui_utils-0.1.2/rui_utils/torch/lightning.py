from abc import ABC

import numpy as np
from loguru import logger
from omegaconf import OmegaConf
from pytorch_lightning import LightningDataModule, LightningModule
from torch import Tensor, nn
from torch.optim import Adam
from torch.utils.data import DataLoader, Dataset, random_split


class PLData(LightningDataModule):
    r"""
    Basic pytorch lightning data module
    """

    def __init__(self, dataset: Dataset, cfg: OmegaConf, val_ratio: float = 0.0):
        super().__init__()
        self.cfg = cfg
        if val_ratio > 0:
            self.train_dataset, self.val_dataset = random_split(dataset, [1 - val_ratio, val_ratio])
        self.train_dataset = dataset.get("train")
        self.val_dataset = dataset.get("val")

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.cfg.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.cfg.batch_size)

    def test_dataloader(self):
        return DataLoader(self.test_dataset, batch_size=self.cfg.batch_size)


class PLModel(LightningModule, ABC):
    r"""
    Basic pytorch lightning model
    """

    def __init__(self, cfg: OmegaConf | dict):
        super().__init__()
        cfg = OmegaConf.create(cfg) if not isinstance(cfg, OmegaConf) else cfg
        self.cfg = cfg
        self.save_hyperparameters(cfg)

        self.z1_list = []
        self.z2_list = []
        self.z3_list = []

    def configure_optimizers(self):
        optimizer = Adam(self.parameters(), lr=self.cfg.lr, weight_decay=self.cfg.weight_decay)
        return optimizer

    def init_weights(self) -> None:
        self.apply(self._init_weights_module)

    def print_parameter_stats(self, name: str = None) -> None:
        net = getattr(self, name) if name is not None else self
        trainable_keys, frozen_keys = [], []
        for key, par in net.named_parameters():
            if par.requires_grad:
                trainable_keys.append(key)
            else:
                frozen_keys.append(key)
        logger.debug(f"Trainable parameters in {name}: {trainable_keys}")
        logger.debug(f"Frozen parameters in {name}: {frozen_keys}")

    @staticmethod
    def _init_weights_module(module, std=0.02, trunc=2) -> None:
        if isinstance(module, nn.Linear):
            nn.init.trunc_normal_(module.weight, mean=0, std=std, a=-trunc, b=trunc)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.trunc_normal_(module.weight, mean=0, std=std, a=-trunc, b=trunc)
            if module.padding_idx is not None:
                nn.init.zeros_(module.weight[module.padding_idx])
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def loss(self, *args, **kwargs) -> Tensor:
        raise NotImplementedError

    def forward(self, *args, **kwargs) -> Tensor:
        raise NotImplementedError

    def training_step(self, batch: dict[str, Tensor], batch_idx: int) -> Tensor:
        loss = self.loss(batch, "train", log=True)
        return loss

    def validation_step(self, batch: dict[str, Tensor], batch_idx: int) -> None:
        _ = self.loss(batch, "val", log=True)

    def gather_output(self) -> tuple[np.ndarray, np.ndarray] | np.ndarray:
        z_1 = np.vstack(self.z1_list)
        z_2 = np.vstack(self.z2_list) if len(self.z2_list) > 0 else None
        z_3 = np.vstack(self.z3_list) if len(self.z3_list) > 0 else None
        self.z1_list, self.z2_list, self.z3_list = [], [], []
        if z_2 is not None:
            if z_3 is not None:
                return z_1, z_2, z_3
            return z_1, z_2
        else:
            return z_1
