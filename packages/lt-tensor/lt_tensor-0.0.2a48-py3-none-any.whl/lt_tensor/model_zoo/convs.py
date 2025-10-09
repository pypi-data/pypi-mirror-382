__all__ = [
    "ConvBase",
    "BidirectionalConv1d",
    "BidirectionalConv2d",
    "BidirectionalConv3d",
    "TemporalFeatures1D",
    "ReSampleConvND",
    "calc_max_groups",
    "get_padding_2d",
    "get_conv",
    "remove_norm",
    "is_groups_compatible",
    "is_conv",
]
import math
from lt_utils.common import *
from lt_tensor.common import *
from lt_tensor.tensor_ops import get_padding_conv
from lt_utils.misc_utils import filter_kwargs
from torch.nn.utils.parametrize import remove_parametrizations
from torch.nn.utils.parametrizations import weight_norm, spectral_norm
from typing import TypeGuard
import torch.nn.functional as F

TP_SHAPE_1: TypeAlias = Union[int, Tuple[int]]
TP_SHAPE_2: TypeAlias = Union[TP_SHAPE_1, Tuple[int, int]]
TP_SHAPE_3: TypeAlias = Union[TP_SHAPE_2, Tuple[int, int, int]]

TC: TypeAlias = Callable[[Tensor], Tensor]


def _dummy(module: Model, *args, **kwargs):
    return module


def is_groups_compatible(channels_in: int, channels_out: int, groups: int):
    if channels_in < 2 or channels_out < 2:
        return groups == 1
    return groups % channels_in == 0 and groups % channels_out == 0


def calc_max_groups(channels_in: int, channels_out: int):
    return math.gcd(int(channels_in), int(channels_out))


def is_conv(module: nn.Module) -> TypeGuard[nn.modules.conv._ConvNd]:
    return isinstance(
        module,
        (
            nn.Conv1d,
            nn.Conv2d,
            nn.Conv3d,
            nn.ConvTranspose1d,
            nn.ConvTranspose2d,
            nn.ConvTranspose3d,
            nn.LazyConv1d,
            nn.LazyConv2d,
            nn.LazyConv3d,
            nn.LazyConvTranspose1d,
            nn.LazyConvTranspose2d,
            nn.LazyConvTranspose3d,
            nn.modules.conv._ConvNd,
        ),
    )


def get_weight_norm(
    norm_type: Optional[Literal["weight_norm", "spectral_norm"]] = None, **norm_kwargs
) -> Callable[[Union[nn.Module, Model]], Union[nn.Module, Model]]:
    if not norm_type:
        return _dummy
    if norm_type == "weight_norm":
        return lambda x: weight_norm(x, **norm_kwargs)
    return lambda x: spectral_norm(x, **norm_kwargs)


def _init_conv_orthogonal(
    m: Union[nn.Module, Model],
    mean: float = 0.0,
    std: float = 1.0,
    zero_bias: bool = False,
):
    if not hasattr(m, "weight"):
        return False

    nn.init.normal_(m.weight, mean=mean, std=std)

    if zero_bias and hasattr(m, "bias") and m.bias is not None:
        m.bias.zero_()
    return True


def init_conv_orthogonal(
    m: Union[nn.Module, Model], gain: float = 1.0, zero_bias: bool = False
):
    for module in m.modules():
        if not is_conv(module):
            continue
        nn.init.orthogonal_(module.weight, gain)
        if zero_bias and module.bias is not None:
            module.bias.zero_()


def _init_conv_normal(
    m: Union[nn.Module, Model],
    mean: float = 0.0,
    std: float = 1.0,
    zero_bias: bool = False,
):
    if not hasattr(m, "weight"):
        return False

    nn.init.normal_(m.weight, mean=mean, std=std)

    if zero_bias and hasattr(m, "bias") and m.bias is not None:
        m.bias.zero_()
    return True


def init_conv_normal(
    m: Union[nn.Module, Model],
    mean: float = 0.0,
    std: float = 1.0,
    zero_bias: bool = False,
):
    for module in m.modules():
        if not is_conv(module):
            continue
        nn.init.normal_(module.weight, mean=mean, std=std)
        if zero_bias and module.bias is not None:
            module.bias.zero_()


