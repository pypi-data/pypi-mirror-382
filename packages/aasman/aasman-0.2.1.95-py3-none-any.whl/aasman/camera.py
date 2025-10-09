from manim import *

#Làm cho camera auto đi theo target
def make_camera_updater(target):
    def updater(mob):
        mob.move_to(target)
    return updater

