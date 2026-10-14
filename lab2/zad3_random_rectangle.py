#!/usr/bin/env python3
# Task 3 (grade 4.0): rectangle with random vertex colors and a random deformation controlled by parameter d.

import sys
import random

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *


def startup(window):
    width, height = glfwGetFramebufferSize(window)
    update_viewport(window, width, height)
    glClearColor(0.5, 0.5, 0.5, 1.0)


def shutdown():
    pass


def random_color():
    return (random.random(), random.random(), random.random())


def draw_rectangle(x, y, a, b, d=0.0):  # Center (x, y), width a, height b; d = deformation degree (0.0 = perfect rectangle).
    half_a = a / 2.0
    half_b = b / 2.0

    corners = [
        [x - half_a, y - half_b],
        [x + half_a, y - half_b],
        [x + half_a, y + half_b],
        [x - half_a, y + half_b],
    ]

    for corner in corners:
        corner[0] += random.uniform(-d, d) * a
        corner[1] += random.uniform(-d, d) * b

    colors = [random_color() for _ in corners]

    glBegin(GL_TRIANGLES)
    for index in (0, 1, 3, 1, 2, 3):
        glColor3f(*colors[index])
        glVertex2f(*corners[index])
    glEnd()


def render(time):
    glClear(GL_COLOR_BUFFER_BIT)

    random.seed(2137)  # Same seed every frame -> same "random" numbers -> picture doesn't flicker on redraw/resize.

    draw_rectangle(-45.0, 45.0, 70.0, 50.0)
    draw_rectangle(45.0, 45.0, 70.0, 50.0, 0.1)
    draw_rectangle(-45.0, -45.0, 70.0, 50.0, 0.2)
    draw_rectangle(45.0, -45.0, 70.0, 50.0, 0.35)

    glFlush()


def update_viewport(window, width, height):
    if height == 0:
        height = 1
    if width == 0:
        width = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-100.0, 100.0, -100.0 / aspect_ratio, 100.0 / aspect_ratio,
                1.0, -1.0)
    else:
        glOrtho(-100.0 * aspect_ratio, 100.0 * aspect_ratio, -100.0, 100.0,
                1.0, -1.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    startup(window)
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwWaitEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