def _init_conv_kaiming(
    m: Union[nn.Module, Model],
    a: Optional[float] = None,
    mode: Literal["fan_in", "fan_out"] = "fan_in",
    nonlinearity: Literal["relu", "leaky_relu"] = "leaky_relu",
    zero_bias: bool = False,
):
    if not hasattr(m, "weight"):
        return False
    if not a:
        a = math.sqrt(5)
    nn.init.kaiming_uniform_(m.weight, a=a, mode=mode, nonlinearity=nonlinearity)
    if zero_bias and hasattr(m, "bias") and m.bias is not None:
        m.bias.zero_()
    return True


def init_conv_kaiming(
    m: Union[nn.Module, Model],
    a: Optional[float] = None,
    mode: Literal["fan_in", "fan_out"] = "fan_in",
    nonlinearity: Literal["relu", "leaky_relu"] = "leaky_relu",
    zero_bias: bool = False,
):

    if is_conv(m):
        _init_conv_kaiming(m)
    else:
        for module in m.modules():
            if not is_conv(module):
                continue
            _init_conv_kaiming(module, a, mode, nonlinearity, zero_bias)


def remove_norm(module, name: str = "weight"):
    try:
        try:
            remove_parametrizations(module, name, leave_parametrized=False)
        except:
            try:
                remove_parametrizations(module, name, leave_parametrized=True)
            except:
                pass
    except ValueError:
        pass  # not parametrized


def get_conv(
    in_channels: int = 1,
    out_channels: Optional[int] = None,
    kernel_size: TP_SHAPE_3 = 1,
    stride: TP_SHAPE_3 = 1,
    padding: TP_SHAPE_3 = 0,
    output_padding: TP_SHAPE_3 = 0,
    dilation: TP_SHAPE_3 = 1,
    groups: TP_SHAPE_3 = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    dim: Literal["1d", "2d", "3d"] = "1d",
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[
    nn.Conv1d,
    nn.LazyConv1d,
    nn.ConvTranspose1d,
    nn.LazyConvTranspose1d,
    nn.Conv2d,
    nn.LazyConv2d,
    nn.ConvTranspose2d,
    nn.LazyConvTranspose2d,
    nn.Conv3d,
    nn.LazyConv3d,
    nn.ConvTranspose3d,
    nn.LazyConvTranspose3d,
    TC,
]:
    dim = dim.lower().strip()
    assert dim in [
        "1d",
        "2d",
        "3d",
    ], f"Invalid conv dim '{dim}'. It must be either '1d', '2d' or '3d'."
    if norm is not None:
        norm = norm.strip().lower()
        if norm and norm not in ["weight_norm", "spectral_norm"]:
            if norm == "weight":
                norm = "weight_norm"
            elif norm == "spectral":
                norm == "spectral_norm"
            elif norm == "none":
                norm = None
            else:
                raise ValueError(
                    f"Invalid norm '{norm}'. "
                    'It must be either "weight_norm" or "spectral_norm" or None.'
                )
    out_ch = out_channels if out_channels is not None else in_channels
    kwargs = dict(
        in_channels=max(in_channels, 1),
        out_channels=max(out_ch, 1),
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
        output_padding=output_padding,
    )

    match dim:
        case "1d":
            if transposed:
                if lazy:
                    md = nn.LazyConvTranspose1d
                else:
                    md = nn.ConvTranspose1d
            else:
                if lazy:
                    md = nn.LazyConv1d
                else:
                    md = nn.Conv1d
        case "2d":
            if transposed:
                if lazy:
                    md = nn.LazyConvTranspose2d
                else:
                    md = nn.ConvTranspose2d
            else:
                if lazy:
                    md = nn.LazyConv2d
                else:
                    md = nn.Conv2d
        case _:
            if transposed:
                if lazy:
                    md = nn.LazyConvTranspose3d
                else:
                    md = nn.ConvTranspose3d

            else:
                if lazy:
                    md = nn.LazyConv3d
                else:
                    md = nn.Conv3d

    kwargs = filter_kwargs(md, False, [], **kwargs)
    if norm:
        norm_fn = get_weight_norm(norm, **norm_kwargs)
        return norm_fn(md(**kwargs))
    return md(**kwargs)


def get_1d_conv(
    in_channels: int,
    out_channels: Optional[int] = None,
    kernel_size: int = 1,
    stride: int = 1,
    padding: int = 0,
    output_padding: int = 0,
    dilation: int = 1,
    groups: int = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[nn.Conv1d, nn.ConvTranspose1d, TC]:
    return get_conv(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
        output_padding=output_padding,
        transposed=transposed,
        norm=norm,
        norm_kwargs=norm_kwargs,
        dim="1d",
        lazy=lazy,
    )


def get_2d_conv(
    in_channels: int,
    out_channels: Optional[int] = None,
    kernel_size: TP_SHAPE_2 = 1,
    stride: TP_SHAPE_2 = 1,
    padding: TP_SHAPE_2 = 0,
    output_padding: TP_SHAPE_2 = 0,
    dilation: TP_SHAPE_2 = 1,
    groups: int = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[nn.Conv2d, nn.ConvTranspose2d, TC]:
    return get_conv(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
        output_padding=output_padding,
        transposed=transposed,
        norm=norm,
        norm_kwargs=norm_kwargs,
        dim="2d",
        lazy=lazy,
    )


def get_3d_conv(
    in_channels: int,
    out_channels: Optional[int] = None,
    kernel_size: TP_SHAPE_3 = 1,
    stride: TP_SHAPE_3 = 1,
    padding: TP_SHAPE_3 = 0,
    output_padding: TP_SHAPE_3 = 0,
    dilation: TP_SHAPE_3 = 1,
    groups: int = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
    lazy: bool = False,
) -> Union[nn.Conv3d, nn.ConvTranspose3d, TC]:
    return get_conv(
        in_channels=in_channels,
        out_channels=out_channels,
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
        output_padding=output_padding,
        transposed=transposed,
        norm=norm,
        norm_kwargs=norm_kwargs,
        dim="3d",
        lazy=lazy,
    )


class ConvBase(Model):

    @staticmethod
    def get_1d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 0,
        output_padding: int = 0,
        dilation: int = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
        lazy: bool = False,
    ) -> Union[nn.Conv1d, nn.ConvTranspose1d, TC]:
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="1d",
            lazy=lazy,
        )

    @staticmethod
    def get_2d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_2 = 1,
        stride: TP_SHAPE_2 = 1,
        padding: TP_SHAPE_2 = 0,
        output_padding: TP_SHAPE_2 = 0,
        dilation: TP_SHAPE_2 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ) -> Union[nn.Conv2d, nn.ConvTranspose2d, TC]:
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="2d",
        )

    @staticmethod
    def get_3d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_3 = 1,
        stride: TP_SHAPE_3 = 1,
        padding: TP_SHAPE_3 = 0,
        output_padding: TP_SHAPE_3 = 0,
        dilation: TP_SHAPE_3 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ) -> Union[nn.Conv3d, nn.ConvTranspose3d, TC]:
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="3d",
        )

    @staticmethod
    def get_max_groups(in_channels: int, out_channels: int):
        return calc_max_groups(in_channels, out_channels)

    @staticmethod
    def get_padding(kernel_size: int, dilation: int, mode: Literal["a", "b"] = "a"):
        return get_padding_conv(kernel_size, dilation, mode.lower())

    def remove_norms(self, name: str = "weight"):
        for module in self.modules():
            try:
                if is_conv(module):
                    remove_norm(module, name)
            except:
                pass

    @staticmethod
    def _normal_init_default(m: nn.Module, mean=0.0, std=0.01, zero_bias: bool = False):
        if is_conv(m):
            nn.init.normal_(m.weight, mean=mean, std=std)
            if zero_bias and m.bias is not None:
                nn.init.zeros_(m.bias)


