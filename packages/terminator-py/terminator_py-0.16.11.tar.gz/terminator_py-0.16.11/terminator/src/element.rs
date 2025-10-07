use crate::errors::AutomationError;
use crate::selector::Selector;
use crate::ScreenshotResult;
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use std::collections::HashMap;
use std::fmt;
use std::fmt::Debug;
use tracing::{debug, info, instrument, warn};

use super::{ClickResult, Locator};

/// Response structure for exploration result
#[derive(Debug, Default)]
pub struct ExploredElementDetail {
    pub role: String,
    pub name: Option<String>, // Use 'name' consistently for the primary label/text
    pub id: Option<String>,
    pub bounds: Option<(f64, f64, f64, f64)>, // Include bounds for spatial context
    pub value: Option<String>,
    pub description: Option<String>,
    pub text: Option<String>,
    pub parent_id: Option<String>,
    pub children_ids: Vec<String>,
    pub suggested_selector: String,
}

impl ExploredElementDetail {
    /// Create a new ExploredElementDetail from a UIElement
    pub fn from_element(
        element: &UIElement,
        parent_id: Option<String>,
    ) -> Result<Self, AutomationError> {
        let id = element.id_or_empty();
        Ok(Self {
            role: element.role(),
            name: element.name(),
            id: if id.is_empty() {
                None
            } else {
                Some(id.clone())
            },
            bounds: element.bounds().ok(),
            value: element.attributes().value,
            description: element.attributes().description,
            text: element.text(1).ok(),
            parent_id,
            children_ids: Vec::new(),
            suggested_selector: format!("#{id}"),
        })
    }
}

/// Response structure for exploration result
#[derive(Debug)]
pub struct ExploreResponse {
    pub parent: UIElement,                    // The parent element explored
    pub children: Vec<ExploredElementDetail>, // List of direct children details
}

/// Represents a UI element in a desktop application
#[derive(Debug)]
pub struct UIElement {
    inner: Box<dyn UIElementImpl>,
}

/// Serializable version of UIElement for JSON storage and transmission
///
/// This struct contains the same data as UIElement but can be both serialized
/// and deserialized. It's useful for storing UI element data in files, databases,
/// or sending over network connections.
///
/// Note: This struct only contains the element's properties and cannot perform
/// any UI automation actions. To interact with UI elements, you need a live UIElement.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SerializableUIElement {
    #[serde(skip_serializing_if = "is_empty_string")]
    pub id: Option<String>,
    #[serde(skip_serializing_if = "String::is_empty")]
    pub role: String,
    #[serde(skip_serializing_if = "is_empty_string")]
    pub name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bounds: Option<(f64, f64, f64, f64)>,
    #[serde(skip_serializing_if = "is_empty_string")]
    pub value: Option<String>,
    #[serde(skip_serializing_if = "is_empty_string")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "is_empty_string")]
    pub application: Option<String>,
    #[serde(skip_serializing_if = "is_empty_string")]
    pub window_title: Option<String>,
    #[serde(skip_serializing_if = "is_empty_string")]
    pub url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub process_id: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub children: Option<Vec<SerializableUIElement>>,

    // Additional fields for better LLM understanding of UI state
    #[serde(skip_serializing_if = "is_empty_string")]
    pub label: Option<String>,
    #[serde(skip_serializing_if = "is_empty_string")]
    pub text: Option<String>,
    #[serde(skip_serializing_if = "is_false_bool")]
    pub is_keyboard_focusable: Option<bool>,
    #[serde(skip_serializing_if = "is_false_bool")]
    pub is_focused: Option<bool>,
    #[serde(skip_serializing_if = "is_false_bool")]
    pub is_toggled: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub enabled: Option<bool>,
    #[serde(skip_serializing_if = "is_false_bool")]
    pub is_selected: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub child_count: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub index_in_parent: Option<usize>,
}

impl From<&UIElement> for SerializableUIElement {
    fn from(element: &UIElement) -> Self {
        let attrs = element.attributes();
        let bounds = element.bounds().ok();

        Self {
            id: element.id(),
            role: element.role(),
            name: attrs.name,
            bounds,
            value: attrs.value,
            description: attrs.description,
            application: Some(element.application_name()),
            window_title: Some(element.window_title()),
            url: element.url(),
            process_id: element.process_id().ok(),
            children: None,

            // Additional fields for better LLM understanding of UI state
            label: attrs.label,
            text: attrs.text,
            is_keyboard_focusable: attrs.is_keyboard_focusable,
            is_focused: attrs.is_focused,
            is_toggled: attrs.is_toggled,
            enabled: attrs.enabled,
            is_selected: attrs.is_selected,
            child_count: attrs.child_count,
            index_in_parent: attrs.index_in_parent,
        }
    }
}

impl SerializableUIElement {
    /// Create a new SerializableUIElement with minimal data
    pub fn new(role: String) -> Self {
        Self {
            id: None,
            role,
            name: None,
            bounds: None,
            value: None,
            description: None,
            application: None,
            window_title: None,
            url: None,
            process_id: None,
            children: None,

            // Additional fields for better LLM understanding of UI state
            label: None,
            text: None,
            is_keyboard_focusable: None,
            is_focused: None,
            is_toggled: None,
            enabled: None,
            is_selected: None,
            child_count: None,
            index_in_parent: None,
        }
    }

    /// Convert to JSON string
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(self)
    }

    /// Create from JSON string
    pub fn from_json(json: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(json)
    }

    /// Get a display name for this element
    pub fn display_name(&self) -> String {
        self.name
            .clone()
            .or_else(|| self.value.clone())
            .unwrap_or_else(|| self.role.clone())
    }
}

/// Helper functions for clean serialization
fn is_empty_string(opt: &Option<String>) -> bool {
    match opt {
        Some(s) => s.is_empty(),
        None => true,
    }
}

fn is_false_bool(opt: &Option<bool>) -> bool {
    matches!(opt, Some(false) | None)
}

fn is_empty_properties(props: &HashMap<String, Option<serde_json::Value>>) -> bool {
    props.is_empty() || props.values().all(|v| v.is_none())
}

