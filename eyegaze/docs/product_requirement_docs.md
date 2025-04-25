# GazeShift Product Requirements Document (PRD)

## Product Overview

GazeShift is a desktop application designed to enhance perceived eye contact during video calls. It provides a note-taking/display interface and utilizes local AI-powered computer vision to adjust the user's eye gaze in their webcam feed in real-time.

## Problem Statement

During video calls, looking at notes or reference material causes users to appear disengaged as they look away from the camera. This creates a dilemma: either maintain eye contact but without access to notes, or reference notes but appear distracted.

## User Needs

1. **Professional Presence**: Users need to maintain the appearance of engagement and eye contact during remote presentations and meetings.
2. **Reference Access**: Users need to view notes, scripts, or other reference materials during video calls.
3. **Privacy**: Users require that their video and note data remain secure and processed locally.
4. **Ease of Use**: Users need a simple solution that works with existing video conferencing platforms.
5. **Natural Appearance**: Users require that any video modification appears completely natural and undetectable.

## Market Opportunity

The rise of remote work and video conferencing has created a significant need for tools that enhance virtual presence. Existing solutions either:
- Don't address the eye contact problem
- Require external hardware
- Process data in the cloud (privacy concerns)
- Don't include integrated note-taking features

## Product Goals

1. **G1 (Core)**: Provide a mechanism for users to view notes during video calls.
2. **G2 (AI Correction)**: Adjust the user's eye gaze in the output video feed to simulate eye contact with the camera, even when reading notes.
3. **G3 (Local Processing)**: Perform ALL video processing and file handling/conversion locally on the user's device.
4. **G4 (Naturalness & Confidence)**: Prioritize a natural-looking, artifact-free gaze correction.
5. **G5 (User Experience)**: Offer a simple, intuitive interface with user controls for key features.
6. **G6 (Platform Support - MVP)**: Deliver a stable application for Windows and macOS.
7. **G7 (Note Handling - MVP)**: Support direct input/pasting and import of .txt, .doc, .docx files.
8. **G8 (Performance)**: Achieve real-time performance (<100ms latency target) with moderate, optimized resource usage.

## Product Non-Goals (for MVP v1.0)

1. Cloud-based video processing or file conversion.
2. Support for Linux (considered "nice-to-have" post-MVP).
3. AI correction for users wearing glasses.
4. Direct integration with specific note-taking applications (e.g., Notion, Evernote).
5. Advanced text editing features beyond Markdown rendering.
6. Monetization features (licensing, feature gating).
7. Guaranteed undetectability by all forms of screen capture or proctoring software.
8. Correction during extreme head poses or when eyes are fully obscured.

## Target Audience

- Professionals conducting important video meetings or presentations
- Remote workers who regularly participate in video calls
- Educators and students in virtual learning environments
- Anyone who needs to reference notes while maintaining engagement in video calls

## User Stories

1. **As a presenter**, I want to read from my notes while appearing to look directly at my audience so that I can deliver a polished presentation while maintaining connection.

2. **As a job interviewee**, I want to refer to my prepared talking points without appearing distracted so that I make the best impression possible.

3. **As a remote worker**, I want to have my meeting notes visible during calls without seeming disengaged so that I can be fully prepared and present.

4. **As a privacy-conscious user**, I want all video processing to happen on my device so that my video feed and notes never leave my computer.

5. **As a non-technical user**, I want a simple interface that works with my existing video calling apps so that I don't need to learn a completely new system.

## Success Metrics

1. **Naturalness Rating**: User testing shows >90% of viewers cannot distinguish between natural and AI-corrected gaze.
2. **Performance**: Average latency below 100ms on target hardware.
3. **User Satisfaction**: >85% of users report improved meeting effectiveness when using the application.
4. **Platform Compatibility**: Successful operation with the top 5 video conferencing platforms.
5. **Resource Usage**: Average CPU usage <30% and memory footprint <500MB during operation.

## Minimum Viable Product (MVP) Features

1. **AI Gaze Correction**:
   - Manual On/Off toggle
   - Fixed intensity level
   - High confidence threshold for activation

2. **Notes Overlay UI**:
   - Resizable and repositionable
   - Adjustable opacity control
   - Attempt to make overlay resistant to screen capture

3. **Note Management**:
   - Direct typing/pasting
   - Import .txt, .doc, .docx files
   - Render notes using full Markdown syntax
   - Teleprompter auto-scroll option with speed control

4. **Virtual Camera Output**:
   - Register as a system virtual camera
   - Compatible with major video conferencing applications

5. **User Setup & Preview**:
   - One-time calibration step
   - Real-time preview showing original and corrected video feeds

6. **Platform Support**:
   - Windows and macOS compatibility

## Future Enhancements (Post-MVP)

1. User-configurable activation conditions
2. Intensity slider control
3. Support for eyeglasses in AI correction
4. Linux support
5. Integration with note-taking apps (Notion, Evernote, etc.)
6. More sophisticated note editor features
7. Improved AI models for even greater naturalness
8. Potential monetization hooks
9. WCAG compliance

## Constraints & Requirements

1. **Privacy**: No video data or unencrypted note content may be sent to any external server.
2. **Performance**: Must operate in real-time (<100ms latency) on modern consumer hardware.
3. **Quality**: AI correction must only activate when high confidence in a "flawless" result is achieved.
4. **Compatibility**: Must work with major video conferencing platforms (Zoom, Teams, Meet, Webex, etc.).
5. **Usability**: Must be accessible to non-technical users with minimal setup.

## Open Questions & Risks

1. Can we achieve sufficiently natural gaze correction with purely local processing?
2. How well will the solution work across diverse user demographics and lighting conditions?
3. Will the approach to making the overlay resistant to screen capture be effective enough?
4. Can we achieve reliable DOC/DOCX conversion locally with acceptable performance?
5. Will the virtual camera implementation work reliably across different OS versions and security contexts?

## Timeline (TBD)

Phase 1: Research & Prototyping
Phase 2: Core Implementation
Phase 3: Testing & Refinement
Phase 4: Beta Release
Phase 5: Full Release

*(Detailed timeline to be developed with development team.)* 