class BidirectionalConv1d(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        dilation: int = 1,
        padding: int = 0,
        groups_fwd: int = 1,
        groups_bwd: int = 1,
        output_padding: int = 0,
        bias_fwd: bool = True,
        bias_bwd: bool = True,
        transposed: bool = False,
        *,
        return_tuple: bool = False,
        norm: Optional[Literal["weight", "spectral"]] = None,
        flip_back: bool = True,
        flip_dims: List[int] = [-1],
        **kwargs,
    ):
        super().__init__()
        assert (
            isinstance(flip_dims, list)
            and flip_dims
            and all([isinstance(x, int) for x in flip_dims])
        )
        self.fwd = self.get_1d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_fwd,
            dilation=dilation,
            padding=padding,
            stride=stride,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_fwd,
        )
        self.bwd = self.get_1d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_bwd,
            dilation=dilation,
            stride=stride,
            padding=padding,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_bwd,
        )
        self.flip_back = flip_back
        self.return_tuple = return_tuple
        self.flip_dims = flip_dims

    def __call__(self, *args, **kwds) -> Union[Tuple[Tensor, Tensor], Tensor]:
        return super().__call__(*args, **kwds)

    def forward(self, x: Tensor) -> Union[Tuple[Tensor, Tensor], Tensor]:
        # forward path
        y_fwd = self.fwd(x)
        # backward path: flip, convolve, flip back if needed
        y_bwd = self.bwd(x.flip(dims=self.flip_dims))
        if self.flip_back:
            y_bwd = y_bwd.flip(dims=self.flip_dims)
        if self.return_tuple:
            return y_fwd, y_bwd
        return torch.cat((y_fwd, y_bwd), dim=1)


