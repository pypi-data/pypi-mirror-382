import enum

from numpy.typing import NDArray


class FilterMode(enum.Enum):
    kNone = 0

    kLinear = 1

    kBilinear = 2

    kBox = 3

class FourCC(enum.Enum):
    kI420 = 808596553

    kI422 = 842150985

    kI444 = 875836489

    kI400 = 808465481

    kNV21 = 825382478

    kNV12 = 842094158

    kYUY2 = 844715353

    kUYVY = 1498831189

    kI010 = 808529993

    kI210 = 808530505

    kM420 = 808596557

    kARGB = 1111970369

    kBGRA = 1095911234

    kABGR = 1380401729

    kAR30 = 808669761

    kAB30 = 808665665

    kAR64 = 875975233

    kAB64 = 875971137

    k24BG = 1195521074

    kRAW = 544694642

    kRGBA = 1094862674

    kRGBP = 1346520914

    kRGBO = 1329743698

    kR444 = 875836498

    kMJPG = 1196444237

    kYV12 = 842094169

    kYV16 = 909203033

    kYV24 = 875714137

    kYU12 = 842093913

    kJ420 = 808596554

    kJ422 = 842150986

    kJ444 = 875836490

    kJ400 = 808465482

    kF420 = 808596550

    kF422 = 842150982

    kF444 = 875836486

    kH420 = 808596552

    kH422 = 842150984

    kH444 = 875836488

    kU420 = 808596565

    kU422 = 842150997

    kU444 = 875836501

    kF010 = 808529990

    kH010 = 808529992

    kU010 = 808530005

    kF210 = 808530502

    kH210 = 808530504

    kU210 = 808530517

    kP010 = 808530000

    kP210 = 808530512

    kIYUV = 1448433993

    kYU16 = 909202777

    kYU24 = 875713881

    kYUYV = 1448695129

    kYUVS = 1937143161

    kHDYC = 1129923656

    k2VUY = 2037741106

    kJPEG = 1195724874

    kDMB1 = 828534116

    kBA81 = 825770306

    kRGB3 = 859981650

    kBGR3 = 861030210

    kCM32 = 536870912

    kCM24 = 402653184

    kL555 = 892679500

    kL565 = 892745036

    k5551 = 825570613

    kI411 = 825308233

    kQ420 = 808596561

    kRGGB = 1111967570

    kBGGR = 1380403010

    kGRBG = 1195528775

    kGBRG = 1196573255

    kH264 = 875967048

    kANY = -1

class RotationMode(enum.Enum):
    kRotate0 = 0

    kRotate90 = 90

    kRotate180 = 180

    kRotate270 = 270

def nv12_scale(src_y: NDArray, src_uv: NDArray, src_stride_y: int, src_stride_uv: int, src_width: int, src_height: int, dst_y: NDArray, dst_uv: NDArray, dst_stride_y: int, dst_stride_uv: int, dst_width: int, dst_height: int, filtering: FilterMode) -> int: ...

def i420_scale(src_y: NDArray, src_u: NDArray, src_v: NDArray, src_stride_y: int, src_stride_u: int, src_stride_v: int, src_width: int, src_height: int, dst_y: NDArray, dst_u: NDArray, dst_v: NDArray, dst_stride_y: int, dst_stride_u: int, dst_stride_v: int, dst_width: int, dst_height: int, filtering: FilterMode) -> int: ...

def convert_to_i420(sample: NDArray, sample_size: int, dst_y: NDArray, dst_stride_y: int, dst_u: NDArray, dst_stride_u: int, dst_v: NDArray, dst_stride_v: int, crop_x: int, crop_y: int, src_width: int, src_height: int, crop_width: int, crop_height: int, rotation: RotationMode, fourcc: FourCC) -> int: ...

def nv12_to_i420(src_y: NDArray, src_uv: NDArray, src_stride_y: int, src_stride_uv: int, dst_y: NDArray, dst_u: NDArray, dst_v: NDArray, dst_stride_y: int, dst_stride_u: int, dst_stride_v: int, width: int, height: int) -> int: ...

def i420_to_nv12(src_y: NDArray, src_u: NDArray, src_v: NDArray, src_stride_y: int, src_stride_u: int, src_stride_v: int, dst_y: NDArray, dst_uv: NDArray, dst_stride_y: int, dst_stride_uv: int, width: int, height: int) -> int: ...

def rgb24_to_i420(src_rgb24: NDArray, src_stride_rgb24: int, dst_y: NDArray, dst_u: NDArray, dst_v: NDArray, dst_stride_y: int, dst_stride_u: int, dst_stride_v: int, width: int, height: int) -> int: ...

def i420_to_rgb24(src_y: NDArray, src_u: NDArray, src_v: NDArray, src_stride_y: int, src_stride_u: int, src_stride_v: int, dst_rgb24: NDArray, dst_stride_rgb24: int, width: int, height: int) -> int: ...
