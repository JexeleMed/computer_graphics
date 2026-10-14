#!/usr/bin/env python3
# Task 5 (grade 5.0), homework 3.3: chain made of tori, shaped along a closed wavy curve.
# Neighbouring links are rotated by 90 degrees around the curve's tangent, so they interlock.
# Usage: uv run lab3/zad5_torus_chain.py

import sys  # sys.exit() on fatal errors.
import colorsys  # hsv_to_rgb(): an easy way to get a rainbow of colors along the chain.
from math import cos, sin, sqrt, pi  # Trigonometry for the curve and the torus; sqrt for vector lengths.

from glfw.GLFW import *  # GLFW: creates the window + OpenGL context and handles input events (C-style names).

from OpenGL.GL import *  # Core OpenGL functions (gl*) and constants (GL_*).
from OpenGL.GLU import *  # OpenGL Utility Library (glu*); not used yet, kept to match the course template.

MAJOR_RADIUS = 0.6  # R: distance from a link's center to the center of its tube.
MINOR_RADIUS = 0.13  # r: radius of the tube (thickness of the wire).
U_SAMPLES = 16  # Samples of u = angle around the big circle of one link.
V_SAMPLES = 10  # Samples of v = angle around the tube.
LIGHT = (0.4, 0.8, 0.45)  # Direction towards a fake light source, used only to shade vertex colors.

chain_list = None  # ID of the OpenGL display list holding the whole chain; created in startup().


def curve(t):  # Closed curve the chain follows, t in [0, 2*pi].
    return 5.0 * cos(t), 1.0 * sin(3 * t), 5.0 * sin(t)  # Circle of radius 5 in XZ that waves up and down 3 times.


def normalize(vector):  # Returns the vector scaled to length 1.
    length = sqrt(sum(c * c for c in vector))  # Euclidean length sqrt(x^2 + y^2 + z^2).
    return tuple(c / length for c in vector)  # Divide every component by the length.


def cross(a, b):  # Cross product a x b: a vector perpendicular to both a and b.
    return a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]  # Standard formula.


def link_frames():  # Computes the position and orientation of every link along the curve.
    samples = 2000  # The curve is approximated by 2000 short segments to measure its length.
    params = [2 * pi * k / samples for k in range(samples + 1)]  # Values of t from exactly 0 to exactly 2*pi.
    points = [curve(t) for t in params]  # Points on the curve for those t values.
    lengths = [0.0]  # lengths[k] = arc length from the start of the curve to points[k].
    for p, q in zip(points, points[1:]):  # Every pair of consecutive points = one short segment...
        lengths.append(lengths[-1] + sqrt(sum((a - b) ** 2 for a, b in zip(p, q))))  # ...adds its length to the total.

    # Interlocked rings need center spacing below 2 * (R - r); an even count closes the alternating chain.
    count = round(lengths[-1] / (2 * (MAJOR_RADIUS - MINOR_RADIUS) - 0.1))  # Number of links: total length / spacing.
    count += count % 2  # Make it even, so the last link (odd) and the first one (even) are perpendicular.
    spacing = lengths[-1] / count  # Exact spacing that divides the closed curve evenly -> the chain closes.

    frames = []  # One (center, first in-plane axis, second in-plane axis, torus axis) tuple per link.
    k = 0  # Index of the current curve sample; only moves forward, as links are visited in order.
    for link in range(count):  # For every link...
        while lengths[k + 1] < link * spacing:  # ...walk along the curve until its arc length is reached...
            k += 1  # ...one sample at a time.
        t = params[k]  # Curve parameter of this link's center.
        center = curve(t)  # Center of the link lies on the curve.
        tangent = normalize(tuple(b - a for a, b in zip(curve(t - 1e-4), curve(t + 1e-4))))  # Direction of the curve.
        up = (0.0, 1.0, 0.0)  # Reference "up" vector used to build a frame around the tangent.
        dot = sum(a * b for a, b in zip(up, tangent))  # Part of "up" that points along the tangent...
        normal = normalize(tuple(a - dot * b for a, b in zip(up, tangent)))  # ...is removed -> normal is perpendicular to it.
        binormal = cross(tangent, normal)  # Third axis, perpendicular to both tangent and normal.
        if link % 2 == 0:  # Even links...
            frames.append((center, tangent, normal, binormal))  # ...lie in the (tangent, normal) plane: "standing" rings.
        else:  # Odd links...
            frames.append((center, tangent, binormal, normal))  # ...lie in the (tangent, binormal) plane: "lying" rings.
    return frames  # Ready to be turned into torus geometry.