/// Attributes associated with a UI element
#[derive(Clone, Serialize, Deserialize, Default)]
pub struct UIElementAttributes {
    #[serde(default, skip_serializing_if = "String::is_empty")]
    pub role: String,
    #[serde(default, skip_serializing_if = "is_empty_string")]
    pub name: Option<String>,
    #[serde(default, skip_serializing_if = "is_empty_string")]
    pub label: Option<String>,
    #[serde(default, skip_serializing_if = "is_empty_string")]
    pub text: Option<String>,
    #[serde(default, skip_serializing_if = "is_empty_string")]
    pub value: Option<String>,
    #[serde(default, skip_serializing_if = "is_empty_string")]
    pub description: Option<String>,
    #[serde(default, skip_serializing_if = "is_empty_properties")]
    pub properties: HashMap<String, Option<serde_json::Value>>,
    #[serde(default, skip_serializing_if = "is_false_bool")]
    pub is_keyboard_focusable: Option<bool>,
    #[serde(default, skip_serializing_if = "is_false_bool")]
    pub is_focused: Option<bool>,
    #[serde(default, skip_serializing_if = "is_false_bool")]
    pub is_toggled: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bounds: Option<(f64, f64, f64, f64)>, // Only populated for keyboard-focusable elements
    #[serde(skip_serializing_if = "Option::is_none")]
    pub enabled: Option<bool>,
    #[serde(default, skip_serializing_if = "is_false_bool")]
    pub is_selected: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub child_count: Option<usize>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub index_in_parent: Option<usize>,
}

impl fmt::Debug for UIElementAttributes {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let mut debug_struct = f.debug_struct("UIElementAttributes");

        // Only show non-empty role
        if !self.role.is_empty() {
            debug_struct.field("role", &self.role);
        }

        // Only show non-empty name
        if let Some(ref name) = self.name {
            if !name.is_empty() {
                debug_struct.field("name", name);
            }
        }

        // Only show non-empty label
        if let Some(ref label) = self.label {
            if !label.is_empty() {
                debug_struct.field("label", label);
            }
        }

        // Only show non-empty text
        if let Some(ref text) = self.text {
            if !text.is_empty() {
                debug_struct.field("text", text);
            }
        }

        // Only show non-empty value
        if let Some(ref value) = self.value {
            if !value.is_empty() {
                debug_struct.field("value", value);
            }
        }

        // Only show non-empty description
        if let Some(ref description) = self.description {
            if !description.is_empty() {
                debug_struct.field("description", description);
            }
        }

        // Only show non-empty properties
        if !self.properties.is_empty() && self.properties.values().any(|v| v.is_some()) {
            debug_struct.field("properties", &self.properties);
        }

        // Only show keyboard focusable if true
        if let Some(true) = self.is_keyboard_focusable {
            debug_struct.field("is_keyboard_focusable", &true);
        }

        // Only show focused if true
        if let Some(true) = self.is_focused {
            debug_struct.field("is_focused", &true);
        }

        // Only show toggled if true
        if let Some(true) = self.is_toggled {
            debug_struct.field("is_toggled", &true);
        }

        // Only show bounds if present
        if let Some(ref bounds) = self.bounds {
            debug_struct.field("bounds", bounds);
        }

        // Only show selected if true
        if let Some(true) = self.is_selected {
            debug_struct.field("is_selected", &true);
        }

        // Only show child_count if present
        if let Some(count) = self.child_count {
            debug_struct.field("child_count", &count);
        }

        // Only show index_in_parent if present
        if let Some(index) = self.index_in_parent {
            debug_struct.field("index_in_parent", &index);
        }

        debug_struct.finish()
    }
}

/// Interface for platform-specific element implementations
pub trait UIElementImpl: Send + Sync + Debug {
    fn object_id(&self) -> usize;
    fn id(&self) -> Option<String>;
    fn role(&self) -> String;
    fn attributes(&self) -> UIElementAttributes;
    fn name(&self) -> Option<String> {
        self.attributes().name
    }
    fn children(&self) -> Result<Vec<UIElement>, AutomationError>;
    fn parent(&self) -> Result<Option<UIElement>, AutomationError>;
    fn bounds(&self) -> Result<(f64, f64, f64, f64), AutomationError>; // x, y, width, height
    fn click(&self) -> Result<ClickResult, AutomationError>;
    fn double_click(&self) -> Result<ClickResult, AutomationError>;
    fn right_click(&self) -> Result<(), AutomationError>;
    fn hover(&self) -> Result<(), AutomationError>;
    fn focus(&self) -> Result<(), AutomationError>;
    fn invoke(&self) -> Result<(), AutomationError>;
    fn type_text(&self, text: &str, use_clipboard: bool) -> Result<(), AutomationError>;
    fn press_key(&self, key: &str) -> Result<(), AutomationError>;

    fn type_text_with_state(
        &self,
        text: &str,
        use_clipboard: bool,
    ) -> Result<crate::ActionResult, AutomationError> {
        // Default implementation - platforms can override for state tracking
        self.type_text(text, use_clipboard)?;
        Ok(crate::ActionResult {
            action: "type_text".to_string(),
            details: "No state tracking available".to_string(),
            data: Some(serde_json::json!({"text": text, "use_clipboard": use_clipboard})),
        })
    }

    // New methods with state tracking
    fn invoke_with_state(&self) -> Result<crate::ActionResult, AutomationError> {
        // Default implementation - platforms can override for state tracking
        self.invoke()?;
        Ok(crate::ActionResult {
            action: "invoke".to_string(),
            details: "No state tracking available".to_string(),
            data: None,
        })
    }

    fn press_key_with_state(&self, key: &str) -> Result<crate::ActionResult, AutomationError> {
        // Default implementation - platforms can override for state tracking
        self.press_key(key)?;
        Ok(crate::ActionResult {
            action: "press_key".to_string(),
            details: "No state tracking available".to_string(),
            data: Some(serde_json::json!({"key": key})),
        })
    }
    fn get_text(&self, max_depth: usize) -> Result<String, AutomationError>;
    fn set_value(&self, value: &str) -> Result<(), AutomationError>;
    fn is_enabled(&self) -> Result<bool, AutomationError>;
    fn is_visible(&self) -> Result<bool, AutomationError>;
    fn is_focused(&self) -> Result<bool, AutomationError>;
    fn perform_action(&self, action: &str) -> Result<(), AutomationError>;
    fn as_any(&self) -> &dyn std::any::Any;
    fn create_locator(&self, selector: Selector) -> Result<Locator, AutomationError>;
    fn scroll(&self, direction: &str, amount: f64) -> Result<(), AutomationError>;

    fn scroll_with_state(
        &self,
        direction: &str,
        amount: f64,
    ) -> Result<crate::ActionResult, AutomationError> {
        // Default implementation - platforms can override for state tracking
        self.scroll(direction, amount)?;
        Ok(crate::ActionResult {
            action: "scroll".to_string(),
            details: "No state tracking available".to_string(),
            data: Some(serde_json::json!({"direction": direction, "amount": amount})),
        })
    }

    // New method to activate the window containing the element
    fn activate_window(&self) -> Result<(), AutomationError>;

    // New method to minimize the window containing the element
    fn minimize_window(&self) -> Result<(), AutomationError>;

