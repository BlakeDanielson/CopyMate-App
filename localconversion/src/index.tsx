import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { Buffer } from 'buffer';

// Make Buffer available globally for libraries that depend on it
window.Buffer = Buffer;

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 