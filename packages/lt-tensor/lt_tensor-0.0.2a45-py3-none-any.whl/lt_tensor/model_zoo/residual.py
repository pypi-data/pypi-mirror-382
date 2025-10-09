__all__ = [
    "ResBlock",
    "AMPBlock",
    "GatedResBlock",
    "ResBlock2d1x1",
    "PoolResBlock2D",
]
import torch
from torch import nn, Tensor
from lt_utils.common import *
from lt_utils.misc_utils import filter_kwargs
from lt_tensor.model_zoo.fusion import FiLMConv1d
from lt_tensor.model_zoo.convs import ConvBase, BidirectionalConv1d, ConvUndefinedAttn
from lt_tensor.model_zoo.activations import alias_free
from lt_tensor.model_zoo.basic import Scale


class GatedResBlock(ConvBase):
    def __init__(
        self,
        channels: int,
        kernel_size: Union[int, List[int]] = 3,
        dilation: Tuple[int, ...] = (1, 3, 5),
        activation: Callable[[None], nn.Module] = lambda: nn.LeakyReLU(0.1),
        groups: int = 1,
        scale: float = 1.0,
        train_scale: bool = True,
        mode: Literal["mesh", "dense", "hilo"] = "mesh",
        norm: Optional[Literal["weight", "spectral"]] = None,
        conditional: bool = False,
        conditional_size: Optional[int] = None,
        conditional_injection_depth: int = 1,
        stochastic_dropout: float = 0.1,
        init_weights: bool = False,
        init_weights_fn: Optional[Callable[[nn.Module], nn.Module]] = None,
        cond_interp_match: bool = False,
        **kwargs,
    ):
        super().__init__()
        self.conditional = conditional
        self.stochastic_dropout = stochastic_dropout
        self.mode: Literal["mesh", "dense", "hilo"] = mode
        self.dilation_blocks = nn.ModuleList()
        if isinstance(kernel_size, int):
            ks = [kernel_size for _ in range(len(dilation))]
        else:
            ks = ks
        for d, k in zip(dilation, ks):
            self.dilation_blocks.append(
                nn.ModuleDict(
                    {
                        "conv": nn.Sequential(
                            activation(),
                            BidirectionalConv1d(
                                channels,
                                channels,
                                k,
                                dilation=d,
                                padding=self.get_padding(k, d),
                                norm=norm,
                                groups_fwd=groups,
                                groups_bwd=groups,
                            ),
                        ),
                        "proj": nn.Sequential(
                            activation(),
                            self.get_1d_conv(
                                channels,
                                norm=norm,
                                groups=groups,
                            ),
                        ),
                        "scale": Scale((channels, 1), scale, train_scale),
                    }
                )
            )
        self.conditional_injection_depth = max(conditional_injection_depth, 1)
        self.cond = (
            nn.Identity()
            if not conditional
            else FiLMConv1d(
                cond_channels=conditional_size or channels,
                feat_channels=channels,
                kernel_size=3,
                padding=1,
                interp_match=cond_interp_match,
                norm=norm,
            )
        )
        if init_weights:
            if init_weights_fn is None:
                init_weights_fn = lambda m: self._normal_init_default(
                    m=m,
                    **filter_kwargs(self._normal_init_default, False, ["m"], **kwargs),
                )
            self.dilation_blocks.apply(init_weights_fn)

    def _get_gated(self, y: Tensor, x_cond: Optional[Tensor] = None):
        alpha, h = torch.chunk(y, 2, dim=1)
        if x_cond is None:
            return alpha.sigmoid() * h.tanh()
        return alpha.sigmoid() * (h.tanh() + x_cond)

    def _dense_forward(self, x, x_cond=None):
        """Instead of a single running state or a final skip sum, collect all intermediate gated outputs and combine them at the end"""
        feats = []
        h = x
        for i, b in enumerate(self.dilation_blocks):
            y = b["conv"](h)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            feats.append(b["scale"](b["proj"](g)))
            h = h + feats[-1]  # optional local residual
        return x + torch.mean(torch.stack(feats), dim=0)

    def _hilo_forward(self, x, x_cond=None):
        """High-Pass / Low-Pass Split
        Let each block predict a delta that is subtracted as well as added,
        so the residual learns to separate slow and fast components.
        """
        low = x
        high = 0
        for i, b in enumerate(self.dilation_blocks):
            y = b["conv"](x)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            h = b["scale"](b["proj"](g))
            high = high + h
            low = low - h
        return torch.cat([low, high], dim=1)  # double channels

    def _mesh_forward(self, x: Tensor, x_cond: Optional[Tensor] = None):
        skip = torch.zeros_like(x)
        for i, b in enumerate(self.dilation_blocks):
            base = b["conv"](x)
            if i < self.conditional_injection_depth:
                y = self._get_gated(base, x_cond)
            else:
                y = self._get_gated(base, None)

            y = b["proj"](y)
            x = y
            scaled = b["scale"](y)
            skip = scaled + skip
        return skip + x

    def forward(self, x: Tensor, cond: Optional[Tensor] = None):
        if self.conditional and cond is not None:
            x_cond = self.cond(x=x, cond=cond)
        else:
            x_cond = None

        match self.mode:
            case "dense":
                return self._dense_forward(x, x_cond)
            case "hilo":
                return self._hilo_forward(x, x_cond)
            case _:
                return self._mesh_forward(x, x_cond)


