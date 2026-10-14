#!/usr/bin/env python3
# Task 1 (grade 3.0): egg model built from points (GL_POINTS).
# Usage: uv run lab3/zad1_egg_points.py [N]   (N = samples per parameter, default 20)

import sys  # sys.exit() on fatal errors and sys.argv for the command-line N parameter.
from math import cos, sin, pi  # Trigonometry for the parametric equations; pi for the angle range.

from glfw.GLFW import *  # GLFW: creates the window + OpenGL context and handles input events (C-style names).

from OpenGL.GL import *  # Core OpenGL functions (gl*) and constants (GL_*).
from OpenGL.GLU import *  # OpenGL Utility Library (glu*); not used yet, kept to match the course template.

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20  # Samples of u and v from the 1st CLI argument; N x N vertices.

vertices = None  # N x N x 3 table of egg vertices; filled once in startup().


def compute_egg(n):  # Samples the parametric egg surface on an n x n grid of (u, v) values.
    tab = [[[0.0] * 3 for _ in range(n)] for _ in range(n)]  # n x n x 3 table; comprehension avoids shared sub-lists.
    for i in range(n):  # Row index i <-> parameter u.
        u = i / (n - 1)  # Last value must be exactly 1.0, hence n - 1.
        radius = -90 * u ** 5 + 225 * u ** 4 - 270 * u ** 3 + 180 * u ** 2 - 45 * u  # Common factor of x and z.
        y = 160 * u ** 4 - 320 * u ** 3 + 160 * u ** 2 - 5  # Height: -5 at u = 0 and 1 (bottom), 5 at u = 0.5 (top).
        for j in range(n):  # Column index j <-> parameter v.
            v = j / (n - 1)  # v also goes from exactly 0.0 to exactly 1.0.
            tab[i][j][0] = radius * cos(pi * v)  # x: radius rotated by angle pi * v around the Y axis...
            tab[i][j][1] = y  # y: does not depend on v -> every row is a horizontal ring.
            tab[i][j][2] = radius * sin(pi * v)  # z: ...the other component of the same rotation.
    return tab  # Table ready to be fed into glVertex3f().


def startup(window):  # Runs once, after the OpenGL context is ready, before the main loop.
    global vertices  # We assign the module-level variable, not a local one.
    width, height = glfwGetFramebufferSize(window)  # Size in PIXELS (on Retina it is 2x the window size in points).
    update_viewport(window, width, height)  # Set up the viewport and projection for the initial size.
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background, so the yellow points are easy to see.
    glEnable(GL_DEPTH_TEST)  # Depth buffer: closer fragments hide farther ones regardless of drawing order.
    vertices = compute_egg(N)  # Compute the model once; render() only reads it.


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


def draw_egg_points():  # Draws every vertex of the egg as a single point.
    glColor3f(1.0, 1.0, 0.0)  # Yellow; the current color is used by all following vertices.
    glBegin(GL_POINTS)  # Every vertex is drawn as one separate point.
    for row in vertices:  # Each row = one value of u = one horizontal ring of the egg.
        for vertex in row:  # Each vertex in the ring = one value of v.
            glVertex3f(*vertex)  # Unpack [x, y, z] into the three arguments of glVertex3f.
    glEnd()  # Finish the points.


def render(time):  # Draws one frame; "time" = seconds since glfwInit() (unused here).
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear both colors and depths left from the previous frame.
    glLoadIdentity()  # Reset the MODELVIEW matrix so transformations do not accumulate between frames.

    axes()  # Coordinate system first...
    draw_egg_points()  # ...then the egg.

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
