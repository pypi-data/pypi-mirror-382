# CursorFlow User Manual

**The measurement tool for web testing - complete guide to reality-based testing**

CursorFlow is a pure data collection engine that captures comprehensive web application intelligence. Unlike simulation tools that let you control reality, CursorFlow measures actual reality - giving you complete trust in your test results.

---

## 🎯 The CursorFlow Philosophy

### **📊 We Collect Reality, Not Fiction**

**Other tools are simulation tools** - they let you control reality:
- Mock network responses
- Simulate user interactions  
- Create test environments

**CursorFlow is a measurement tool** - we capture reality as-is:
- Real API response times
- Actual network failures
- Genuine browser behavior
- Complete page intelligence

### **🔬 Pure Observation Principle**

**CursorFlow is like a scientific instrument:**
- **Microscopes** don't create the cells they observe
- **Telescopes** don't generate the stars they capture  
- **CursorFlow** doesn't mock the web it measures

When CursorFlow reports `"average_response_time": 416.58ms`, you can tell stakeholders: **"This is what actually happened"** - not "this is what happened in our test simulation."

### **🌟 The Trust Factor**

**Complete Reliability:** Every data point reflects real application behavior
- No mocked responses hiding slow APIs
- No simulated interactions missing real edge cases
- No test environments different from production

**Documentary vs Movie:** Both are valuable, but if you're trying to understand reality, you watch the documentary. CursorFlow is the documentary of web testing.

---

## 📋 Table of Contents