    // New method to maximize the window containing the element
    fn maximize_window(&self) -> Result<(), AutomationError>;

    // Add a method to clone the box
    fn clone_box(&self) -> Box<dyn UIElementImpl>;

    // New method for keyboard focusable
    fn is_keyboard_focusable(&self) -> Result<bool, AutomationError>;

    // New method for mouse drag
    fn mouse_drag(
        &self,
        start_x: f64,
        start_y: f64,
        end_x: f64,
        end_y: f64,
    ) -> Result<(), AutomationError>;

    // New methods for mouse control
    fn mouse_click_and_hold(&self, x: f64, y: f64) -> Result<(), AutomationError>;
    fn mouse_move(&self, x: f64, y: f64) -> Result<(), AutomationError>;
    fn mouse_release(&self) -> Result<(), AutomationError>;

    // New methods to get containing application and window
    fn application(&self) -> Result<Option<UIElement>, AutomationError>;
    fn window(&self) -> Result<Option<UIElement>, AutomationError>;

    // New method to highlight the element with optional text overlay
    fn highlight(
        &self,
        color: Option<u32>,
        duration: Option<std::time::Duration>,
        text: Option<&str>,
        text_position: Option<crate::TextPosition>,
        font_style: Option<crate::FontStyle>,
    ) -> Result<crate::HighlightHandle, AutomationError>;

    /// Sets the transparency of the window.
    /// The percentage value ranges from 0 (completely transparent) to 100 (completely opaque).
    fn set_transparency(&self, percentage: u8) -> Result<(), AutomationError>;

    // New method to get the process ID of the element
    fn process_id(&self) -> Result<u32, AutomationError>;

    // New method to capture a screenshot of the element
    fn capture(&self) -> Result<ScreenshotResult, AutomationError>;

    /// Close the element if it's closable (like windows, applications)
    /// Does nothing for non-closable elements (like buttons, text, etc.)
    fn close(&self) -> Result<(), AutomationError>;

    // New method to get the URL if the element is in a browser window
    fn url(&self) -> Option<String>;

    // New high-level input functions
    fn select_option(&self, option_name: &str) -> Result<(), AutomationError>;
    fn list_options(&self) -> Result<Vec<String>, AutomationError>;

    fn select_option_with_state(
        &self,
        option_name: &str,
    ) -> Result<crate::ActionResult, AutomationError> {
        // Default implementation - platforms can override for state tracking
        self.select_option(option_name)?;
        Ok(crate::ActionResult {
            action: "select_option".to_string(),
            details: "No state tracking available".to_string(),
            data: Some(serde_json::json!({"option_selected": option_name})),
        })
    }
    fn is_toggled(&self) -> Result<bool, AutomationError>;
    fn set_toggled(&self, state: bool) -> Result<(), AutomationError>;

    fn set_toggled_with_state(&self, state: bool) -> Result<crate::ActionResult, AutomationError> {
        // Default implementation - platforms can override for state tracking
        self.set_toggled(state)?;
        Ok(crate::ActionResult {
            action: "set_toggled".to_string(),
            details: "No state tracking available".to_string(),
            data: Some(serde_json::json!({"state": state})),
        })
    }
    fn get_range_value(&self) -> Result<f64, AutomationError>;
    fn set_range_value(&self, value: f64) -> Result<(), AutomationError>;
    fn is_selected(&self) -> Result<bool, AutomationError>;
    fn set_selected(&self, state: bool) -> Result<(), AutomationError>;

    fn set_selected_with_state(&self, state: bool) -> Result<crate::ActionResult, AutomationError> {
        // Default implementation - platforms can override for state tracking
        self.set_selected(state)?;
        Ok(crate::ActionResult {
            action: "set_selected".to_string(),
            details: "No state tracking available".to_string(),
            data: Some(serde_json::json!({"state": state})),
        })
    }

    /// Returns the `Monitor` object that contains this element.
    ///
    /// By default this implementation uses the element's bounding box and
    /// the `xcap` crate to locate the monitor that contains the element's
    /// top-left corner. Individual platforms can override this for a more
    /// accurate or cheaper implementation.
    fn monitor(&self) -> Result<crate::Monitor, AutomationError> {
        // 1. Get element bounds (x, y) with better error handling
        let (x, y, _w, _h) = match self.bounds() {
            Ok(bounds) => bounds,
            Err(e) => {
                // If we can't get bounds, fall back to primary monitor
                warn!("Failed to get element bounds for monitor detection: {}", e);
                return self.get_primary_monitor_fallback();
            }
        };

        // 2. Enumerate available monitors using xcap (already a dependency)
        let monitors = xcap::Monitor::all().map_err(|e| {
            AutomationError::PlatformError(format!("Failed to enumerate monitors: {e}"))
        })?;

        // 3. Find the first monitor whose geometry contains the element's
        //    upper-left corner.
        for (idx, mon) in monitors.iter().enumerate() {
            // Guard every call because each accessor returns Result<_>
            let mon_x = mon.x().map_err(|e| {
                AutomationError::PlatformError(format!("Failed to get monitor x: {e}"))
            })?;
            let mon_y = mon.y().map_err(|e| {
                AutomationError::PlatformError(format!("Failed to get monitor y: {e}"))
            })?;
            let mon_w = mon.width().map_err(|e| {
                AutomationError::PlatformError(format!("Failed to get monitor width: {e}"))
            })? as i32;
            let mon_h = mon.height().map_err(|e| {
                AutomationError::PlatformError(format!("Failed to get monitor height: {e}"))
            })? as i32;

            // Simple contains check (include edges)
            let within_x = (x as i32) >= mon_x && (x as i32) < mon_x + mon_w;
            let within_y = (y as i32) >= mon_y && (y as i32) < mon_y + mon_h;

            if within_x && within_y {
                // Build our internal Monitor struct from the xcap monitor
                let name = mon.name().map_err(|e| {
                    AutomationError::PlatformError(format!("Failed to get monitor name: {e}"))
                })?;
                let is_primary = mon.is_primary().map_err(|e| {
                    AutomationError::PlatformError(format!(
                        "Failed to get monitor primary flag: {e}"
                    ))
                })?;
                let scale_factor = mon.scale_factor().map_err(|e| {
                    AutomationError::PlatformError(format!(
                        "Failed to get monitor scale factor: {e}"
                    ))
                })? as f64;

                // Get work area for this monitor if it's Windows and primary
                #[cfg(target_os = "windows")]
                let work_area = if is_primary {
                    use crate::platforms::windows::element::WorkArea;
                    if let Ok(work_area) = WorkArea::get_primary() {
                        Some(crate::WorkAreaBounds {
                            x: work_area.x,
                            y: work_area.y,
                            width: work_area.width as u32,
                            height: work_area.height as u32,
                        })
                    } else {
                        None
                    }
                } else {
                    Some(crate::WorkAreaBounds {
                        x: mon_x,
                        y: mon_y,
                        width: mon_w as u32,
                        height: mon_h as u32,
                    })
                };

                #[cfg(not(target_os = "windows"))]
                let work_area = Some(crate::WorkAreaBounds {
                    x: mon_x,
                    y: mon_y,
                    width: mon_w as u32,
                    height: mon_h as u32,
                });

                return Ok(crate::Monitor {
                    id: format!("monitor_{idx}"),
                    name,
                    is_primary,
                    width: mon_w as u32,
                    height: mon_h as u32,
                    x: mon_x,
                    y: mon_y,
                    scale_factor,
                    work_area,
                });
            }
        }

        // If no monitor found containing the element, fall back to primary
        warn!(
            "Element coordinates ({}, {}) not found on any monitor, falling back to primary",
            x, y
        );
        self.get_primary_monitor_fallback()
    }