class BidirectionalConv2d(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        dilation: int = 1,
        padding: int = 0,
        groups_fwd: int = 1,
        groups_bwd: int = 1,
        output_padding: int = 0,
        bias_fwd: bool = True,
        bias_bwd: bool = True,
        transposed: bool = False,
        *,
        return_tuple: bool = False,
        norm: Optional[Literal["weight", "spectral"]] = None,
        flip_back: bool = True,
        flip_dims: List[int] = [-2, -1],
        **kwargs,
    ):
        super().__init__()
        assert (
            isinstance(flip_dims, list)
            and flip_dims
            and all([isinstance(x, int) for x in flip_dims])
        )
        self.fwd = self.get_2d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_fwd,
            dilation=dilation,
            padding=padding,
            stride=stride,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_fwd,
        )
        self.bwd = self.get_2d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_bwd,
            dilation=dilation,
            stride=stride,
            padding=padding,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_bwd,
        )
        self.return_tuple = return_tuple
        self.flip_back = flip_back
        self.flip_dims = flip_dims

    def __call__(self, *args, **kwds) -> Union[Tuple[Tensor, Tensor], Tensor]:
        return super().__call__(*args, **kwds)

    def forward(self, x: Tensor) -> Union[Tuple[Tensor, Tensor], Tensor]:
        y_fwd = self.fwd(x)
        y_bwd = self.bwd(x.flip(dims=self.flip_dims))
        if self.flip_back:
            y_bwd = y_bwd.flip(dims=self.flip_dims)
        if self.return_tuple:
            return y_fwd, y_bwd
        return torch.cat((y_fwd, y_bwd), dim=1)


class BidirectionalConv3d(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        dilation: int = 1,
        padding: int = 0,
        groups_fwd: int = 1,
        groups_bwd: int = 1,
        output_padding: int = 0,
        bias_fwd: bool = True,
        bias_bwd: bool = True,
        transposed: bool = False,
        *,
        return_tuple: bool = False,
        norm: Optional[Literal["weight", "spectral"]] = None,
        flip_back: bool = True,
        flip_dims: List[int] = [-3, -2, -1],
        **kwargs,
    ):
        super().__init__()
        assert (
            isinstance(flip_dims, list)
            and flip_dims
            and all([isinstance(x, int) for x in flip_dims])
        )
        self.fwd = self.get_3d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_fwd,
            dilation=dilation,
            padding=padding,
            stride=stride,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_fwd,
        )
        self.bwd = self.get_3d_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            groups=groups_bwd,
            dilation=dilation,
            stride=stride,
            padding=padding,
            norm=norm,
            output_padding=output_padding,
            transposed=transposed,
            bias=bias_bwd,
        )
        self.return_tuple = return_tuple
        self.flip_back = flip_back
        self.flip_dims = flip_dims

    def __call__(self, *args, **kwds) -> Union[Tuple[Tensor, Tensor], Tensor]:
        return super().__call__(*args, **kwds)

    def forward(self, x: Tensor) -> Union[Tuple[Tensor, Tensor], Tensor]:
        y_fwd = self.fwd(x)
        y_bwd = self.bwd(x.flip(dims=self.flip_dims))
        if self.flip_back:
            y_bwd = y_bwd.flip(dims=self.flip_dims)
        if self.return_tuple:
            return y_fwd, y_bwd
        return torch.cat((y_fwd, y_bwd), dim=1)


class ReSampleConvND(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: int = 1,
        stride: int = 1,
        dilation: int = 1,
        groups: int = 1,
        padding: int = 0,
        output_padding: int = 0,
        bias: bool = False,
        *,
        scale_factor: int = 2,
        transposed: bool = False,
        dim: Literal["1d", "2d", "3d"] = "1d",
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    ):
        super().__init__()
        self.scale_factor = scale_factor
        if out_channels is None:
            out_channels = in_channels
        if in_channels == out_channels:
            self.learned = nn.Identity()
        else:
            self.learned = get_conv(
                in_channels,
                out_channels,
                kernel_size,
                stride,
                padding,
                output_padding,
                dilation,
                groups,
                bias=bias,
                transposed=transposed,
                norm=norm,
                dim=dim,
            )

    def forward(self, x: Tensor):
        x = F.interpolate(x, scale_factor=self.scale_factor, mode="nearest")
        return self.learned(x)


