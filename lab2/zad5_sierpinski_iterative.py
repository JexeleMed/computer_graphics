#!/usr/bin/env python3
# Task 5 (grade 5.0): the Sierpinski carpet again, but ITERATIVE (no recursion) - the alternative allowed by the slides.
# Idea ("domain of allowed coordinates"): split the carpet into a 3^n x 3^n grid of cells. Cell (i, j) is a hole
# if, at some position, the base-3 digits of BOTH i and j are 1 (= middle third at that level of subdivision).
# Usage: uv run lab2/zad5_sierpinski_iterative.py [level]   (default 3)

import sys  # sys.exit() on fatal errors and sys.argv for the command-line level parameter.

from glfw.GLFW import *  # GLFW: creates the window + OpenGL context and handles input events (C-style names).

from OpenGL.GL import *  # Core OpenGL functions (gl*) and constants (GL_*).
from OpenGL.GLU import *  # OpenGL Utility Library (glu*); not used yet, kept to match the course template.

LEVEL = int(sys.argv[1]) if len(sys.argv) > 1 else 4  # Degree of self-similarity from the 1st CLI argument, 4 if not given.

CARPET_WIDTH = 180.0  # Width of the whole carpet in world units.
CARPET_HEIGHT = 120.0  # Height of the whole carpet.


def startup(window):  # Runs once, after the OpenGL context is ready, before the main loop.
    width, height = glfwGetFramebufferSize(window)  # Size in PIXELS (on Retina it is 2x the window size in points).
    update_viewport(window, width, height)  # Set up the viewport and projection for the initial size.
    glClearColor(1.0, 1.0, 1.0, 1.0)  # White background: it shows through the holes of the carpet.


def shutdown():  # Runs once after the main loop ends; place to free OpenGL resources.
    pass  # Nothing to free in this program.


def draw_rectangle(x, y, a, b):  # Rectangle centered at (x, y), width a, height b, made of two triangles.
    half_a = a / 2.0  # Half of the width.
    half_b = b / 2.0  # Half of the height.

    glBegin(GL_TRIANGLES)  # 6 vertices -> 2 triangles.
    glVertex2f(x - half_a, y - half_b)  # Triangle 1: bottom-left.
    glVertex2f(x + half_a, y - half_b)  # Triangle 1: bottom-right.
    glVertex2f(x - half_a, y + half_b)  # Triangle 1: top-left.
    glVertex2f(x + half_a, y - half_b)  # Triangle 2: bottom-right.
    glVertex2f(x + half_a, y + half_b)  # Triangle 2: top-right.
    glVertex2f(x - half_a, y + half_b)  # Triangle 2: top-left.
    glEnd()  # Finish the two triangles.


def is_filled(i, j):  # True if grid cell (column i, row j) belongs to the carpet, False if it lies in some hole.
    while i > 0 or j > 0:  # Check base-3 digits from the least significant one, until both numbers run out.
        if i % 3 == 1 and j % 3 == 1:  # Both digits are 1 -> middle column AND middle row at this level...
            return False  # ...so the cell is inside a cut-out hole.
        i //= 3  # Drop the last base-3 digit of i (integer division)...
        j //= 3  # ...and of j, moving to the next (bigger) level of subdivision.
    return True  # No level put this cell in a hole -> it is part of the carpet.


def draw_carpet(x, y, a, b, level):  # Carpet centered at (x, y), size a x b, "level" subdivisions - without recursion.
    cells = 3 ** level  # Number of cells along each side of the finest grid (3^level).
    cell_a = a / cells  # Width of a single cell.
    cell_b = b / cells  # Height of a single cell.
    left = x - a / 2.0  # X of the carpet's left edge.
    bottom = y - b / 2.0  # Y of the carpet's bottom edge.

    for i in range(cells):  # Every column of the grid...
        for j in range(cells):  # ...and every row: plain nested loops instead of recursion.
            if is_filled(i, j):  # Draw only cells that belong to the carpet.
                draw_rectangle(left + (i + 0.5) * cell_a,  # Center X of cell i: left edge + i and a half cells.
                               bottom + (j + 0.5) * cell_b,  # Center Y of cell j: bottom edge + j and a half cells.
                               cell_a, cell_b)  # Size of one cell.


def render(time):  # Draws one frame; "time" = seconds since glfwInit() (unused here).
    glClear(GL_COLOR_BUFFER_BIT)  # Fill the whole color buffer with the white clear color.

    glColor3f(0.0, 0.35, 0.6)  # Dark blue, to tell it apart from the recursive version at a glance.
    draw_carpet(0.0, 0.0, CARPET_WIDTH, CARPET_HEIGHT, LEVEL)  # Whole carpet centered in the window.

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

    window = glfwCreateWindow(600, 400, __file__, None, None)  # 600x400 window (wide, to fit the wide carpet).
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
