import manim as _manim

from .camera import *
from .updateFormAlphaFunc import *
from .draw_polygon import *
from .bounceText import *

globals().update({k: getattr(_manim, k) for k in dir(_manim) if not k.startswith("_")})
__all__ = [k for k in dir(_manim) if not k.startswith("_")]
__all__ += [k for k in dir() if not k.startswith("_") and k not in __all__]