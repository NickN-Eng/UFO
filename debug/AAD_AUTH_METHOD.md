# Azure AD Authentication Method Configuration

## Overview

The UFO project now supports configurable Azure AD authentication methods, allowing you to choose between Device Code, Interactive Browser, or automatic detection.

## Configuration

### Adding to config.yaml

For each agent that uses Azure AD authentication, add the `AAD_AUTH_METHOD` parameter:

```yaml
HOST_AGENT: {
  VISUAL_MODE: True,
  REASONING_MODEL: False,
  API_TYPE: "azure_ad",
  API_BASE: "https://YOUR-RESOURCE.cognitiveservices.azure.com/",
  API_VERSION: "2024-12-01-preview",
  API_MODEL: "gpt-5-mini",
  API_DEPLOYMENT_ID: "gpt-5-mini",
  AAD_TENANT_ID: "YOUR_TENANT_ID",
  AAD_API_SCOPE: "https://cognitiveservices.azure.com/.default",
  AAD_API_SCOPE_BASE: "https://cognitiveservices.azure.com",
  AAD_AUTH_METHOD: "device_code"  # NEW PARAMETER
}
```

## Available Authentication Methods

### 1. Device Code (RECOMMENDED - Default)

**Value:** `"device_code"`

**How it works:**
1. You run your UFO application
2. A code is displayed in the terminal (e.g., "ABC123XYZ")
3. You open a browser to https://microsoft.com/devicelogin
4. You enter the code
5. You sign in with your Microsoft account
6. Return to terminal - authentication completes automatically

**Advantages:**
- Most reliable across all environments
- Works with MFA/2FA
- No silent failures or hanging
- Works through proxies
- Works in restricted environments

**Disadvantages:**
- Requires manual browser interaction
- Not fully automated

**When to use:**
- Production environments
- When reliability is critical
- When Interactive Browser hangs
- In restricted network environments

### 2. Interactive Browser

**Value:** `"browser"`

**How it works:**
1. You run your UFO application
2. A browser window opens automatically
3. You sign in with your Microsoft account
4. Browser closes, authentication completes

**Advantages:**
- Seamless user experience when it works
- No code entry required

**Disadvantages:**
- May hang silently on some Windows configurations
- Requires Windows Account Manager (WAM) to work properly
- Can fail without error messages
- May not work through proxies

**When to use:**
- Development environments where you've tested it works
- When you want the most seamless experience
- On properly configured Windows/macOS systems

### 3. Auto (Automatic Detection)

**Value:** `"auto"` or omit the parameter

**How it works:**
1. If Azure CLI is installed and logged in: Uses Azure CLI credentials
2. Otherwise, on Windows/macOS: Tries Interactive Browser
3. If browser fails: Falls back to Device Code

**Advantages:**
- Intelligent selection based on environment
- Good for mixed environments

**Disadvantages:**
- May hang when trying Interactive Browser first
- Less predictable behavior

**When to use:**
- When you have Azure CLI installed (`az login`)
- Mixed environments with different user setups
- When you want the system to decide

## Implementation Details

### How the Parameter Works

The `AAD_AUTH_METHOD` parameter is passed through the authentication chain:

1. **Config file** → User specifies method in [config.yaml](../ufo/config/config.yaml)
2. **OpenAIService** → Reads `AAD_AUTH_METHOD` from config
3. **get_openai_client()** → Passes to token provider
4. **get_aad_token_provider()** → Sets authentication flags:
   - `device_code` → `use_device_code=True`, `use_broker_login=False`
   - `browser` → `use_device_code=False`, `use_broker_login=True`
   - `auto` → Both `None`, uses implicit mode

### Code Changes

**Modified files:**
- [ufo/llm/openai.py](../ufo/llm/openai.py) - Added `aad_auth_method` parameter
- [ufo/config/config.yaml](../ufo/config/config.yaml) - Set default to `device_code`
- [ufo/config/config.yaml.template](../ufo/config/config.yaml.template) - Documented parameter

## Changing Authentication Methods

### Quick Change

Edit [ufo/config/config.yaml](../ufo/config/config.yaml):

```yaml
# Change from:
AAD_AUTH_METHOD: "device_code"

# To:
AAD_AUTH_METHOD: "browser"
```

### Per-Agent Configuration

You can use different methods for different agents:

```yaml
HOST_AGENT: {
  AAD_AUTH_METHOD: "device_code"  # Use Device Code for Host Agent
}

APP_AGENT: {
  AAD_AUTH_METHOD: "auto"  # Use automatic detection for App Agent
}

EVALUATION_AGENT: {
  AAD_AUTH_METHOD: "browser"  # Use browser for Evaluation Agent
}
```

## Troubleshooting

### Device Code Not Appearing

**Problem:** No code displayed when using Device Code method

**Solution:** Check that `AAD_AUTH_METHOD` is set to `"device_code"` in config

### Browser Hangs

**Problem:** Application hangs when using `"browser"` or `"auto"`

**Solution:** Change to `"device_code"`:
```yaml
AAD_AUTH_METHOD: "device_code"
```

### Invalid Authentication Method

**Problem:** Error about invalid authentication method

**Solution:** Valid values are: `"device_code"`, `"browser"`, `"auto"`

## Testing Authentication

Use the debug script to test different methods:

```bash
python debug/azure_ad_test.py
```

The script will prompt you to choose an authentication method and test it.

## Compatibility

- **Windows:** All methods supported
- **macOS:** All methods supported
- **Linux:** Device Code recommended (browser may require additional setup)
- **WSL:** Device Code recommended
- **Docker/Containers:** Device Code only

## Default Behavior

If `AAD_AUTH_METHOD` is not specified:
- **Default value:** `"device_code"` (most reliable)
- **Original behavior:** `"auto"` (automatic detection)

The default has been changed to Device Code for maximum reliability across all environments.

## Migration Guide

### From Previous Version

If you're upgrading from a version without `AAD_AUTH_METHOD`:

1. **No action required** - Default is now Device Code
2. **To use old behavior** - Set `AAD_AUTH_METHOD: "auto"`
3. **To force browser** - Set `AAD_AUTH_METHOD: "browser"`

### Example Migration

**Old config (no AAD_AUTH_METHOD):**
```yaml
HOST_AGENT: {
  API_TYPE: "azure_ad",
  AAD_TENANT_ID: "...",
  AAD_API_SCOPE_BASE: "..."
}
```

**New config (explicit Device Code):**
```yaml
HOST_AGENT: {
  API_TYPE: "azure_ad",
  AAD_TENANT_ID: "...",
  AAD_API_SCOPE_BASE: "...",
  AAD_AUTH_METHOD: "device_code"  # NEW
}
```

## References

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting guide
- [Azure AD Authentication Test](azure_ad_test.py) - Test script
- [ufo/llm/openai.py](../ufo/llm/openai.py) - Implementation
