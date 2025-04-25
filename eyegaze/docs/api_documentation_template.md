# GazeShift API Documentation Template

This document serves as a template and guide for documenting the GazeShift project's APIs and modules. Consistent and thorough documentation is essential for maintainability and developer onboarding.

## Documentation Standards

All code in the GazeShift project should be documented using [JSDoc](https://jsdoc.app/) for JavaScript/TypeScript code. This documentation template provides guidelines and examples for documenting different components of the codebase.

## Table of Contents

1. [Module Documentation](#module-documentation)
2. [Class Documentation](#class-documentation)
3. [Function Documentation](#function-documentation)
4. [Interface Documentation](#interface-documentation)
5. [Type Definition Documentation](#type-definition-documentation)
6. [Examples](#examples)
7. [Generating Documentation](#generating-documentation)

## Module Documentation

Each module should have a header comment that describes its purpose and usage.

```typescript
/**
 * @module VideoCapture
 * @description Manages webcam capture and provides video frames for processing.
 * This module handles webcam access, frame capture, and error conditions.
 * 
 * @example
 * import { VideoCapture } from './videoCapture';
 * 
 * const capture = new VideoCapture();
 * capture.start().then(() => {
 *   console.log('Video capture started');
 * });
 */
```

## Class Documentation

Classes should be documented with a description, examples, and details on properties and methods.

```typescript
/**
 * @class GazeEstimator
 * @description Estimates the user's gaze direction based on facial landmarks.
 * Uses a machine learning model to predict eye gaze vectors.
 * 
 * @example
 * const estimator = new GazeEstimator(modelConfig);
 * const gazeDirection = await estimator.estimateGaze(faceData);
 */
class GazeEstimator {
  // Class implementation...
}
```

## Function Documentation

Functions should be documented with descriptions, parameter and return value details, and examples.

```typescript
/**
 * Calculates the confidence score for gaze correction quality.
 * 
 * @param {FaceData} faceData - Detected face landmarks and features
 * @param {GazeVector} gazeVector - Estimated gaze direction vector
 * @param {ConfidenceOptions} [options] - Optional configuration parameters
 * @returns {number} Confidence score between 0.0 and 1.0
 * 
 * @example
 * const score = calculateConfidence(faceData, gazeVector);
 * if (score > CONFIDENCE_THRESHOLD) {
 *   // Apply gaze correction
 * }
 */
function calculateConfidence(faceData, gazeVector, options) {
  // Function implementation...
}
```

## Interface Documentation

Interfaces should be documented with descriptions and details on each property.

```typescript
/**
 * Configuration options for the AI processing pipeline.
 * 
 * @interface AIProcessingConfig
 */
interface AIProcessingConfig {
  /**
   * Minimum confidence threshold for applying gaze correction.
   * Values should be between 0.0 and 1.0.
   */
  confidenceThreshold: number;
  
  /**
   * Whether to use GPU acceleration if available.
   */
  useGPU: boolean;
  
  /**
   * Maximum processing time (in ms) before skipping a frame.
   */
  maxProcessingTime: number;
  
  /**
   * Model paths and configurations.
   */
  models: {
    /**
     * Path to the face detection model.
     */
    faceDetection: string;
    
    /**
     * Path to the landmark detection model.
     */
    landmarkDetection: string;
    
    /**
     * Path to the gaze estimation model.
     */
    gazeEstimation: string;
  };
}
```

## Type Definition Documentation

Type definitions should be documented with descriptions and possible values.

```typescript
/**
 * Status of the gaze correction process.
 * 
 * @typedef {string} GazeCorrectionStatus
 * @property {'idle'} IDLE - The correction is not active
 * @property {'active'} ACTIVE - Correction is being applied
 * @property {'low_confidence'} LOW_CONFIDENCE - Face detected but confidence too low
 * @property {'no_face'} NO_FACE - No face detected in frame
 * @property {'error'} ERROR - An error occurred during processing
 */
type GazeCorrectionStatus = 'idle' | 'active' | 'low_confidence' | 'no_face' | 'error';
```

## Examples

Include usage examples in documentation whenever possible. Examples help developers understand how to use the API correctly.

```typescript
/**
 * @example
 * // Basic usage
 * import { NoteManager } from './noteManager';
 * 
 * const noteManager = new NoteManager();
 * noteManager.loadNote('my-note.md').then(() => {
 *   console.log('Note loaded');
 * });
 * 
 * @example
 * // Importing and converting a document
 * import { NoteManager } from './noteManager';
 * 
 * const noteManager = new NoteManager();
 * noteManager.importDocument('presentation.docx').then(({ success, markdown }) => {
 *   if (success) {
 *     console.log('Document imported and converted to Markdown');
 *   }
 * });
 */
```

## Event Documentation

Document events that components can emit.

```typescript
/**
 * @event VideoCapture#frame
 * @description Fired when a new video frame is captured
 * @type {Object}
 * @property {ImageData} imageData - The raw image data from the video frame
 * @property {number} timestamp - Timestamp when the frame was captured
 */

/**
 * @fires VideoCapture#frame
 */
captureFrame() {
  // Method implementation...
}
```

## Generating Documentation

We use [TypeDoc](https://typedoc.org/) to generate API documentation from JSDoc comments. To generate documentation:

```bash
# Install TypeDoc if not already installed
npm install --save-dev typedoc

# Generate documentation
npm run docs
```

This will generate HTML documentation in the `docs/api` directory.

## Documentation Style Guide

- Use clear, concise language
- Provide examples for non-trivial functionality
- Document parameters with their types and descriptions
- Specify return values and their types
- Document possible errors or exceptions
- Use proper grammar and punctuation
- Keep documentation up to date with code changes

## Required Documentation Elements

For each major component type, ensure the following elements are included:

### Modules
- Description
- Usage example
- Dependencies
- Exported components

### Classes
- Description
- Constructor parameters
- Properties with types and descriptions
- Methods with parameters and return values
- Usage examples

### Functions
- Description
- Parameters with types and descriptions
- Return value with type and description
- Usage examples
- Throws/errors information if applicable

### Interfaces/Types
- Description
- Properties with types and descriptions
- Usage context

## Common Documentation Tags

- `@module` - Identifies a module
- `@class` - Identifies a class
- `@interface` - Identifies an interface
- `@typedef` - Identifies a custom type
- `@param` - Documents a function parameter
- `@returns` - Documents a function return value
- `@example` - Provides usage examples
- `@throws` - Documents potential errors
- `@see` - References related documentation
- `@deprecated` - Marks a deprecated feature
- `@since` - Indicates when a feature was added
- `@fires` - Documents events emitted by a method
- `@listens` - Documents events handled by a method
- `@async` - Indicates an asynchronous function
- `@private` - Indicates a private member
- `@protected` - Indicates a protected member
- `@public` - Indicates a public member 