class GatedAttnResBlock(ConvBase):
    def __init__(
        self,
        channels: int,
        kernel_size: Union[int, List[int]] = 3,
        dilation: Tuple[int, ...] = (1, 3, 5),
        activation: Callable[[None], nn.Module] = lambda: nn.LeakyReLU(0.1),
        groups: int = 1,
        scale: float = 1.0,
        train_scale: bool = True,
        mode: Literal["mesh", "dense", "hilo"] = "mesh",
        norm: Optional[Literal["weight", "spectral"]] = None,
        conditional: bool = False,
        conditional_size: Optional[int] = None,
        conditional_injection_depth: int = 1,
        stochastic_dropout: float = 0.1,
        init_weights: bool = False,
        init_weights_fn: Optional[Callable[[nn.Module], nn.Module]] = None,
        cond_interp_match: bool = False,
        **kwargs,
    ):
        super().__init__()
        self.conditional = conditional
        self.stochastic_dropout = stochastic_dropout
        self.mode: Literal["mesh", "dense", "hilo"] = mode
        self.dilation_blocks = nn.ModuleList()
        if isinstance(kernel_size, int):
            ks = [kernel_size for _ in range(len(dilation))]
        else:
            ks = ks
        for d, k in zip(dilation, ks):
            self.dilation_blocks.append(
                nn.ModuleDict(
                    {
                        "attn": ConvUndefinedAttn(channels, channels * 2),
                        "conv": nn.Sequential(
                            activation(),
                            BidirectionalConv1d(
                                channels,
                                channels,
                                k,
                                dilation=d,
                                padding=self.get_padding(k, d),
                                norm=norm,
                                groups_fwd=groups,
                                groups_bwd=groups,
                            ),
                        ),
                        "proj": nn.Sequential(
                            activation(),
                            self.get_1d_conv(
                                channels,
                                norm=norm,
                                groups=groups,
                            ),
                        ),
                        "scale": Scale((channels, 1), scale, train_scale),
                    }
                )
            )
        self.conditional_injection_depth = max(conditional_injection_depth, 1)
        self.cond = (
            nn.Identity()
            if not conditional
            else FiLMConv1d(
                cond_channels=conditional_size or channels,
                feat_channels=channels,
                kernel_size=3,
                padding=1,
                interp_match=cond_interp_match,
                norm=norm,
            )
        )
        if init_weights:
            if init_weights_fn is None:
                init_weights_fn = lambda m: self._normal_init_default(
                    m=m,
                    **filter_kwargs(self._normal_init_default, False, ["m"], **kwargs),
                )
            self.dilation_blocks.apply(init_weights_fn)

    def _get_gated(self, y: Tensor, x_cond: Optional[Tensor] = None):
        alpha, h = torch.chunk(y, 2, dim=1)
        if x_cond is None:
            return alpha.sigmoid() * h.tanh()
        return alpha.sigmoid() * (h.tanh() + x_cond)

    def _dense_forward(self, x, x_cond=None):
        """Instead of a single running state or a final skip sum, collect all intermediate gated outputs and combine them at the end"""
        feats = []
        h = x
        for i, b in enumerate(self.dilation_blocks):
            attended = b["attn"](h)
            y = b["conv"](h + attended)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            feats.append(b["scale"](b["proj"](g)))
            h = h + feats[-1]  # optional local residual
        return x + torch.mean(torch.stack(feats), dim=0)

    def _hilo_forward(self, x, x_cond=None):
        """High-Pass / Low-Pass Split
        Let each block predict a delta that is subtracted as well as added,
        so the residual learns to separate slow and fast components.
        """
        low = x
        high = 0
        for i, b in enumerate(self.dilation_blocks):
            attended = b["attn"](x)
            y = b["conv"](low + attended)
            g = self._get_gated(
                y, x_cond if i < self.conditional_injection_depth else None
            )
            h = b["scale"](b["proj"](g))
            high = high + h
            low = low - h
        return torch.cat([low, high], dim=1)  # double channels

    def _mesh_forward(self, x: Tensor, x_cond: Optional[Tensor] = None):
        skip = torch.zeros_like(x)
        for i, b in enumerate(self.dilation_blocks):
            attended = b["attn"](x)
            base = b["conv"](x + attended)
            if i < self.conditional_injection_depth:
                y = self._get_gated(base, x_cond)
            else:
                y = self._get_gated(base, None)

            y = b["proj"](y)
            x = y
            scaled = b["scale"](y)
            skip = scaled + skip
        return skip + x

    def forward(self, x: Tensor, cond: Optional[Tensor] = None):
        if self.conditional and cond is not None:
            x_cond = self.cond(x=x, cond=cond)
        else:
            x_cond = None

        match self.mode:
            case "dense":
                return self._dense_forward(x, x_cond)
            case "hilo":
                return self._hilo_forward(x, x_cond)
            case _:
                return self._mesh_forward(x, x_cond)