class TemporalFeatures1D(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        hidden_dim: int = 128,
        kernel_size: int = 1,
        stride: int = 1,
        dilation: int = 1,
        groups: int = 1,
        groups_fwd: int = 1,
        groups_bwd: int = 1,
        padding: int = 0,
        output_padding: int = 0,
        bias_residual: bool = False,
        bias_fw: bool = False,
        bias_bw: bool = False,
        bias_output: bool = False,
        *,
        activation: Type[nn.Module] = lambda: nn.LeakyReLU(0.1),
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        alpha: float = 1.0,
        alpha_trainable: bool = False,
        init_weights: bool = True,
    ):
        super().__init__()
        self.norm = norm
        # self.dropout = nn.Dropout1d(dropout)
        self.activ = activation()
        self.alpha = nn.Parameter(
            torch.tensor(float(alpha), dtype=torch.float32),
            requires_grad=alpha_trainable,
        )
        self.bi_directional = BidirectionalConv1d(
            in_channels,
            hidden_dim,
            kernel_size=kernel_size,
            stride=stride,
            dilation=dilation,
            padding=padding,
            groups_bwd=groups_bwd,
            groups_fwd=groups_fwd,
            bias_fwd=bias_fw,
            bias_bwd=bias_bw,
            norm=norm,
            return_tuple=True,
        )
        self.proj_wvf = self.get_1d_conv(
            hidden_dim,
            hidden_dim,
            kernel_size,
            stride,
            padding,
            output_padding,
            dilation,
            groups,
            bias=bias_residual,
            transposed=transposed,
            norm=norm,
        )
        self.proj_wvb = self.get_1d_conv(
            hidden_dim,
            hidden_dim,
            kernel_size,
            stride,
            padding,
            output_padding,
            dilation,
            groups,
            bias=bias_residual,
            transposed=transposed,
            norm=norm,
        )
        self.proj_o = self.get_1d_conv(
            hidden_dim * 3, out_channels, kernel_size=1, bias=bias_output, norm=norm
        )
        if init_weights:
            self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m: nn.Module):
        if is_conv(m):
            nn.init.orthogonal_(m.weight, gain=2.0)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        x = self.activ(x)
        fwd, bwd = self.bi_directional(x)
        wvf_k = self.proj_wvf(F.sigmoid(fwd) * bwd.tanh())
        wvb_k = self.proj_wvb(fwd * bwd.cos())
        wv_fb_g = fwd.tanh() * bwd.sin()
        wv_o = torch.cat([wvf_k, wvb_k, wv_fb_g], dim=1)
        return self.proj_o(wv_o)


class TemporalFeatures2D(ConvBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        hidden_dim: int = 128,
        kernel_size: int = 1,
        stride: int = 1,
        dilation: int = 1,
        groups: int = 1,
        groups_fwd: int = 1,
        groups_bwd: int = 1,
        padding: int = 0,
        output_padding: int = 0,
        bias_residual: bool = False,
        bias_fw: bool = False,
        bias_bw: bool = False,
        bias_output: bool = False,
        *,
        activation: Type[nn.Module] = lambda: nn.LeakyReLU(0.1),
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        alpha: float = 1.0,
        alpha_trainable: bool = False,
        init_weights: bool = True,
    ):
        super().__init__()
        self.norm = norm
        # self.dropout = nn.Dropout1d(dropout)
        self.activ = activation()
        self.alpha = nn.Parameter(
            torch.tensor(float(alpha), dtype=torch.float32),
            requires_grad=alpha_trainable,
        )
        self.bi_directional = BidirectionalConv2d(
            in_channels,
            hidden_dim,
            kernel_size=kernel_size,
            stride=stride,
            dilation=dilation,
            padding=padding,
            groups_bwd=groups_bwd,
            groups_fwd=groups_fwd,
            bias_fwd=bias_fw,
            bias_bwd=bias_bw,
            norm=norm,
            return_tuple=True,
        )
        self.proj_wvf = self.get_2d_conv(
            hidden_dim,
            hidden_dim,
            kernel_size,
            stride,
            padding,
            output_padding,
            dilation,
            groups,
            bias=bias_residual,
            transposed=transposed,
            norm=norm,
        )
        self.proj_wvb = self.get_2d_conv(
            hidden_dim,
            hidden_dim,
            kernel_size,
            stride,
            padding,
            output_padding,
            dilation,
            groups,
            bias=bias_residual,
            transposed=transposed,
            norm=norm,
        )
        self.proj_o = self.get_2d_conv(
            hidden_dim * 3, out_channels, kernel_size=1, bias=bias_output, norm=norm
        )
        if init_weights:
            self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m: nn.Module):
        if is_conv(m):
            nn.init.orthogonal_(m.weight, gain=2.0)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, x: Tensor) -> Tuple[Tensor, Tensor]:
        x = self.activ(x)
        fwd, bwd = self.bi_directional(x)
        wvf_k = self.proj_wvf(F.sigmoid(fwd) * bwd.tanh())
        wvb_k = self.proj_wvb(fwd * bwd.cos())
        wv_fb_g = fwd.tanh() * bwd.sin()
        wv_o = torch.cat([wvf_k, wvb_k, wv_fb_g], dim=1)
        return self.proj_o(wv_o)


