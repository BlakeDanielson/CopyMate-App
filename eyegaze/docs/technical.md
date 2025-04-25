# GazeShift Technical Specification

## Development Environment

### Supported Development Platforms
- macOS 12+ (Monterey or newer)
- Windows 10 (64-bit) or Windows 11

### Development Tools
- **IDE**: Visual Studio Code with appropriate extensions for React/Electron development
- **Version Control**: Git with GitHub repository
- **Package Management**: npm or yarn
- **Build Tools**: Electron Forge/Builder
- **Testing Framework**: Jest for unit tests, Spectron for application testing
- **Continuous Integration**: GitHub Actions

## Technology Stack

### Application Framework
The application will be built using **Electron** with **React** for the following reasons:
- Cross-platform support (Windows, macOS)
- Familiar web technologies (HTML, CSS, JavaScript/TypeScript)
- Rich ecosystem of libraries and tools
- Better developer efficiency compared to native code for this use case
- Allows for faster iteration and prototyping

### Frontend Technologies
- **UI Framework**: React 18+ (using functional components and hooks)
- **Styling**: CSS/SCSS modules or Styled Components
- **State Management**: React Context API and/or Redux (if needed for complexity)
- **UI Components**: Custom components with minimal dependencies

### Core Technologies
- **Language**: TypeScript 4.9+ for type safety and developer experience
- **Runtime**: Node.js 20+ LTS
- **Electron**: Version 28+ for the desktop application shell

### AI / Computer Vision
The AI processing pipeline will leverage:
- **MediaPipe**: For face detection and facial landmark detection
- **TensorFlow Lite** and/or **ONNX Runtime**: For optimized local model inference
- **OpenCV.js**: For image processing operations
- **CoreML** (macOS) / **DirectML** (Windows): For GPU acceleration where available

Potential model architectures:
- Face Detection: BlazeFace or similar lightweight model
- Facial Landmark Detection: MediaPipe Face Mesh
- Gaze Estimation: Custom trained model (TBD)
- Gaze Synthesis: Generative model or geometric warping approach (R&D required)

All models will be optimized and quantized for performance on consumer hardware.

### File Conversion
For local .doc/.docx conversion:
- **Mammoth.js**: Browser-based .docx to HTML/Markdown converter
- **Pandoc WASM**: If a more robust conversion is needed (compiled to WebAssembly)
- Custom conversion pipeline running in a worker thread to maintain UI responsiveness

### Markdown Rendering
- **react-markdown**: For rendering Markdown content
- **remark** and **rehype** plugins: For extended Markdown features

### Virtual Camera Implementation
- **macOS**: Integration with AVFoundation and CoreMediaIO
- **Windows**: Integration with DirectShow virtual camera API
- Alternative: Embedding/leveraging parts of OBS Virtual Camera if licensing permits

## Data Storage
- **User Preferences**: Electron's built-in `electron-store` or similar
- **Notes Storage**: Local file system with appropriate sandboxing
- **Calibration Data**: Encrypted local storage

## Security Considerations
- All files will be processed locally within the application sandbox
- No telemetry or data will be sent to external servers without explicit user consent
- Camera permissions will be requested with clear explanation
- Local file access limited to what's necessary for the application

## Performance Targets
- **Video Processing Latency**: <100ms end-to-end
- **CPU Usage**: <30% on quad-core CPU from the last 5 years
- **Memory Usage**: <500MB during normal operation
- **Startup Time**: <3 seconds to fully loaded state

## Testing Strategy
- **Unit Testing**: Core algorithm and utility functions
- **Component Testing**: UI components and interaction
- **Integration Testing**: End-to-end workflow testing
- **Performance Testing**: Benchmarking on reference hardware
- **Compatibility Testing**: Across supported platforms and with major video conferencing apps

## Build and Distribution
- **macOS**: Code signed .dmg or .pkg installer
- **Windows**: NSIS installer or similar
- **Auto-Update**: Electron's auto-updater or similar mechanism (for future versions)

## Third-Party Dependencies
All dependencies will be evaluated for:
- License compatibility
- Security history
- Maintenance status
- Performance impact
- Bundle size impact

## Development Workflow
1. Feature branch development
2. PR reviews with linting and automated tests
3. Staging builds for internal testing
4. Release candidate builds
5. Official releases

## Documentation
- API documentation with JSDoc
- Component documentation
- Developer setup guide
- Architecture documentation (this document and architecture.md)
- User documentation

## Known Technical Challenges
1. **AI Model Optimization**: Balancing quality and performance for the gaze correction
2. **Local DOC/DOCX Conversion**: Finding the right approach for reliable conversion
3. **Virtual Camera Integration**: Platform-specific implementations
4. **Screen Capture Resistance**: Technical limitations may exist
5. **Performance Optimization**: Meeting target latency across varied hardware

## Research & Development Areas
1. Best approaches for natural, high-confidence gaze correction
2. Efficient local document conversion techniques
3. Methods for overlay resistance to screen capture
4. Performance optimization for the AI pipeline 