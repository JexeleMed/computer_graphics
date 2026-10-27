#!/usr/bin/env python3

import sys
import colorsys
from math import cos, sin, sqrt, pi

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

MAJOR_RADIUS = 0.6
MINOR_RADIUS = 0.13
U_SAMPLES = 16
V_SAMPLES = 10
LIGHT = (0.4, 0.8, 0.45)

chain_list = None


def curve(t):
    return 5.0 * cos(t), 1.0 * sin(3 * t), 5.0 * sin(t)


def normalize(vector):
    length = sqrt(sum(c * c for c in vector))
    return tuple(c / length for c in vector)


def cross(a, b):
    return a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]


def link_frames():
    samples = 2000
    params = [2 * pi * k / samples for k in range(samples + 1)]
    points = [curve(t) for t in params]
    lengths = [0.0]
    for p, q in zip(points, points[1:]):
        lengths.append(lengths[-1] + sqrt(sum((a - b) ** 2 for a, b in zip(p, q))))

    count = round(lengths[-1] / (2 * (MAJOR_RADIUS - MINOR_RADIUS) - 0.1))
    count += count % 2
    spacing = lengths[-1] / count

    frames = []
    k = 0
    for link in range(count):
        while lengths[k + 1] < link * spacing:
            k += 1
        t = params[k]
        center = curve(t)
        tangent = normalize(tuple(b - a for a, b in zip(curve(t - 1e-4), curve(t + 1e-4))))
        up = (0.0, 1.0, 0.0)
        dot = sum(a * b for a, b in zip(up, tangent))
        normal = normalize(tuple(a - dot * b for a, b in zip(up, tangent)))
        binormal = cross(tangent, normal)
        if link % 2 == 0:
            frames.append((center, tangent, normal, binormal))
        else:
            frames.append((center, tangent, binormal, normal))
    return frames


def torus_link(center, first, second, axis, color):
    vertices = [[None] * V_SAMPLES for _ in range(U_SAMPLES)]
    colors = [[None] * V_SAMPLES for _ in range(U_SAMPLES)]
    for i in range(U_SAMPLES):
        u = i / (U_SAMPLES - 1)
        radial = tuple(cos(2 * pi * u) * a + sin(2 * pi * u) * b for a, b in zip(first, second))
        for j in range(V_SAMPLES):
            v = j / (V_SAMPLES - 1)
            ring = MAJOR_RADIUS + MINOR_RADIUS * cos(2 * pi * v)
            vertices[i][j] = tuple(c + ring * r + MINOR_RADIUS * sin(2 * pi * v) * a
                                   for c, r, a in zip(center, radial, axis))
            normal = tuple(cos(2 * pi * v) * r + sin(2 * pi * v) * a for r, a in zip(radial, axis))
            # Simple fake lighting baked into vertex colors, so the round shape is visible.
            shade = 0.3 + 0.7 * max(0.0, sum(n * l for n, l in zip(normal, normalize(LIGHT))))
            colors[i][j] = tuple(c * shade for c in color)
    return vertices, colors


def draw_link(vertices, colors):
    for i in range(U_SAMPLES - 1):
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(V_SAMPLES):
            glColor3f(*colors[i][j])
            glVertex3f(*vertices[i][j])
            glColor3f(*colors[i + 1][j])
            glVertex3f(*vertices[i + 1][j])
        glEnd()


def startup(window):
    global chain_list
    width, height = glfwGetFramebufferSize(window)
    update_viewport(window, width, height)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    frames = link_frames()
    chain_list = glGenLists(1)
    glNewList(chain_list, GL_COMPILE)
    for link, (center, first, second, axis) in enumerate(frames):
        color = colorsys.hsv_to_rgb(link / len(frames), 0.6, 1.0)
        draw_link(*torus_link(center, first, second, axis, color))
    glEndList()


def shutdown():
    glDeleteLists(chain_list, 1)


def render(time):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glRotatef(35.0, 1.0, 0.0, 0.0)
    glRotatef(time * 20.0, 0.0, 1.0, 0.0)
    glCallList(chain_list)

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
