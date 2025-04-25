# GazeShift (Tentative Name) - v1.0

## Overview

GazeShift is a desktop application designed to enhance perceived eye contact during video calls. It provides a note-taking/display interface and uses strictly local AI-powered computer vision to adjust the user's eye gaze in their webcam feed in real-time. This modified feed is output via a virtual camera, allowing users to reference notes while appearing fully engaged. All processing occurs locally, ensuring data privacy.

*(Based on Technical Specification v1.0, 2025-04-17)*

## Key Features (MVP v1.0)

*   **AI Gaze Correction:** Real-time, local adjustment of eye gaze in the video feed to simulate eye contact.
    *   Manual On/Off toggle.
    *   High confidence threshold activation (prioritizes naturalness).
    *   Handles obstructions/low light; ignores glasses (MVP).
*   **Notes Overlay:** Semi-transparent, resizable, and repositionable overlay for displaying notes.
    *   Adjustable opacity.
    *   Best-effort resistance to screen capture.
*   **Note Management:**
    *   Direct typing/pasting.
    *   Import `.txt`, `.doc`, `.docx` (local conversion to Markdown).
    *   Full Markdown rendering.
    *   Teleprompter auto-scroll with speed control.
*   **Virtual Camera Output:** Registers as a system virtual camera for use in video conferencing apps.
*   **User Setup & Preview:** Simple calibration and real-time preview.
*   **Platform Support:** Windows and macOS.

## Goals

*   **(G1)** Provide a mechanism for users to view notes during video calls.
*   **(G2)** Adjust user's eye gaze via AI to simulate eye contact.
*   **(G3)** Perform all processing locally.
*   **(G4)** Prioritize natural, artifact-free gaze correction (high confidence activation).
*   **(G5)** Simple, intuitive user experience.
*   **(G6)** Stable application for Windows and macOS (MVP).
*   **(G7)** Support `.txt`/`.doc`/`.docx` import (local conversion) and Markdown rendering (MVP).
*   **(G8)** Real-time performance (<100ms latency target) with moderate resource usage.

## Technology Stack (Proposed)

*   **Application Framework:** Electron with React (preferred) or Native (Swift/Obj-C for macOS, C++/C# for Windows).
*   **UI (Electron):** React, HTML5, CSS3.
*   **Core Logic (Electron):** Node.js, TypeScript/JavaScript.
*   **AI / Computer Vision:** MediaPipe, OpenCV, ONNX Runtime, TensorFlow Lite, Core ML (local inference).
*   **DOC/DOCX Conversion:** Local library (e.g., WASM-based Pandoc).
*   **Markdown Rendering:** React Markdown library.
*   **Virtual Camera:** Platform-specific APIs/libraries (e.g., obs-virtual-cam, AkVirtualCamera).
*   **Build Tools (Electron):** npm/yarn, Electron Forge/Builder.

## Architecture Overview

GazeShift operates as a client-side desktop application with a local processing pipeline:

1.  **Video Input:** Captures frames from the physical webcam.
2.  **AI Analysis (Local):** Performs face detection, landmark detection, gaze estimation, and confidence scoring on the user's device (CPU/GPU).
3.  **Conditional Gaze Synthesis (Local):** If confidence is high, modifies the eye region; otherwise, passes the original frame.
4.  **Virtual Camera Output:** Sends the processed frame to the system's virtual camera.
5.  **Note Handling:** Manages note input, local file conversion (for `.doc`/`.docx`), storage, and Markdown rendering in the overlay UI.

*Asynchronous operations are used for AI processing and file conversion to maintain UI responsiveness.*

## Key Risks & Challenges

*   **AI Model Development/Optimization:** Achieving natural, real-time, high-confidence local gaze correction is challenging.
*   **Local DOC/DOCX Conversion:** Reliable local conversion is complex.
*   **Performance:** Meeting the <100ms latency target across varied hardware requires significant optimization.
*   **Overlay Undetectability:** Making the overlay resistant to all screen capture is difficult.

## Getting Started / Setup (Placeholder)

*(Instructions on how to build, install, and run the application will go here.)*

## Contributing (Placeholder)

*(Guidelines for contributors will go here.)*

## License (Placeholder)

*(License information will go here.)* 