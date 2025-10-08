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

**Inspect elements:**
```bash
cursorflow inspect --base-url http://localhost:3000 --selector ".message-item"
cursorflow count --base-url http://localhost:3000 --selector ".message-item"
```

**View timeline:**
```bash
cursorflow timeline --session session_12345
```

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
