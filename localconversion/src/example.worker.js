// This is a simple example worker that will be expanded later
// for actual file conversion

// Set up the worker context
const ctx = self;

// Listen for messages from the main thread
ctx.addEventListener('message', (event) => {
  // Echo the received message back to the main thread
  // In the future, this will handle file conversion logic
  ctx.postMessage({
    type: 'ECHO',
    payload: event.data,
    message: 'Worker received message and echoed it back'
  });
});

// Inform main thread that the worker is ready
ctx.postMessage({
  type: 'READY',
  message: 'Worker initialized and ready'
}); 