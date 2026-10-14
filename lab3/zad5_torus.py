#!/usr/bin/env python3
# Task 5 (grade 5.0): additional model - a spinning torus built from triangle strips (GL_TRIANGLE_STRIP).
# Usage: uv run lab3/zad5_torus.py [N]   (N = samples per parameter, default 30)

import sys  # sys.exit() on fatal errors and sys.argv for the command-line N parameter.
import random  # Random numbers for vertex colors.
from math import cos, sin, pi  # Trigonometry for the parametric equations; pi for the angle range.

from glfw.GLFW import *  # GLFW: creates the window + OpenGL context and handles input events (C-style names).

from OpenGL.GL import *  # Core OpenGL functions (gl*) and constants (GL_*).
from OpenGL.GLU import *  # OpenGL Utility Library (glu*); not used yet, kept to match the course template.

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30  # Samples of u and v from the 1st CLI argument; N x N vertices.

MAJOR_RADIUS = 4.0  # Distance from the torus center to the center of its tube.
MINOR_RADIUS = 2.0  # Radius of the tube; 4 + 2 = 6 fits the [-7.5, 7.5] view even when rotated.

vertices = None  # N x N x 3 table of egg vertices; filled once in startup().
colors = None  # N x N x 3 table of RGB colors, one per vertex; filled once in startup().


def compute_torus(n):  # Samples the parametric torus surface on an n x n grid of (u, v) values.
    tab = [[[0.0] * 3 for _ in range(n)] for _ in range(n)]  # n x n x 3 table; comprehension avoids shared sub-lists.
    for i in range(n):  # Row index i <-> parameter u (angle around the big circle).
        u = i / (n - 1)  # u from exactly 0.0 to exactly 1.0, so the torus closes.
        for j in range(n):  # Column index j <-> parameter v (angle around the tube).
            v = j / (n - 1)  # v from exactly 0.0 to exactly 1.0, so the tube closes.
            ring = MAJOR_RADIUS + MINOR_RADIUS * cos(2 * pi * v)  # Distance from the Y axis of a point on the tube's cross-section.
            tab[i][j][0] = ring * cos(2 * pi * u)  # x: that distance rotated by a full turn (2 * pi * u) around the Y axis...
            tab[i][j][1] = MINOR_RADIUS * sin(2 * pi * v)  # y: height of the point on the tube's cross-section.
            tab[i][j][2] = ring * sin(2 * pi * u)  # z: ...the other component of the same rotation.
    return tab  # Table ready to be fed into glVertex3f().


def startup(window):  # Runs once, after the OpenGL context is ready, before the main loop.
    global vertices, colors  # We assign the module-level variables, not local ones.
    width, height = glfwGetFramebufferSize(window)  # Size in PIXELS (on Retina it is 2x the window size in points).
    update_viewport(window, width, height)  # Set up the viewport and projection for the initial size.
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background.
    glEnable(GL_DEPTH_TEST)  # Depth buffer: closer fragments hide farther ones regardless of drawing order.
    vertices = compute_torus(N)  # Compute the model once; render() only reads it.
    colors = random_colors(N)  # Generated once, so the colors do not flicker (not re-randomized every frame).


def shutdown():  # Runs once after the main loop ends; place to free OpenGL resources.
    pass  # Nothing to free in this program.


def axes():  # Draws a simple coordinate system: X red, Y green, Z blue.
    glBegin(GL_LINES)  # Every 2 consecutive vertices form one separate line segment.

    glColor3f(1.0, 0.0, 0.0)  # Red for the X axis.
    glVertex3f(-5.0, 0.0, 0.0)  # X axis start.
    glVertex3f(5.0, 0.0, 0.0)  # X axis end.

    glColor3f(0.0, 1.0, 0.0)  # Green for the Y axis.
    glVertex3f(0.0, -5.0, 0.0)  # Y axis start.
    glVertex3f(0.0, 5.0, 0.0)  # Y axis end.

    glColor3f(0.0, 0.0, 1.0)  # Blue for the Z axis (points at the viewer, so it is barely visible).
    glVertex3f(0.0, 0.0, -5.0)  # Z axis start.
    glVertex3f(0.0, 0.0, 5.0)  # Z axis end.

    glEnd()  # Finish the line segments.


def random_colors(n):  # Random color per vertex, but coinciding vertices get the same color.
    tab = [[[random.random() for _ in range(3)] for _ in range(n)] for _ in range(n)]  # n x n table of random RGB colors, each component in [0, 1).
    # Both parameters wrap around, so the last row/column must reuse the first one's colors.
    for i in range(n):  # For every row u...
        tab[i][n - 1] = tab[i][0]  # ...v = 1 is the same point as v = 0 (tube closes), so copy the color.
    for j in range(n):  # For every column v...
        tab[n - 1][j] = tab[0][j]  # ...u = 1 is the same point as u = 0 (ring closes), so copy the color.
    return tab  # Colors ready; both seams now look continuous.