def torus_link(center, first, second, axis, color):  # Vertices and colors of one torus with the given frame.
    vertices = [[None] * V_SAMPLES for _ in range(U_SAMPLES)]  # U_SAMPLES x V_SAMPLES table of [x, y, z] points.
    colors = [[None] * V_SAMPLES for _ in range(U_SAMPLES)]  # Same-sized table of RGB colors.
    for i in range(U_SAMPLES):  # Row index i <-> parameter u.
        u = i / (U_SAMPLES - 1)  # u from exactly 0.0 to exactly 1.0, so the ring closes.
        radial = tuple(cos(2 * pi * u) * a + sin(2 * pi * u) * b for a, b in zip(first, second))  # Unit vector from the link center towards the tube, in the link's plane.
        for j in range(V_SAMPLES):  # Column index j <-> parameter v.
            v = j / (V_SAMPLES - 1)  # v from exactly 0.0 to exactly 1.0, so the tube closes.
            ring = MAJOR_RADIUS + MINOR_RADIUS * cos(2 * pi * v)  # Distance from the link center (R + r cos 2*pi*v), as in the torus equation.
            vertices[i][j] = tuple(c + ring * r + MINOR_RADIUS * sin(2 * pi * v) * a  # center + that distance along "radial" + r sin 2*pi*v along the axis...
                                   for c, r, a in zip(center, radial, axis))  # ...computed for x, y and z at once.
            normal = tuple(cos(2 * pi * v) * r + sin(2 * pi * v) * a for r, a in zip(radial, axis))  # Direction the surface faces at this point.
            # Simple fake lighting baked into vertex colors, so the round shape is visible.
            shade = 0.3 + 0.7 * max(0.0, sum(n * l for n, l in zip(normal, normalize(LIGHT))))  # Brighter where the surface faces the light; 0.3 minimum.
            colors[i][j] = tuple(c * shade for c in color)  # Link's base color darkened by the shade.
    return vertices, colors  # Geometry of one link.


def draw_link(vertices, colors):  # Draws one link with one triangle strip per layer, like the egg in task 4.
    for i in range(U_SAMPLES - 1):  # U_SAMPLES - 1 layers: between row i and row i + 1.
        glBegin(GL_TRIANGLE_STRIP)  # Every new vertex forms a triangle with the 2 previous ones.
        for j in range(V_SAMPLES):  # Walk around the whole tube, including the last column, to close it.
            glColor3f(*colors[i][j])  # Color of vertex (i, j)...
            glVertex3f(*vertices[i][j])  # ...and its position: even strip index, row i.
            glColor3f(*colors[i + 1][j])  # Color of vertex (i + 1, j)...
            glVertex3f(*vertices[i + 1][j])  # ...and its position: odd strip index, row i + 1 (zig-zag).
        glEnd()  # Finish this layer's strip.


