from yta_validation import PythonValidator
from typing import Union

import numpy as np
import moderngl


class _Uniforms:
    """
    *For internal use only*

    Class to wrap the functionality related to
    handling the opengl program uniforms.
    """

    @property
    def uniforms(
        self
    ) -> dict:
        """
        The uniforms in the program, as a dict, in
        the format `{key, value}`.
        """
        return {
            key: self.program[key].value
            for key in self.program
            if PythonValidator.is_instance_of(self.program[key], moderngl.Uniform)
        }

    def __init__(
        self,
        program: moderngl.Program
    ):
        self.program: moderngl.Program = program
        """
        The program instance this handler class
        belongs to.
        """

    def get(
        self,
        name: str
    ) -> Union[any, None]:
        """
        Get the value of the uniform with the
        given 'name'.
        """
        return self.uniforms.get(name, None)

    # TODO: I need to refactor these method to
    # accept a **kwargs maybe, or to auto-detect
    # the type and add the uniform as it must be
    # done
    def set(
        self,
        name: str,
        value
    ) -> '_Uniforms':
        """
        Set the provided 'value' to the normal type
        uniform with the given 'name'. Here you have
        some examples of defined uniforms we can set
        with this method:
        - `uniform float name;`

        TODO: Add more examples
        """
        if name in self.program:
            self.program[name].value = value

        return self
    
    def set_vec(
        self,
        name: str,
        values
    ) -> '_Uniforms':
        """
        Set the provided 'value' to the normal type
        uniform with the given 'name'. Here you have
        some examples of defined uniforms we can set
        with this method:
        - `uniform vec2 name;`

        TODO: Is this example ok? I didn't use it yet
        """
        if name in self.program:
            self.program[name].write(np.array(values, dtype = 'f4').tobytes())

        return self

    def set_mat(
        self,
        name: str,
        value
    ) -> '_Uniforms':
        """
        Set the provided 'value' to a `matN` type
        uniform with the given 'name'. The 'value'
        must be a NxN matrix (maybe numpy array)
        transformed to bytes ('.tobytes()').
        
        This uniform must be defined in the vertex
        like this:
        - `uniform matN name;`

        TODO: Maybe we can accept a NxN numpy 
        array and do the .tobytes() by ourselves...
        """
        if name in self.program:
            self.program[name].write(value)

        return self
    
    def print(
        self
    ) -> '_Uniforms':
        """
        Print the defined uniforms in console.
        """
        for key, value in self.uniforms.items():
            print(f'"{key}": {str(value)}')