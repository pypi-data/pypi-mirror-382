from yta_video_opengl.nodes.video import WavingNode
from yta_video_opengl.nodes.audio import ChorusNode, VolumeNode
from yta_video_opengl.nodes import TimedNode
from yta_video_opengl.utils import texture_to_frame
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_programming.decorators import singleton_old
from typing import Union

import moderngl


class _AudioEffects:
    """
    *For internal use only*

    The audio effects that will be available
    throught our internal _Effects class to
    wrap and make available all the audio
    effects we want to be available.
    """

    def __init__(
        self,
        effects: 'Effects'
    ):
        self._effects: Effects = effects
        """
        The parent instance that includes this
        class instance as a property.
        """

    """
    Here below we expose all the effects
    we want the users to have available to
    be used.
    """
    def chorus(
        self,
        sample_rate: int,
        depth: int = 0,
        frequency: float = 0.25,
        start: Union[int, float, 'Fraction'] = 0,
        end: Union[int, float, 'Fraction', None] = None
    ):
        return _create_node(
            ChorusNode(
                sample_rate = sample_rate,
                depth = depth,
                frequency = frequency
            ),
            start = start,
            end = end
        )

    def volume(
        self,
        factor: callable,
        start: Union[int, float, 'Fraction'] = 0,
        end: Union[int, float, 'Fraction', None] = None
    ):
        return _create_node(
            VolumeNode(
                factor_fn = factor
            ),
            start = start,
            end = end
        )
    
    # TODO: Include definitive and tested audio
    # effects here below

class _VideoEffects:
    """
    *For internal use only*

    The video effects that will be available
    throught our internal _Effects class to
    wrap and make available all the video
    effects we want to be available.
    """

    def __init__(
        self,
        effects: 'Effects'
    ):
        self._effects: Effects = effects
        """
        The parent instance that includes this
        class instance as a property.
        """

    """
    Here below we expose all the effects
    we want the users to have available to
    be used.
    """
    def waving_node(
        self,
        # TODO: Maybe 'frame_size' (?)
        size: tuple[int, int],
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0,
        start: Union[int, float, 'Fraction'] = 0.0,
        end: Union[int, float, 'Fraction', None] = None
    ) -> 'TimedNode':
        """
        TODO: Explain this better.

        The 'start' and 'end' time moments are the
        limits of the time range in which the effect
        has to be applied to the frames inside that
        time range. Providing start=0 and end=None
        will make the effect to be applied to any
        frame.
        """
        return _create_node(
            WavingNode(
                context = self._effects.opengl_context,
                size = size,
                amplitude = amplitude,
                frequency = frequency,
                speed = speed
            ),
            start = start,
            end = end
        )
    
    # TODO: Include definitive and tested video
    # effects here below

@singleton_old
class Effects:
    """
    Singleton instance.

    It is a singleton instance to have a
    unique context for all the instances
    that need it and instantiate this
    class to obtain it. Here we group all
    the nodes we have available for the
    user.

    This class is to simplify the access to
    the effect nodes and also to have the
    single context always available.

    Even though we can have more effects,
    this class is also the way we expose only
    the ones we actually want to expose to 
    the user.

    The GPU will make the calculations in
    parallel by itself, so we can handle a
    single context to make the nodes share
    textures and buffers.
    """

    def __init__(
        self
    ):
        self.opengl_context = moderngl.create_context(standalone = True)
        """
        The opengl context that will be shared
        by all the opengl nodes.
        """
        self.audio: _AudioEffects = _AudioEffects(self)
        """
        Shortcut to the audio effects that are
        available.
        """
        self.video: _VideoEffects = _VideoEffects(self)
        """
        Shortcut to the video effects that are
        available.
        """

def _create_node(
    node: Union['_AudioNode', '_VideoNode'],
    start: Union[int, float, 'Fraction'],
    end: Union[int, float, 'Fraction', None]
):
    # We could be other classes in the middle,
    # because an OpenglNode inherits from
    # other class
    ParameterValidator.validate_mandatory_subclass_of('node', node, ['_AudioNode', '_VideoNode', 'OpenglNodeBase'])

    # We have to create a node wrapper with the
    # time range in which it has to be applied
    # to all the frames.
    return TimedNode(
        node = node,
        start = start,
        end = end
    )

class _EffectStacked:
    """
    Class to wrap an effect that will be
    stacked with an specific priority.

    Priority is higher when lower value,
    and lower when higher value.
    """

    @property
    def is_audio_effect(
        self
    ) -> bool:
        """
        Flag to indicate if it is an audio effect
        or not.
        """
        return self.effect.is_audio_node

    @property
    def is_video_effect(
        self
    ) -> bool:
        """
        Flag to indicate if it is a video effect
        or not.
        """
        return self.effect.is_video_node

    def __init__(
        self,
        effect: TimedNode,
        priority: int
    ):
        self.effect: TimedNode = effect
        """
        The effect to be applied.
        """
        self.priority: int = priority
        """
        The priority this stacked frame has versus
        the other stacked effects.
        """

