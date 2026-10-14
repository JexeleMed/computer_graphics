#!/usr/bin/env python3
# Task 5 (grade 5.0): additional model - a spinning torus built from triangle strips (GL_TRIANGLE_STRIP).
# Usage: uv run lab3/zad5_torus.py [N]   (N = samples per parameter, default 30)

import sys
import random
from math import cos, sin, pi

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30

MAJOR_RADIUS = 4.0
MINOR_RADIUS = 2.0

vertices = None
colors = None


def compute_torus(n):
    tab = [[[0.0] * 3 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        u = i / (n - 1)
        for j in range(n):
            v = j / (n - 1)
            ring = MAJOR_RADIUS + MINOR_RADIUS * cos(2 * pi * v)
            tab[i][j][0] = ring * cos(2 * pi * u)
            tab[i][j][1] = MINOR_RADIUS * sin(2 * pi * v)
            tab[i][j][2] = ring * sin(2 * pi * u)
    return tab


def startup(window):
    global vertices, colors
    width, height = glfwGetFramebufferSize(window)
    update_viewport(window, width, height)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    vertices = compute_torus(N)
    colors = random_colors(N)


def shutdown():
    pass


def axes():
    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()


def random_colors(n):
    tab = [[[random.random() for _ in range(3)] for _ in range(n)] for _ in range(n)]
    # Both parameters wrap around, so the last row/column must reuse the first one's colors.
    for i in range(n):
        tab[i][n - 1] = tab[i][0]
    for j in range(n):
        tab[n - 1][j] = tab[0][j]
    return tab


def draw_vertex(i, j):
    glColor3f(*colors[i][j])
    glVertex3f(*vertices[i][j])


def draw_torus_strips():
    for i in range(N - 1):
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(N):
            draw_vertex(i, j)
            draw_vertex(i + 1, j)
        glEnd()


def spin(angle):
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)


def render(time):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    axes()
    spin(time * 180 / pi)
    draw_torus_strips()

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
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)
    else:
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)

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
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