class ResBlock(ConvBase):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: Callable[[Any], nn.Module] = lambda: nn.LeakyReLU(0.1),
        groups: int = 1,
        version: Literal["v1", "v2"] = "v1",
        norm: Optional[Literal["weight", "spectral"]] = None,
        init_weights: bool = False,
        init_weights_fn: Optional[Callable[[nn.Module], nn.Module]] = None,
        **kwargs,
    ):
        super().__init__()
        self.resblock_version = version
        self.convs1 = nn.ModuleList()
        self.convs2 = nn.ModuleList()
        cnn2_padding = self.get_padding(kernel_size, 1)
        for i, d in enumerate(dilation):
            mdk = dict(
                in_channels=channels,
                kernel_size=kernel_size,
                dilation=d,
                padding=self.get_padding(kernel_size, d),
                norm=norm,
                groups=groups,
            )
            if self.resblock_version == "v1":
                self.convs2.append(
                    nn.Sequential(
                        activation(),
                        self.get_1d_conv(
                            channels,
                            kernel_size=kernel_size,
                            dilation=1,
                            padding=cnn2_padding,
                            norm=norm,
                            groups=groups,
                        ),
                    )
                )
            else:
                self.convs2.append(nn.Identity())

            if i == 0:
                self.convs1.append(self.get_1d_conv(**mdk))
            else:
                self.convs1.append(nn.Sequential(activation(), self.get_1d_conv(**mdk)))
        if init_weights:
            if init_weights_fn is None:
                init_weights_fn = lambda m: self._normal_init_default(
                    m=m,
                    **filter_kwargs(self._normal_init_default, False, ["m"], **kwargs),
                )
            self.convs1.apply(init_weights_fn)
            if self.resblock_version == "v1":
                self.convs2.apply(init_weights_fn)

    def forward(self, x: Tensor):
        for c1, c2 in zip(self.convs1, self.convs2):
            xt = c1(x)
            x = c2(xt) + x
        return x


