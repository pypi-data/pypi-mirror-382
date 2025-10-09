__all__ = ["HifiganGenerator", "HifiganConfig"]


from lt_utils.common import *
import torch
from torch import nn, Tensor
from lt_tensor.model_zoo.convs import ConvBase, _dummy
from lt_utils.file_ops import is_file, load_json
from lt_tensor.model_base import ModelConfig
from torch.nn.utils.parametrizations import weight_norm
from lt_tensor.model_zoo.residual import (
    ResBlock,
    AMPBlock,
    GatedResBlock,
)
from lt_tensor.model_zoo.basic import SkipWrap


def get_snake(name: Literal["snake", "snakebeta"] = "snake"):
    assert name.lower() in [
        "snake",
        "snakebeta",
    ], f"'{name}' is not a valid snake activation! use 'snake' or 'snakebeta'"
    from lt_tensor.model_zoo.activations import snake

    if name.lower() == "snake":
        return snake.Snake
    return snake.SnakeBeta


class HifiganConfig(ModelConfig):
    in_channels: int = 80
    upsample_rates: List[Union[int, List[int]]] = [8, 8, 2, 2]
    upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16, 4, 4]
    upsample_initial_channel: int = 768
    resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11]
    resblock_dilation_sizes: List[Union[int, List[int]]] = [
        [1, 3, 5],
        [1, 3, 5],
        [1, 3, 5],
    ]
    activation: str = "leakyrelu"
    resblock_activation: str = "leakyrelu"
    activation_kwargs: Dict[str, Any] = dict()
    use_tanh: bool = True
    do_clamp_if_not_tanh: bool = True
    use_bias_on_final_layer: bool = False

    snake_logscale: bool = True
    residual_scale: float = 0.5
    resblock_version: Literal["v1", "v2"] = "v1"
    residual_groups: Union[int, List[Union[int, Tuple[int, int]]]] = 1
    resblock_name: Literal["resblock", "gatedresblock", "ampblock"] = "resblock"
    alpha_logscale: bool = False
    snake_alpha: float = 1.0
    aliasfree_up_ratio: int = 2
    aliasfree_down_ratio: int = 2
    aliasfree_up_kernel_size: int = 12
    aliasfree_down_kernel_size: int = 12
    use_activation_on_pw: bool = False
    snake_activ_choice: Literal["snake", "snakebeta"] = "snake"
    groups: Union[int, List[int]] = 1
    norm: Optional[Literal["weight", "spectral"]] = "weight"
    norm_residual: Optional[Literal["weight", "spectral"]] = "weight"
    gated_alpha: float = 1.0
    gated_train_alpha: bool = False
    gated_stochastic_dropout: float = 0.1
    use_residual_skip_wrapper: bool = False
    init_weights_residual: bool = True
    last_activation: str = "leakyrelu"
    residual_mode: Literal["mesh", "dense", "hilo"] = "mesh"

    def __init__(
        self,
        in_channels: int = 80,
        upsample_rates: List[Union[int, List[int]]] = [8, 8, 2, 2],
        upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16, 4, 4],
        upsample_initial_channel: int = 512,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        *,
        activation: str = "leakyrelu",
        activation_kwargs: Dict[str, Any] = dict(negative_slope=0.1),
        resblock_activation_kwargs: Dict[str, Any] = dict(negative_slope=0.1),
        use_bias_on_final_layer: bool = False,
        use_tanh: bool = True,
        groups: Union[int, List[int]] = 1,
        do_clamp_if_not_tanh: bool = True,
        snake_logscale: bool = True,
        use_residual_skip_wrapper: bool = False,
        resblock_activation: str = "leakyrelu",
        resblock_name: Literal["resblock", "gatedresblock", "ampblock"] = "resblock",
        resblock_version: Literal["v1", "v2"] = "v1",
        residual_groups: Union[int, List[int]] = 1,
        residual_scale: float = 0.5,
        residual_mode: Literal["mesh", "dense", "hilo"] = "mesh",
        gated_alpha: float = 1.0,
        gated_train_alpha: bool = False,
        gated_stochastic_dropout: float = 0.1,
        alpha_logscale: bool = False,
        use_activation_on_pw: bool = False,
        snake_alpha: float = 1.0,
        aliasfree_up_ratio: int = 2,
        aliasfree_down_ratio: int = 2,
        aliasfree_up_kernel_size: int = 12,
        aliasfree_down_kernel_size: int = 12,
        snake_activ_choice: Literal["snake", "snakebeta"] = "snake",
        norm: Optional[Literal["weight", "spectral"]] = "weight",
        norm_residual: Optional[Literal["weight", "spectral"]] = "weight",
        init_weights_residual: bool = True,
        last_activation: str = "leakyrelu",
        **kwargs,
    ):
        settings = {
            "in_channels": kwargs.get("n_mels", in_channels),
            "upsample_rates": upsample_rates,
            "upsample_kernel_sizes": upsample_kernel_sizes,
            "upsample_initial_channel": upsample_initial_channel,
            "resblock_kernel_sizes": resblock_kernel_sizes,
            "resblock_dilation_sizes": resblock_dilation_sizes,
            "activation": activation,
            "resblock_activation": resblock_activation,
            "resblock_activation_kwargs": resblock_activation_kwargs,
            "activation_kwargs": activation_kwargs,
            "use_tanh": use_tanh,
            "use_bias_on_final_layer": use_bias_on_final_layer,
            "do_clamp_if_not_tanh": do_clamp_if_not_tanh,
            "snake_logscale": snake_logscale,
            "residual_groups": residual_groups,
            "residual_scale": residual_scale,
            "alpha_logscale": alpha_logscale,
            "snake_alpha": snake_alpha,
            "aliasfree_up_ratio": aliasfree_up_ratio,
            "aliasfree_down_ratio": aliasfree_down_ratio,
            "aliasfree_up_kernel_size": aliasfree_up_kernel_size,
            "aliasfree_down_kernel_size": aliasfree_down_kernel_size,
            "use_activation_on_pw": use_activation_on_pw,
            "residual_mode": residual_mode,
            "resblock_name": resblock_name,
            "resblock_version": resblock_version,
            "snake_activ_choice": snake_activ_choice,
            "groups": groups,
            "norm": norm,
            "norm_residual": norm_residual,
            "gated_alpha": gated_alpha,
            "gated_train_alpha": gated_train_alpha,
            "gated_stochastic_dropout": gated_stochastic_dropout,
            "user_residual_skip_wrapper": use_residual_skip_wrapper,
            "init_weights_residual": init_weights_residual,
            "last_activation": last_activation,
        }
        super().__init__(**settings)
        self._forbidden_list.append("_resblock_cal")

    def _get_resblock_activation(self, **kwargs):
        if "snake" in self.resblock_activation:
            if "alpha_logscale" not in kwargs:
                kwargs["alpha_logscale"] = self.alpha_logscale
            if "snake_alpha" not in kwargs:
                kwargs["snake_alpha"] = self.snake_alpha
        elif "aliasfree" in self.resblock_activation:
            if "up_ratio" not in kwargs:
                kwargs["up_ratio"] = self.aliasfree_up_ratio
            if "down_ratio" not in kwargs:
                kwargs["down_ratio"] = self.aliasfree_down_ratio
            if "up_kernel_size" not in kwargs:
                kwargs["up_kernel_size"] = self.aliasfree_up_kernel_size
            if "down_kernel_size" not in kwargs:
                kwargs["down_kernel_size"] = self.aliasfree_down_kernel_size
            return lambda: get_snake(self.snake_activ_choice)(
                kwargs.get("channels"),
                alpha=self.snake_alpha,
                alpha_logscale=self.alpha_logscale,
            )

        return self.get_activation(self.resblock_activation, as_callable=True, **kwargs)

    def retrieve_resblock(
        self,
        channels: int,
        dilation: Tuple[int, ...],
        kernel_size: int,
        activation_kwargs: Dict[str, Any] = {},
        groups: int = 1,
    ) -> Union[ResBlock, AMPBlock, GatedResBlock]:
        match self.resblock_name:
            case "resblock":
                return ResBlock(
                    channels=channels,
                    kernel_size=kernel_size,
                    dilation=dilation,
                    activation=self._get_resblock_activation(**activation_kwargs),
                    groups=groups,
                    version=self.resblock_version,
                    norm=self.norm_residual,
                    init_weights=self.init_weights_residual,
                )
            case "ampblock":
                return AMPBlock(
                    channels=channels,
                    kernel_size=kernel_size,
                    dilation=dilation,
                    activation=self._get_resblock_activation(**activation_kwargs),
                    groups=groups,
                    version=self.resblock_version,
                    norm=self.norm_residual,
                    init_weights=self.init_weights_residual,
                )
            case _:
                return GatedResBlock(
                    channels=channels,
                    kernel_size=kernel_size,
                    dilation=dilation,
                    activation=self._get_resblock_activation(**activation_kwargs),
                    mode=self.residual_mode,
                    norm=self.norm_residual,
                    groups=groups,
                    alpha=self.gated_alpha,
                    alpha_train=self.gated_train_alpha,
                    conditional=False,
                    stochastic_dropout=self.gated_stochastic_dropout,
                    init_weights=self.init_weights_residual,
                )

    def post_process(self):
        self.resblock_activation = self.resblock_activation.lower().strip()
        self.activation = self.activation.lower().strip()
        pass

    @staticmethod
    def get_cfg_v1():
        return {
            "upsample_rates": [8, 8, 2, 2],
            "upsample_kernel_sizes": [16, 16, 4, 4],
            "upsample_initial_channel": 512,
            "resblock_kernel_sizes": [3, 7, 11],
            "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
            "resblock": 0,
            "use_tanh": True,
            "use_bias_on_final_layer": True,
            "norm": "weight",
        }

    @staticmethod
    def get_cfg_v2():
        return {
            "upsample_rates": [8, 8, 2, 2],
            "upsample_kernel_sizes": [16, 16, 4, 4],
            "upsample_initial_channel": 128,
            "resblock_kernel_sizes": [3, 7, 11],
            "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
            "resblock": 0,
            "use_tanh": True,
            "use_bias_on_final_layer": True,
            "norm": "weight",
        }

    @staticmethod
    def get_cfg_v3():
        return {
            "upsample_rates": [8, 8, 4],
            "upsample_kernel_sizes": [16, 16, 8],
            "upsample_initial_channel": 256,
            "resblock_kernel_sizes": [3, 5, 7],
            "resblock_dilation_sizes": [[1, 2], [2, 6], [3, 12]],
            "resblock": 1,
            "use_tanh": True,
            "use_bias_on_final_layer": True,
            "norm": "weight",
        }


