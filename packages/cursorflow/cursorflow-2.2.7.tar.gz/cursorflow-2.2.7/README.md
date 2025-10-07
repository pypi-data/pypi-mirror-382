# CursorFlow

**The measurement tool for web testing - we capture reality, not fiction**

CursorFlow is a pure data collection engine that captures comprehensive web application intelligence. Unlike simulation tools that let you control reality, CursorFlow measures actual reality - giving you complete trust in your test results.

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

## 🎯 Pass-Through Architecture

CursorFlow doesn't limit you - it exposes the full power of Playwright:

**94+ Playwright actions available:**
```bash
# Any Playwright Page method works
cursorflow test --actions '[
  {"hover": ".menu"},
  {"dblclick": ".editable"},
  {"press": "Enter"},
  {"drag_and_drop": {"source": ".item", "target": ".zone"}},
  {"check": "#checkbox"},
  {"evaluate": "window.scrollTo(0, 500)"}
]'
```

**Full configuration pass-through:**
```json
{
  "browser_config": {
    "browser_launch_options": {"devtools": true, "channel": "chrome"}
  },
  "context_options": {
    "color_scheme": "dark",
    "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
    "timezone_id": "America/Los_Angeles"
  }
}
```

**Forward-compatible:** New Playwright features work immediately without CursorFlow updates.