    /// Helper method to get primary monitor as fallback
    fn get_primary_monitor_fallback(&self) -> Result<crate::Monitor, AutomationError> {
        let monitors = xcap::Monitor::all().map_err(|e| {
            AutomationError::PlatformError(format!("Failed to enumerate monitors: {e}"))
        })?;

        for (idx, monitor) in monitors.iter().enumerate() {
            let is_primary = monitor.is_primary().map_err(|e| {
                AutomationError::PlatformError(format!("Failed to check primary status: {e}"))
            })?;

            if is_primary {
                let name = monitor.name().map_err(|e| {
                    AutomationError::PlatformError(format!("Failed to get monitor name: {e}"))
                })?;
                let width = monitor.width().map_err(|e| {
                    AutomationError::PlatformError(format!("Failed to get monitor width: {e}"))
                })?;
                let height = monitor.height().map_err(|e| {
                    AutomationError::PlatformError(format!("Failed to get monitor height: {e}"))
                })?;
                let x = monitor.x().map_err(|e| {
                    AutomationError::PlatformError(format!("Failed to get monitor x: {e}"))
                })?;
                let y = monitor.y().map_err(|e| {
                    AutomationError::PlatformError(format!("Failed to get monitor y: {e}"))
                })?;
                let scale_factor = monitor.scale_factor().map_err(|e| {
                    AutomationError::PlatformError(format!(
                        "Failed to get monitor scale factor: {e}"
                    ))
                })? as f64;

                // Get work area for primary monitor (Windows only)
                #[cfg(target_os = "windows")]
                let work_area = {
                    use crate::platforms::windows::element::WorkArea;
                    if let Ok(work_area) = WorkArea::get_primary() {
                        Some(crate::WorkAreaBounds {
                            x: work_area.x,
                            y: work_area.y,
                            width: work_area.width as u32,
                            height: work_area.height as u32,
                        })
                    } else {
                        None
                    }
                };

                #[cfg(not(target_os = "windows"))]
                let work_area = Some(crate::WorkAreaBounds {
                    x,
                    y,
                    width,
                    height,
                });

                return Ok(crate::Monitor {
                    id: format!("monitor_{idx}"),
                    name,
                    is_primary,
                    width,
                    height,
                    x,
                    y,
                    scale_factor,
                    work_area,
                });
            }
        }

        Err(AutomationError::PlatformError(
            "No primary monitor found".to_string(),
        ))
    }
}

impl UIElement {
    /// Create a new UI element from a platform-specific implementation
    pub fn new(impl_: Box<dyn UIElementImpl>) -> Self {
        Self { inner: impl_ }
    }

    /// Get the element's ID
    #[instrument(level = "debug", skip(self))]
    pub fn id(&self) -> Option<String> {
        self.inner.id()
    }

    /// Get the element's role (e.g., "button", "textfield")
    pub fn role(&self) -> String {
        self.inner.role()
    }

    /// Get all attributes of the element
    pub fn attributes(&self) -> UIElementAttributes {
        self.inner.attributes()
    }

    /// Get child elements
    pub fn children(&self) -> Result<Vec<UIElement>, AutomationError> {
        self.inner.children()
    }

    /// Get parent element
    pub fn parent(&self) -> Result<Option<UIElement>, AutomationError> {
        self.inner.parent()
    }

    /// Get element bounds (x, y, width, height)
    pub fn bounds(&self) -> Result<(f64, f64, f64, f64), AutomationError> {
        self.inner.bounds()
    }

    /// Click on this element
    #[instrument(level = "debug", skip(self))]
    pub fn click(&self) -> Result<ClickResult, AutomationError> {
        self.inner.click()
    }

    /// Double-click on this element
    #[instrument(level = "debug", skip(self))]
    pub fn double_click(&self) -> Result<ClickResult, AutomationError> {
        self.inner.double_click()
    }

    /// Right-click on this element
    #[instrument(level = "debug", skip(self))]
    pub fn right_click(&self) -> Result<(), AutomationError> {
        self.inner.right_click()
    }

    /// Hover over this element
    pub fn hover(&self) -> Result<(), AutomationError> {
        self.inner.hover()
    }

    /// Focus this element
    pub fn focus(&self) -> Result<(), AutomationError> {
        self.inner.focus()
    }

    /// Invoke this element
    #[instrument(level = "debug", skip(self))]
    pub fn invoke(&self) -> Result<(), AutomationError> {
        self.inner.invoke()
    }

    /// Invoke this element with state tracking
    #[instrument(level = "debug", skip(self))]
    pub fn invoke_with_state(&self) -> Result<crate::ActionResult, AutomationError> {
        self.inner.invoke_with_state()
    }

    /// Type text into this element
    pub fn type_text(&self, text: &str, use_clipboard: bool) -> Result<(), AutomationError> {
        self.inner.type_text(text, use_clipboard)
    }

    /// Type text with state tracking
    #[instrument(level = "debug", skip(self))]
    pub fn type_text_with_state(
        &self,
        text: &str,
        use_clipboard: bool,
    ) -> Result<crate::ActionResult, AutomationError> {
        self.inner.type_text_with_state(text, use_clipboard)
    }

    /// Press a key while this element is focused
    pub fn press_key(&self, key: &str) -> Result<(), AutomationError> {
        self.inner.press_key(key)
    }

    /// Press a key with state tracking
    #[instrument(level = "debug", skip(self))]
    pub fn press_key_with_state(&self, key: &str) -> Result<crate::ActionResult, AutomationError> {
        self.inner.press_key_with_state(key)
    }

