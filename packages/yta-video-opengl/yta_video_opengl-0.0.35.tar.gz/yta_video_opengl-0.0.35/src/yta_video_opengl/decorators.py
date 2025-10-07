from functools import wraps
from yta_video_opengl.utils import frame_to_texture
from yta_validation import PythonValidator


def force_inputs_as_textures(
    func
):
    """
    Transform any parameter that starts with 'input'
    and is a numpy array into a 'moderngl.Texture',
    if needed. If it is already a texture it will do
    nothing.

    This decorator uses a `self.context` attribute.
    """
    @wraps(func)
    def wrapper(
        self,
        *args,
        **kwargs
    ):
        # Get argument names
        arg_names = func.__code__.co_varnames[1:func.__code__.co_argcount]

        # Transform arguments if positional
        new_args = []
        for name, val in zip(arg_names, args):
            if (
                name.startswith('input') and
                PythonValidator.is_numpy_array(val)
            ):
                val = frame_to_texture(val, self.context)

            new_args.append(val)

        # Transform arguments if named
        for key, val in kwargs.items():
            if (
                key.startswith('input') and
                PythonValidator.is_numpy_array(val)
            ):
                kwargs[key] = frame_to_texture(val, self.context)

        return func(self, *new_args, **kwargs)
    
    return wrapper

"""
I'm implementing the decorator in all the
subclasses, in the 'process' method, but it
seems to be a way to force it. I don't want
to implement it by now, but here it is:

class AutoTextureMeta(ABCMeta):
    def __new__(mcls, name, bases, attrs):
        # si la subclase define process, lo envolvemos
        if 'process' in attrs:
            attrs['process'] = auto_texture_inputs(attrs['process'])
        return super().__new__(mcls, name, bases, attrs)

class Base(metaclass=AutoTextureMeta):
    @abstractmethod
    def process(self, *args, **kwargs):
        pass
"""