class ConvUndefinedAttn(ConvBase):
    def __init__(
        self,
        feature_size: int,
        d_model: int = 128,
        hidden_channels: int = 128,
        kqv_kernel: int = 1,
        k_dilation: int = 1,
        q_dilation: int = 1,
        v_dilation: int = 1,
        o_bias: bool = False,
    ):
        super().__init__()
        self.encoder_net = nn.Sequential(
            nn.ConvTranspose1d(feature_size, hidden_channels, 3, stride=2),  # expand
            nn.AvgPool1d(2),  # retract based on avg
            nn.LeakyReLU(0.1),
            nn.Conv1d(hidden_channels, hidden_channels, 7, padding=3),
            nn.LeakyReLU(0.1),
            nn.Conv1d(hidden_channels, hidden_channels, 1),
            nn.LeakyReLU(0.1),
            nn.Conv1d(hidden_channels, d_model * 3, 1),
        )

        self.qW = nn.Conv1d(
            d_model,
            feature_size,
            kqv_kernel,
            padding=self.get_padding(kqv_kernel, q_dilation),
            dilation=q_dilation,
        )
        self.kW = nn.Conv1d(
            d_model,
            feature_size,
            kqv_kernel,
            padding=self.get_padding(kqv_kernel, k_dilation),
            dilation=k_dilation,
        )
        self.vV = nn.Conv1d(
            d_model,
            feature_size,
            kqv_kernel,
            padding=self.get_padding(kqv_kernel, v_dilation),
            dilation=v_dilation,
        )
        self.oW = nn.Linear(feature_size, feature_size, bias=o_bias)
        self.init_linear()
        self.init_convs()

    def init_convs(
        self,
        mode: Literal["orthogonal", "xavier", "norm"] = "orthogonal",
        mean: float = 0.0,
        std: float = 0.01,
        gain: float = 1.0,
        zero_bias: bool = True,
    ):
        for m in self.modules():
            if not is_conv(m):
                continue
            if mode == "orthogonal":
                nn.init.orthogonal_(m.weight, gain=gain)
            elif mode == "xavier":
                nn.init.xavier_uniform_(m.weight, gain=gain)
            else:
                nn.init.normal_(m.weight, mean=mean, std=std)
            if m.bias is not None:
                if not zero_bias:
                    nn.init.normal_(m.bias, mean=mean, std=std)
                else:
                    nn.init.zeros_(m.bias)

    def init_linear(
        self,
        mode: Literal["orthogonal", "xavier", "norm"] = "xavier",
        mean: float = 0.0,
        std: float = 0.01,
        gain: float = 1.0,
        zero_bias: bool = True,
    ):
        for m in self.modules():
            if not isinstance(m, nn.Linear):
                continue
            if mode == "orthogonal":
                nn.init.orthogonal_(m.weight, gain=gain)
            elif mode == "xavier":
                nn.init.xavier_uniform_(m.weight, gain=gain)
            else:
                nn.init.normal_(m.weight, mean=mean, std=std)
            if m.bias is not None:
                if not zero_bias:
                    nn.init.normal_(m.bias, mean=mean, std=std)
                else:
                    nn.init.zeros_(m.bias)

    def forward(self, x: Tensor):
        q, k, v = torch.chunk(self.encoder_net(x), 3, dim=1)

        Qw = self.qW(q)
        Kw = self.kW(k)
        Vw = self.vV(v)

        QKVw = (x * torch.sigmoid(Qw + Kw)) - F.gelu(Vw)

        return self.oW(QKVw.transpose(-1, -2)).transpose(-1, -2)