class AMPBlock(ConvBase):
    """Modified from 'https://github.com/NVIDIA/BigVGAN/blob/main/bigvgan.py' under MIT license, found in 'bigvgan/LICENSE'

    AMPBlock applies Snake / SnakeBeta activation functions with trainable parameters that control periodicity, defined for each layer.

    """

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: tuple = (1, 3, 5),
        activation: Optional[Callable[[Tensor], Tensor]] = None,
        version: Literal["v1", "v2"] = "v1",
        groups: int = 1,
        norm: Optional[Literal["weight", "spectral"]] = None,
        alias_up_ratio: int = 2,
        alias_down_ratio: int = 2,
        alias_up_kernel_size: int = 12,
        alias_down_kernel_size: int = 12,
        snake_alpha: float = 1.0,
        snake_logscale: bool = True,
        init_weights: bool = False,
        init_weights_fn: Optional[Callable[[nn.Module], nn.Module]] = None,
        **kwargs,
    ):
        super().__init__()

        self.resblock_version = version
        if activation is None:
            from lt_tensor.model_zoo.activations import snake

            activation = lambda: snake.SnakeBeta(
                channels,
                alpha_logscale=snake_logscale,
                alpha=snake_alpha,
                requires_grad=True,
            )

        ch1_kwargs = dict(in_channels=channels, kernel_size=kernel_size, norm=norm)
        ch2_kwargs = dict(
            in_channels=channels,
            kernel_size=kernel_size,
            padding=self.get_padding(kernel_size, 1),
            norm=norm,
        )
        alias_kwargs = dict(
            up_ratio=alias_up_ratio,
            down_ratio=alias_down_ratio,
            up_kernel_size=alias_up_kernel_size,
            down_kernel_size=alias_down_kernel_size,
        )
        self.convs = nn.ModuleList()
        for i, d in enumerate(dilation):
            if version == "v1":
                self.convs.append(
                    nn.Sequential(
                        alias_free.Activation1d(
                            activation=activation(), **alias_kwargs
                        ),
                        self.get_1d_conv(
                            **ch1_kwargs,
                            dilation=d,
                            padding=self.get_padding(kernel_size, d),
                            groups=groups,
                        ),
                        alias_free.Activation1d(
                            activation=activation(), **alias_kwargs
                        ),
                        self.get_1d_conv(**ch2_kwargs, groups=groups),
                    )
                )
            else:
                self.convs.append(
                    nn.Sequential(
                        alias_free.Activation1d(
                            activation=activation(), **alias_kwargs
                        ),
                        self.get_1d_conv(
                            **ch1_kwargs,
                            dilation=d,
                            padding=self.get_padding(kernel_size, d),
                            groups=groups,
                        ),
                    ),
                )

        self.num_layers = len(self.convs)
        if init_weights:
            if init_weights_fn is None:
                init_weights_fn = lambda m: self._normal_init_default(
                    m=m,
                    **filter_kwargs(self._normal_init_default, False, ["m"], **kwargs),
                )
            self.convs.apply(init_weights_fn)

    def forward(self, x):
        for layer in self.convs:
            x = layer(x) + x
        return x


