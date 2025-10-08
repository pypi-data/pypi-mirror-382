from torch import nn


def build_mlp(dims: list[int], dropout: float = 0.1, last_linear: bool = True) -> nn.Sequential:
    layers = []
    for in_dim, out_dim in zip(dims[:-2], dims[1:-1]):
        layers += [
            nn.Linear(in_dim, out_dim, bias=True),
            nn.BatchNorm1d(out_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        ]
    if last_linear:
        layers.append(nn.Linear(dims[-2], dims[-1], bias=True))
    else:
        layers += [
            nn.Linear(dims[-2], dims[-1], bias=True),
            nn.BatchNorm1d(dims[-1]),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
        ]
    return nn.Sequential(*layers)