def startup(window):  # Runs once, after the OpenGL context is ready, before the main loop.
    global chain_list  # We assign the module-level variable, not a local one.
    width, height = glfwGetFramebufferSize(window)  # Size in PIXELS (on Retina it is 2x the window size in points).
    update_viewport(window, width, height)  # Set up the viewport and projection for the initial size.
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background.
    glEnable(GL_DEPTH_TEST)  # Depth buffer: closer fragments hide farther ones, so interlocked links look right.

    frames = link_frames()  # Position and orientation of every link.
    # Display list: the geometry is sent once and replayed every frame (much faster in Python).
    chain_list = glGenLists(1)  # Reserve one display list ID.
    glNewList(chain_list, GL_COMPILE)  # Start recording: following gl* drawing calls are stored, not executed.
    for link, (center, first, second, axis) in enumerate(frames):  # For every link and its frame...
        color = colorsys.hsv_to_rgb(link / len(frames), 0.6, 1.0)  # ...pick a hue that goes around the color wheel along the chain...
        draw_link(*torus_link(center, first, second, axis, color))  # ...build its torus and record its drawing.
    glEndList()  # Stop recording.


def shutdown():  # Runs once after the main loop ends; place to free OpenGL resources.
    glDeleteLists(chain_list, 1)  # Free the display list created in startup().


def render(time):  # Draws one frame; "time" = seconds since glfwInit(), drives the rotation.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear both colors and depths left from the previous frame.
    glLoadIdentity()  # Reset the MODELVIEW matrix so transformations do not accumulate between frames.

    glRotatef(35.0, 1.0, 0.0, 0.0)  # Tilt the scene by 35 degrees around X, so the chain is seen from an angle.
    glRotatef(time * 20.0, 0.0, 1.0, 0.0)  # Slowly turn it around Y: 20 degrees per second.
    glCallList(chain_list)  # Replay the recorded chain.

    glFlush()  # Push all queued OpenGL commands to the GPU to be executed.


def update_viewport(window, width, height):  # Called on start and whenever the framebuffer is resized.
    if height == 0:  # A minimized window can report height 0...
        height = 1  # ...which would cause division by zero below, so clamp it.
    if width == 0:  # Same protection for the width...
        width = 1  # ...so the aspect ratio is always a valid positive number.
    aspect_ratio = width / height  # Width-to-height ratio, used to keep shapes from being stretched.

    glMatrixMode(GL_PROJECTION)  # Following matrix calls modify the PROJECTION matrix (world -> screen mapping).
    glViewport(0, 0, width, height)  # Map OpenGL output onto the whole framebuffer: x, y of lower-left corner, w, h.
    glLoadIdentity()  # Reset the projection matrix to identity (drop any previous projection).

    if width <= height:  # Window is tall (or square): X keeps the [-7.5, 7.5] range...
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)  # ...and Y is extended; Z also [-7.5, 7.5].
    else:  # Window is wide: Y keeps the [-7.5, 7.5] range...
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)  # ...and X is extended instead.

    glMatrixMode(GL_MODELVIEW)  # Switch back to the MODELVIEW matrix (object transformations).
    glLoadIdentity()  # Start with no object transformation.


def main():  # Program entry point: window setup, main loop, cleanup.
    if not glfwInit():  # Initialize the GLFW library; returns False on failure...
        sys.exit(-1)  # ...in which case there is nothing we can do.

    window = glfwCreateWindow(400, 400, __file__, None, None)  # 400x400 window titled with the script path.
    if not window:  # Window (or OpenGL context) creation failed...
        glfwTerminate()  # ...release what GLFW allocated...
        sys.exit(-1)  # ...and quit with an error code.

    glfwMakeContextCurrent(window)  # Make this window's OpenGL context the target of all gl* calls.
    glfwSetFramebufferSizeCallback(window, update_viewport)  # Recompute the projection on every resize.
    glfwSwapInterval(1)  # V-sync: swap buffers at most once per monitor refresh.

    startup(window)  # One-time initialization.
    while not glfwWindowShouldClose(window):  # Loop until the user closes the window.
        render(glfwGetTime())  # Draw the frame into the back buffer.
        glfwSwapBuffers(window)  # Show the back buffer on screen (double buffering).
        glfwPollEvents()  # Process pending events without waiting, so the loop keeps rendering frames.
    shutdown()  # One-time cleanup.

    glfwTerminate()  # Destroy the window and release GLFW resources.


if __name__ == '__main__':  # Run main() only when executed directly, not when imported.
    main()  # Start the program.