def draw_vertex(i, j):  # Emits vertex (i, j) of the grid together with its own color.
    glColor3f(*colors[i][j])  # Set the color first: glVertex takes the color that is current at that moment.
    glVertex3f(*vertices[i][j])  # Then the position [x, y, z] of the same grid element.


def draw_torus_strips():  # Draws the torus with one triangle strip per layer (pair of neighbouring rows).
    for i in range(N - 1):  # N - 1 layers: between row i and row i + 1.
        glBegin(GL_TRIANGLE_STRIP)  # Every new vertex forms a triangle with the 2 previous ones.
        for j in range(N):  # Walk around the whole tube, including the last column, to close it.
            draw_vertex(i, j)  # Even strip index: vertex from row i...
            draw_vertex(i + 1, j)  # ...odd strip index: vertex from row i + 1 (zig-zag).
        glEnd()  # Finish this layer's strip.


def spin(angle):  # Rotates everything drawn afterwards by "angle" degrees around X, then Y, then Z.
    glRotatef(angle, 1.0, 0.0, 0.0)  # Rotate by angle (degrees) around the X axis (vector [1, 0, 0]).
    glRotatef(angle, 0.0, 1.0, 0.0)  # Rotate by angle (degrees) around the Y axis (vector [0, 1, 0]).
    glRotatef(angle, 0.0, 0.0, 1.0)  # Rotate by angle (degrees) around the Z axis (vector [0, 0, 1]).


def render(time):  # Draws one frame; "time" = seconds since glfwInit(), drives the rotation.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear both colors and depths left from the previous frame.
    glLoadIdentity()  # Reset the MODELVIEW matrix so transformations do not accumulate between frames.

    axes()  # Axes are drawn before spin(), so they stay still while the model rotates.
    spin(time * 180 / pi)  # Treat time as radians and convert to degrees: one full turn every 2*pi seconds.
    draw_torus_strips()  # Draw the (rotated) colored torus.

    glFlush()  # Push all queued OpenGL commands to the GPU to be executed.


def update_viewport(window, width, height):  # Called on start and whenever the framebuffer is resized.
    if height == 0:  # A minimized window can report height 0...
        height = 1  # ...which would cause division by zero below, so clamp it.
    if width == 0:  # Same protection for the width...
        width = 1  # ...so the aspect ratio is always a valid positive number.
    aspect_ratio = width / height  # Width-to-height ratio, used to keep shapes from being stretched.

    glMatrixMode(GL_PROJECTION)  # Following matrix calls modify the PROJECTION matrix (world -> screen mapping).
    glViewport(0, 0, width, height)  # Map OpenGL output onto the whole framebuffer: x, y of lower-left corner, w, h.
    glLoadIdentity()  # Reset the MODELVIEW matrix so transformations do not accumulate between frames.

    if width <= height:  # Window is tall (or square): X keeps the [-7.5, 7.5] range...
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)  # ...and Y is extended; Z also [-7.5, 7.5].
    else:  # Window is wide: Y keeps the [-7.5, 7.5] range...
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)  # ...and X is extended instead.

    glMatrixMode(GL_MODELVIEW)  # Switch back to the MODELVIEW matrix (object transformations).
    glLoadIdentity()  # Reset the MODELVIEW matrix so transformations do not accumulate between frames.


def main():  # Program entry point: window setup, main loop, cleanup.
    if not glfwInit():  # Initialize the GLFW library; returns False on failure...
        sys.exit(-1)  # ...in which case there is nothing we can do.

    window = glfwCreateWindow(400, 400, __file__, None, None)  # 400x400 window titled with the script path.
    if not window:  # Window (or OpenGL context) creation failed...
        glfwTerminate()  # ...release what GLFW allocated...
        sys.exit(-1)  # ...in which case there is nothing we can do.

    glfwMakeContextCurrent(window)  # Make this window's OpenGL context the target of all gl* calls.
    glfwSetFramebufferSizeCallback(window, update_viewport)  # Recompute the projection on every resize.
    glfwSwapInterval(1)  # V-sync: swap buffers at most once per monitor refresh.

    startup(window)  # One-time initialization.
    while not glfwWindowShouldClose(window):  # Loop until the user closes the window.
        render(glfwGetTime())  # Draw the frame into the back buffer.
        glfwSwapBuffers(window)  # Show the back buffer on screen (double buffering).
        glfwPollEvents()  # Process pending events without waiting, so the loop keeps rendering frames.
    shutdown()  # One-time cleanup.

    glfwTerminate()  # ...release what GLFW allocated...


if __name__ == '__main__':  # Run main() only when executed directly, not when imported.
    main()  # Start the program.
