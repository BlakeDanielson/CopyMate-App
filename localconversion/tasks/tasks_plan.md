# Tasks Plan: Local File Converter v1.0 MVP

## Phase 1: Project Setup & Core UI

- [x] **Setup-1:** Initialize React project using chosen build tool (Vite/Webpack).
- [x] **Setup-2:** Configure build tool for WASM and Web Worker support.
- [x] **Setup-3:** Choose and integrate styling solution (CSS Modules/Styled-components/Tailwind).
- [x] **Setup-4:** Implement basic application layout/shell.
- [x] **UI-1 (F1):** Implement file selection UI (Drag-and-drop area).
- [x] **UI-2 (F1):** Implement file selection UI (Browse button - `<input type="file">`).
- [x] **UI-3 (F2):** Implement UI for selecting target output format (dynamically populated).
- [x] **UI-4 (F5):** Implement basic UI for progress indication (placeholder for spinner/percentage).
- [x] **UI-5 (F6):** Implement UI element to display/trigger download link.
- [x] **UI-6 (F7):** Implement basic UI area for displaying error messages.
- [x] **Core-1 (F3):** Implement client-side file reading (metadata) via File API.
- [x] **Core-2 (F3):** Implement client-side file size validation (< 100MB).
- [x] **Core-3:** Implement basic Web Worker setup and communication channel (main thread <-> worker).
- [x] **Core-4 (F7):** Implement initial error handling framework.

## Phase 2: MVP Conversion Implementation (Iterative)

*(Note: Each conversion requires finding/building/integrating JS/WASM, implementing worker logic, updating UI)*

- [x] **Core-5:** Implement base conversion worker architecture and worker factory.
- [x] **Conv-3 (JPG -> PNG):** Implement conversion logic using Canvas API.
- [x] **Conv-4 (PNG -> JPG):** Implement conversion logic using Canvas API.

### Document Conversion (WASM Implementation)
- [ ] **WASM-1:** Research and evaluate PDF.js and docx.js libraries for document conversions.
- [ ] **WASM-2:** Set up WASM module structure for document conversions.
- [ ] **WASM-3:** Implement PDF.js integration for PDF processing.
- [ ] **WASM-4:** Implement docx.js integration for DOCX processing.
- [ ] **Conv-1 (PDF -> DOCX):** Implement conversion pipeline and worker logic.
- [ ] **Conv-2 (DOCX -> PDF):** Implement conversion pipeline and worker logic.
- [ ] **Conv-6 (JPG -> PDF):** Implement conversion pipeline for single image to PDF.
- [ ] **Conv-7 (PNG -> PDF):** Implement conversion pipeline with transparency support.
- [ ] **Conv-9 (PDF -> JPG):** Implement page selection/extraction functionality.

### Media Conversion (WASM Implementation)
- [ ] **WASM-5:** Research and evaluate ffmpeg.wasm for media conversions.
- [ ] **WASM-6:** Set up WASM module structure for audio/video conversions.
- [ ] **WASM-7:** Implement ffmpeg.wasm integration with optimization for browser performance.
- [ ] **Conv-8 (MP4 -> MP3):** Implement audio extraction pipeline.
- [ ] **Conv-10 (MOV -> MP4):** Implement video conversion pipeline.
- [ ] **Conv-11 (MP4 -> GIF):** Implement video to GIF pipeline with basic configuration options.

### Special Formats Conversion (WASM Implementation)
- [ ] **WASM-8:** Research and evaluate heic-decode or alternative libraries for HEIC conversion.
- [ ] **WASM-9:** Set up WASM module structure for special format conversions.
- [ ] **Conv-5 (HEIC -> JPG):** Implement HEIC decoding and conversion pipeline.

### Integration and Optimization
- [ ] **WASM-10:** Implement lazy loading strategy for WASM modules.
- [ ] **WASM-11:** Optimize memory usage and transfer between main thread and workers.
- [ ] **WASM-12:** Implement comprehensive progress reporting from WASM to UI.

## Phase 3: Refinement & Testing

- [ ] **Refine-1 (F5):** Integrate actual progress reporting (percentage or indeterminate) from workers to UI.
- [ ] **Refine-2 (F6):** Implement Blob URL generation and download link logic.
- [ ] **Refine-3 (F7):** Enhance user-friendliness of error messages.
- [ ] **Refine-4:** Implement lazy loading for conversion modules if feasible.
- [ ] **Test-1:** Write Unit Tests for core components and utilities.
- [ ] **Test-2:** Write Integration Tests for main thread/worker communication.
- [ ] **Test-3:** Implement E2E tests for key conversion flows (Recommended).
- [ ] **Test-4:** Perform Cross-Browser Testing.
- [ ] **Security-1:** Implement Content Security Policy (CSP).
- [ ] **Deploy-1:** Set up static hosting and deployment pipeline.

## Known Issues / Backlog

- WASM modules size might impact initial load time - consider implementing progress indicators for module loading.
- Browser compatibility for certain WASM features might vary - need comprehensive testing across supported browsers.
- Memory management for large files (close to 100MB) needs careful implementation to avoid browser crashes. 