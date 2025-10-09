from manim import *

# Bay lên
def up_UpdateFormAlphaFunc(distance=1):
    def updater(mob, alpha):
        mob.set_y(ORIGIN[1] + alpha * distance)
        mob.set_opacity(1 - alpha)
    return updater

# Bay xuống
def down_UpdateFormAlphaFunc(distance=1):
    def updater(mob, alpha):
        mob.set_y(ORIGIN[1] - alpha * distance)
        mob.set_opacity(1 - alpha)
    return updater

# Bay sang phải
def right_UpdateFormAlphaFunc(distance=1):
    def updater(mob, alpha):
        mob.set_x(ORIGIN[0] + alpha * distance)
        mob.set_opacity(1 - alpha)
    return updater

# Bay sang trái
def left_UpdateFormAlphaFunc(distance=1):
    def updater(mob, alpha):
        mob.set_x(ORIGIN[0] - alpha * distance)
        mob.set_opacity(1 - alpha)
    return updater