    /// Get text content of this element
    pub fn text(&self, max_depth: usize) -> Result<String, AutomationError> {
        self.inner.get_text(max_depth)
    }

    /// Set value of this element
    pub fn set_value(&self, value: &str) -> Result<(), AutomationError> {
        self.inner.set_value(value)
    }

    /// Check if element is enabled
    #[instrument(level = "debug", skip(self))]
    pub fn is_enabled(&self) -> Result<bool, AutomationError> {
        self.inner.is_enabled()
    }

    /// Check if element is visible
    pub fn is_visible(&self) -> Result<bool, AutomationError> {
        self.inner.is_visible()
    }

    /// Check if element is focused
    pub fn is_focused(&self) -> Result<bool, AutomationError> {
        self.inner.is_focused()
    }

    /// Perform a named action on this element
    pub fn perform_action(&self, action: &str) -> Result<(), AutomationError> {
        self.inner.perform_action(action)
    }

    /// Get the underlying implementation as a specific type
    pub(crate) fn as_any(&self) -> &dyn std::any::Any {
        self.inner.as_any()
    }

    /// Find elements matching the selector within this element
    pub fn locator(&self, selector: impl Into<Selector>) -> Result<Locator, AutomationError> {
        let selector = selector.into();
        self.inner.create_locator(selector)
    }

    /// Scroll the element in a given direction
    pub fn scroll(&self, direction: &str, amount: f64) -> Result<(), AutomationError> {
        self.inner.scroll(direction, amount)
    }

    /// Scroll with state tracking
    #[instrument(level = "debug", skip(self))]
    pub fn scroll_with_state(
        &self,
        direction: &str,
        amount: f64,
    ) -> Result<crate::ActionResult, AutomationError> {
        self.inner.scroll_with_state(direction, amount)
    }

    /// Activate the window containing this element (bring to foreground)
    pub fn activate_window(&self) -> Result<(), AutomationError> {
        self.inner.activate_window()
    }

    pub fn minimize_window(&self) -> Result<(), AutomationError> {
        self.inner.minimize_window()
    }

    pub fn maximize_window(&self) -> Result<(), AutomationError> {
        self.inner.maximize_window()
    }

    /// Get the element's name
    #[instrument(level = "debug", skip(self))]
    pub fn name(&self) -> Option<String> {
        self.inner.name()
    }

    /// Check if element is keyboard focusable
    pub fn is_keyboard_focusable(&self) -> Result<bool, AutomationError> {
        self.inner.is_keyboard_focusable()
    }

    /// Drag mouse from start to end coordinates
    pub fn mouse_drag(
        &self,
        start_x: f64,
        start_y: f64,
        end_x: f64,
        end_y: f64,
    ) -> Result<(), AutomationError> {
        self.inner.mouse_drag(start_x, start_y, end_x, end_y)
    }

    /// Press and hold mouse at (x, y)
    pub fn mouse_click_and_hold(&self, x: f64, y: f64) -> Result<(), AutomationError> {
        self.inner.mouse_click_and_hold(x, y)
    }

    /// Move mouse to (x, y)
    pub fn mouse_move(&self, x: f64, y: f64) -> Result<(), AutomationError> {
        self.inner.mouse_move(x, y)
    }

    /// Release mouse button
    pub fn mouse_release(&self) -> Result<(), AutomationError> {
        self.inner.mouse_release()
    }

    /// Get the containing application element
    pub fn application(&self) -> Result<Option<UIElement>, AutomationError> {
        self.inner.application()
    }

    /// Get the containing window element (e.g., tab, dialog)
    pub fn window(&self) -> Result<Option<UIElement>, AutomationError> {
        self.inner.window()
    }

    /// Highlights the element with a colored border and optional text overlay.
    ///
    /// # Arguments
    /// * `color` - Optional BGR color code (32-bit integer). Default: 0x0000FF (red)
    /// * `duration` - Optional duration for the highlight.
    /// * `text` - Optional text to display as overlay. Text will be truncated to 30 characters.
    /// * `text_position` - Optional position for the text overlay (Top, Bottom, etc.)
    /// * `font_style` - Optional font styling (size, bold, color)
    #[cfg(target_os = "windows")]
    pub fn highlight(
        &self,
        color: Option<u32>,
        duration: Option<std::time::Duration>,
        text: Option<&str>,
        text_position: Option<crate::TextPosition>,
        font_style: Option<crate::FontStyle>,
    ) -> Result<crate::HighlightHandle, AutomationError> {
        self.inner
            .highlight(color, duration, text, text_position, font_style)
    }

    /// Highlights the element with a colored border (simplified version for non-Windows platforms).
    ///
    /// # Arguments
    /// * `color` - Optional BGR color code (32-bit integer). Default: 0x0000FF (red)
    /// * `duration` - Optional duration for the highlight.
    #[cfg(not(target_os = "windows"))]
    pub fn highlight(
        &self,
        color: Option<u32>,
        duration: Option<std::time::Duration>,
        _text: Option<&str>,
        _text_position: Option<crate::TextPosition>,
        _font_style: Option<crate::FontStyle>,
    ) -> Result<crate::HighlightHandle, AutomationError> {
        // For non-Windows platforms, ignore text parameters and create dummy handle
        self.inner.highlight(color, duration, None, None, None)
    }

    /// Capture a screenshot of the element
    pub fn capture(&self) -> Result<ScreenshotResult, AutomationError> {
        self.inner.capture()
    }

    /// Capture a screenshot of the element and perform OCR to extract text
    ///
    /// # Returns
    /// * `Ok(String)` - The extracted text from the element screenshot
    /// * `Err(AutomationError)` - If screenshot capture or OCR fails
    ///
    /// # Examples
    /// ```rust
    /// use terminator::Desktop;
    ///
    /// # async fn example() -> Result<(), terminator::AutomationError> {
    /// let desktop = Desktop::new(false, false)?;
    /// let element = desktop.locator("role:Button").first(None).await?;
    /// let text = element.ocr().await?;
    /// println!("Button text: {}", text);
    /// # Ok(())
    /// # }
    /// ```
    pub async fn ocr(&self) -> Result<String, AutomationError> {
        // First capture the element screenshot
        let screenshot = self.capture()?;

        // Convert the screenshot to a DynamicImage
        let img_buffer = image::ImageBuffer::from_raw(
            screenshot.width,
            screenshot.height,
            screenshot.image_data,
        )
        .ok_or_else(|| {
            AutomationError::PlatformError(
                "Failed to create image buffer from screenshot data".to_string(),
            )
        })?;

        let dynamic_image = image::DynamicImage::ImageRgba8(img_buffer);

        // Perform OCR using uni_ocr directly
        let engine = uni_ocr::OcrEngine::new(uni_ocr::OcrProvider::Auto).map_err(|e| {
            AutomationError::PlatformError(format!("Failed to create OCR engine: {e}"))
        })?;

        let (text, _language, _confidence) = engine
            .recognize_image(&dynamic_image)
            .await
            .map_err(|e| AutomationError::PlatformError(format!("OCR recognition failed: {e}")))?;

        Ok(text)
    }