class DummyFusion(nn.Module):
    """Similar to identity, but receives more than one input, with will only return the first"""

    def __init__(self, *args, **kwargs):
        super().__init__()
        nn.Identity

    def forward(self, x: Tensor, cond: Tensor, *args, **kwargs):
        return x


class HifiganGenerator(ConvBase):
    def __init__(
        self,
        cfg: Union[HifiganConfig, Dict[str, object]] = HifiganConfig(),
        extra_layer: nn.Module = nn.Identity(),
        cond_processor: nn.Module = nn.Identity(),
        cond_fuse: Type[nn.Module] = DummyFusion,
    ):
        super().__init__()
        cfg = cfg if isinstance(cfg, HifiganConfig) else HifiganConfig(**cfg)
        self.cfg = cfg

        self.num_kernels = len(cfg.resblock_kernel_sizes)
        self.num_upsamples = len(cfg.upsample_rates)
        self.conv_pre = self.get_1d_conv(
            self.cfg.in_channels,
            self.cfg.upsample_initial_channel,
            7,
            padding=3,
            norm="weight_norm",
        )

        # self.activation = cfg.get_activation(cfg.activation, True, kwargs=)
        if isinstance(self.cfg.groups, (list, tuple)):
            assert len(self.cfg.groups) == len(
                self.cfg.upsample_kernel_sizes
            ), "if Groups is a list, it must have the size of upsample kernel sizes."
            self.groups = self.cfg.groups
        else:
            self.groups = [
                self.cfg.groups for _ in range(len(self.cfg.upsample_kernel_sizes))
            ]

        if isinstance(self.cfg.residual_groups, (list, tuple)):
            assert len(self.cfg.residual_groups) == len(
                self.cfg.upsample_kernel_sizes
            ), "if Residual Groups is a list, it must have the size of upsample kernel sizes"
            self.resblocks_groups = self.cfg.residual_groups
        else:
            self.resblocks_groups = [
                self.cfg.residual_groups
                for _ in range(len(self.cfg.upsample_kernel_sizes))
            ]

        self.ups = nn.ModuleList()

        for i, (u, k, g) in enumerate(
            zip(cfg.upsample_rates, cfg.upsample_kernel_sizes, self.groups)
        ):
            in_ch = cfg.upsample_initial_channel // (2**i)
            self.ups.append(
                nn.ModuleDict(
                    dict(
                        cond=cond_fuse(cfg.upsample_initial_channel // (2 ** (i + 1))),
                        up=nn.Sequential(
                            cfg.get_activation(
                                cfg.activation,
                                in_features=in_ch,
                                in_channels=in_ch,
                                channels=in_ch,
                                negative_slope=0.1,
                            ),
                            self.get_1d_conv(
                                in_channels=in_ch,
                                out_channels=cfg.upsample_initial_channel
                                // (2 ** (i + 1)),
                                kernel_size=k,
                                stride=u,
                                padding=(k - u) // 2,
                                groups=g,
                                norm="weight_norm",
                                transposed=True,
                            ),
                        ),
                    ),
                )
            )

        if isinstance(self.cfg.residual_groups, (list, tuple)):

            if len(self.cfg.residual_groups) != len(self.ups):

                print(
                    "Number of gropus does not match with the number of upsample layers!"
                )
                self.residual_groups = self.cfg.groups = [self.cfg.residual_groups]
            self.groups = self.cfg.groups

        skip_wrapper = _dummy if not self.cfg.use_residual_skip_wrapper else SkipWrap
        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = cfg.upsample_initial_channel // (2 ** (i + 1))
            for j, (k, d) in enumerate(
                zip(cfg.resblock_kernel_sizes, cfg.resblock_dilation_sizes)
            ):
                self.resblocks.append(
                    skip_wrapper(
                        self.cfg.retrieve_resblock(
                            ch,
                            d,
                            k,
                            activation_kwargs=dict(
                                in_features=ch, channels=ch, negative_slope=0.1
                            ),
                            groups=self.resblocks_groups[i],
                        )
                    )
                )

        out_ch = cfg.upsample_initial_channel // (2**i)
        self.conv_post = nn.Sequential(
            cfg.get_activation(
                cfg.last_activation,
                in_features=out_ch,
                channels=out_ch,
                negative_slope=0.1,
            ),
            weight_norm(
                nn.Conv1d(ch, 1, 7, 1, padding=3, bias=self.cfg.use_bias_on_final_layer)
            ),
        )
        self.extra_layer = extra_layer

        self.ups.apply(self._normal_init_default)
        self.conv_pre.apply(self._normal_init_default)
        self.conv_post[-1].apply(self._normal_init_default)
        self.resblocks.apply(self._normal_init_default)
        self.cond = cond_processor

    def forward(self, x: Tensor, cond: Optional[Tensor] = None):
        x = self.conv_pre(x)
        if cond is not None:
            encoded_cond = self.cond(cond)
        for i in range(self.num_upsamples):
            if cond is not None:
                x = self.ups[i]["cond"](x, encoded_cond)
            x = self.ups[i]["up"](x)
            xs = torch.zeros_like(x, device=x.device)
            for j in range(self.num_kernels):
                xs += self.resblocks[i * self.num_kernels + j](x)
            x = xs / self.num_kernels
        x = self.conv_post(x)
        x = self.extra_layer(x)
        if self.cfg.use_tanh:
            return x.tanh()
        if self.cfg.do_clamp_if_not_tanh:
            return x.clamp(min=-1.0, max=1.0)
        return x

    @classmethod
    def from_pretrained(
        cls,
        model_file: PathLike,
        model_config: Union[
            HifiganConfig, Dict[str, Any], Dict[str, Any], PathLike
        ] = HifiganConfig(),
        *,
        remove_norms: bool = False,
        strict: bool = False,
        map_location: Union[str, torch.device] = torch.device("cpu"),
        weights_only: bool = False,
        mmap: Optional[bool] = None,
        assign: bool = False,
        **kwargs,
    ):
        is_file(model_file, validate=True)
        if isinstance(map_location, str):
            map_location = torch.device(map_location)
        model_state_dict = torch.load(
            model_file,
            weights_only=weights_only,
            map_location=map_location,
            mmap=mmap,
        )

        if isinstance(model_config, (HifiganConfig, dict)):
            h = model_config
        elif isinstance(model_config, (str, Path, bytes)):
            h = HifiganConfig(**load_json(model_config, {}))

        model = cls(h)
        if remove_norms:
            model.remove_norms()
        try:
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
            return model
        except RuntimeError as e:
            if remove_norms:
                raise e
            print(f"[INFO] Removing norms...")
            model.remove_norms()
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
        return model
