declare module "*.worker.js" {
  class WebpackWorker extends Worker {
    constructor();
  }
  export default WebpackWorker;
}

declare module "*.wasm" {
  const content: any;
  export default content;
} 