1. [⚡ Quick Start](#quick-start)
2. [📦 Installation](#installation)
3. [🔧 Core Features](#core-features)
4. [🎯 Basic Usage](#basic-usage)
5. [📋 CLI Commands](#cli-commands)
6. [🐍 Python API](#python-api)
7. [💡 Examples](#examples)
8. [🔧 Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start

### Install and Test in 2 Minutes

```bash
# Install CursorFlow
pip install cursorflow

# Test your real application
cursorflow test --base-url http://localhost:3000 --path "/dashboard"
```

**That's it!** CursorFlow captures screenshots, DOM data, network activity, console logs, and performance metrics automatically - all from your real application behavior.

---

## 📦 Installation

### Requirements
- Python 3.8+
- A web application running locally or remotely
- Development server with HMR support (optional but recommended)

### Install CursorFlow
```bash
pip install cursorflow
```

### Install Browser (automatic on first use)
```bash
playwright install chromium  # Optional - happens automatically
```

### Install Cursor Rules (for AI assistance)
```bash
cursorflow install-rules
```

---

## 🔧 Core Features

### **Reality-Based Data Collection**

CursorFlow captures actual application behavior, not simulated or mocked responses:

- **Real network timing** - actual API response times
- **Genuine errors** - real console errors and network failures  
- **Actual performance** - true load times and memory usage
- **Complete page state** - real DOM, styles, and interactions

### **Hot Reload Intelligence**

CursorFlow automatically detects and monitors Hot Module Replacement (HMR) events from your development server, enabling precise timing for CSS iteration workflows.

**Supported Development Frameworks:**
- ✅ **Vite** (port 5173, WebSocket `/__vite_hmr`)
- ✅ **Webpack Dev Server** (port 3000, WebSocket `/sockjs-node`)
- ✅ **Next.js** (port 3000, WebSocket `/_next/webpack-hmr`)
- ✅ **Parcel** (port 1234, WebSocket `/hmr`)
- ✅ **Laravel Mix** (port 3000, WebSocket `/browser-sync/socket.io`)

**Perfect CSS iteration workflow:**
```python
# Start HMR monitoring
await browser.start_hmr_monitoring()

# Take baseline screenshot
await browser.screenshot("baseline.png")

# Wait for developer to make CSS changes
await browser.wait_for_css_update()  # Precise timing

# Capture after changes are applied
await browser.screenshot("updated.png")
```

### **Advanced Element Intelligence**

Every element is captured with multiple selector strategies and comprehensive accessibility data.

**Multi-Selector Strategy** - Every element gets 7 ways to find it:
```json
{
  "selectors": {
    "css": "#nav-menu",
    "xpath": "//nav[@id='nav-menu']", 
    "text": "Navigation Menu",
    "role": "navigation",
    "testid": "main-nav",
    "aria_label": "Main navigation",
    "unique_css": "body > header > #nav-menu"
  }
}
```

**Complete Accessibility Data:**
```json
{
  "accessibility": {
    "role": "navigation",
    "aria_label": "Main navigation", 
    "tabindex": 0,
    "focusable": true,
    "interactive": true,
    "semantic_role": "landmark"
  }
}
```

**Visual Context Intelligence:**
```json
{
  "visual_context": {
    "bounding_box": {"x": 0, "y": 0, "width": 1200, "height": 60},
    "visibility": {
      "is_visible": true,
      "in_viewport": true,
      "opacity": 1,
      "display": "flex"
    },
    "layering": {
      "z_index": "100",
      "stacking_context": true
    },
    "size_classification": "large"
  }
}
```

### **Comprehensive Page Analysis**

CursorFlow captures complete intelligence about every aspect of your page.

**Font Loading Intelligence:**
```json
{
  "font_status": {
    "totalFonts": 8,
    "loadedFonts": 7,
    "loadingFonts": 1,
    "failedFonts": 0,
    "fontDetails": [
      {
        "family": "Inter",
        "weight": 400,
        "status": "loaded",
        "source": "google-fonts"
      }
    ],
    "loadingMetrics": {
      "averageLoadTime": 120,
      "slowestFont": "Inter Bold"
    }
  }
}
```

**Animation State Tracking:**
```json
{
  "animation_status": {
    "totalAnimatedElements": 5,
    "runningAnimations": 3,
    "pausedAnimations": 0,
    "finishedAnimations": 2,
    "animationDetails": [
      {
        "name": "fadeInUp",
        "duration": 800,
        "playState": "running",
        "element": ".hero-title"
      }
    ]
  }
}
```

**Resource Loading Analysis:**
```json
{
  "resource_status": {
    "totalResources": 42,
    "resourcesByType": {
      "script": 12,
      "stylesheet": 8,
      "image": 18,
      "font": 4
    },
    "loadingPerformance": {
      "fastestResource": {"name": "main.css", "loadTime": 45},
      "slowestResource": {"name": "hero-image.jpg", "loadTime": 1200},
      "averageLoadTime": 320
    },
    "criticalResources": ["main.css", "app.js"]
  }
}
```

**Storage State Capture:**
```json
{
  "storage_status": {
    "localStorage": {
      "itemCount": 5,
      "estimatedSize": 2048,
      "keys": ["theme", "user_preferences", "cart_data"]
    },
    "sessionStorage": {
      "itemCount": 2,
      "estimatedSize": 512,
      "keys": ["temp_form_data"]
    },
    "cookies": {
      "count": 8,
      "names": ["session_id", "csrf_token", "analytics_id"]
    },
    "indexedDB": {
      "available": true,
      "databases": ["app_cache", "offline_data"]
    }
  }
}
```

### **Enhanced Error Context Collection**

CursorFlow collects comprehensive error context data with smart screenshot deduplication to provide rich debugging information while maintaining efficiency.

**Smart Screenshot Deduplication:**
- Reuses screenshots when page content hasn't changed
- Avoids duplicate captures for multiple errors in quick succession
- Maintains complete error context while being storage-efficient

**Rich Error Context:**
```json
{
  "error_context": {
    "error_timestamp": 1703123456.789,
    "screenshot_info": {
      "path": ".cursorflow/artifacts/diagnostics/error_1703123456.png",
      "is_reused": false,
      "content_hash": "abc123def456"
    },
    "dom_snapshot": "...",
    "page_state": {
      "url": "http://localhost:3000/dashboard",
      "title": "Dashboard",
      "viewport": {"width": 1920, "height": 1080}
    },
    "console_context": [...],
    "network_context": [...],
    "recent_actions": [
      {"timestamp": 1703123450.1, "action": "click", "selector": "#refresh-btn"}
    ],
    "element_visibility_map": [...]
  }
}
```

### **Enhanced Browser Data Capture**

CursorFlow integrates with Playwright's advanced capabilities to provide comprehensive browser interaction data.

**Playwright Trace Integration:**
```python
# Complete trace recording for debugging
trace_path = await browser.start_trace_recording("test_session")
# ... perform actions ...
await browser.stop_trace_recording()
# Trace file: .cursorflow/artifacts/traces/test_session.zip
```

**Complete Response Body Capture:**
```json
{
  "network_request": {
    "url": "https://api.example.com/data",
    "method": "POST",
    "status": 200,
    "headers": {...},
    "response_body": "...",  // Complete response content
    "error_analysis": {
      "category": "success",
      "cause": null
    }
  }
}
```

**Performance Metrics with Reliability:**
```json
{
  "performance_data": {
    "navigation": {
      "domContentLoaded": 1234,
      "loadComplete": 2456
    },
    "paint": {
      "firstPaint": 890,
      "firstContentfulPaint": 1100
    },
    "_reliability": {
      "navigation_timing": "available",
      "paint_timing": "available", 
      "note": "All metrics reliable in headed mode"
    }
  }
}
```

---

## 🎯 Basic Usage

### 1. Test Any Page with Complete Intelligence
```bash
cursorflow test --base-url http://localhost:3000 --path "/dashboard"
```

### 2. Test with Custom Actions
```bash
cursorflow test --base-url http://localhost:3000 --actions '[
  {"navigate": "/login"},
  {"fill": {"selector": "#username", "value": "test@example.com"}},
  {"fill": {"selector": "#password", "value": "password123"}},
  {"click": "#login-button"},
  {"wait_for": ".dashboard"},
  {"screenshot": "logged-in"}
]'
```

### 3. Enhanced Screenshot Options

CursorFlow provides precise screenshot control for focused testing and privacy-aware captures:

```bash
# Component-focused screenshots
cursorflow test --base-url http://localhost:3000 --actions '[
  {"navigate": "/components"},
  {"screenshot": {
    "name": "button-component",
    "options": {"clip": {"selector": ".component-demo"}}
  }}
]'

# Privacy-aware screenshots (mask sensitive data)
cursorflow test --base-url http://localhost:3000 --actions '[
  {"navigate": "/admin"},
  {"screenshot": {
    "name": "admin-safe",
    "options": {
      "mask": [".api-key", ".user-data", ".sensitive-info"],
      "full_page": true
    }
  }}
]'

# Coordinate-based clipping
cursorflow test --base-url http://localhost:3000 --actions '[
  {"navigate": "/dashboard"},
  {"screenshot": {
    "name": "dashboard-section",
    "options": {
      "clip": {"x": 100, "y": 200, "width": 800, "height": 400},
      "quality": 90
    }
  }}
]'

# JPEG with quality control (requires .jpg/.jpeg filename)
cursorflow test --base-url http://localhost:3000 --actions '[
  {"navigate": "/dashboard"},
  {"screenshot": {
    "name": "dashboard.jpg",
    "options": {
      "quality": 95,
      "full_page": true
    }
  }}
]'
```

**Screenshot Options:**
- **`clip`**: Focus on specific elements or coordinates
  - `{"selector": "#element"}` - Clip to element bounding box
  - `{"x": 0, "y": 0, "width": 800, "height": 600}` - Clip to coordinates
- **`mask`**: Hide sensitive information
  - `[".password", ".api-key", ".user-email"]` - CSS selectors to hide
- **`full_page`**: Capture entire page (default: viewport only)
- **`quality`**: JPEG quality 0-100 (default: 80) - **Note**: Only works with .jpg/.jpeg filenames

### 4. Parallel Viewport Testing

CursorFlow can test the same actions across multiple viewports simultaneously, providing comprehensive responsive design validation:

```bash
# Responsive testing across standard viewports
cursorflow test --base-url http://localhost:3000 --path "/dashboard" --responsive

# Responsive testing with custom actions
cursorflow test --base-url http://localhost:3000 --responsive --actions '[
  {"navigate": "/products"},
  {"fill": {"selector": "#search", "value": "laptop"}},
  {"click": "#search-btn"},
  {"screenshot": {"name": "results", "options": {"clip": {"selector": ".results"}}}}
]'
```

**Standard Responsive Viewports:**
- **Mobile**: 375x667 (iPhone-like)
- **Tablet**: 768x1024 (iPad-like)  
- **Desktop**: 1440x900 (standard desktop)

**Benefits:**
- Test responsive design in parallel (faster than sequential)
- Compare performance across viewports
- Identify viewport-specific issues
- Comprehensive responsive analysis

### 5. Compare Design to Implementation
```bash
cursorflow compare-mockup https://mockup.com/design \
  --base-url http://localhost:3000 \
  --mockup-actions '[{"navigate": "/"}]' \
  --implementation-actions '[{"navigate": "/"}]'
```

### 4. CSS Iteration with HMR
```bash
cursorflow iterate-mockup https://mockup.com/design \
  --base-url http://localhost:3000 \
  --css-improvements '[
    {"name": "fix-spacing", "css": ".container { gap: 2rem; }"},
    {"name": "improve-colors", "css": ".button { background: #007bff; }"}
  ]'
```

---

## 🔬 Complete Page Intelligence

Every test captures comprehensive data for AI analysis:

```python
# Every test provides complete data
results = await flow.execute_and_collect([
    {"navigate": "/dashboard"},
    {"screenshot": "loaded"}
])

# Access comprehensive data
screenshot = results['artifacts']['screenshots'][0]

# Enhanced Data Available
dom_data = screenshot['dom_analysis']           # 7 selectors per element
network_data = screenshot['network_data']       # Complete request/response
console_data = screenshot['console_data']       # Error correlation  
performance = screenshot['performance_data']    # Reliability indicators
font_status = screenshot['font_status']         # Font loading analysis
animation_status = screenshot['animation_status'] # Animation tracking
resource_status = screenshot['resource_status']   # Resource analysis
storage_status = screenshot['storage_status']     # Storage state
hmr_status = screenshot['hmr_status']            # HMR event data
```

### **Mockup Comparison with Enhanced Analysis**
Compare designs to implementation with comprehensive analysis:

```python
# Enhanced mockup comparison
comparison = await flow.compare_mockup_to_implementation(
    mockup_url="https://mockup.com/design",
    implementation_url="/dashboard",
    mockup_actions=[{"navigate": "/"}],
    implementation_actions=[{"navigate": "/dashboard"}]
)

# Enhanced Comparison Data
visual_diff = comparison['visual_analysis']
dom_comparison = comparison['dom_comparison']      # Structural analysis
css_recommendations = comparison['css_recommendations'] # Smart suggestions
accessibility_analysis = comparison['accessibility_analysis'] # A11y comparison
```

### **CSS Iteration with HMR Intelligence**
Precise timing for CSS changes:

```python
# HMR-powered CSS iteration
results = await flow.iterative_mockup_matching(
    mockup_url="https://mockup.com/design",
    implementation_url="/page",
    css_improvements=[
        {"name": "fix-layout", "css": ".grid { gap: 2rem; }"},
        {"name": "improve-typography", "css": ".heading { font-size: 2.5rem; }"}
    ]
)

# HMR Integration Data
hmr_events = results['hmr_correlation']         # CSS change timing
framework_detection = results['framework_info'] # Auto-detected framework
timing_analysis = results['timing_analysis']    # Change application speed
```

### **Error Context with Smart Diagnostics**
Enhanced error debugging:

```python
# Smart error context collection
error_context = await browser.capture_interaction_error_context(
    action_description="Submit form",
    error_details={"type": "validation_error", "message": "Required field missing"}
)

# Smart Context Data
screenshot_info = error_context['screenshot_info']  # Deduplication info
dom_snapshot = error_context['dom_snapshot']        # Complete DOM state
action_correlation = error_context['recent_actions'] # Action timeline
element_visibility = error_context['element_visibility_map'] # Visibility analysis
```

---

## 📋 CLI Commands

### **Complete CLI Options Reference**

#### **`cursorflow test`** - Universal Testing
```bash
cursorflow test --base-url URL [OPTIONS]

Options:
  --base-url, -u TEXT         Base URL (required)
  --path, -p TEXT            Simple navigation path (e.g., "/dashboard")
  --actions, -a TEXT         JSON array of actions to perform
  --output, -o TEXT          Output file path (auto-generated if not specified)
  --logs, -l TEXT            Log source: local|ssh|docker [default: local]
  --headless / --headed      Browser mode [default: headless]
  --timeout INTEGER          Timeout in seconds [default: 30]
  --config, -c PATH          Config file path
  --verbose, -v              Verbose output

Examples:
  # Simple page test with complete intelligence
  cursorflow test --base-url http://localhost:3000 --path "/dashboard"
  
  # Complex interaction test
  cursorflow test --base-url http://localhost:3000 --actions '[
    {"navigate": "/login"},
    {"fill": {"selector": "#email", "value": "test@example.com"}},
    {"click": "#login-btn"},
    {"wait_for": ".dashboard"},
    {"screenshot": "logged-in"}
  ]'
  
  # Test with HMR monitoring
  cursorflow test --base-url http://localhost:5173 --path "/app" --verbose
```

#### **`cursorflow compare-mockup`** - Design Comparison
```bash
cursorflow compare-mockup MOCKUP_URL --base-url URL [OPTIONS]

Options:
  --base-url, -u TEXT        Implementation URL (required)
  --mockup-actions TEXT      JSON actions for mockup
  --implementation-actions   JSON actions for implementation  
  --viewports TEXT           JSON viewport configurations
  --diff-threshold FLOAT     Visual difference threshold [default: 0.1]
  --output, -o TEXT          Output file path

Examples:
  # Basic design comparison with comprehensive analysis
  cursorflow compare-mockup https://mockup.com/design \
    --base-url http://localhost:3000
    
  # Advanced comparison with actions
  cursorflow compare-mockup https://mockup.com/design \
    --base-url http://localhost:3000 \
    --mockup-actions '[{"navigate": "/"}]' \
    --implementation-actions '[{"navigate": "/dashboard"}]'
```

#### **`cursorflow iterate-mockup`** - CSS Iteration with HMR
```bash
cursorflow iterate-mockup MOCKUP_URL --base-url URL [OPTIONS]

Options:
  --base-url, -u TEXT        Implementation URL (required)
  --css-improvements TEXT    JSON array of CSS changes to test
  --base-actions TEXT        JSON actions to perform before each test
  --diff-threshold FLOAT     Visual difference threshold [default: 0.1]
  --output, -o TEXT          Output file path

Examples:
  # HMR-powered CSS iteration
  cursorflow iterate-mockup https://mockup.com/design \
    --base-url http://localhost:5173 \
    --css-improvements '[
      {"name": "fix-spacing", "css": ".container { gap: 2rem; }"},
      {"name": "improve-colors", "css": ".button { background: #007bff; }"}
    ]'
```

#### **`cursorflow install-rules`** - Cursor AI Integration
```bash
cursorflow install-rules [OPTIONS]

Options:
  --force, -f               Overwrite existing rules
  --project-dir PATH        Target project directory [default: current]

Examples:
  # Install Cursor rules for AI assistance
  cursorflow install-rules
  
  # Force reinstall rules
  cursorflow install-rules --force
```

---

## 🐍 Python API

### **Core API Usage**

#### **Basic Usage with Complete Features**
```python
import asyncio
from cursorflow import CursorFlow

async def test_with_complete_features():
    # Initialize with complete capabilities
    flow = CursorFlow(
        base_url="http://localhost:3000",
        browser_config={"headless": True},
        log_config={"source": "local", "paths": {"app": "logs/app.log"}}
    )
    
    # Test with complete intelligence
    results = await flow.execute_and_collect([
        {"navigate": "/dashboard"},
        {"wait_for": "#main-content"},
        {"screenshot": "dashboard-loaded"}
    ])
    
    # Access enhanced data
    screenshot = results['artifacts']['screenshots'][0]
    
    # Advanced Element Intelligence
    for element in screenshot['dom_analysis']['elements']:
        print(f"Element: {element['selector']}")
        print(f"  Selectors: {list(element['selectors'].keys())}")
        print(f"  Accessibility: {element['accessibility']['role']}")
        print(f"  Visible: {element['visual_context']['visibility']['is_visible']}")
    
    # Comprehensive Page Analysis
    print(f"Fonts loaded: {screenshot['font_status']['loadedFonts']}")
    print(f"Animations running: {screenshot['animation_status']['runningAnimations']}")
    print(f"Resources loaded: {screenshot['resource_status']['totalResources']}")
    
    # HMR Status
    if 'hmr_status' in screenshot:
        print(f"Framework detected: {screenshot['hmr_status']['framework']}")
    
    return results

# Run the test
results = asyncio.run(test_with_complete_features())
```

#### **Enhanced Screenshot Options**
```python
import asyncio
from cursorflow import CursorFlow

async def enhanced_screenshot_examples():
    flow = CursorFlow("http://localhost:3000", {"headless": True})
    
    # Component-focused screenshots
    component_results = await flow.execute_and_collect([
        {"navigate": "/components"},
        {"screenshot": {
            "name": "button-component",
            "options": {"clip": {"selector": ".component-demo"}}
        }}
    ])
    
    # Privacy-aware screenshots
    privacy_results = await flow.execute_and_collect([
        {"navigate": "/admin"},
        {"screenshot": {
            "name": "admin-safe",
            "options": {
                "mask": [".api-key", ".user-data", ".sensitive-info"],
                "full_page": True,
                "quality": 95
            }
        }}
    ])
    
    # Coordinate-based clipping
    coordinate_results = await flow.execute_and_collect([
        {"navigate": "/dashboard"},
        {"screenshot": {
            "name": "dashboard-section",
            "options": {
                "clip": {"x": 100, "y": 200, "width": 800, "height": 400}
            }
        }}
    ])
    
    return {
        "component_focused": component_results,
        "privacy_aware": privacy_results,
        "coordinate_clipped": coordinate_results
    }

# Run enhanced screenshot examples
results = asyncio.run(enhanced_screenshot_examples())
```

#### **Parallel Viewport Testing**
```python
import asyncio
from cursorflow import CursorFlow

async def responsive_testing_example():
    flow = CursorFlow("http://localhost:3000", {"headless": True})
    
    # Define responsive viewports
    viewports = [
        {"width": 375, "height": 667, "name": "mobile"},
        {"width": 768, "height": 1024, "name": "tablet"},
        {"width": 1440, "height": 900, "name": "desktop"}
    ]
    
    # Test same actions across all viewports
    results = await flow.test_responsive(viewports, [
        {"navigate": "/dashboard"},
        {"wait_for": "#main-content"},
        {"screenshot": "dashboard-loaded"},
        {"click": "#menu-toggle"},
        {"screenshot": {"name": "menu", "options": {"clip": {"selector": "#navigation"}}}}
    ])
    
    # Analyze responsive results
    execution_summary = results['execution_summary']
    print(f"Viewports tested: {execution_summary['successful_viewports']}/{execution_summary['total_viewports']}")
    print(f"Total execution time: {execution_summary['execution_time']:.2f}s")
    
    # Performance analysis
    perf = results['responsive_analysis']['performance_analysis']
    print(f"Fastest viewport: {perf['fastest_viewport']}")
    print(f"Slowest viewport: {perf['slowest_viewport']}")
    
    return results

# Run responsive testing
results = asyncio.run(responsive_testing_example())
```

#### **HMR-Powered CSS Iteration**
```python
async def css_iteration_with_hmr():
    flow = CursorFlow("http://localhost:5173", {"headless": False})
    
    # HMR Intelligence
    results = await flow.iterative_mockup_matching(
        mockup_url="https://mockup.com/design",
        implementation_url="/app",
        css_improvements=[
            {
                "name": "improve-spacing",
                "css": ".container { gap: 2rem; padding: 2rem; }"
            },
            {
                "name": "enhance-typography", 
                "css": ".heading { font-size: 2.5rem; line-height: 1.2; }"
            }
        ]
    )
    
    # HMR Correlation Data
    for iteration in results['iterations']:
        print(f"Change: {iteration['name']}")
        print(f"  HMR Event: {iteration['hmr_event']}")
        print(f"  Framework: {iteration['framework_detected']}")
        print(f"  Apply Time: {iteration['css_apply_time']}ms")
    
    return results
```

#### **Enhanced Error Context Collection**
```python
async def error_context_example():
    flow = CursorFlow("http://localhost:3000", {"headless": True})
    
    try:
        # Perform action that might fail
        await flow.execute_and_collect([
            {"navigate": "/form"},
            {"click": "#submit-without-data"}  # This will cause an error
        ])
    except Exception as e:
        # Enhanced Error Context
        error_context = await flow.browser.capture_interaction_error_context(
            action_description="Submit empty form",
            error_details={"type": "validation_error", "error": str(e)}
        )
        
        # Rich diagnostic data
        print(f"Error screenshot: {error_context['screenshot_info']['path']}")
        print(f"Screenshot reused: {error_context['screenshot_info']['is_reused']}")
        print(f"Recent actions: {len(error_context['recent_actions'])}")
        print(f"Visible elements: {len(error_context['element_visibility_map'])}")
        
        return error_context
```

#### **Complete Page Analysis**
```python
async def comprehensive_analysis():
    flow = CursorFlow("http://localhost:3000", {"headless": True})
    
    # Capture with full analysis
    results = await flow.execute_and_collect([
        {"navigate": "/complex-page"},
        {"wait_for": "body"},
        {"screenshot": "full-analysis"}
    ])
    
    screenshot = results['artifacts']['screenshots'][0]
    
    # Comprehensive Analysis
    analysis_summary = {
        'elements_analyzed': len(screenshot['dom_analysis']['elements']),
        'fonts_status': screenshot['font_status'],
        'animations_active': screenshot['animation_status']['runningAnimations'],
        'resources_loaded': screenshot['resource_status']['totalResources'],
        'storage_items': {
            'localStorage': screenshot['storage_status']['localStorage']['itemCount'],
            'sessionStorage': screenshot['storage_status']['sessionStorage']['itemCount'],
            'cookies': screenshot['storage_status']['cookies']['count']
        },
        'performance_reliable': screenshot['performance_data']['_reliability'],
        'hmr_available': 'hmr_status' in screenshot
    }
    
    print("📊 Comprehensive Analysis:")
    for key, value in analysis_summary.items():
        print(f"  {key}: {value}")
    
    return analysis_summary
```

---

## 💡 Examples

### **Example 1: HMR-Powered Development Workflow**
```python
"""
Hot Reload Intelligence: Perfect CSS iteration with HMR intelligence
"""
import asyncio
from cursorflow import CursorFlow

async def hmr_development_workflow():
    # Connect to Vite dev server (auto-detected)
    flow = CursorFlow("http://localhost:5173", {"headless": False})
    
    print("🔥 Starting HMR-powered development workflow...")
    
    # Start HMR monitoring
    await flow.browser.start_hmr_monitoring()
    
    # Take baseline screenshot
    baseline = await flow.execute_and_collect([
        {"navigate": "/dashboard"},
        {"wait_for": "#main-content"},
        {"screenshot": "baseline"}
    ])
    
    print(f"✅ Baseline captured: {baseline['artifacts']['screenshots'][0]['path']}")
    
    # Wait for developer to make CSS changes
    print("⏳ Waiting for CSS changes... (make changes in your editor)")
    
    hmr_event = await flow.browser.wait_for_css_update(timeout=60)
    if hmr_event:
        print(f"🔥 HMR event detected: {hmr_event['event_type']} at {hmr_event['timestamp']}")
        
        # Capture immediately after HMR update
        updated = await flow.execute_and_collect([
            {"screenshot": "updated"}
        ])
        
        print(f"✅ Updated captured: {updated['artifacts']['screenshots'][0]['path']}")
        
        # Get HMR status
        hmr_status = await flow.browser.get_hmr_status()
        print(f"📊 Framework: {hmr_status['detected_framework']}")
        print(f"📊 Events captured: {hmr_status['events_history_count']}")
    
    await flow.browser.stop_hmr_monitoring()
    print("🎉 HMR workflow completed!")

# Run the workflow
asyncio.run(hmr_development_workflow())
```

### **Example 2: Advanced Element Intelligence**
```python
"""
Multi-selector element analysis with accessibility data
"""
async def advanced_element_analysis():
    flow = CursorFlow("http://localhost:3000", {"headless": True})
    
    results = await flow.execute_and_collect([
        {"navigate": "/form"},
        {"screenshot": "form-analysis"}
    ])
    
    elements = results['artifacts']['screenshots'][0]['dom_analysis']['elements']
    
    print("🧠 Advanced Element Intelligence Analysis:")
    for element in elements[:5]:  # Show first 5 elements
        print(f"\n📍 Element: {element['selector']}")
        
        # Multiple selector strategies
        print("  🎯 Selectors:")
        for strategy, selector in element['selectors'].items():
            print(f"    {strategy}: {selector}")
        
        # Accessibility intelligence
        if element['accessibility']['interactive']:
            print(f"  ♿ Accessible: {element['accessibility']['role']}")
            print(f"  ♿ Focusable: {element['accessibility']['focusable']}")
            print(f"  ♿ ARIA Label: {element['accessibility'].get('aria_label', 'None')}")
        
        # Visual context
        visibility = element['visual_context']['visibility']
        print(f"  👁️  Visible: {visibility['is_visible']}")
        print(f"  👁️  In Viewport: {visibility['in_viewport']}")
        print(f"  👁️  Opacity: {visibility['opacity']}")

asyncio.run(advanced_element_analysis())
```

### **Example 3: Comprehensive Page Analysis**
```python
"""
Complete page intelligence with all analysis types
"""
async def comprehensive_page_intelligence():
    flow = CursorFlow("http://localhost:3000", {"headless": True})
    
    results = await flow.execute_and_collect([
        {"navigate": "/dashboard"},
        {"wait_for": "body"},
        {"screenshot": "comprehensive"}
    ])
    
    data = results['artifacts']['screenshots'][0]
    
    print("📊 Comprehensive Page Intelligence:")
    
    # Font Analysis
    font_status = data['font_status']
    print(f"\n🔤 Font Intelligence:")
    print(f"  Total fonts: {font_status['totalFonts']}")
    print(f"  Loaded: {font_status['loadedFonts']}")
    print(f"  Loading: {font_status['loadingFonts']}")
    print(f"  Average load time: {font_status['loadingMetrics']['averageLoadTime']}ms")
    
    # Animation Analysis
    animation_status = data['animation_status']
    print(f"\n🎬 Animation Intelligence:")
    print(f"  Animated elements: {animation_status['totalAnimatedElements']}")
    print(f"  Running animations: {animation_status['runningAnimations']}")
    print(f"  Active transitions: {animation_status['runningTransitions']}")
    
    # Resource Analysis
    resource_status = data['resource_status']
    print(f"\n📦 Resource Intelligence:")
    print(f"  Total resources: {resource_status['totalResources']}")
    print(f"  By type: {resource_status['resourcesByType']}")
    performance = resource_status['loadingPerformance']
    print(f"  Fastest: {performance['fastestResource']['name']} ({performance['fastestResource']['loadTime']}ms)")
    print(f"  Slowest: {performance['slowestResource']['name']} ({performance['slowestResource']['loadTime']}ms)")
    
    # Storage Analysis
    storage_status = data['storage_status']
    print(f"\n💾 Storage Intelligence:")
    print(f"  localStorage items: {storage_status['localStorage']['itemCount']}")
    print(f"  sessionStorage items: {storage_status['sessionStorage']['itemCount']}")
    print(f"  Cookies: {storage_status['cookies']['count']}")
    print(f"  IndexedDB available: {storage_status['indexedDB']['available']}")

asyncio.run(comprehensive_page_intelligence())
```

### **Example 4: Smart Error Context Collection**
```python
"""
Enhanced error diagnostics with smart screenshot deduplication
"""
async def smart_error_diagnostics():
    flow = CursorFlow("http://localhost:3000", {"headless": True})
    
    # Simulate multiple errors in quick succession
    errors = [
        {"type": "validation_error", "field": "email"},
        {"type": "validation_error", "field": "password"},
        {"type": "network_error", "request": "/api/login"}
    ]
    
    print("🎯 Smart Error Context Collection:")
    
    for i, error in enumerate(errors):
        print(f"\n📍 Error {i+1}: {error['type']}")
        
        # Smart error context with deduplication
        context = await flow.browser.capture_interaction_error_context(
            action_description=f"Handle {error['type']}",
            error_details=error
        )
        
        screenshot_info = context['screenshot_info']
        print(f"  📸 Screenshot: {screenshot_info['path']}")
        print(f"  📸 Reused: {screenshot_info['is_reused']}")
        if screenshot_info['is_reused']:
            print(f"  📸 Reason: {screenshot_info['reason']}")
        
        print(f"  🔍 Recent actions: {len(context['recent_actions'])}")
        print(f"  🌐 Network context: {len(context['network_context'])}")
        print(f"  📝 Console context: {len(context['console_context'])}")
    
    # Get summary of all error contexts
    summary = await flow.browser.get_error_context_summary()
    print(f"\n📊 Error Context Summary:")
    print(f"  Total errors: {summary['total_errors_collected']}")
    print(f"  Unique screenshots: {summary['total_diagnostic_screenshots']}")
    print(f"  Deduplication rate: {summary['screenshot_deduplication_rate']}")

asyncio.run(smart_error_diagnostics())
```

---

## 🔧 Troubleshooting

### **Performance Metrics Reliability**
Performance metrics behavior varies between headed and headless modes:

```json
{
  "performance_data": {
    "navigation": {
      "domContentLoaded": null,  // Expected in headless mode
      "loadComplete": null,      // Expected in headless mode
      "_note": "Navigation timing not available (likely headless mode)"
    },
    "_reliability": {
      "navigation_timing": "unavailable",
      "paint_timing": "unavailable",
      "note": "Performance metrics may be limited in headless mode"
    }
  }
}
```

**Key Point**: `null` values are expected and normal in headless mode. The CSS/DOM data (which is what matters most for UI testing) is always 100% reliable.

### **Missing Dependencies**
```bash
# If you see PIL/Pillow errors:
pip install --upgrade cursorflow  # Includes all dependencies

# Manual fix for older versions:
pip install pillow numpy websockets
```

### **HMR Detection Issues**
```bash
# Issue: HMR not detected
# Solution: Check if your dev server is running and accessible

# Verify dev server
curl http://localhost:5173  # For Vite
curl http://localhost:3000  # For Webpack/Next.js

# Test HMR detection manually
python -c "
from cursorflow.core.hmr_detector import HMRDetector
import asyncio

async def test_hmr():
    detector = HMRDetector('http://localhost:5173')
    framework = await detector.auto_detect_framework()
    print(f'Detected: {framework}')

asyncio.run(test_hmr())
"
```

### **Error Context Collection Issues**
```python
# Issue: Error context not collecting
# Solution: Ensure error context collector is initialized

from cursorflow.core.browser_controller import BrowserController

controller = BrowserController("http://localhost:3000", {"headless": True})
# Error context collector is automatically initialized

# Check if it's available
print(f"Error context available: {hasattr(controller, 'error_context_collector')}")
```

### **Log Source Warnings**
Non-critical log warnings are normal and can be ignored:
```bash
# These are expected and non-critical:
# "SSH connection issue (may be expected)" - appears when SSH monitoring isn't configured
# "Non-critical log file issue" - appears when log files don't exist yet
```

### **Browser Installation**
```bash
# If browser installation fails
playwright install chromium --force

# Check browser installation
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        print('✅ Browser installed correctly')
        await browser.close()

asyncio.run(test_browser())
"
```

### **Common CLI Issues**
```bash
# Issue: Command not found
# Solution: Ensure CursorFlow is installed correctly
pip install --upgrade cursorflow

# Issue: Import errors
# Solution: Check Python path
python -c "import cursorflow; print('✅ CursorFlow imported successfully')"

# Issue: Permission errors
# Solution: Install with user flag
pip install --user cursorflow
```

---

## 🚀 Getting Started

CursorFlow provides complete page intelligence for AI-driven development. With Hot Reload Intelligence, Advanced Element Analysis, and Comprehensive Page Intelligence, you have unprecedented insight into your web applications.

### **Key Advantages:**
- **Precise CSS iteration** with HMR timing
- **Multi-selector element intelligence** with 7 selector strategies per element  
- **Complete page analysis** covering fonts, animations, resources, storage
- **Smart error diagnostics** with deduplication and rich context
- **Enhanced browser data** with Playwright traces and response bodies

### **Perfect for:**
- ✅ **Rapid UI development** with instant visual feedback
- ✅ **Design-to-code workflows** with pixel-perfect comparison
- ✅ **Accessibility testing** with comprehensive A11y data
- ✅ **Performance optimization** with detailed resource analysis
- ✅ **Error debugging** with smart context collection
- ✅ **AI-driven development** with structured, actionable data

**Ready to experience complete page intelligence for AI-driven development? Start with CursorFlow today!**

---

*CursorFlow - Complete page intelligence for AI-driven development*