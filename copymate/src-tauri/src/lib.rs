// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH, Duration};
use std::thread;
use tauri::{State, AppHandle, Emitter};
use tauri_plugin_clipboard_manager::ClipboardExt;
use serde::{Deserialize, Serialize};

// Data structure for clipboard items
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClipboardItem {
    pub id: u64,
    pub content: String,
    pub timestamp: u64,
    pub content_type: String,
}

// Application state to store clipboard history
pub type ClipboardHistory = Arc<Mutex<VecDeque<ClipboardItem>>>;

// Global flag to track when we're programmatically setting clipboard
pub type IgnoreNextClipboard = Arc<Mutex<bool>>;

// Tauri command to get current clipboard content
#[tauri::command]
fn get_clipboard_text(app: tauri::AppHandle) -> Result<String, String> {
    match app.clipboard().read_text() {
        Ok(text) => Ok(text),
        Err(e) => Err(format!("Failed to read clipboard: {}", e)),
    }
}

// Tauri command to get clipboard history
#[tauri::command]
async fn get_clipboard_history(history: State<'_, ClipboardHistory>) -> Result<Vec<ClipboardItem>, String> {
    let history_guard = history.lock().map_err(|e| format!("Failed to lock history: {}", e))?;
    Ok(history_guard.iter().cloned().collect())
}

// Tauri command to add item to clipboard history manually (for testing)
#[tauri::command]
async fn add_to_history(
    content: String,
    history: State<'_, ClipboardHistory>
) -> Result<(), String> {
    add_item_to_history(&content, &history).await
}

// Helper function to add items to history (used by both manual and automatic monitoring)
async fn add_item_to_history(content: &str, history: &ClipboardHistory) -> Result<(), String> {
    if content.trim().is_empty() {
        return Ok(()); // Don't add empty content
    }

    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
    
    let mut history_guard = history.lock().map_err(|e| format!("Failed to lock history: {}", e))?;
    
    // Check if this content is already the most recent item (avoid duplicates)
    if let Some(latest) = history_guard.front() {
        if latest.content == content {
            return Ok(()); // Don't add duplicate
        }
    }
    
    // Generate a simple ID based on timestamp and length
    let id = timestamp + history_guard.len() as u64;
    
    let item = ClipboardItem {
        id,
        content: content.to_string(),
        timestamp,
        content_type: "text".to_string(),
    };
    
    // Add to front of deque (newest first)
    history_guard.push_front(item);
    
    // Keep only last 100 items
    if history_guard.len() > 100 {
        history_guard.pop_back();
    }
    
    Ok(())
}

// Tauri command to start clipboard monitoring
#[tauri::command]
async fn start_clipboard_monitoring(
    app: AppHandle,
    history: State<'_, ClipboardHistory>,
    ignore_flag: State<'_, IgnoreNextClipboard>
) -> Result<(), String> {
    let app_clone = app.clone();
    let history_clone = history.inner().clone();
    let ignore_flag_clone = ignore_flag.inner().clone();
    
    // Spawn background thread for clipboard monitoring
    thread::spawn(move || {
        let mut last_clipboard_content = String::new();
        
        loop {
            // Check clipboard every 500ms
            thread::sleep(Duration::from_millis(500));
            
            // Get current clipboard content
            if let Ok(current_content) = app_clone.clipboard().read_text() {
                // If content changed, check if we should ignore it
                if current_content != last_clipboard_content && !current_content.trim().is_empty() {
                    // Check if we should ignore this change
                    let should_ignore = {
                        if let Ok(mut ignore_guard) = ignore_flag_clone.lock() {
                            let ignore = *ignore_guard;
                            if ignore {
                                *ignore_guard = false; // Reset flag after checking
                                true
                            } else {
                                false
                            }
                        } else {
                            false
                        }
                    };
                    
                    if should_ignore {
                        last_clipboard_content = current_content;
                        continue;
                    }
                    // Create a simple blocking version for the thread
                    let timestamp = SystemTime::now()
                        .duration_since(UNIX_EPOCH)
                        .unwrap()
                        .as_secs();
                    
                    if let Ok(mut history_guard) = history_clone.lock() {
                        // Check if this content is already the most recent item
                        if let Some(latest) = history_guard.front() {
                            if latest.content == current_content {
                                continue; // Skip duplicate
                            }
                        }
                        
                        let id = timestamp + history_guard.len() as u64;
                        let item = ClipboardItem {
                            id,
                            content: current_content.clone(),
                            timestamp,
                            content_type: "text".to_string(),
                        };
                        
                        history_guard.push_front(item);
                        
                        // Keep only last 100 items
                        if history_guard.len() > 100 {
                            history_guard.pop_back();
                        }
                        
                        println!("Added clipboard item: {}", current_content.chars().take(50).collect::<String>());
                        
                        // Emit event to frontend to refresh history
                        if let Err(e) = app_clone.emit("clipboard-updated", &current_content) {
                            eprintln!("Failed to emit clipboard update event: {}", e);
                        }
                    }
                    
                    last_clipboard_content = current_content;
                }
            }
        }
    });
    
    Ok(())
}

// Tauri command to copy text to clipboard without triggering monitoring
#[tauri::command]
async fn copy_to_clipboard(
    app: AppHandle,
    content: String,
    ignore_flag: State<'_, IgnoreNextClipboard>
) -> Result<(), String> {
    // Set flag to ignore the next clipboard change
    {
        let mut ignore_guard = ignore_flag.lock().map_err(|e| format!("Failed to lock ignore flag: {}", e))?;
        *ignore_guard = true;
    }
    
    // Copy to clipboard
    app.clipboard().write_text(content)
        .map_err(|e| format!("Failed to write to clipboard: {}", e))?;
    
    Ok(())
}

// Tauri command to clear clipboard history
#[tauri::command]
async fn clear_clipboard_history(history: State<'_, ClipboardHistory>) -> Result<(), String> {
    let mut history_guard = history.lock().map_err(|e| format!("Failed to lock history: {}", e))?;
    history_guard.clear();
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Initialize clipboard history state
    let clipboard_history: ClipboardHistory = Arc::new(Mutex::new(VecDeque::new()));
    // Initialize ignore flag state
    let ignore_next_clipboard: IgnoreNextClipboard = Arc::new(Mutex::new(false));

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_clipboard_manager::init())
        .manage(clipboard_history)
        .manage(ignore_next_clipboard)
        .invoke_handler(tauri::generate_handler![
            get_clipboard_text,
            get_clipboard_history,
            add_to_history,
            start_clipboard_monitoring,
            copy_to_clipboard,
            clear_clipboard_history
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