    /// Close the element if it's closable (like windows, applications)
    /// Does nothing for non-closable elements (like buttons, text, etc.)
    pub fn close(&self) -> Result<(), AutomationError> {
        self.inner.close()
    }

    /// Get the URL if the element is in a browser window
    pub fn url(&self) -> Option<String> {
        self.inner.url()
    }

    /// Selects an option in a dropdown or combobox by its visible text.
    pub fn select_option(&self, option_name: &str) -> Result<(), AutomationError> {
        self.inner.select_option(option_name)
    }

    /// Selects an option with state tracking
    #[instrument(level = "debug", skip(self))]
    pub fn select_option_with_state(
        &self,
        option_name: &str,
    ) -> Result<crate::ActionResult, AutomationError> {
        self.inner.select_option_with_state(option_name)
    }

    /// Lists all available option strings from a dropdown or list box.
    pub fn list_options(&self) -> Result<Vec<String>, AutomationError> {
        self.inner.list_options()
    }

    /// Checks if a control (like a checkbox or toggle switch) is currently toggled on.
    pub fn is_toggled(&self) -> Result<bool, AutomationError> {
        self.inner.is_toggled()
    }

    /// Sets the state of a toggleable control.
    /// It only performs an action if the control is not already in the desired state.
    pub fn set_toggled(&self, state: bool) -> Result<(), AutomationError> {
        self.inner.set_toggled(state)
    }

    /// Set toggle state with state tracking
    #[instrument(level = "debug", skip(self))]
    pub fn set_toggled_with_state(
        &self,
        state: bool,
    ) -> Result<crate::ActionResult, AutomationError> {
        self.inner.set_toggled_with_state(state)
    }

    /// Gets the current value from a range-based control like a slider or progress bar.
    pub fn get_range_value(&self) -> Result<f64, AutomationError> {
        self.inner.get_range_value()
    }

    /// Sets the value of a range-based control like a slider.
    pub fn set_range_value(&self, value: f64) -> Result<(), AutomationError> {
        self.inner.set_range_value(value)
    }

    /// Checks if a selectable item (e.g., in a calendar, list, or tab) is currently selected.
    pub fn is_selected(&self) -> Result<bool, AutomationError> {
        self.inner.is_selected()
    }

    /// Sets the selection state of a selectable item.
    pub fn set_selected(&self, state: bool) -> Result<(), AutomationError> {
        self.inner.set_selected(state)
    }

    /// Set selection state with state tracking
    #[instrument(level = "debug", skip(self))]
    pub fn set_selected_with_state(
        &self,
        state: bool,
    ) -> Result<crate::ActionResult, AutomationError> {
        self.inner.set_selected_with_state(state)
    }

    /// Return the `Monitor` that contains this UI element.
    ///
    /// This is useful when you need to perform monitor-specific operations
    /// (e.g. capturing the screen area around the element).
    pub fn monitor(&self) -> Result<crate::Monitor, AutomationError> {
        self.inner.monitor()
    }

    // Convenience methods to reduce verbosity with optional properties

    /// Scrolls until the element is visible within its window viewport.
    ///
    /// Strategy:
    /// - If already visible, returns immediately.
    /// - Otherwise, estimates direction based on the element vs window bounds and
    ///   issues small scroll steps using the existing `scroll` implementation
    ///   (which finds a scrollable ancestor and uses UIScrollPattern or key fallbacks).
    /// - Re-checks visibility and bounds after each step and stops when visible
    ///   or when the maximum number of steps is reached.
    pub fn scroll_into_view(&self) -> Result<(), AutomationError> {
        // Configuration tuned for reliability without over-scrolling
        const MAX_STEPS: usize = 24; // up to ~24 directional adjustments
        const STEP_AMOUNT: f64 = 0.5; // Reduced from 1.0 to avoid over-scrolling - uses smaller increments

        // Helper: check whether element intersects window bounds (best-effort viewport proxy)
        fn intersects(a: (f64, f64, f64, f64), b: (f64, f64, f64, f64)) -> bool {
            let (ax, ay, aw, ah) = a;
            let (bx, by, bw, bh) = b;
            let a_right = ax + aw;
            let a_bottom = ay + ah;
            let b_right = bx + bw;
            let b_bottom = by + bh;
            ax < b_right && a_right > bx && ay < b_bottom && a_bottom > by
        }

        // Helper: check if element is within work area (excluding taskbar)
        #[cfg(target_os = "windows")]
        fn is_in_work_area(elem_bounds: (f64, f64, f64, f64)) -> bool {
            use crate::platforms::windows::element::WorkArea;
            if let Ok(work_area) = WorkArea::get_primary() {
                let (x, y, width, height) = elem_bounds;
                work_area.intersects(x, y, width, height)
            } else {
                true // If we can't get work area, assume it's visible
            }
        }

        #[cfg(not(target_os = "windows"))]
        fn is_in_work_area(_elem_bounds: (f64, f64, f64, f64)) -> bool {
            true // On non-Windows platforms, no taskbar adjustment needed
        }

        // Initial snapshot for diagnostics
        let init_visible = self.is_visible().unwrap_or(false);
        let init_bounds = self.bounds().ok();
        let window_bounds = self.window().ok().flatten().and_then(|w| w.bounds().ok());

        debug!(
            "scroll_into_view:start visible={:?} elem_bounds={:?} window_bounds={:?}",
            init_visible, init_bounds, window_bounds
        );

        // Fast path
        if init_visible {
            return Ok(());
        }

        // Iteratively adjust
        let mut steps_taken: usize = 0;
        loop {
            // Refresh visibility and geometry each iteration
            let visible = self.is_visible().unwrap_or(false);
            let elem_bounds = match self.bounds() {
                Ok(b) => b,
                Err(e) => {
                    warn!("scroll_into_view:failed_to_get_bounds error={}", e);
                    return Err(e);
                }
            };

            // If visible and, when available, intersecting the window area AND within work area, we are done
            if visible {
                // Also check if element is within work area (not behind taskbar)
                let in_work_area = is_in_work_area(elem_bounds);

                if let Some(wb) = window_bounds {
                    if intersects(elem_bounds, wb) && in_work_area {
                        info!(
                            "scroll_into_view:done steps_taken={} final_bounds={:?}",
                            steps_taken, elem_bounds
                        );
                        return Ok(());
                    }
                } else if in_work_area {
                    info!(
                        "scroll_into_view:done (no window bounds) steps_taken={} final_bounds={:?}",
                        steps_taken, elem_bounds
                    );
                    return Ok(());
                }
            }

            // Determine scroll directions based on position relative to window bounds and work area
            let mut vertical_dir: Option<&'static str> = None;
            let mut horizontal_dir: Option<&'static str> = None;

            // Check if element is behind taskbar (Windows only)
            #[cfg(target_os = "windows")]
            {
                use crate::platforms::windows::element::WorkArea;
                if let Ok(work_area) = WorkArea::get_primary() {
                    let (_ex, ey, _ew, eh) = elem_bounds;
                    let work_bottom = (work_area.y + work_area.height) as f64;

                    // If element is below work area (behind taskbar), scroll down
                    if ey + eh > work_bottom {
                        vertical_dir = Some("down");
                    }
                }
            }

            // Standard scroll direction logic based on window bounds
            if vertical_dir.is_none() {
                if let Some((wx, wy, ww, wh)) = window_bounds {
                    let (ex, ey, ew, eh) = elem_bounds;
                    // Vertical
                    if ey + eh <= wy {
                        // Element is above the viewport -> scroll up
                        vertical_dir = Some("up");
                    } else if ey >= wy + wh {
                        // Element is below the viewport -> scroll down
                        vertical_dir = Some("down");
                    }
                    // Horizontal (best effort)
                    if ex + ew <= wx {
                        horizontal_dir = Some("left");
                    } else if ex >= wx + ww {
                        horizontal_dir = Some("right");
                    }
                } else {
                    // Without window bounds, attempt a sensible default sequence
                    // Try down first (common case), then up; we alternate if no progress.
                    vertical_dir = Some(if steps_taken % 2 == 0 { "down" } else { "up" });
                }
            }

            // Perform one vertical step if needed
            if let Some(dir) = vertical_dir {
                debug!(
                    "scroll_into_view:vertical_step dir={} step={} amount={}",
                    dir,
                    steps_taken + 1,
                    STEP_AMOUNT
                );
                // Ignore individual step errors and continue to try alternate axes
                let _ = self.scroll(dir, STEP_AMOUNT);
                steps_taken += 1;
            }

            // Perform one horizontal step if needed (after vertical)
            if let Some(dir) = horizontal_dir {
                debug!(
                    "scroll_into_view:horizontal_step dir={} step={} amount={}",
                    dir,
                    steps_taken + 1,
                    STEP_AMOUNT
                );
                let _ = self.scroll(dir, STEP_AMOUNT);
                steps_taken += 1;
            }

            // Safety cap
            if steps_taken >= MAX_STEPS {
                return Err(AutomationError::Timeout(format!(
                    "scroll_into_view: exceeded max steps ({MAX_STEPS}). elem_bounds={elem_bounds:?} window_bounds={window_bounds:?}"
                )));
            }

            // Small delay to allow the UI to update between scrolls
            std::thread::sleep(std::time::Duration::from_millis(60));
        }
    }

