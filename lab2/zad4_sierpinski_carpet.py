#!/usr/bin/env python3
# Task 4 (grade 4.5): rectangular Sierpinski carpet, drawn recursively.
# Usage: uv run lab2/zad4_sierpinski_carpet.py [level]   (level = degree of self-similarity, default 4)

import sys

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

LEVEL = int(sys.argv[1]) if len(sys.argv) > 1 else 4

CARPET_WIDTH = 180.0
CARPET_HEIGHT = 120.0


def startup(window):
    width, height = glfwGetFramebufferSize(window)
    update_viewport(window, width, height)
    glClearColor(1.0, 1.0, 1.0, 1.0)


def shutdown():
    pass


def draw_rectangle(x, y, a, b):
    half_a = a / 2.0
    half_b = b / 2.0

    glBegin(GL_TRIANGLES)
    glVertex2f(x - half_a, y - half_b)
    glVertex2f(x + half_a, y - half_b)
    glVertex2f(x - half_a, y + half_b)
    glVertex2f(x + half_a, y - half_b)
    glVertex2f(x + half_a, y + half_b)
    glVertex2f(x - half_a, y + half_b)
    glEnd()


def draw_carpet(x, y, a, b, level):
    if level <= 0:
        draw_rectangle(x, y, a, b)
        return

    third_a = a / 3.0
    third_b = b / 3.0

    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            if i == 0 and j == 0:
                continue  # Central cell is the hole: skip it.
            draw_carpet(x + i * third_a,
                        y + j * third_b,
                        third_a, third_b,
                        level - 1)


def render(time):
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0.6, 0.2, 0.0)
    draw_carpet(0.0, 0.0, CARPET_WIDTH, CARPET_HEIGHT, LEVEL)

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

    window = glfwCreateWindow(600, 400, __file__, None, None)
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
