from typing import Any, Dict, List, Optional, Tuple, Union
import torch
import torch.nn.functional as F
from torch import Tensor, nn
from torch.nn.common_types import _size_2_t
import inspect

# ----------- Utils ----------- #
def get_layer_map():
    """
    Dynamically generates a dictionary mapping class names to classes,
    filtering to include only those that are subclasses of nn.Module,
    ensuring they are relevant neural network layers.
    """
    layer_map = {}
    from yolo.model import module

    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, nn.Module) and obj is not nn.Module:
            layer_map[name] = obj
    return layer_map


def auto_pad(kernel_size: _size_2_t, dilation: _size_2_t = 1, **kwargs) -> Tuple[int, int]:
    """
    Auto Padding for the convolution blocks
    """
    if isinstance(kernel_size, int):
        kernel_size = (kernel_size, kernel_size)
    if isinstance(dilation, int):
        dilation = (dilation, dilation)

    pad_h = ((kernel_size[0] - 1) * dilation[0]) // 2
    pad_w = ((kernel_size[1] - 1) * dilation[1]) // 2
    return (pad_h, pad_w)


def create_activation_function(activation: str) -> nn.Module:
    """
    Retrieves an activation function from the PyTorch nn module based on its name, case-insensitively.
    """
    if not activation or activation.lower() in ["false", "none"]:
        return nn.Identity()

    activation_map = {
        name.lower(): obj
        for name, obj in nn.modules.activation.__dict__.items()
        if isinstance(obj, type) and issubclass(obj, nn.Module)
    }
    if activation.lower() in activation_map:
        return activation_map[activation.lower()](inplace=True)
    else:
        raise ValueError(f"Activation function '{activation}' is not found in torch.nn")


def round_up(x: Union[int, Tensor], div: int = 1) -> Union[int, Tensor]:
    """
    Rounds up `x` to the bigger-nearest multiple of `div`.
    """
    return x + (-x % div)


# ----------- Basic Class ----------- #
class Conv(nn.Module):
    """A basic convolutional block that includes convolution, batch normalization, and activation."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_2_t,
        *,
        activation: Optional[str] = "SiLU",
        **kwargs,
    ):
        super().__init__()
        kwargs.setdefault("padding", auto_pad(kernel_size, **kwargs))
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, bias=False, **kwargs)
        self.bn = nn.BatchNorm2d(out_channels, eps=1e-3, momentum=3e-2)
        self.act = create_activation_function(activation)

    def forward(self, x: Tensor) -> Tensor:
        return self.act(self.bn(self.conv(x)))


class Pool(nn.Module):
    """A generic pooling block supporting 'max' and 'avg' pooling methods."""

    def __init__(self, method: str = "max", kernel_size: _size_2_t = 2, **kwargs):
        super().__init__()
        kwargs.setdefault("padding", auto_pad(kernel_size, **kwargs))
        pool_classes = {"max": nn.MaxPool2d, "avg": nn.AvgPool2d}
        self.pool = pool_classes[method.lower()](kernel_size=kernel_size, **kwargs)

    def forward(self, x: Tensor) -> Tensor:
        return self.pool(x)


class Concat(nn.Module):
    def __init__(self, dim=1):
        super(Concat, self).__init__()
        self.dim = dim

    def forward(self, x):
        return torch.cat(x, self.dim)


# ----------- Detection Class ----------- #
class Detection(nn.Module):
    """A single YOLO Detection head for detection models"""

    def __init__(self, in_channels: Tuple[int], num_classes: int, *, reg_max: int = 16, use_group: bool = True):
        super().__init__()

        groups = 4 if use_group else 1
        anchor_channels = 4 * reg_max

        first_neck, in_channels = in_channels
        anchor_neck = max(round_up(first_neck // 4, groups), anchor_channels, reg_max)
        class_neck = max(first_neck, min(num_classes * 2, 128))

        self.anchor_conv = nn.Sequential(
            Conv(in_channels, anchor_neck, 3),
            Conv(anchor_neck, anchor_neck, 3, groups=groups),
            nn.Conv2d(anchor_neck, anchor_channels, 1, groups=groups),
        )
        self.class_conv = nn.Sequential(
            Conv(in_channels, class_neck, 3), Conv(class_neck, class_neck, 3), nn.Conv2d(class_neck, num_classes, 1)
        )

        self.anc2vec = Anchor2Vec(reg_max=reg_max)

        self.anchor_conv[-1].bias.data.fill_(1.0)
        self.class_conv[-1].bias.data.fill_(-10)  # TODO: math.log(5 * 4 ** idx / 80 ** 3)

    def forward(self, x: Tensor) -> Tuple[Tensor]:
        anchor_x = self.anchor_conv(x)
        class_x = self.class_conv(x)
        anchor_x, vector_x = self.anc2vec(anchor_x)
        return class_x, anchor_x, vector_x


class MultiheadDetection(nn.Module):
    """Mutlihead Detection module for Dual detect or Triple detect"""

    def __init__(self, in_channels: List[int], num_classes: int, **head_kwargs):
        super().__init__()
        DetectionHead = Detection

        if head_kwargs.pop("version", None) == "v7":
            DetectionHead = IDetection

        self.heads = nn.ModuleList(
            [DetectionHead((in_channels[0], in_channel), num_classes, **head_kwargs) for in_channel in in_channels]
        )

    def forward(self, x_list: List[torch.Tensor]) -> List[torch.Tensor]:
        return [head(x) for x, head in zip(x_list, self.heads)]


class Anchor2Vec(nn.Module):
    def __init__(self, reg_max: int = 16) -> None:
        super().__init__()
        reverse_reg = torch.arange(reg_max, dtype=torch.float32).view(1, reg_max, 1, 1, 1)
        self.anc2vec = nn.Conv3d(in_channels=reg_max, out_channels=1, kernel_size=1, bias=False)
        self.anc2vec.weight = nn.Parameter(reverse_reg, requires_grad=False)

    def forward(self, anchor_x: Tensor) -> Tensor:
        #anchor_x = rearrange(anchor_x, "B (P R) h w -> B R P h w", P=4)
        B, PR, h, w = anchor_x.shape
        P = 4
        R = PR // P
        anchor_x = anchor_x.reshape(B, P, R, h, w).permute(0, 2, 1, 3, 4) 
        vector_x = anchor_x.softmax(dim=1)
        vector_x = self.anc2vec(vector_x)[:, 0]
        return anchor_x, vector_x


# ----------- Backbone Class ----------- #
class RepConv(nn.Module):
    """A convolutional block that combines two convolution layers (kernel and point-wise)."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_2_t = 3,
        *,
        activation: Optional[str] = "SiLU",
        **kwargs,
    ):
        super().__init__()
        self.act = create_activation_function(activation)
        self.conv1 = Conv(in_channels, out_channels, kernel_size, activation=False, **kwargs)
        self.conv2 = Conv(in_channels, out_channels, 1, activation=False, **kwargs)

    def forward(self, x: Tensor) -> Tensor:
        return self.act(self.conv1(x) + self.conv2(x))


