# Freeze Frame Camera View for Maya

A powerful utility for Autodesk Maya that instantly creates a static, floating viewport from any camera's current perspective.

This script is an essential workflow enhancement for anyone doing match-moving, set modeling to plates, or complex scene layout. It solves the common problem of needing to reference a camera's view from one frame while working on another.

## The Problem

When modeling or animating based on background footage (a plate), artists frequently need to jump back and forth between different points in time to use parallax for placing elements correctly. This process is slow, inefficient, and breaks concentration.

## The Solution

With a single execution, this script creates a "frozen" duplicate of the active camera at the current frame. It generates a new, independent viewport for this frozen camera, allowing you to work in your main viewport while constantly referencing the frozen shot.

### Key Features

*   **One-Click Operation:** Simply run the script with your cursor over any model panel.
*   **Works with Any Camera:** Freezes perspective, orthographic, and animated cameras instantly.
*   **Robust Image Plane Handling:** The script's biggest strength. It correctly finds and duplicates image planes associated with the source camera, and intelligently freezes them:
    *   It handles image planes with **animated sequences** (`useFrameExtension`).
    *   It correctly **disconnects the timeline** and sets a static frame, perfectly preserving the background plate at the moment of creation.
*   **Complete Attribute Freezing:** Duplicates and locks all key camera attributes, including focal length, film aperture, and clipping planes, ensuring a perfect 1:1 copy of the view.
*   **Smart UI Creation:** Generates a new, floating model panel for each frozen camera, with a unique name based on the camera and frame number to prevent conflicts.
*   **Inherited Viewport Settings:** The new viewport copies the display settings (like wireframe on shaded, textures, etc.) from the source panel for a consistent look.

### Ideal Workflows

*   **Match-Moving & Set Modeling:** Work on a model at frame 100 while using the frozen view from frame 1 to line up points.
*   **VFX Plate Alignment:** Ensure 3D elements perfectly match the background plate from multiple angles and times.
*   **3D Layout & Composition:** Create multiple "snapshot" views to compare compositions without moving your main camera.

### How to Use

1.  Load the script into Maya's Script Editor.
2.  Move the timeline to the frame you want to freeze.
3.  Place your mouse cursor over the camera viewport you want to duplicate.
4.  Execute the script.
5.  A new floating window with the frozen view will appear.
