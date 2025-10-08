# Universal CursorFlow - Usage Guide

## 🌌 **Built for the Universe**

This testing framework adapts to **any web architecture** - use the same commands and concepts whether you're testing legacy Perl systems, modern React apps, or anything in between.

## 📋 **Action Format Reference**

### **Valid Action Formats**

CursorFlow supports multiple action formats for flexibility:

**Simple format (action type as key):**
```json
{"navigate": "/dashboard"}
{"click": ".button"}
{"wait": 2}
{"screenshot": "page-loaded"}
```

**Configuration format (action with options):**
```json
{"click": {"selector": ".button"}}
{"fill": {"selector": "#username", "value": "test@example.com"}}
{"wait_for": {"selector": ".loaded", "timeout": 5000}}
```

**Explicit type format (for programmatic generation):**
```json
{"type": "click", "selector": ".button"}
{"type": "fill", "selector": "#email", "value": "user@test.com"}
```

### **Supported Action Types**

**CursorFlow-specific:**
- `navigate` - Navigate to URL or path
- `screenshot` - Capture screenshot with comprehensive data
- `authenticate` - Use authentication handler

**Any Playwright Page method works:**
- `click`, `dblclick`, `hover`, `tap`
- `fill`, `type`, `press`
- `check`, `uncheck`, `select_option`
- `focus`, `blur`
- `drag_and_drop`
- `wait_for_selector`, `wait_for_load_state`, `wait_for_timeout`
- `goto`, `reload`, `go_back`, `go_forward`
- `evaluate`, `route`, `expose_function`
- And 80+ more Playwright methods

**Full API:** https://playwright.dev/python/docs/api/class-page

**Pass-Through Architecture:** CursorFlow provides smart defaults but doesn't limit you. Any Playwright Page method works, and you can configure ANY browser/context option. This makes CursorFlow forward-compatible with future Playwright releases.

**Configuration Pass-Through:**
```json
{
  "browser_config": {
    "browser_launch_options": {
      "devtools": true,
      "channel": "chrome",
      "proxy": {"server": "http://proxy:3128"}
    }
  },
  "context_options": {
    "color_scheme": "dark",
    "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
    "timezone_id": "America/New_York"
  }
}
```

See Playwright docs for all options:
- Browser: https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch
- Context: https://playwright.dev/python/docs/api/class-browser#browser-new-context

### **Complete Workflow Example**

```json
[
  {"navigate": "/login"},
  {"wait_for": "#login-form"},
  {"fill": {"selector": "#username", "value": "admin"}},
  {"fill": {"selector": "#password", "value": "pass123"}},
  {"click": "#submit-button"},
  {"wait_for": ".dashboard"},
  {"screenshot": "logged-in"},
  {"validate": {"selector": ".error", "exists": false}}
]
```

## 🚀 **CLI Commands**

### **Testing Commands**

**Basic test:**
```bash
cursorflow test --base-url http://localhost:3000 --path /page
```

**Inline actions:**
```bash
cursorflow test --base-url http://localhost:3000 \
  --path /login \
  --wait-for "#login-form" \
  --fill "#username=admin" \
  --fill "#password=secret" \
  --click "#submit" \
  --screenshot "logged-in" \
  --show-console \
  --open-trace
```

**Wait strategies:**
```bash
--wait-for ".selector"              # Wait for element
--wait-timeout 60                   # Timeout in seconds
--wait-for-network-idle             # Wait for no network activity
```

**Output options:**
```bash
--show-console                      # Show errors and warnings
--show-all-console                  # Show all console messages
--open-trace                        # Auto-open Playwright trace
--quiet                             # JSON output only
```

### **Authenticated Session Management**

**Requires auth_config** - Session persistence is designed for testing authenticated pages.

**Configure authentication in `.cursorflow/config.json`:**
```json
{
  "base_url": "http://localhost:3000",
  "auth": {
    "method": "form",
    "username": "test@example.com",
    "password": "testpass",
    "username_selector": "#email",
    "password_selector": "#password",
    "submit_selector": "#login-button",
    "session_storage": ".cursorflow/sessions/"
  }
}
```

