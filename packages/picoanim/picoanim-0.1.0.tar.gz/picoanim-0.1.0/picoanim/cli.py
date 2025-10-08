from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import runpy
import sys
from types import ModuleType


def _load_module_from_path(path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location("_picoanim_user_module_", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _resolve_scene(target: str):  # noqa: ANN001
    # target of the form module:Class or path.py:Class
    if ":" not in target:
        raise SystemExit("Target must be of the form 'module_or_file:SceneClass'")
    mod_part, class_name = target.split(":", 1)
    if os.path.isfile(mod_part):
        mod = _load_module_from_path(mod_part)
    else:
        mod = importlib.import_module(mod_part)
    SceneClass = getattr(mod, class_name, None)
    if SceneClass is None:
        raise SystemExit(f"Class '{class_name}' not found in '{mod_part}'")
    return SceneClass


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="picoanim", description="Tiny 2D animation engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_render = sub.add_parser("render", help="Render a scene")
    p_render.add_argument("target", help="module_or_file:SceneClass")
    p_render.add_argument("-o", "--output", default="output.mp4", help="Output file (mp4 or gif)")
    p_render.add_argument("--fps", type=int, default=None, help="Override FPS")
    p_render.add_argument("--size", type=str, default=None, help="Frame size as WIDTHxHEIGHT")
    p_render.add_argument("--bg", type=str, default=None, help="Background color (e.g., #ffffff)")

    args = parser.parse_args(argv)

    if args.cmd == "render":
        SceneClass = _resolve_scene(args.target)
        width, height = 640, 360
        if args.size:
            try:
                w, h = args.size.lower().split("x")
                width, height = int(w), int(h)
            except Exception as e:
                raise SystemExit(f"Invalid --size '{args.size}': {e}")
        kwargs = {"width": width, "height": height}
        if args.fps is not None:
            kwargs["fps"] = int(args.fps)
        if args.bg is not None:
            kwargs["bg_color"] = args.bg
        scene = SceneClass(**kwargs)
        scene.render(args.output)


if __name__ == "__main__":  # pragma: no cover
    main()
