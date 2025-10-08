# picoanim

A tiny 2D, programmatic animation engine inspired by Manim.

- **Backend**: Pillow (raster drawing) + imageio (MP4/GIF writing)
- **Use case**: Quickly script simple animated scenes with shapes and text

## Quickstart

1. Create and activate a virtual environment (recommended)
2. Install the package in editable mode:

```bash
pip install -e .
```

3. Render the included example scene:

```bash
picoanim render examples/hello_scene.py:HelloScene -o hello.mp4 --fps 30 --size 1280x720
```

This will create `hello.mp4` in the project root.

## Minimal example

Create `my_scene.py`:

```python
from picoanim import Scene, Circle, Text, MoveTo, FadeIn, ScaleTo

class MyScene(Scene):
    def construct(self):
        dot = Circle(radius=40, fill="#4F46E5", stroke="#1F2937", stroke_width=6)
        dot.x = -250
        self.add(dot)

        label = Text("Hello", font_size=48, color="white")
        label.opacity = 0
        self.add(label)

        self.play(MoveTo(dot, (0, 0), duration=1.5))
        self.play(FadeIn(label, duration=0.8))
        self.play(ScaleTo(dot, 0.6, duration=0.6))
        self.wait(0.5)
```

Render it:

```bash
picoanim render my_scene.py:MyScene -o out.mp4 --fps 30 --size 1280x720
```

## Features

- **Scene graph**: Add `MObject`-based shapes: `Circle`, `Rectangle`, `Line`, `Text`
- **Animations**: `MoveTo`, `FadeIn`, `FadeOut`, `ScaleTo` with easing (`linear`, `ease_in_out`)
- **Rendering**: MP4 (via ffmpeg) or GIF output

## Requirements

- Python 3.9+
- On Windows/macOS/Linux, `imageio-ffmpeg` provides an ffmpeg binary automatically.

## License

MIT

## Install (after publishing)

```bash
pip install picoanim
```

## Local development (Python 3)

```powershell
# Windows PowerShell
python3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## Publish to PyPI

1) Build distributions

```powershell
python3 -m pip install --upgrade pip build twine
python3 -m build
python3 -m twine check dist/*
```

2) Test upload to TestPyPI

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-TESTPYPI_TOKEN"
python3 -m twine upload --repository testpypi dist/*
```

3) Test installation from TestPyPI (optional)

```powershell
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple picoanim
```

4) Upload to PyPI

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-LIVE_TOKEN"
python3 -m twine upload dist/*
```

Notes:

- **Versioning**: Update `version` in `pyproject.toml` before uploading new releases.
- **What’s included**: `MANIFEST.in` ensures `README.md`, `LICENSE`, and `examples/` are shipped in the sdist.
