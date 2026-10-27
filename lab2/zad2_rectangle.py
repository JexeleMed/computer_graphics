#!/usr/bin/env python3
# Task 2 (grade 3.5): a function drawing a rectangle at a given place, built from exactly two triangles.

import sys

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *


def startup(window):
    width, height = glfwGetFramebufferSize(window)
    update_viewport(window, width, height)
    glClearColor(0.5, 0.5, 0.5, 1.0)


def shutdown():
    pass


def draw_rectangle(x, y, a, b):
    half_a = a / 2.0
    half_b = b / 2.0

    left = x - half_a
    right = x + half_a
    bottom = y - half_b
    top = y + half_b

    glBegin(GL_TRIANGLES)
    glVertex2f(left, bottom)
    glVertex2f(right, bottom)
    glVertex2f(left, top)

    glVertex2f(right, bottom)
    glVertex2f(right, top)
    glVertex2f(left, top)
    glEnd()


def render(time):
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0.8, 0.2, 0.2)
    draw_rectangle(-40.0, 30.0, 80.0, 50.0)

    glColor3f(0.2, 0.3, 0.9)
    draw_rectangle(45.0, -35.0, 40.0, 90.0)

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