# TODO: Move to another py file (?)
class EffectsStack:
    """
    Class to include a collection of effects
    we want to apply in some entity, that 
    will make easier to apply them.

    You can use this stack to keep the effects
    you want to apply on a Media or on the
    Timeline of your video editor.
    """

    @property
    def copy(
        self
    ) -> 'EffectsStack':
        """
        Get a copy of this instance.
        """
        effects_stack = EffectsStack()

        for effect_sttacked in self._effects:
            effects_stack.add_effect(
                effect = effect_sttacked.effect.copy,
                priority = effect_sttacked.priority
            )

        return effects_stack

    @property
    def video_effects(
        self
    ) -> list[_EffectStacked]:
        """
        The video effects but ordered by 'priority'
        and 'start' time moment.
        """
        return sorted(
            [
                effect
                for effect in self._effects
                if effect.is_video_effect
            ],
            key = lambda effect: (effect.priority, effect.effect.start)
        )
    
    @property
    def audio_effects(
        self
    ) -> list[_EffectStacked]:
        """
        The audio effects but ordered by 'priority'
        and 'start' time moment.
        """
        return sorted(
            [
                effect
                for effect in self._effects
                if effect.is_audio_effect
            ],
            key = lambda effect: (effect.priority, effect.effect.start)
        )
    
    @property
    def lowest_audio_priority(
        self
    ) -> int:
        """
        The priority of the audio effect with the
        lowest one, or 0 if no audio effects.
        """
        return min(
            self.audio_effects,
            key = lambda effect: effect.priority,
            default = 0
        )

    @property
    def lowest_video_priority(
        self
    ) -> int:
        """
        The priority of the video effect with the
        lowest one, or 0 if no video effects.
        """
        return min(
            self.video_effects,
            key = lambda effect: effect.priority,
            default = 0
        )
    
    def __init__(
        self
    ):
        self._effects: list[_EffectStacked] = []
        """
        A list containing all the effects that
        have been added to this stack, unordered.
        """

    def get_audio_effects_for_t(
        self,
        t: Union[int, float, 'Fraction']
    ) -> list[TimedNode]:
        """
        Get the audio effects, ordered by priority
        and the 'start' field, that must be applied
        within the 't' time moment provided because
        it is within the [start, end) time range.
        """
        return [
            effect.effect
            for effect in self.audio_effects
            if effect.effect.is_within_time(t)
        ]

    def get_video_effects_for_t(
        self,
        t: Union[int, float, 'Fraction']
    ) -> list[TimedNode]:
        """
        Get the video effects, ordered by priority
        and the 'start' field, that must be applied
        within the 't' time moment provided because
        it is within the [start, end) time range.
        """
        return [
            effect.effect
            for effect in self.video_effects
            if effect.effect.is_within_time(t)
        ]

    def add_effect(
        self,
        effect: TimedNode,
        priority: Union[int, None] = None
    ) -> 'EffectsStack':
        """
        Add the provided 'effect' to the stack.
        """
        ParameterValidator.validate_mandatory_instance_of('effect', effect, TimedNode)
        ParameterValidator.validate_positive_int('priority', priority, do_include_zero = True)

        # TODO: What about the same effect added
        # twice during the same time range? Can we
        # allow it? It will be applied twice for
        # specific 't' time moments but with 
        # different attributes. is it ok (?)

        # TODO: What if priority is already taken?
        # Should we let some effects have the same
        # priority (?)
        priority = (
            self.lowest_audio_priority + 1
            if (
                priority is None and
                effect.is_audio_node
            ) else
            self.lowest_video_priority + 1
            if (
                priority is None and
                effect.is_video_node
            ) else
            priority
        )

        self._effects.append(_EffectStacked(
            effect = effect,
            priority = priority
        ))

        return self
    
    def apply_video_effects_at_t(
        self,
        frame: 'np.ndarray',
        t: Union[int, float, 'Fraction']
    ) -> 'np.ndarray':
        """
        Apply all the video effects that must be
        applied for the given 't' time moment to
        the provided 'frame' (that must be the
        video frame of that time moment).
        """
        for effect in self.get_video_effects_for_t(t):
            frame = effect.process(frame, t)

        # TODO: Check when the frame comes as a
        # Texture and when as a numpy array. I
        # think when we apply an opengl node it
        # is a texture, but we need to return it
        # as a numpy, always
        return (
            texture_to_frame(frame)
            if PythonValidator.is_instance_of(frame, moderngl.Texture) else
            frame
        )
    
    def apply_audio_effects_at_t(
        self,
        frame: 'np.ndarray',
        t: Union[int, float, 'Fraction']
    ) -> 'np.ndarray':
        """
        Apply all the video effects that must be
        applied for the given 't' time moment to
        the provided 'frame' (that must be the
        audio frame of that time moment).
        """
        for effect in self.get_audio_effects_for_t(t):
            frame = effect.process(frame, t)

        # Frame can only by a numpy array here
        return frame
    
    # TODO: Create 'remove_effect'