from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import imageio

from .animation import Animation
from .colors import parse_color
from .mobject import MObject
from .renderer import Renderer


@dataclass
class _Segment:
    animations: List[Animation]
    duration: float


class Scene:
    def __init__(self, width: int = 640, height: int = 360, fps: int = 30, bg_color: object = "white"):
        self.width = int(width)
        self.height = int(height)
        self.fps = int(fps)
        self.bg_color = parse_color(bg_color)
        self.renderer = Renderer(self.width, self.height, self.bg_color)
        self.mobjects: List[MObject] = []
        self._segments: List[_Segment] = []
        self._initial_state: Dict[int, Dict[str, float]] = {}
        self._virtual_state: Dict[int, Dict[str, float]] = {}
        self._constructed = False

    # override in user code
    def construct(self) -> None:  # noqa: D401
        """Override to build the scene (add mobjects, call play/wait)."""
        pass

    # scene graph
    def add(self, *mobs: MObject) -> None:
        for m in mobs:
            if m not in self.mobjects:
                self.mobjects.append(m)
                m._scene = self
                st = m.get_state()
                self._initial_state[id(m)] = dict(st)
                self._virtual_state[id(m)] = dict(st)

    def remove(self, *mobs: MObject) -> None:
        for m in mobs:
            if m in self.mobjects:
                self.mobjects.remove(m)
                self._initial_state.pop(id(m), None)
                self._virtual_state.pop(id(m), None)

    # timeline
    def play(self, *anims: Animation, duration: float | None = None) -> None:
        # Ensure anims know their start and end states and update virtual state
        if not anims:
            return
        # attach missing targets to scene
        for a in anims:
            if a.target not in self.mobjects:
                self.add(a.target)
        for a in anims:
            st = dict(self._virtual_state[id(a.target)])
            # Each animation subclass must implement configure()
            a.configure(st)
        seg_dur = max((a.duration for a in anims), default=0.0)
        if duration is not None:
            seg_dur = float(duration)
        # commit end states into virtual state
        for a in anims:
            self._virtual_state[id(a.target)].update(a._end)
        self._segments.append(_Segment(list(anims), seg_dur))

    def wait(self, seconds: float) -> None:
        self._segments.append(_Segment([], float(seconds)))

    # rendering
    def _reset_states(self) -> None:
        for m in self.mobjects:
            st = self._initial_state.get(id(m))
            if st:
                m.set_state(st)

    def _iter_frames(self):  # noqa: ANN001
        for seg in self._segments:
            frames = max(1, int(round(seg.duration * self.fps)))
            for i in range(frames):
                alpha = 0.0 if frames == 1 else i / (frames - 1)
                for a in seg.animations:
                    a.apply_at(alpha)
                img = self.renderer.draw(self.mobjects)
                yield self.renderer.as_frame(img)
            # finalize states at end of segment (ensures exact end values)
            for a in seg.animations:
                a.apply_at(1.0)

    def render(self, output: str, fps: int | None = None, format: str | None = None) -> None:
        if not self._constructed:
            self.construct()
            self._constructed = True
        self._reset_states()
        fps_eff = int(fps or self.fps)
        fmt = (format or (output.split(".")[-1].lower() if "." in output else "mp4")).lower()
        writer_args = {"fps": fps_eff}
        if fmt == "gif":
            writer_args.update({"loop": 0})
        with imageio.get_writer(output, **writer_args) as w:
            for frame in self._iter_frames():
                w.append_data(frame)