class Bottleneck(nn.Module):
    """A bottleneck block with optional residual connections."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        kernel_size: Tuple[int, int] = (3, 3),
        residual: bool = True,
        expand: float = 1.0,
        **kwargs,
    ):
        super().__init__()
        neck_channels = int(out_channels * expand)
        self.conv1 = RepConv(in_channels, neck_channels, kernel_size[0], **kwargs)
        self.conv2 = Conv(neck_channels, out_channels, kernel_size[1], **kwargs)
        self.residual = residual

        if residual and (in_channels != out_channels):
            self.residual = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.conv2(self.conv1(x))
        return x + y if self.residual else y


class RepNCSP(nn.Module):
    """RepNCSP block with convolutions, split, and bottleneck processing."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        *,
        csp_expand: float = 0.5,
        repeat_num: int = 1,
        neck_args: Dict[str, Any] = {},
        **kwargs,
    ):
        super().__init__()

        neck_channels = int(out_channels * csp_expand)
        self.conv1 = Conv(in_channels, neck_channels, kernel_size, **kwargs)
        self.conv2 = Conv(in_channels, neck_channels, kernel_size, **kwargs)
        self.conv3 = Conv(2 * neck_channels, out_channels, kernel_size, **kwargs)

        self.bottleneck = nn.Sequential(
            *[Bottleneck(neck_channels, neck_channels, **neck_args) for _ in range(repeat_num)]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = self.bottleneck(self.conv1(x))
        x2 = self.conv2(x)
        return self.conv3(torch.cat((x1, x2), dim=1))


class ELAN(nn.Module):
    """ELAN  structure."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        part_channels: int,
        *,
        process_channels: Optional[int] = None,
        **kwargs,
    ):
        super().__init__()

        if process_channels is None:
            process_channels = part_channels // 2

        self.conv1 = Conv(in_channels, part_channels, 1, **kwargs)
        self.conv2 = Conv(part_channels // 2, process_channels, 3, padding=1, **kwargs)
        self.conv3 = Conv(process_channels, process_channels, 3, padding=1, **kwargs)
        self.conv4 = Conv(part_channels + 2 * process_channels, out_channels, 1, **kwargs)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1, x2 = self.conv1(x).chunk(2, 1)
        x3 = self.conv2(x2)
        x4 = self.conv3(x3)
        x5 = self.conv4(torch.cat([x1, x2, x3, x4], dim=1))
        return x5


class RepNCSPELAN(nn.Module):
    """RepNCSPELAN block combining RepNCSP blocks with ELAN structure."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        part_channels: int,
        *,
        process_channels: Optional[int] = None,
        csp_args: Dict[str, Any] = {},
        csp_neck_args: Dict[str, Any] = {},
        **kwargs,
    ):
        super().__init__()

        if process_channels is None:
            process_channels = part_channels // 2

        self.conv1 = Conv(in_channels, part_channels, 1, **kwargs)
        self.conv2 = nn.Sequential(
            RepNCSP(part_channels // 2, process_channels, neck_args=csp_neck_args, **csp_args),
            Conv(process_channels, process_channels, 3, padding=1, **kwargs),
        )
        self.conv3 = nn.Sequential(
            RepNCSP(process_channels, process_channels, neck_args=csp_neck_args, **csp_args),
            Conv(process_channels, process_channels, 3, padding=1, **kwargs),
        )
        self.conv4 = Conv(part_channels + 2 * process_channels, out_channels, 1, **kwargs)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1, x2 = self.conv1(x).chunk(2, 1)
        x3 = self.conv2(x2)
        x4 = self.conv3(x3)
        x5 = self.conv4(torch.cat([x1, x2, x3, x4], dim=1))
        return x5


class AConv(nn.Module):
    """Downsampling module combining average and max pooling with convolution for feature reduction."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        mid_layer = {"kernel_size": 3, "stride": 2}
        self.avg_pool = Pool("avg", kernel_size=2, stride=1)
        self.conv = Conv(in_channels, out_channels, **mid_layer)

    def forward(self, x: Tensor) -> Tensor:
        x = self.avg_pool(x)
        x = self.conv(x)
        return x

class ADown(nn.Module):
    """Downsampling module combining average and max pooling with convolution for feature reduction."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        half_in_channels = in_channels // 2
        half_out_channels = out_channels // 2
        mid_layer = {"kernel_size": 3, "stride": 2}
        self.avg_pool = Pool("avg", kernel_size=2, stride=1)
        self.conv1 = Conv(half_in_channels, half_out_channels, **mid_layer)
        self.max_pool = Pool("max", **mid_layer)
        self.conv2 = Conv(half_in_channels, half_out_channels, kernel_size=1)

    def forward(self, x: Tensor) -> Tensor:
        x = self.avg_pool(x)
        x1, x2 = x.chunk(2, dim=1)
        x1 = self.conv1(x1)
        x2 = self.max_pool(x2)
        x2 = self.conv2(x2)
        return torch.cat((x1, x2), dim=1)


class CBLinear(nn.Module):
    """Convolutional block that outputs multiple feature maps split along the channel dimension."""

    def __init__(self, in_channels: int, out_channels: List[int], kernel_size: int = 1, **kwargs):
        super(CBLinear, self).__init__()
        kwargs.setdefault("padding", auto_pad(kernel_size, **kwargs))
        self.conv = nn.Conv2d(in_channels, sum(out_channels), kernel_size, **kwargs)
        self.out_channels = list(out_channels)

    def forward(self, x: Tensor) -> Tuple[Tensor]:
        x = self.conv(x)
        return x.split(self.out_channels, dim=1)

class CBFuse(nn.Module):
    def __init__(self, index: List[int], mode: str = "nearest"):
        super().__init__()
        self.idx = index
        self.mode = mode

    def forward(self, x_list: List[torch.Tensor]) -> List[Tensor]:
        target = x_list[-1]
        target_size = target.shape[2:]  # Batch, Channel, H, W

        res = [F.interpolate(x[pick_id], size=target_size, mode=self.mode) for pick_id, x in zip(self.idx, x_list)]
        out = torch.stack(res + [target]).sum(dim=0)
        return out
        
class SPPELAN(nn.Module):
    """SPPELAN module comprising multiple pooling and convolution layers."""

    def __init__(self, in_channels: int, out_channels: int, neck_channels: Optional[int] = None):
        super(SPPELAN, self).__init__()
        neck_channels = neck_channels or out_channels // 2

        self.conv1 = Conv(in_channels, neck_channels, kernel_size=1)
        self.pools = nn.ModuleList([Pool("max", 5, stride=1) for _ in range(3)])
        self.conv5 = Conv(4 * neck_channels, out_channels, kernel_size=1)

    def forward(self, x: Tensor) -> Tensor:
        features = [self.conv1(x)]
        for pool in self.pools:
            features.append(pool(features[-1]))
        return self.conv5(torch.cat(features, dim=1))


class UpSample(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.UpSample = nn.Upsample(**kwargs)

    def forward(self, x):
        return self.UpSample(x)