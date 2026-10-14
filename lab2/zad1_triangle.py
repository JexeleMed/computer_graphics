#!/usr/bin/env python3
# Task 1 (grade 3.0): draw a single triangle whose every vertex has a different color.

import sys  # Standard module, used here only for sys.exit() on fatal errors.

from glfw.GLFW import *  # GLFW: creates the window + OpenGL context and handles input events (C-style names).

from OpenGL.GL import *  # Core OpenGL functions (gl*) and constants (GL_*).
from OpenGL.GLU import *  # OpenGL Utility Library (glu*); not used yet, kept to match the course template.


def startup(window):  # Runs once, after the OpenGL context is ready, before the main loop.
    width, height = glfwGetFramebufferSize(window)  # Size in PIXELS (on Retina it is 2x the window size in points).
    update_viewport(window, width, height)  # Set up the viewport and projection for the initial size.
    glClearColor(0.5, 0.5, 0.5, 1.0)  # Color used by glClear(): RGBA, each 0.0-1.0 -> mid gray, fully opaque.


def shutdown():  # Runs once after the main loop ends; place to free OpenGL resources.
    pass  # Nothing to free in this program, "pass" is an empty statement (placeholder).


def render(time):  # Draws one frame; "time" = seconds since glfwInit() (unused here).
    glClear(GL_COLOR_BUFFER_BIT)  # Fill the whole color buffer with the clear color set in startup().

    glBegin(GL_TRIANGLES)  # Start a primitive: every 3 consecutive vertices form one separate triangle.
    glColor3f(1.0, 0.0, 0.0)  # Set the "current color" to red; it sticks to every following vertex.
    glVertex2f(-50.0, -50.0)  # Bottom-left vertex (x, y); z defaults to 0. Takes the current color: red.
    glColor3f(0.0, 1.0, 0.0)  # Change the current color to green.
    glVertex2f(50.0, -50.0)  # Bottom-right vertex, green.
    glColor3f(0.0, 0.0, 1.0)  # Change the current color to blue.
    glVertex2f(0.0, 50.0)  # Top vertex, blue. Third vertex -> the triangle is complete.
    glEnd()  # Finish the primitive; pixels inside get colors interpolated between the 3 vertex colors.

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
