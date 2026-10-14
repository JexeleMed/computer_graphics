#!/usr/bin/env python3
# Task 4 (grade 4.5): spinning egg model built from triangle strips (GL_TRIANGLE_STRIP), one strip per layer.
# Usage: uv run lab3/zad4_egg_triangle_strip.py [N]   (N = samples per parameter, default 20)

import sys
import random
from math import cos, sin, pi

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20

vertices = None
colors = None


def compute_egg(n):
    tab = [[[0.0] * 3 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        u = i / (n - 1)  # Last value must be exactly 1.0, hence n - 1.
        radius = -90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u
        y = 160 * u ** 4 - 320 * u ** 3 + 160 * u ** 2 - 5
        for j in range(n):
            v = j / (n - 1)
            tab[i][j][0] = radius * cos(pi * v)
            tab[i][j][1] = y
            tab[i][j][2] = radius * sin(pi * v)
    return tab


def startup(window):
    global vertices, colors
    width, height = glfwGetFramebufferSize(window)
    update_viewport(window, width, height)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    vertices = compute_egg(N)
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
    # Vertices that coincide in 3D must share a color, otherwise seams are visible.
    for i in range(n):
        tab[i][n - 1] = tab[n - 1 - i][0]  # Edge v = 1 overlaps edge v = 0 mirrored in u.
    for j in range(n):
        tab[0][j] = tab[0][0]  # Bottom pole (u = 0 and u = 1).
        tab[n - 1][j] = tab[0][0]
    if n % 2 == 1:
        for j in range(n):
            tab[n // 2][j] = tab[n // 2][0]  # Top pole (u = 0.5).
    return tab


def draw_vertex(i, j):
    glColor3f(*colors[i][j])
    glVertex3f(*vertices[i][j])


def draw_egg_strips():
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
    draw_egg_strips()

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
