#!/usr/bin/env python3
# Task 3 (grade 4.0): rectangle with random vertex colors and a random deformation controlled by parameter d.

import sys  # Standard module, used here only for sys.exit() on fatal errors.
import random  # Standard pseudo-random number generator.

from glfw.GLFW import *  # GLFW: creates the window + OpenGL context and handles input events (C-style names).

from OpenGL.GL import *  # Core OpenGL functions (gl*) and constants (GL_*).
from OpenGL.GLU import *  # OpenGL Utility Library (glu*); not used yet, kept to match the course template.


def startup(window):  # Runs once, after the OpenGL context is ready, before the main loop.
    width, height = glfwGetFramebufferSize(window)  # Size in PIXELS (on Retina it is 2x the window size in points).
    update_viewport(window, width, height)  # Set up the viewport and projection for the initial size.
    glClearColor(0.5, 0.5, 0.5, 1.0)  # Color used by glClear(): RGBA, each 0.0-1.0 -> mid gray, fully opaque.


def shutdown():  # Runs once after the main loop ends; place to free OpenGL resources.
    pass  # Nothing to free in this program.


def random_color():  # Returns a random RGB color as a tuple of 3 floats.
    return (random.random(), random.random(), random.random())  # random.random() is in [0.0, 1.0) - exactly the glColor3f range.


def draw_rectangle(x, y, a, b, d=0.0):  # Center (x, y), width a, height b; d = deformation degree (0.0 = perfect rectangle).
    half_a = a / 2.0  # Half of the width.
    half_b = b / 2.0  # Half of the height.

    corners = [  # The 4 corners of the undeformed rectangle, counter-clockwise from bottom-left.
        [x - half_a, y - half_b],  # 0: bottom-left.
        [x + half_a, y - half_b],  # 1: bottom-right.
        [x + half_a, y + half_b],  # 2: top-right.
        [x - half_a, y + half_b],  # 3: top-left.
    ]  # Lists (not tuples) so the coordinates can be modified below.

    for corner in corners:  # Deform: move every corner by a random offset.
        corner[0] += random.uniform(-d, d) * a  # Shift X by up to d * width in either direction.
        corner[1] += random.uniform(-d, d) * b  # Shift Y by up to d * height in either direction.

    colors = [random_color() for _ in corners]  # One random color per corner (shared corners keep the same color).

    glBegin(GL_TRIANGLES)  # 6 vertices -> 2 triangles.
    for index in (0, 1, 3, 1, 2, 3):  # Triangle (0,1,3) and triangle (1,2,3); they share the 1-3 diagonal.
        glColor3f(*colors[index])  # Set this corner's color; "*" unpacks the tuple into 3 arguments.
        glVertex2f(*corners[index])  # Emit the corner; "*" unpacks [x, y] into 2 arguments.
    glEnd()  # Finish; colors are interpolated across each triangle.


def render(time):  # Draws one frame; "time" = seconds since glfwInit() (unused here).
    glClear(GL_COLOR_BUFFER_BIT)  # Fill the whole color buffer with the clear color.

    random.seed(2137)  # Same seed every frame -> same "random" numbers -> picture doesn't flicker on redraw/resize.

    draw_rectangle(-45.0, 45.0, 70.0, 50.0)  # d defaults to 0.0: random colors, no deformation.
    draw_rectangle(45.0, 45.0, 70.0, 50.0, 0.1)  # Slight deformation.
    draw_rectangle(-45.0, -45.0, 70.0, 50.0, 0.2)  # Stronger deformation.
    draw_rectangle(45.0, -45.0, 70.0, 50.0, 0.35)  # Strong deformation (triangles may start to fold over).

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

    if width <= height:  # Window is tall (or square): X keeps the [-100, 100] range...
        glOrtho(-100.0, 100.0, -100.0 / aspect_ratio, 100.0 / aspect_ratio,  # ...and the Y range is stretched.
                1.0, -1.0)  # Near/far clipping planes along Z; for 2D only z = 0 must fit in between.
    else:  # Window is wide: Y keeps the [-100, 100] range...
        glOrtho(-100.0 * aspect_ratio, 100.0 * aspect_ratio, -100.0, 100.0,  # ...and the X range is stretched.
                1.0, -1.0)  # Same clipping planes as above.

    glMatrixMode(GL_MODELVIEW)  # Switch back to the MODELVIEW matrix (object transformations) used while drawing.
    glLoadIdentity()  # Start with no transformation: vertex coordinates are used as given.


def main():  # Program entry point: window setup and the main loop.
    if not glfwInit():  # Initialize the GLFW library; returns false on failure.
        sys.exit(-1)  # Without GLFW we cannot open a window, so quit with an error code.

    window = glfwCreateWindow(400, 400, __file__, None, None)  # 400x400 window titled with this file's path; no fullscreen monitor, no shared context.
    if not window:  # Window (or its OpenGL context) could not be created...
        glfwTerminate()  # ...release what glfwInit() allocated...
        sys.exit(-1)  # ...and quit with an error code.

    glfwMakeContextCurrent(window)  # Make this window's OpenGL context current: all gl* calls now target it.
    glfwSetFramebufferSizeCallback(window, update_viewport)  # Call update_viewport(window, w, h) whenever the window is resized.
    glfwSwapInterval(1)  # Enable V-Sync: swap buffers at most once per monitor refresh.

    startup(window)  # One-time initialization of our OpenGL state.
    while not glfwWindowShouldClose(window):  # Loop until the user closes the window.
        render(glfwGetTime())  # Draw a new frame into the hidden (back) buffer.
        glfwSwapBuffers(window)  # Show the back buffer on screen and swap it with the front buffer (double buffering).
        glfwWaitEvents()  # Sleep until an event (resize, key, mouse...) arrives, then process it.
    shutdown()  # One-time cleanup after the loop.

    glfwTerminate()  # Destroy the window and release all GLFW resources.


if __name__ == '__main__':  # True only when this file is run directly, not when imported as a module.
    main()  # Start the program.