**See:** [Playwright API Documentation](https://playwright.dev/python/docs/api/class-page)

---

## 🧹 Artifact Management

CursorFlow generates valuable debugging data (screenshots, traces, sessions). Manage disk space:

```bash
# Clean old artifacts (>7 days)
cursorflow cleanup --artifacts --old-only

# Clean all artifacts
cursorflow cleanup --artifacts

# Clean saved sessions
cursorflow cleanup --sessions

# Clean everything
cursorflow cleanup --all

# Preview before deleting
cursorflow cleanup --all --dry-run
```

**See:** [Complete Usage Guide](docs/user/USAGE_GUIDE.md#artifact-management)

---

## 🚀 Complete Page Intelligence

Every test captures everything needed for debugging:

### **📊 Comprehensive Data Collection**
- **DOM**: All elements with 7 selector strategies + event handlers
- **Network**: Requests, responses, and complete request/response bodies  
- **Console**: All logs, errors, warnings - displayed prominently
- **JavaScript**: Global functions, variables, specific window objects
- **Storage**: localStorage, sessionStorage, cookies (sensitive data masked)
- **Forms**: All field values at capture time (passwords masked)
- **Performance**: Load times, memory usage, reliability indicators
- **Visual**: Screenshots with comprehensive page analysis
- **Sessions**: Save/restore authenticated browser state (requires auth_config)

### **🔄 Hot Reload Intelligence**
- **Framework auto-detection** (Vite, Webpack, Next.js, Parcel, Laravel Mix)
- **Perfect timing** for CSS change detection
- **HMR event correlation** for understanding change impact
- **Persistent sessions** that survive code changes

### **🎯 Enhanced Screenshot Options**
```python
# Clip to specific components
{"screenshot": {"name": "header", "options": {"clip": {"selector": "#header"}}}}

# Hide sensitive information
{"screenshot": {"name": "profile", "options": {"mask": [".user-email", ".api-key"]}}}

# Full page with quality control
{"screenshot": {"name": "page", "options": {"full_page": True, "quality": 90}}}
```

### **📱 Parallel Viewport Testing**
```python
# Test across multiple viewports simultaneously
await flow.test_responsive([
    {"width": 375, "height": 667, "name": "mobile"},
    {"width": 768, "height": 1024, "name": "tablet"},
    {"width": 1440, "height": 900, "name": "desktop"}
], [
    {"navigate": "/dashboard"},
    {"screenshot": "responsive-test"}
])
```

### **🤖 AI-First Design**
All data structured for AI consumption:
- Consistent JSON format across all features
- **Multi-selector element identification** for robust automation
- **Accessibility-aware** element analysis  
- Error correlation with **smart screenshot deduplication**
- Performance insights with **reliability metadata**

## 🚀 Quick Start

### Step 1: Install CursorFlow Package
```bash
pip install cursorflow
playwright install chromium
```

### Step 2: Initialize Your Project (One-Time Setup)
```bash
cd /path/to/your/project
cursorflow install-rules

# Or skip prompts for automation/CI
cursorflow install-rules --yes
```

This creates:
- `.cursor/rules/` - Cursor AI integration rules
- `.cursorflow/config.json` - Project-specific configuration
- `.cursorflow/` - Artifacts and session storage
- `.gitignore` entries for CursorFlow artifacts

### Step 3: Start Testing

**Simple page capture:**
```bash
cursorflow test --base-url http://localhost:3000 --path /dashboard
```

**Interactive testing with inline actions:**
```bash
cursorflow test --base-url http://localhost:3000 \
  --path /messages \
  --wait-for ".message-item" \
  --hover ".message-item:first-child" \
  --click ".message-item:first-child" \
  --screenshot "clicked" \
  --show-console \
  --open-trace
```

**Custom actions with JSON:**
```bash
cursorflow test --base-url http://localhost:3000 --actions '[
  {"navigate": "/login"},
  {"fill": {"selector": "#email", "value": "test@example.com"}},
  {"click": "#login-btn"},
  {"screenshot": {"name": "result", "options": {"mask": [".sensitive-data"]}}}
]'
```

## 💻 Python API Examples

### **Complete Page Intelligence**
```python
from cursorflow import CursorFlow

async def capture_reality():
    flow = CursorFlow("http://localhost:3000", {"source": "local", "paths": ["logs/app.log"]})
    
    # Capture everything
    results = await flow.execute_and_collect([
        {"navigate": "/dashboard"},
        {"screenshot": "complete-analysis"}
    ])
    
    # Access comprehensive data
    screenshot = results['artifacts']['screenshots'][0]
    print(f"Real load time: {screenshot['performance_data']['page_load_time']}ms")
    print(f"Actual memory usage: {screenshot['performance_data']['memory_usage_mb']}MB")
    print(f"Elements found: {len(screenshot['dom_analysis']['elements'])}")
```

### **Enhanced Screenshot Options**
```python
# Component-focused testing
await flow.execute_and_collect([
    {"navigate": "/components"},
    {"screenshot": {
        "name": "button-component",
        "options": {"clip": {"selector": ".component-demo"}}
    }}
])

# Privacy-aware testing
await flow.execute_and_collect([
    {"navigate": "/admin"},
    {"screenshot": {
        "name": "admin-safe",
        "options": {
            "full_page": True,
            "mask": [".api-key", ".user-data", ".sensitive-info"]
        }
    }}
])
```

### **Hot Reload Intelligence**
```python
# Perfect CSS iteration timing
async def hmr_workflow():
    flow = CursorFlow("http://localhost:5173", {"headless": False})
    
    # Auto-detect and monitor HMR
    await flow.browser.start_hmr_monitoring()
    
    # Baseline capture
    await flow.execute_and_collect([{"screenshot": "baseline"}])
    
    # Wait for real CSS changes with perfect timing
    hmr_event = await flow.browser.wait_for_css_update()
    print(f"🔥 {hmr_event['framework']} detected real change!")
    
    # Capture immediately after actual change
    await flow.execute_and_collect([{"screenshot": "updated"}])
```

### **Parallel Viewport Testing**
```python
# Test responsive design across multiple viewports
async def test_responsive_design():
    flow = CursorFlow("http://localhost:3000", {"source": "local", "paths": ["logs/app.log"]})
    
    # Define viewports
    viewports = [
        {"width": 375, "height": 667, "name": "mobile"},
        {"width": 768, "height": 1024, "name": "tablet"},
        {"width": 1440, "height": 900, "name": "desktop"}
    ]
    
    # Test same actions across all viewports
    results = await flow.test_responsive(viewports, [
        {"navigate": "/dashboard"},
        {"click": "#menu-toggle"},
        {"screenshot": {"name": "navigation", "options": {"clip": {"selector": "#nav"}}}}
    ])
    
    # Analyze responsive behavior
    print(f"Tested {results['execution_summary']['successful_viewports']} viewports")
    print(f"Fastest: {results['responsive_analysis']['performance_analysis']['fastest_viewport']}")
```

## 🔧 CLI Commands

### **Universal Testing**
```bash
# Simple page test with complete intelligence
cursorflow test --base-url http://localhost:3000 --path "/dashboard"

# Responsive testing across multiple viewports
cursorflow test --base-url http://localhost:3000 --path "/dashboard" --responsive

# Complex interaction testing
cursorflow test --base-url http://localhost:3000 --actions '[
  {"navigate": "/form"},
  {"fill": {"selector": "#name", "value": "Test User"}},
  {"click": "#submit"},
  {"screenshot": {"name": "result", "options": {"clip": {"selector": ".result-area"}}}}
]'

# Responsive testing with custom actions
cursorflow test --base-url http://localhost:3000 --responsive --actions '[
  {"navigate": "/products"},
  {"fill": {"selector": "#search", "value": "laptop"}},
  {"screenshot": "search-results"}
]'

# Custom output location
cursorflow test --base-url http://localhost:3000 --path "/api" --output "api-test-results.json"
```

### **Design Comparison**
```bash
# Compare mockup to implementation
cursorflow compare-mockup https://mockup.com/design \
  --base-url http://localhost:3000 \
  --mockup-actions '[{"navigate": "/"}]' \
  --implementation-actions '[{"navigate": "/dashboard"}]'

# CSS iteration with HMR intelligence
cursorflow iterate-mockup https://mockup.com/design \
  --base-url http://localhost:5173 \
  --css-improvements '[
    {"name": "fix-spacing", "css": ".container { gap: 2rem; }"}
  ]'
```

### **AI Integration**
```bash
# Install Cursor AI rules
cursorflow install-rules

# Update to latest version and rules
cursorflow update
```

## 🧠 Why This Matters

### **For Job Board v4 Testing:**
✅ **Real API response times** from `/ajax_rq.smpl?fn=gjapi_typeahead`  
✅ **Actual network failures** when they occur  
✅ **Real browser console errors** from production code  
✅ **Genuine performance metrics** under real load  

❌ **With mocking:** You'd never know the typeahead is slow in production!

### **For Any Web Application:**
- **Trust your test results** - they reflect actual behavior
- **Find real performance bottlenecks** - no artificial speed boosts
- **Discover actual edge cases** - no simulation gaps
- **Debug genuine issues** - real errors, real timing, real context

## 🌟 Framework Support

**Universal Compatibility:**
- Works with **any web application** regardless of technology
- **Framework-agnostic** core operations  
- **Smart adaptation** to different environments

**HMR Auto-Detection:**
- ✅ **Vite** (port 5173)
- ✅ **Webpack Dev Server** (port 3000)  
- ✅ **Next.js** (port 3000)
- ✅ **Parcel** (port 1234)
- ✅ **Laravel Mix** (port 3000)

## 📖 Documentation

- **[Complete User Manual](docs/USER_MANUAL.md)** - Full feature guide
- **[Examples](examples/)** - Practical usage examples  
- **[API Reference](docs/api/)** - Complete Python API documentation

## 🎪 The CursorFlow Advantage

### **Other Tools Say:**
*"We let you mock and simulate"*

### **CursorFlow Says:**  
*"We tell you the truth"*

**When you need to understand reality, choose the measurement tool - not the simulation tool.**

---

**Complete page intelligence • Real behavior measurement • AI-first design • Pure observation**