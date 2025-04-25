declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.worker.js' {
  class WebpackWorker extends Worker {
    constructor();
  }
  export default WebpackWorker;
}

declare module '*.worker.ts' {
  class WebpackWorker extends Worker {
    constructor();
  }
  export default WebpackWorker;
}

declare module '*.wasm' {
  const content: any;
  export default content;
} 