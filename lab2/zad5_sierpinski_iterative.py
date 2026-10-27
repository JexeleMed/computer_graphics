#!/usr/bin/env python3
# Usage: uv run lab2/zad5_sierpinski_iterative.py [level]

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


def is_filled(i, j):
    while i > 0 or j > 0:
        if i % 3 == 1 and j % 3 == 1:  # Middle column AND middle row at this level -> hole.
            return False
        i //= 3
        j //= 3
    return True


def draw_carpet(x, y, a, b, level):
    cells = 3 ** level
    cell_a = a / cells
    cell_b = b / cells
    left = x - a / 2.0
    bottom = y - b / 2.0

    for i in range(cells):
        for j in range(cells):
            if is_filled(i, j):
                draw_rectangle(left + (i + 0.5) * cell_a,
                               bottom + (j + 0.5) * cell_b,
                               cell_a, cell_b)


def render(time):
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0.0, 0.35, 0.6)
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
