from manim import *
import numpy as np

def bounce_text(
    scene: Scene,
    text_str: str = "HELLO MANIM!",
    font: str = "Consolas",
    color: str = YELLOW,
    start_y: float = 3,
    end_y: float = -3,
    fall_time: float = 1.0,
    bounce_strength: float = 2.5,
    rotation_strength: float = 0.4,
    scale_strength: float = 0.1,
    decay: float = 0.5,
    run_time: float = 6.0,
    freq: float = 5.0,
    final_hold: float = 0.5,
):
    """
    Hiệu ứng text rớt từ trên cao xuống, nảy và lắc vật lý.
    --------------------------------------------
    scene: Scene hoặc subclass của Scene
    text_str: nội dung Text
    font: font chữ
    color: màu chữ
    start_y, end_y: vị trí rơi từ trên xuống dưới
    fall_time: thời gian rơi tự do trước khi chạm đất
    bounce_strength: độ cao nảy lên
    rotation_strength: biên độ xoay khi nảy
    scale_strength: độ rung co giãn khi nảy
    decay: tốc độ giảm biên độ nảy (giá trị lớn thì dừng nhanh hơn)
    run_time: tổng thời gian animation
    freq: tần số dao động (nảy nhanh/chậm)
    final_hold: thời gian giữ lại cuối cùng
    """

    text = Text(text_str, font=font, color=color).scale(1.3)
    text.move_to([0, start_y, 0])
    t = ValueTracker(0)

    def fall_y():
        return start_y - (start_y - end_y) * (t.get_value() / fall_time) ** 2

    def bounce_y():
        time = t.get_value() - fall_time
        return end_y + np.exp(-decay * time) * np.abs(np.cos(freq * time)) * bounce_strength

    def rotation_angle():
        time = t.get_value() - fall_time
        return np.exp(-decay * time) * np.sin(freq * 1.2 * time) * rotation_strength

    def bounce_scale():
        time = t.get_value() - fall_time
        return 1 + np.exp(-decay * 1.2 * time) * np.cos(freq * 1.5 * time) * scale_strength

    def get_text():
        if t.get_value() < fall_time:
            return text.copy().move_to([0, fall_y(), 0])
        else:
            return (
                text.copy()
                .move_to([0, bounce_y(), 0])
                .rotate(rotation_angle())
                .scale(bounce_scale())
            )

    moving_text = always_redraw(get_text)

    scene.add(moving_text)
    scene.play(t.animate.set_value(fall_time + 5 * np.pi), run_time=run_time, rate_func=linear)

    final_text = Text(text_str, font=font, color=color).scale(1.3)
    final_text.move_to([0, end_y, 0])
    scene.play(Transform(moving_text, final_text), run_time=0.8, rate_func=smooth)
    scene.wait(final_hold)