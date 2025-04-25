# AI Libraries Evaluation

## Overview
This document evaluates various AI libraries for face detection, facial landmark detection, and gaze estimation/correction for the GazeShift application.

## Requirements
- Must be able to run efficiently on consumer hardware
- Should support cross-platform deployment (Windows, macOS, Linux)
- Latency should be under 100ms per frame
- Accuracy should be sufficient for video call scenarios
- Should be able to run locally (no cloud dependencies)

## Libraries Evaluated

### MediaPipe
- **Description**: Google's toolkit for building multimodal ML solutions
- **Strengths**:
  - Pre-optimized for cross-platform use (Web, mobile, desktop)
  - Face detection and facial landmark models available
  - WebAssembly support for browser integration
  - Designed for real-time applications
  - Well-documented with many examples
- **Weaknesses**:
  - No direct gaze correction implementation
  - May require additional custom models for gaze correction
- **Integration Complexity**: Medium
- **License**: Apache 2.0
- **Performance**: Excellent, optimized for real-time applications
- **Recommendation**: High priority for evaluation, particularly for face detection and landmarks

### TensorFlow Lite
- **Description**: Lightweight version of TensorFlow designed for edge devices
- **Strengths**:
  - Optimized for on-device inference
  - Supports model quantization for faster inference
  - Extensive ecosystem and documentation
  - Can run pre-trained models for face detection
- **Weaknesses**:
  - May require more manual work for custom models
  - Integration with Electron requires native bindings
- **Integration Complexity**: Medium-High
- **License**: Apache 2.0
- **Performance**: Good for optimized models
- **Recommendation**: Strong candidate for running custom gaze models if needed

### ONNX Runtime
- **Description**: Cross-platform inference engine for ONNX models
- **Strengths**:
  - Model interoperability (can use models trained in various frameworks)
  - Good performance
  - WebAssembly support
  - Runs on most platforms
- **Weaknesses**:
  - May require conversion of models to ONNX format
  - Less direct support for real-time video processing
- **Integration Complexity**: Medium
- **License**: MIT
- **Performance**: Good, with optimization options
- **Recommendation**: Good option for model interoperability

### Face-api.js
- **Description**: JavaScript face detection and recognition library
- **Strengths**:
  - Directly usable in Electron (browser environment)
  - Pre-trained models for face detection and landmarks
  - Simple API
- **Weaknesses**:
  - Limited to what's available in the pre-trained models
  - JavaScript performance limitations
  - No direct gaze estimation or correction
- **Integration Complexity**: Low
- **License**: MIT
- **Performance**: Moderate
- **Recommendation**: Good for quick prototyping, may not be sufficient for full production

## Model Considerations

### Face Detection Models
- SSD (Single Shot MultiBox Detector) - fast but less accurate
- BlazeFace - optimized for mobile/real-time
- MTCNN (Multi-task Cascaded Convolutional Networks) - more accurate but slower

### Facial Landmark Detection
- MediaPipe Face Mesh (468 points)
- dlib (68 points)
- Custom models may be needed for high accuracy

### Gaze Estimation/Correction
- Will likely require custom models or adaptation of research models
- Potential approaches:
  - Direct regression for gaze vector estimation
  - GAN-based approaches for image-to-image translation
  - 3D face model-based approaches

## Preliminary Recommendations

1. **Primary Choice**: MediaPipe for face detection and facial landmarks
   - Well-optimized for real-time applications
   - Good cross-platform support
   - Active development and support

2. **Secondary/Complementary**: TensorFlow Lite or ONNX Runtime
   - For running custom gaze estimation/correction models
   - Flexibility to integrate research models

## Next Steps
1. Create proof-of-concept implementations using MediaPipe
2. Benchmark performance on target platforms
3. Evaluate the need for custom models for gaze estimation/correction
4. If needed, train or adapt custom models using TensorFlow and convert to TF Lite or ONNX 