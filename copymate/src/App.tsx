import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import "./App.css";

// TypeScript interface matching our Rust ClipboardItem
interface ClipboardItem {
  id: number;
  content: string;
  timestamp: number;
  content_type: string;
}

function App() {
  const [clipboardHistory, setClipboardHistory] = useState<ClipboardItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Function to load clipboard history from Rust backend
  const loadClipboardHistory = async () => {
    try {
      const history: ClipboardItem[] = await invoke("get_clipboard_history");
      setClipboardHistory(history);
    } catch (error) {
      console.error("Failed to load clipboard history:", error);
    }
  };

  // Function to copy text to clipboard and highlight selection
  const copyToClipboard = async (content: string, id: number) => {
    try {
      await invoke("copy_to_clipboard", { content });
      setSelectedId(id);
      // Clear selection after a brief moment
      setTimeout(() => setSelectedId(null), 200);
    } catch (error) {
      console.error("Failed to copy to clipboard:", error);
    }
  };

  // Function to start automatic clipboard monitoring
  const startMonitoring = async () => {
    try {
      await invoke("start_clipboard_monitoring");
      console.log("Clipboard monitoring started!");
    } catch (error) {
      console.error("Failed to start clipboard monitoring:", error);
    }
  };

  // Truncate long text for display
  const truncateText = (text: string, maxLength: number = 60) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  // Format timestamp
  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Load initial data when component mounts
  useEffect(() => {
    loadClipboardHistory();
    
    // Set up event listener for automatic clipboard updates
    const unlisten = listen<string>("clipboard-updated", (event) => {
      console.log("Clipboard updated:", event.payload);
      loadClipboardHistory(); // Refresh history when clipboard changes
    });

    // Start monitoring automatically
    startMonitoring();

    // Cleanup listener on unmount
    return () => {
      unlisten.then(fn => fn());
    };
  }, []);

  return (
    <div className="app">
      <div className="app-content">
        <div className="header">
          <h3>CopyMate</h3>
          <span className="count">{clipboardHistory.length} items</span>
        </div>
        
        <div className="clipboard-list">
          {clipboardHistory.length === 0 ? (
            <div className="empty-state">
              <p>No clipboard history yet</p>
              <small>Copy something to get started</small>
            </div>
          ) : (
            clipboardHistory.map((item) => (
              <div
                key={item.id}
                className={`clipboard-item ${selectedId === item.id ? 'selected' : ''}`}
                onClick={() => copyToClipboard(item.content, item.id)}
                title={item.content} // Show full content on hover
              >
                <div className="item-content">
                  {truncateText(item.content)}
                </div>
                <div className="item-time">
                  {formatTime(item.timestamp)}
                </div>
              </div>
            ))
          )}
        </div>

        {clipboardHistory.length > 0 && (
          <div className="footer">
            <button 
              className="clear-btn"
              onClick={async () => {
                try {
                  await invoke("clear_clipboard_history");
                  loadClipboardHistory();
                } catch (error) {
                  console.error("Failed to clear history:", error);
                }
              }}
            >
              Clear All
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
