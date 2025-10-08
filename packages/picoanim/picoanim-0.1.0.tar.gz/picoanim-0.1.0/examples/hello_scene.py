from picoanim import Scene, Circle, Rectangle, Line, Text, MoveTo, FadeIn, FadeOut, ScaleTo


class HelloScene(Scene):
    def construct(self):
        # Background rectangle for contrast
        bg = Rectangle(width=self.width - 80, height=self.height - 80, fill="#111827", stroke="#111827", stroke_width=0)
        self.add(bg)

        dot = Circle(radius=80, fill="#4F46E5", stroke="#1F2937", stroke_width=8)
        dot.x = -300
        self.add(dot)

        label = Text("picoanim", font_size=56, color="white")
        label.opacity = 0.0
        self.add(label)

        self.play(MoveTo(dot, (0, 0), duration=1.2, easing="ease_in_out"))
        self.play(FadeIn(label, duration=0.8))
        self.play(ScaleTo(dot, 0.6, duration=0.6))
        self.wait(0.5)