    /// Get element ID or empty string if not available
    pub fn id_or_empty(&self) -> String {
        self.id().unwrap_or_default()
    }

    /// Get element name or empty string if not available  
    pub fn name_or_empty(&self) -> String {
        self.name().unwrap_or_default()
    }

    /// Get element name or fallback string if not available
    pub fn name_or(&self, fallback: &str) -> String {
        self.name().unwrap_or_else(|| fallback.to_string())
    }

    /// Get element value or empty string if not available
    pub fn value_or_empty(&self) -> String {
        self.attributes().value.unwrap_or_default()
    }

    /// Get element description or empty string if not available
    pub fn description_or_empty(&self) -> String {
        self.attributes().description.unwrap_or_default()
    }

    /// Get application name safely
    pub fn application_name(&self) -> String {
        self.application()
            .ok()
            .flatten()
            .and_then(|app| app.name())
            .unwrap_or_default()
    }

    /// Get window title safely
    pub fn window_title(&self) -> String {
        match self.window() {
            Ok(Some(window)) => window.name_or_empty(),
            _ => String::new(),
        }
    }

    /// Convert this UIElement to a SerializableUIElement
    ///
    /// This creates a snapshot of the element's current state that can be
    /// serialized to JSON, stored in files, or transmitted over networks.
    pub fn to_serializable(&self) -> SerializableUIElement {
        SerializableUIElement::from(self)
    }

    /// Sets the transparency of the window.
    /// The percentage value ranges from 0 (completely transparent) to 100 (completely opaque).
    pub fn set_transparency(&self, percentage: u8) -> Result<(), AutomationError> {
        self.inner.set_transparency(percentage)
    }

    /// Get the process ID of the application containing this element
    pub fn process_id(&self) -> Result<u32, AutomationError> {
        self.inner.process_id()
    }

    /// Recursively build a SerializableUIElement tree from this element.
    ///
    /// # Arguments
    /// * `max_depth` - Maximum depth to traverse (inclusive). Use a reasonable limit to avoid huge trees.
    ///
    /// # Example
    /// ```no_run
    /// # use terminator::Desktop;
    /// # async fn example() -> Result<(), Box<dyn std::error::Error>> {
    /// let desktop = Desktop::new(false, false)?;
    /// let element = desktop.locator("name:Calculator").first(None).await?;
    /// let tree = element.to_serializable_tree(5);
    /// println!("{}", serde_json::to_string_pretty(&tree).unwrap());
    /// # Ok(())
    /// # }
    /// ```
    pub fn to_serializable_tree(&self, max_depth: usize) -> SerializableUIElement {
        fn build(element: &UIElement, depth: usize, max_depth: usize) -> SerializableUIElement {
            let mut serializable = element.to_serializable();

            // For child elements (depth > 0), remove redundant window/app info.
            // This information is only needed at the root of the tree.
            if depth > 0 {
                serializable.application = None;
                serializable.window_title = None;
                serializable.process_id = None;
                serializable.url = None;
            }

            let children = if depth < max_depth {
                match element.children() {
                    Ok(children) => {
                        let v: Vec<SerializableUIElement> = children
                            .iter()
                            .map(|child| build(child, depth + 1, max_depth))
                            .collect();
                        if v.is_empty() {
                            None
                        } else {
                            Some(v)
                        }
                    }
                    Err(_) => None,
                }
            } else {
                None
            };
            serializable.children = children;
            serializable
        }
        build(self, 0, max_depth)
    }

    /// Execute JavaScript in the browser using dev tools console
    /// Opens dev tools with F12, switches to console, runs script, extracts result
    pub async fn execute_browser_script(&self, script: &str) -> Result<String, AutomationError> {
        crate::browser_script::execute_script(self, script).await
    }
}

