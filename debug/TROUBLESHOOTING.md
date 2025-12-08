# Azure AD Authentication Troubleshooting Guide

## Issue: GPT-5 Model Issues

### Problem 1: Empty Response (Reasoning Token Exhaustion)

**Symptom:**
```
Response Content: '(empty)'
Content Length: 0
Usage: 11 prompt tokens, 10 completion tokens
Finish Reason: length
```

The API call succeeds, authentication works, but the response `content` is an empty string despite consuming completion tokens.

**Root Cause:**

GPT-5-mini is a **reasoning model** (similar to OpenAI's o1 models). It uses internal "reasoning tokens" to think through problems before generating output. With a low `max_completion_tokens` limit (e.g., 10-50), the model exhausts all tokens on internal reasoning and has none left for the visible response.

From [Microsoft documentation](https://community.openai.com/t/empty-incomplete-details-from-gpt-5-with-max-output-tokens/1355725) and [GitHub issues](https://github.com/openai/openai-python/issues/2546):
- Simple prompts can use **hundreds of reasoning tokens** before producing output
- With low token limits, you get `finish_reason: "length"` and empty content
- The model is working correctly - it just needs more tokens

**Solution:**

Two approaches to fix empty responses:

**Option 1: Increase Token Limit (Required)**

Increase `max_completion_tokens` to at least **500-1000**:

```yaml
# In ufo/config/config.yaml
MAX_TOKENS: 4000  # GPT-5 reasoning models need higher limits
```

**Option 2: Use Minimal Reasoning Effort (Recommended for Fast Responses)**

Set `reasoning_effort` to `"minimal"` to reduce reasoning tokens:

```yaml
# In ufo/config/config.yaml
REASONING_EFFORT: "minimal"  # Fastest, uses fewer reasoning tokens
```

**Options for reasoning_effort:**
- **"minimal"** - Uses very few or no reasoning tokens (fastest, best for simple queries)
- **"low"** - Light reasoning
- **"medium"** - Balanced (default)
- **"high"** - Maximum reasoning (slowest, best for complex problems)

**Why?** GPT-5 models spend tokens on:
1. **Internal reasoning** (thinking, planning) - can be 100-1000+ tokens depending on effort level
2. **Visible output** (the actual response) - what you see

Low token limits + high reasoning effort = empty responses.

**Best Practice:** Use `reasoning_effort="minimal"` for UI/chat applications and `"high"` for complex analysis tasks.

### Problem 2: Parameter Errors

**Error 1: max_tokens not supported**
```
Error code: 400 - {'error': {'message': "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead."}}
```

**Error 2: temperature not supported**
```
Error code: 400 - {'error': {'message': "Unsupported value: 'temperature' does not support 0 with this model. Only the default (1) value is supported."}}
```

**Root Cause:**

GPT-5 models have different API parameters than GPT-4 models:

1. **Token Parameter**: GPT-5 uses `max_completion_tokens` instead of `max_tokens`
2. **Temperature Parameter**: GPT-5 only supports the default temperature value (1), no custom values
3. **Top-P Parameter**: GPT-5 likely doesn't support custom `top_p` values either

This is because GPT-5 models use complex multi-round reasoning internally that would be destabilized by external temperature control.

**Solution:**

Both the debug script and UFO code have been updated to automatically detect GPT-5 models and use the correct parameters:

**In [ufo/llm/openai.py](../ufo/llm/openai.py):**
- Detects GPT-5 models by checking if "gpt-5" is in the model name
- Uses `max_completion_tokens` instead of `max_tokens`
- Excludes `temperature` and `top_p` parameters entirely
- Adds `reasoning_effort` parameter from config (minimal/low/medium/high)

**In [debug/azure_ad_test.py](azure_ad_test.py):**
- Uses `max_completion_tokens` for the test
- Removes `temperature` parameter
- Sets `reasoning_effort="low"` for faster test responses

No manual configuration changes needed - the code automatically adapts based on the model name.

### Problem 3: `reasoning_effort` Parameter

**What is reasoning_effort?**

The `reasoning_effort` parameter controls how long GPT-5 models spend thinking before responding. Available values:
- **minimal**: Fastest, minimal reasoning tokens (best for simple queries, UI/chat)
- **low**: Light reasoning
- **medium**: Balanced reasoning (default)
- **high**: Maximum reasoning (best for complex problems, analysis)

**Configuration:**

```yaml
# In ufo/config/config.yaml
REASONING_EFFORT: "medium"  # Change to "minimal" for faster responses
```

The UFO code automatically applies this parameter to all GPT-5 model API calls.

## Issue: Browser Window Not Opening

### Problem Description

When running the Azure AD authentication test, the script hangs at:
```
-> Attempting InteractiveBrowserBrokerCredential authentication...
  Initiating interactive authentication...
  [!] A browser window will open for you to sign in
```

**The browser never appears, and the script hangs indefinitely.**

### Root Cause

Based on research and testing, this is a known issue with `InteractiveBrowserBrokerCredential` on Windows:

1. **Windows Authentication Broker (WAM) Issues**: The broker may fail silently without showing any error
2. **Parent Window Handle Problems**: The console window handle may not work correctly in all environments
3. **Broker Component Unavailable**: WAM may not be properly configured or available on your system
4. **Silent Failures**: The `authenticate()` method hangs instead of timing out or raising an error

### Solutions

## Solution 1: Use Device Code Flow (RECOMMENDED)

The most reliable method that works in all environments.

### For UFO Project (Main Application)

Set the authentication method in your [config.yaml](../ufo/config/config.yaml):

```yaml
HOST_AGENT: {
  # ... other settings ...
  AAD_AUTH_METHOD: "device_code"  # Options: "device_code", "browser", "auto"
}

APP_AGENT: {
  # ... other settings ...
  AAD_AUTH_METHOD: "device_code"
}

EVALUATION_AGENT: {
  # ... other settings ...
  AAD_AUTH_METHOD: "device_code"
}
```

**Available options:**
- **"device_code"** (RECOMMENDED): Most reliable, requires manual browser login with code
- **"browser"**: Interactive browser authentication (may hang on some systems)
- **"auto"**: Automatic detection based on environment (tries browser first, may hang)

### For Test Script

**Run the test script** - it will automatically fall back to Device Code after 60 seconds:

```bash
python debug/azure_ad_test.py
```

Wait for the timeout, then you'll see:
```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code XXXXXXXXX to authenticate.
```

**Steps:**
1. Open browser manually
2. Go to https://microsoft.com/devicelogin
3. Enter the displayed code
4. Sign in with your Microsoft account
5. Return to terminal - authentication will complete automatically

## Solution 2: Install Azure CLI (EASIEST)

Azure CLI provides the most seamless experience:

**Install Azure CLI:**
- Download from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows
- Or use winget: `winget install Microsoft.AzureCLI`

**Login once:**
```bash
az login --tenant 5f8bc481-8908-47bf-9c84-c3ef37fe8c16
```

**Then run the test:**
```bash
python debug/azure_ad_test.py
```

The test will automatically use your Azure CLI credentials!

## Solution 3: Try Direct Browser Credential (Alternative)

If you want to force a browser-based flow, modify the UFO code to use `InteractiveBrowserCredential` instead of `InteractiveBrowserBrokerCredential`:

In [ufo/llm/openai.py](../ufo/llm/openai.py), around line 415, replace:
```python
identity = InteractiveBrowserBrokerCredential(...)
```

With:
```python
from azure.identity import InteractiveBrowserCredential
identity = InteractiveBrowserCredential(
    tenant_id=tenant_id,
    cache_persistence_options=token_cache_option,
)
```

**Note**: This opens a regular browser window instead of using the Windows broker.

## Why This Happens

### Technical Details

According to Microsoft documentation and community reports:

1. **Broker Authentication Requirements**:
   - Requires proper Windows Account Manager (WAM) setup
   - Needs correct parent window handle
   - May fail on certain Windows configurations

2. **Common Failure Scenarios**:
   - Windows 11 upgrade issues
   - Proxy/network configuration conflicts
   - Missing or outdated broker components
   - Terminal/console window handle incompatibility

3. **Silent Failure Behavior**:
   - `InteractiveBrowserBrokerCredential.authenticate()` may hang indefinitely
   - No error messages or exceptions are raised
   - Browser dialog never appears

### What the Fixed Test Script Does

The updated `azure_ad_test.py` now:

1. **Adds a 60-second timeout** to detect hanging authentication
2. **Runs authentication in a separate thread** to enable timeout detection
3. **Automatically falls back to DeviceCodeCredential** if browser auth fails
4. **Provides clear error messages** and next steps

## Verification Steps

After authentication succeeds, verify it worked:

```bash
# Check authentication status
python debug/check_auth_status.py

# Should show:
# [OK] azure-identity installed
# [OK] Token cache found
```

## Applying to UFO Project

Once device code authentication works in the test script, the **same authentication flow will work in UFO** because both use identical Azure Identity libraries.

### For UFO to use Device Code automatically:

The UFO project code already supports this! The authentication chain in [ufo/llm/openai.py](../ufo/llm/openai.py) will:

1. Try Azure CLI first (if installed)
2. Try Interactive Browser Broker (may hang)
3. Fall back to Device Code (will work!)

However, to **skip the hanging step**, consider modifying UFO to use Device Code directly:

In [ufo/llm/openai.py](../ufo/llm/openai.py) around line 397-428, you can comment out the Interactive Browser Broker section and go straight to Device Code.

## References

- [Azure Identity Broker Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-broker-readme?view=azure-python)
- [Using MSAL Python with Web Account Manager](https://learn.microsoft.com/en-us/entra/msal/python/advanced/wam)
- [InteractiveBrowserBrokerCredential API Reference](https://learn.microsoft.com/en-us/python/api/azure-identity-broker/azure.identity.broker.interactivebrowserbrokercredential?view=azure-python)
- [Additional Authentication Methods](https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/additional-methods)

## Quick Reference Commands

```bash
# Check status
python debug/check_auth_status.py

# Run authentication test
python debug/azure_ad_test.py

# Install Azure CLI (Windows)
winget install Microsoft.AzureCLI

# Login with Azure CLI
az login --tenant 5f8bc481-8908-47bf-9c84-c3ef37fe8c16

# Test Azure OpenAI access after auth
python debug/azure_ad_test.py
```

## Expected Timeline

- **Device Code Flow**: 2-3 minutes (manual browser interaction)
- **Azure CLI**: 1 minute (one-time setup, then automatic)
- **Browser Broker**: May hang indefinitely (not recommended)

## Success Indicators

When authentication works, you'll see:

```
[OK] Successfully acquired token via Device Code
  Token (first 50 chars): eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI...

[OK] AzureOpenAI client created successfully

[OK] SUCCESS! Chat completion received:
  Response: Hello
  Model: gpt-5-mini
  Usage: 7 prompt tokens, 1 completion tokens

[PASS] ALL TESTS PASSED!
```

## Still Having Issues?

If authentication continues to fail:

1. **Verify Azure Permissions**:
   - Go to Azure Portal → Your OpenAI Resource → Access Control (IAM)
   - Ensure you have "Cognitive Services OpenAI User" role

2. **Verify Deployment Exists**:
   - Go to Azure OpenAI Studio: https://oai.azure.com/
   - Check that deployment "gpt-5-mini" exists and is active

3. **Check Network**:
   - Ensure you can access `*.cognitiveservices.azure.com`
   - Disable VPN/proxy temporarily

4. **Check Tenant ID**:
   - Verify: `5f8bc481-8908-47bf-9c84-c3ef37fe8c16`
   - Must match your Azure subscription tenant