**Then use session save/restore:**
```bash
# Login once and save session
cursorflow test --base-url http://localhost:3000 \
  --path /login \
  --save-session "authenticated"
# AuthHandler logs in, saves cookies + localStorage + sessionStorage

# Reuse saved session (skip login)
cursorflow test --base-url http://localhost:3000 \
  --path /dashboard \
  --use-session "authenticated"
# AuthHandler restores saved state, already logged in

# Manage sessions
cursorflow sessions list
cursorflow sessions delete "name"
```

**Authentication Methods:**
- `form` - Username/password form submission
- `cookies` - Pre-configured cookies
- `headers` - HTTP header authentication (Bearer tokens, etc.)

**Without auth_config:** Session flags will be ignored (testing public pages doesn't need session persistence).

### **Quick Commands**

**Rerun last test:**
```bash
cursorflow rerun
cursorflow rerun --click ".other-element"
```

**Inspect elements (comprehensive data):**
```bash
# Inspect with full element analysis
cursorflow inspect --base-url http://localhost:3000 --selector "#messages-panel"

# Inspect with custom path
cursorflow inspect -u http://localhost:3000 -p /dashboard -s ".card"

# Show all computed CSS properties
cursorflow inspect -u http://localhost:3000 -s ".button" --verbose
```

**Measure element dimensions (surgical precision):**
```bash
# Quick dimension check
cursorflow measure --base-url http://localhost:3000 --selector "#panel"

# Multiple elements at once
cursorflow measure -u http://localhost:3000 -s "#panel1" -s "#panel2"

# Show all CSS properties
cursorflow measure -u http://localhost:3000 -s ".card" --verbose
```

**Count elements:**
```bash
cursorflow count --base-url http://localhost:3000 --selector ".message-item"
```

**View timeline:**
```bash
cursorflow timeline --session session_12345
```

### **Element Analysis Commands**

CursorFlow provides powerful element inspection tools for CSS debugging and layout analysis.

#### **`inspect` - Comprehensive Element Analysis**

The `inspect` command captures full page data and displays detailed element information:

**What you get:**
- **Computed CSS** - All browser-computed styles (display, position, flex, dimensions, etc.)
- **Dimensions** - Rendered width, height, and position
- **Selectors** - Unique CSS selector for targeting
- **Accessibility** - Role, interactive state, ARIA attributes
- **Visual Context** - Visibility, z-index, viewport position
- **Screenshot** - Visual reference saved to artifacts

**Example output:**
```
═══ Element 1/1 ═══
Tag:       div
ID:        #messages-panel
Classes:   .console-panel.message-list-panel

📐 Dimensions:
   Position:  x=320, y=73
   Size:      532w × 927h

🎨 Key CSS Properties:
   display:   flex
   flex:      1 1 0%
   flex-basis: 260px
   width:     532px

♿ Accessibility:
   Role:         None
   Interactive:  ❌

👁️  Visual Context:
   Visibility:   ✅ Visible

📸 Screenshot saved: .cursorflow/artifacts/screenshots/inspection.png
```

**Use cases:**
- Debug CSS layout issues
- Verify flex/grid calculations
- Check computed vs authored styles
- Find optimal selectors for automation
- Analyze element visibility and positioning

#### **`measure` - Surgical Dimension Checking**

The `measure` command provides quick dimension and CSS checks without verbose output:

**What you get:**
- **Rendered dimensions** - Actual width × height on screen
- **Position** - x, y coordinates
- **Key CSS** - display, width, flex properties
- **Multiple elements** - Measure several at once
- **All CSS (--verbose)** - Complete computed styles (76+ properties)

**Example output:**
```
h1
  📐 Rendered:  600w × 38h
  📍 Position:  x=420, y=133
  🎨 Display:   block
  📦 CSS Width: 600px
  🔧 Flex:      0 1 auto
  💡 Use --verbose to see all 76 CSS properties
```

**Use cases:**
- Verify CSS changes took effect
- Check flex layout calculations
- Compare dimensions across breakpoints
- Quick dimension reference during development
- Validate responsive behavior

#### **Comparison: inspect vs measure**

| Feature | `inspect` | `measure` |
|---------|-----------|-----------|
| **Purpose** | Comprehensive analysis | Quick dimension check |
| **Output** | Detailed, multi-section | Concise, focused |
| **Screenshot** | Always included | Captured but not shown |
| **Use when** | Debugging complex CSS | Verifying dimensions |
| **Speed** | ~3 seconds | ~2 seconds |
| **Multiple elements** | One at a time | Multiple with `-s` flags |

**Workflow example:**
```bash
# 1. Use measure for quick check
cursorflow measure -u http://localhost:3000 -s "#panel"
# Output: 260w × 900h

# 2. If dimensions seem wrong, use inspect for full analysis
cursorflow inspect -u http://localhost:3000 -s "#panel" --verbose
# Output: Full CSS, accessibility, visual context, screenshot

# 3. Make CSS changes based on insights

# 4. Verify with measure again
cursorflow measure -u http://localhost:3000 -s "#panel"
# Output: 532w × 900h ✅ Fixed!
```

### **Visual Comparison Commands**

CursorFlow provides visual comparison tools for iterating toward design specifications through pure measurement.

#### **`compare-mockup` - Visual Design Comparison**

Compare a design mockup against your work-in-progress implementation:

**What you get (pure data)**:
- **Screenshots** - Both mockup and implementation captured
- **Visual diff images** - Pixel-by-pixel difference highlighting
- **Similarity percentage** - Quantified visual match (0-100%)
- **Element position data** - X, Y coordinates for both versions
- **Size measurements** - Width, height comparisons
- **CSS property data** - Computed styles for matching elements

**Philosophy**: CursorFlow observes both realities (mockup + implementation) and provides measurements. Cursor analyzes the data and decides what changes to make.

**Basic usage**:
```bash
cursorflow compare-mockup https://mockup.example.com/dashboard \
  --base-url http://localhost:3000 \
  --output comparison-results.json
```

**With custom actions**:
```bash
cursorflow compare-mockup https://mockup.example.com/dashboard \
  --base-url http://localhost:3000 \
  --mockup-actions '[{"navigate": "/dashboard"}]' \
  --implementation-actions '[{"navigate": "/dashboard"}, {"wait_for": "#main-content"}]'
```

**With multiple viewports**:
```bash
cursorflow compare-mockup https://mockup.example.com \
  --base-url http://localhost:3000 \
  --viewports '[
    {"width": 1440, "height": 900, "name": "desktop"},
    {"width": 768, "height": 1024, "name": "tablet"}
  ]'
```

**Output structure**:
```json
{
  "comparison_id": "mockup_comparison_123456",
  "mockup_url": "https://mockup.example.com",
  "implementation_url": "http://localhost:3000",
  "summary": {
    "average_similarity": 87.73,
    "viewports_tested": 2,
    "similarity_by_viewport": [
      {"viewport": "desktop", "similarity": 89.5},
      {"viewport": "tablet", "similarity": 85.96}
    ]
  },
  "results": [
    {
      "viewport": {"width": 1440, "height": 900, "name": "desktop"},
      "mockup_screenshot": "path/to/mockup.png",
      "implementation_screenshot": "path/to/impl.png",
      "visual_diff": {
        "similarity_score": 89.5,
        "different_pixels": 45000,
        "total_pixels": 1296000,
        "diff_image": "path/to/diff.png",
        "highlighted_diff": "path/to/highlighted.png"
      },
      "layout_analysis": {
        "mockup_elements": 45,
        "implementation_elements": 52,
        "differences": [...]
      }
    }
  ]
}
```

**Use cases**:
- Compare implementation to Figma exports
- Verify design system component accuracy
- Measure progress toward design specifications
- Document visual differences for stakeholders

#### **`iterate-mockup` - CSS Iteration with Measurement**

Test multiple CSS changes and observe which gets closer to the mockup:

**Basic usage**:
```bash
cursorflow iterate-mockup https://mockup.example.com/dashboard \
  --base-url http://localhost:3000 \
  --css-improvements '[
    {"name": "spacing-fix", "css": ".header { padding: 2rem; }"},
    {"name": "color-adjust", "css": ".btn { background: #007bff; }"}
  ]'
```

**What it does**:
1. Captures baseline similarity
2. Temporarily injects each CSS change
3. Observes the REAL rendered result
4. Captures similarity for each variation
5. Provides measurements for Cursor to analyze

**Output**: Similarity data for each CSS variation (Cursor decides which to apply)

### **Artifact Management**

CursorFlow generates screenshots, traces, and session data. Clean up regularly:

**Clean old artifacts (>7 days):**
```bash
cursorflow cleanup --artifacts --old-only --yes
```

**Clean everything:**
```bash
cursorflow cleanup --all --yes
```

**Preview first:**
```bash
cursorflow cleanup --all --dry-run
```

**Best practices:**
- Run `cleanup --artifacts --old-only --yes` weekly
- Always use `--yes` for autonomous/CI operation
- Use `--dry-run` to preview before deleting
- Clean sessions periodically: `cleanup --sessions --yes`

**Typical growth:** 50-100MB/day light usage, 500MB-1GB/day heavy usage

### **Visual Comparison Commands**

CursorFlow provides mockup comparison for visual iteration - comparing your implementation to design specifications through pure data collection.

#### **compare-mockup - Visual Measurement**

Compare two URLs and get quantified similarity data:

```bash
# Basic comparison
cursorflow compare-mockup "https://mockup.example.com" \
  --base-url http://localhost:3000

# With custom actions
cursorflow compare-mockup "https://mockup.example.com" \
  --base-url http://localhost:3000 \
  --implementation-actions '[{"navigate": "/dashboard"}]'

# Multiple viewports
cursorflow compare-mockup "https://mockup.example.com" \
  --base-url http://localhost:3000 \
  --viewports '[{"width": 1440, "height": 900, "name": "desktop"}, {"width": 375, "height": 667, "name": "mobile"}]'
```

**Output Data Structure**:
```json
{
  "comparison_id": "mockup_comparison_123456",
  "mockup_url": "https://mockup.example.com",
  "implementation_url": "http://localhost:3000",
  "results": [
    {
      "viewport": {"width": 1440, "height": 900, "name": "desktop"},
      "mockup_screenshot": "path/to/mockup.png",
      "implementation_screenshot": "path/to/impl.png",
      "visual_diff": {
        "diff_image": "path/to/diff.png",
        "highlighted_diff": "path/to/highlighted.png",
        "similarity_score": 87.3,
        "different_pixels": 45230,
        "total_pixels": 1296000
      }
    }
  ],
  "summary": {
    "average_similarity": 87.3,
    "viewports_tested": 1,
    "similarity_by_viewport": [...]
  }
}
```

**Philosophy**: Pure data collection - provides measurements, Cursor interprets them.

#### **iterate-mockup - CSS Experimentation**

Test multiple CSS variations and observe real outcomes:

```bash
# Create CSS improvements JSON
cat > improvements.json << 'EOF'
[
  {
    "name": "fix-spacing",
    "css": ".container { padding: 2rem; gap: 1.5rem; }"
  },
  {
    "name": "adjust-colors",
    "css": ".btn-primary { background: #007bff; }"
  }
]
EOF

# Run iteration
cursorflow iterate-mockup "https://mockup.example.com" \
  --base-url http://localhost:3000 \
  --css-improvements improvements.json
```

**What it does**:
1. Captures baseline comparison
2. Temporarily injects each CSS variation
3. Captures screenshot of REAL outcome
4. Measures similarity for each variation
5. Provides quantified data for each experiment

**Output**: Similarity percentages for each CSS variation, Cursor decides which to apply.

**Use case**: Rapid CSS experimentation with quantified feedback.

## ⚡ **Quick Usage Examples**

### **OpenSAS/Mod_Perl (Our Current Project)**
```bash
# Test message console with staging server logs
cursor-test test message-console \
  --framework mod_perl \
  --base-url https://staging.resumeblossom.com \
  --logs ssh \
  --params orderid=6590532419829

# Auto-detect and test
cd /path/to/opensas
cursor-test auto-test --environment staging
```

### **React Application** 
```bash
# Test React dashboard with local logs
cursor-test test user-dashboard \
  --framework react \
  --base-url http://localhost:3000 \
  --logs local \
  --params userId=123

# Test Next.js app
cursor-test test admin-panel \
  --framework react \
  --base-url http://localhost:3000 \
  --workflows auth,data_load,interaction
```

### **PHP/Laravel System**
```bash
# Test with Docker container logs
cursor-test test admin-users \
  --framework php \
  --base-url https://app.example.com \
  --logs docker \
  --params token=abc123
```

### **Django Application**
```bash
# Test with systemd logs
cursor-test test blog-editor \
  --framework django \
  --base-url http://localhost:8000 \
  --logs systemd \
  --params postId=456
```

## 🔧 **Installation & Setup**

### **1. Install the Framework**
```bash
# Install universal testing agent
pip install cursorflow
playwright install chromium

# Or install from source
git clone /path/to/cursorflow
cd cursorflow
pip install -e .
```

### **2. Initialize Any Project**
```bash
# Auto-detect framework and create config
cursor-test init . --framework auto-detect

# Or specify framework manually
cursor-test init . --framework mod_perl
cursor-test init . --framework react
cursor-test init . --framework php
```

### **3. Configure for Your Environment**
Edit the generated `cursor-test-config.json`:

```json
{
  "framework": "mod_perl",
  "environments": {
    "local": {
      "base_url": "http://localhost:8080",
      "logs": "local",
      "log_paths": {"app": "logs/app.log"}
    },
    "staging": {
      "base_url": "https://staging.example.com", 
      "logs": "ssh",
      "ssh_config": {
        "hostname": "staging-server",
        "username": "deploy",
        "key_filename": "~/.ssh/staging_key"
      },
      "log_paths": {
        "apache_error": "/var/log/httpd/error_log"
      }
    }
  }
}
```

## 📋 **Common Test Patterns**

### **Smoke Testing (Any Framework)**
```bash
# Test basic functionality
cursor-test test component-name --workflows smoke_test

# Test all components
cursor-test auto-test
```

### **Debugging Specific Issues**
```bash
# Test with verbose logging
cursor-test test component-name --verbose --workflows load,ajax,interaction

# Focus on specific functionality
cursor-test test message-console --workflows modal_test --params orderid=123
```

### **Performance Testing**
```bash
# Monitor performance during test
cursor-test test dashboard --workflows load,data_refresh --capture-performance

# Continuous monitoring
cursor-test monitor critical-component --interval 300
```

## 🎯 **Framework-Specific Features**

### **Mod_Perl/OpenSAS Features**
- **AJAX Authentication**: Automatically handles pid/hash/timestamp
- **Component Loading**: Waits for OpenSAS component initialization
- **Perl Error Detection**: Recognizes compilation errors, missing functions
- **Database Error Correlation**: Matches DBD::mysql errors with actions

### **React Features**
- **Component Mounting**: Waits for React component lifecycle
- **State Management**: Monitors Redux/Context state changes
- **API Integration**: Tracks fetch requests and responses
- **Hydration Detection**: Identifies SSR hydration issues

### **PHP Features**
- **Laravel Routing**: Handles Laravel route patterns
- **Eloquent Errors**: Detects ORM and database issues
- **Blade Templates**: Monitors template rendering errors
- **Session Management**: Tracks authentication state

## 📊 **Understanding Test Results**

### **Success Indicators**
- `✅ PASSED` - All workflows completed without critical issues
- Low error count in correlations
- No failed network requests
- Performance metrics within acceptable ranges

### **Failure Indicators**
- `❌ FAILED` - Critical issues found or workflows failed
- High correlation confidence between browser actions and server errors
- Console errors or failed network requests
- Performance degradation

### **Report Sections**
1. **Test Summary** - Overview of test execution
2. **Critical Issues** - Problems requiring immediate attention
3. **Recommendations** - Suggested fixes and improvements
4. **Workflow Results** - Step-by-step execution details
5. **Performance Metrics** - Timing and resource usage
6. **Debug Information** - Raw data for deep debugging

## 🛠️ **Advanced Usage**

### **Custom Test Definitions**
Create `test_definitions/component-name.yaml`:

```yaml
my_component:
  framework: react  # or mod_perl, php, django
  
  workflows:
    custom_workflow:
      - navigate: {params: {id: "123"}}
      - wait_for: "[data-testid='loaded']"
      - click: {selector: "#action-button"}
      - validate: {selector: ".success", exists: true}
      
  assertions:
    - selector: "#main-content"
      not_empty: true
    - api_response: "/api/data"
      status: 200
```

### **Programmatic Usage**
```python
from cursor_testing_agent import TestAgent

# Any framework with same API
agent = TestAgent('react', 'http://localhost:3000', logs='local')
results = await agent.test('user-dashboard', {'userId': '123'})

# Chain multiple tests
components = ['login', 'dashboard', 'profile']
for component in components:
    result = await agent.test(component)
    if not result['success']:
        print(f"❌ {component} failed")
        break
```

### **Integration with CI/CD**
```yaml
# .github/workflows/ui-tests.yml
- name: Run UI Tests
  run: |
    cursor-test auto-test --environment staging
    cursor-test test critical-component --workflows full
```

## 🔍 **Troubleshooting**

### **Common Issues**
- **SSH Connection Failed**: Check SSH config and key permissions
- **Log Files Not Found**: Verify log paths exist and are readable
- **Browser Launch Failed**: Reinstall Playwright browsers
- **Framework Not Detected**: Manually specify framework with `--framework`

### **Debug Commands**
```bash
# Test SSH connection
ssh deploy@staging-server "echo test"

# Verify log files
ssh deploy@staging-server "tail -5 /var/log/httpd/error_log"

# Test browser automation
python -c "from cursor_testing_agent import TestAgent; print('✅ Import successful')"
```

## 🎯 **Best Practices**

### **For Any Framework**
1. **Start with smoke tests** to catch basic issues
2. **Use environment-specific configs** for different deployment stages
3. **Monitor logs during active development** to catch issues early
4. **Create custom workflows** for your specific user journeys

### **For Team Usage**
1. **Share config files** across team members
2. **Standardize test definitions** for consistency
3. **Use in CI/CD pipelines** for automated quality gates
4. **Generate reports** for debugging sessions

## 🚀 **Scaling Across Projects**

### **Single Developer, Multiple Projects**
```bash
# Same tool, different projects
cd /path/to/react-project && cursor-test auto-test
cd /path/to/opensas-project && cursor-test auto-test  
cd /path/to/laravel-project && cursor-test auto-test
```

### **Team with Mixed Tech Stack**
```bash
# Everyone uses same commands regardless of tech stack
cursor-test test login-component     # Works for React
cursor-test test message-console     # Works for Mod_Perl  
cursor-test test admin-panel         # Works for PHP
```

**The power**: Learn once, test everywhere! 🌌

## 💡 **Success Stories**

**Scenario 1**: Debug OpenSAS AJAX issues
- **Before**: Manual clicking + SSH terminal + guesswork
- **After**: `cursor-test test message-console` → automatic correlation + fix recommendations

**Scenario 2**: Test React component across environments  
- **Before**: Manual testing on local, staging, production
- **After**: `cursor-test test component --environment staging` → consistent testing everywhere

**Scenario 3**: Onboard new team member
- **Before**: Complex setup docs for each framework
- **After**: `cursor-test init .` → auto-configured testing for any project

**The vision**: Universal testing that scales across frameworks, environments, and teams! 🚀✨