impl PartialEq for UIElement {
    fn eq(&self, other: &Self) -> bool {
        self.inner.object_id() == other.inner.object_id()
    }
}

impl Eq for UIElement {}

impl std::hash::Hash for UIElement {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.inner.object_id().hash(state);
    }
}

impl Clone for UIElement {
    fn clone(&self) -> Self {
        // We can't directly clone the inner Box<dyn UIElementImpl>,
        // but we can create a new UIElement with the same identity
        // that will behave the same way
        Self {
            inner: self.inner.clone_box(),
        }
    }
}

/// Utility functions for working with UI elements
pub mod utils {
    use super::*;

    /// Get the display text for an element (name, value, or role as fallback)
    pub fn display_text(element: &UIElement) -> String {
        element
            .name()
            .or_else(|| element.attributes().value)
            .unwrap_or_else(|| element.role())
    }

    /// Check if element has any text content
    pub fn has_text_content(element: &UIElement) -> bool {
        element.name().is_some()
            || element.attributes().value.is_some()
            || !element.text(1).unwrap_or_default().trim().is_empty()
    }

    /// Get a human-readable identifier for the element
    pub fn element_identifier(element: &UIElement) -> String {
        if let Some(name) = element.name() {
            format!("{} ({})", name, element.role())
        } else if let Some(id) = element.id() {
            format!("#{} ({})", id, element.role())
        } else {
            element.role()
        }
    }

    /// Create a minimal attributes struct with just the essentials
    pub fn essential_attributes(element: &UIElement) -> UIElementAttributes {
        UIElementAttributes {
            role: element.role(),
            name: element.name(),
            text: None,
            value: element.attributes().value,
            bounds: None, // Not included in minimal attributes
            ..Default::default()
        }
    }
}

/// Serialize implementation for UIElement
///
/// This implementation serializes the accessible properties of a UI element to JSON.
/// The following fields are included in the serialized output:
/// - `id`: Element identifier (if available)
/// - `role`: Element role (e.g., "button", "textfield")
/// - `name`: Element name/label (if available)
/// - `bounds`: Element position and size as (x, y, width, height)
/// - `value`: Element value (if available)
/// - `description`: Element description (if available)
/// - `application`: Name of the containing application
/// - `window_title`: Title of the containing window
///
/// Note: This serializes the element's current state and properties, but does not
/// serialize the underlying platform-specific implementation or maintain any
/// interactive capabilities.
impl Serialize for UIElement {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        self.to_serializable().serialize(serializer)
    }
}

// TODO: Deserialize is pretty much very experimental and untested

/// Deserialize implementation for UIElement
///
/// This implementation attempts to find the actual UI element in the current UI tree
/// using the deserialized data (ID, role, name, bounds). If the element cannot be found,
/// deserialization fails with an error.
///
/// This ensures all UIElement instances are always "live" and can perform UI operations.
/// There are no more "mock" or "dead" elements - if deserialization succeeds, the element
/// exists and can be interacted with.
///
/// Search strategy:
/// 1. Try to find by ID if available
/// 2. Try to find by role + name combination
/// 3. Verify bounds match (with 10px tolerance) if available
///
/// Note: This approach requires the UI element to actually exist in the current UI tree
/// at the time of deserialization. If the UI has changed since serialization,
/// deserialization will fail.
impl<'de> Deserialize<'de> for UIElement {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        use serde::de::Error;

        // First deserialize into our SerializableUIElement
        let serializable = SerializableUIElement::deserialize(deserializer)?;

        // Try to find the actual live element
        // Note: find_live_element now returns None instead of panicking in async contexts
        find_live_element(&serializable).ok_or_else(|| {
            // Check if we're in an async context - if so, provide a more helpful error message
            if tokio::runtime::Handle::try_current().is_ok() {
                Error::custom(format!(
                    "UIElement deserialization skipped in async context (role='{}', name={:?})",
                    serializable.role, serializable.name
                ))
            } else {
                Error::custom(format!(
                    "Could not find UI element with role '{}' and name '{:?}' in current UI tree",
                    serializable.role, serializable.name
                ))
            }
        })
    }
}

/// Attempts to find a live UI element matching the serializable data
fn find_live_element(serializable: &SerializableUIElement) -> Option<UIElement> {
    // Try to create a Desktop instance and search the UI tree
    // If any step fails (Desktop creation or element search), return None
    std::panic::catch_unwind(|| {
        // Desktop::new is now synchronous, so we can call it directly
        let desktop = crate::Desktop::new(false, false).ok()?;

        // Check if we're already in an async runtime context
        if let Ok(_handle) = tokio::runtime::Handle::try_current() {
            // We're already in an async context, use the existing runtime
            // This happens during MCP workflow conversion
            // We can't use block_on here, so just return None
            tracing::debug!(
                "Skipping live element lookup for role='{}', name={:?} (in async context)",
                serializable.role,
                serializable.name
            );
            return None;
        }

        // We're in a sync context, create a new runtime for the async operation
        let rt = tokio::runtime::Runtime::new().ok()?;
        rt.block_on(async { find_element_in_tree(&desktop, serializable).await })
    })
    .unwrap_or(None)
}

/// Helper function to search for element in the UI tree
async fn find_element_in_tree(
    desktop: &crate::Desktop,
    serializable: &SerializableUIElement,
) -> Option<crate::UIElement> {
    // Try to find by ID first
    if let Some(ref id) = serializable.id {
        let id_selector = format!("#{id}");
        if let Ok(element) = desktop
            .locator(id_selector.as_str())
            .first(Some(std::time::Duration::from_secs(1)))
            .await
        {
            return Some(element);
        }
    }

    // Try to find by role and name
    let mut selector = format!("role:{}", serializable.role);
    if let Some(ref name) = serializable.name {
        selector = format!("{selector}name:{name}");
    }

    if let Ok(element) = desktop
        .locator(selector.as_str())
        .first(Some(std::time::Duration::from_secs(1)))
        .await
    {
        // Verify bounds match (with tolerance) if available
        if let Some((target_x, target_y, target_w, target_h)) = serializable.bounds {
            if let Ok((fx, fy, fw, fh)) = element.bounds() {
                let tolerance = 10.0; // 10 pixel tolerance

                if (fx - target_x).abs() <= tolerance
                    && (fy - target_y).abs() <= tolerance
                    && (fw - target_w).abs() <= tolerance
                    && (fh - target_h).abs() <= tolerance
                {
                    return Some(element);
                }
            }
        } else {
            // If no bounds to check, return the element
            return Some(element);
        }
    }

    None
}
