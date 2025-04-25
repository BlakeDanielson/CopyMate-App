# GazeShift Active Development Context

This document tracks the current state of development, active decisions, recent changes, and next steps for the GazeShift project.

## Current Development Status

The project is in the early planning and documentation phase. We have established the foundational documents:

- **README.md**: Basic project overview and information
- **docs/product_requirement_docs.md**: Detailed product requirements
- **docs/architecture.md**: System architecture and component relationships
- **docs/technical.md**: Technical specifications and development environment
- **docs/user_guide.md**: Comprehensive user guide outline
- **docs/developer_setup.md**: Developer environment setup instructions
- **docs/api_documentation_template.md**: Template and guidelines for API documentation
- **tasks/tasks_plan.md**: Detailed task backlog and project planning

No code implementation has started yet. The current focus is on completing the documentation, research, and planning before proceeding to implementation.

## Active Decisions and Considerations

### Application Framework Selection
- **Current Decision**: Electron with React for cross-platform support and developer efficiency
- **Considerations**: 
  - Native implementation would potentially offer better performance but at the cost of development speed and cross-platform support
  - Electron allows for faster iteration and prototyping
  - Monitoring resource usage will be critical to ensure the Electron approach meets performance requirements

### AI Processing Approach
- **Current Decision**: Research phase; evaluating MediaPipe, TensorFlow Lite, and ONNX Runtime for local inference
- **Considerations**:
  - Need to validate that real-time (<100ms) local gaze correction is feasible
  - Must determine the right balance between quality and performance
  - Confidence scoring mechanism is critical to avoid unnatural corrections

### File Conversion Strategy
- **Current Decision**: Investigating browser-based solutions (Mammoth.js) and WASM-based approaches (Pandoc)
- **Considerations**:
  - Must prioritize reliable conversion while maintaining local processing
  - Need to evaluate performance impact during document conversion
  - Asynchronous processing will be essential to maintain UI responsiveness

### Virtual Camera Implementation
- **Current Decision**: Platform-specific implementations required (AVFoundation/CoreMediaIO for macOS, DirectShow for Windows)
- **Considerations**:
  - Evaluating whether to leverage existing solutions like OBS Virtual Camera
  - Need to address potential permission and security constraints
  - Must ensure compatibility with major video conferencing platforms

## Recent Changes

- Created core documentation structure
- Defined system architecture with component relationships
- Established detailed task breakdown and project phases
- Identified key technical challenges and research areas
- Documented product requirements and user stories
- Created comprehensive user guide outline
- Developed detailed developer setup instructions
- Created API documentation template and guidelines

## Next Steps

### Immediate (Next 1-2 Weeks)
1. ~~Complete remaining documentation~~
   - ~~User guide/manual outline~~ ✓
   - ~~Developer setup instructions~~ ✓
   - ~~API documentation template~~ ✓

2. Begin research phase
   - Evaluate AI libraries for face/landmark detection
   - Investigate gaze estimation and correction approaches
   - Research virtual camera implementations
   - Explore document conversion libraries

3. Set up development environment
   - Initialize repository structure
   - Configure development toolchain
   - Set up basic Electron/React application

### Short-Term (Next 3-4 Weeks)
1. Develop proof-of-concept implementations
   - Basic webcam capture and display
   - Face and landmark detection
   - Simple virtual camera output
   - Document import and Markdown rendering

2. Validate core technical assumptions
   - Measure performance of AI processing pipeline
   - Test virtual camera compatibility
   - Evaluate document conversion approaches

3. Begin core implementation
   - Application framework setup
   - Basic UI structure
   - Video capture pipeline

## Open Questions

1. What is the optimal approach for gaze correction that balances quality and performance?
2. How can we make the overlay maximally resistant to screen capture?
3. What is the most reliable way to implement local DOC/DOCX conversion?
4. How can we ensure consistent virtual camera functionality across platforms and video apps?
5. What performance optimizations will be needed to meet the <100ms latency target?

## Resource Allocation

Current resources are focused on:
- Documentation and planning (completed)
- Research and validation of key technical approaches (starting now)
- Setup of development environment and toolchain (upcoming)

## Dependencies and Blockers

1. **Technical Validation**: Need to confirm feasibility of real-time local gaze correction
2. **Platform Support**: Virtual camera implementations have platform-specific requirements and potential OS constraints
3. **Performance Requirements**: <100ms latency target is ambitious and may require significant optimization 