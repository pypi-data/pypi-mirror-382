"""
Working with video frames has to be done
with nodes that use OpenGL because this
way, by using the GPU, is the best way.
"""
from yta_video_opengl.nodes.video.opengl import WavingNode
from yta_video_opengl.nodes.video.opengl.experimental import RotatingInCenterFrame

# Expose all the nodes we have

__all__ = [
    'WavingNode',
    'RotatingInCenterFrame'
]