class ResBlock2d1x1(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        hidden_size: Optional[int] = None,
        dilation: int = 1,
        kernel_size: Union[int, Sequence[int]] = 3,
        pool_kernel_size: Union[int, Sequence[int]] = (1, 2),
        activation: Type[nn.Module] = lambda: nn.LeakyReLU(0.1, inplace=True),
        norm: Optional[Literal["weight", "spectral"]] = None,
        groups: int = 1,
        bias: bool = False,
        c1x1_stride: int = 1,
        c1x1_transposed: bool = False,
        c1x1_dilation: int = 1,
        c1x1_padding: int = 0,
        c1x1_kernel_size: int = 1,
        c1x1_groups: int = 1,
        c1x1_bias: bool = False,
    ):
        super().__init__()
        # BN / LReLU / MaxPool layer before the conv layer - see Figure 1b in the paper
        self.pre_conv = nn.Sequential(
            nn.BatchNorm2d(num_features=in_channels),
            activation(),
            nn.MaxPool2d(kernel_size=pool_kernel_size),
        )
        if not hidden_size:
            hidden_size = (in_channels + out_channels) // 2

        # conv layers

        self.conv = nn.Sequential(
            self.get_2d_conv(
                in_channels=in_channels,
                out_channels=hidden_size,
                kernel_size=kernel_size,
                groups=groups,
                dilation=dilation,
                padding=self.get_padding(kernel_size, dilation, mode="b"),
                bias=bias,
                norm=norm,
            ),
            nn.BatchNorm2d(hidden_size),
            activation(),
            self.get_2d_conv(
                in_channels=hidden_size,
                out_channels=out_channels,
                kernel_size=kernel_size,
                groups=groups,
                padding=self.get_padding(kernel_size, 1, mode="b"),
                bias=bias,
                norm=norm,
            ),
        )

        self.learned_dx = in_channels != out_channels
        if not self.learned_dx:
            self.conv1x1 = nn.Identity()
        else:
            self.conv1x1 = self.get_2d_conv(
                in_channels=in_channels,
                out_channels=out_channels,
                kernel_size=c1x1_kernel_size,
                stride=c1x1_stride,
                dilation=c1x1_dilation,
                groups=c1x1_groups,
                padding=c1x1_padding,
                transposed=c1x1_transposed,
                bias=c1x1_bias,
                norm=norm,
            )

    def forward(self, x: Tensor):
        x = self.pre_conv(x)
        return self.conv(x) + self.conv1x1(x)


class PoolResBlock2D(ConvBase):
    def __init__(
        self,
        pool_features: int = 256,
        pool_activation: nn.Module = nn.LeakyReLU(0.1, inplace=True),
        pool_kernel_size: Union[int, Sequence[int]] = (1, 4),
        resblock_activation: Type[nn.Module] = lambda: nn.LeakyReLU(0.1, inplace=True),
        residual_sizes: List[Tuple[int, int]] = [(64, 128), (128, 192), (192, 256)],
        residual_dilation_sizes: List[Union[int, Sequence[int]]] = [1, 1, 1],
        residual_hidden_sizes: List[int] = [128, 192, 256],
        residual_kernel_sizes: List[Union[int, Sequence[int]]] = [3, 3, 3],
        residual_pool_kernel_sizes: List[Union[int, Sequence[int]]] = [
            (1, 2),
            (1, 2),
            (1, 2),
        ],
        dropout: float = 0.0,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    ):
        super().__init__()
        assert (
            len(residual_sizes)
            == len(residual_kernel_sizes)
            == len(residual_pool_kernel_sizes)
            == len(residual_dilation_sizes)
            == len(residual_hidden_sizes)
        )

        self.bn = nn.BatchNorm2d(num_features=pool_features)
        self.pool = nn.MaxPool2d(kernel_size=pool_kernel_size)
        self.activation = pool_activation
        self.dropout = nn.Dropout(dropout)
        self.resblocks = nn.Sequential()

        for (sz_in, sz_out), kernel_sz, kernel_sz_pool, dilation, hidden_dim in zip(
            residual_sizes,
            residual_kernel_sizes,
            residual_pool_kernel_sizes,
            residual_dilation_sizes,
            residual_hidden_sizes,
        ):
            self.resblocks.append(
                ResBlock2d1x1(
                    in_channels=sz_in,
                    out_channels=sz_out,
                    hidden_size=hidden_dim,
                    dilation=dilation,
                    kernel_size=kernel_sz,
                    pool_kernel_size=kernel_sz_pool,
                    activation=resblock_activation,
                    norm=norm,
                )
            )

    def forward(self, x: Tensor) -> Tensor:
        x = self.resblocks(x)
        x = self.activation(self.bn(x))
        return self.pool(x)
