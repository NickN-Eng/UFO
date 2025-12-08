# GPT-5-Mini with Azure AD Implementation Summary

## Overview

This document summarizes all changes made to support GPT-5-mini model with Azure AD authentication in the UFO project.

## Configuration Changes

### 1. Main Configuration (ufo/config/config.yaml)

Added complete Azure AD configuration for all three agents:

```yaml
HOST_AGENT:
  API_TYPE: "azure_ad"
  API_BASE: "https://nicholasniem-9000-resource.cognitiveservices.azure.com/"
  API_VERSION: "2024-12-01-preview"
  API_MODEL: "gpt-5-mini"
  API_DEPLOYMENT_ID: "gpt-5-mini"
  AAD_TENANT_ID: "5f8bc481-8908-47bf-9c84-c3ef37fe8c16"
  AAD_API_SCOPE: "https://cognitiveservices.azure.com/.default"
  AAD_API_SCOPE_BASE: "https://cognitiveservices.azure.com"
```

### 2. Configuration Template (ufo/config/config.yaml.template)

Added comprehensive examples for Azure AD setup with documentation.

### 3. Pricing Configuration (ufo/config/config_prices.yaml)

Added GPT-5-mini pricing:
```yaml
"openai/gpt-5-mini": {"input": 0.00025, "output": 0.002}
"azure/gpt-5-mini": {"input": 0.00025, "output": 0.002}
```

**Cost**: $0.25 per 1M input tokens, $2 per 1M output tokens

## Code Changes

### 1. Azure AD Scope Handling (ufo/llm/openai.py:323-330)

**Problem**: Code expected "api://..." format, but Azure Cognitive Services uses "https://..."

**Solution**: Added dual support for both standard Azure scopes and custom API app scopes:

```python
# Support both Azure Cognitive Services (standard) and custom API app scopes
if aad_api_scope_base.startswith("http://") or aad_api_scope_base.startswith("https://"):
    # Azure Cognitive Services scope (e.g., "https://cognitiveservices.azure.com")
    scope = aad_api_scope_base if aad_api_scope_base.endswith("/.default") else aad_api_scope_base + "/.default"
else:
    # Custom API app scope (original behavior for custom apps)
    api_scope_base = "api://" + aad_api_scope_base
    scope = api_scope_base + "/.default"
```

### 2. GPT-5 Model Parameter Handling (ufo/llm/openai.py:80-144)

**Problems**:
1. GPT-5 requires `max_completion_tokens` instead of `max_tokens`
2. GPT-5 doesn't support custom `temperature` values (only default: 1)
3. GPT-5 doesn't support custom `top_p` values

**Solution**: Automatic GPT-5 detection and parameter adaptation:

```python
# GPT-5 models require max_completion_tokens instead of max_tokens
# GPT-5 models also don't support custom temperature/top_p (only default value of 1)
is_gpt5_model = "gpt-5" in model.lower()
token_param_name = "max_completion_tokens" if is_gpt5_model else "max_tokens"

# Then conditionally include/exclude parameters:
if is_gpt5_model:
    # GPT-5 models don't support temperature/top_p parameters
    response = self.client.chat.completions.create(
        model=model,
        messages=messages,
        n=1,
        **{token_param_name: max_tokens},
        stream=stream,
        **kwargs,
    )
else:
    # GPT-4 and earlier models support all parameters
    response = self.client.chat.completions.create(
        model=model,
        messages=messages,
        n=1,
        temperature=temperature,
        **{token_param_name: max_tokens},
        top_p=top_p,
        stream=stream,
        **kwargs,
    )
```

## Debug Tools Created

### 1. debug/azure_ad_test.py

Comprehensive authentication testing script that:
- Tests Azure Identity package installation
- Detects available authentication methods (Azure CLI, Interactive Browser, Device Code)
- Implements 60-second timeout for hanging browser authentication
- Automatically falls back to Device Code authentication
- Tests actual Azure OpenAI API calls with GPT-5-mini
- Uses correct GPT-5 parameters (max_completion_tokens, no temperature)

**Usage**:
```bash
python debug/azure_ad_test.py
```

### 2. debug/check_auth_status.py

Quick status checker that:
- Checks Azure CLI installation and login status
- Verifies required Python packages
- Checks for token cache files
- Provides setup recommendations

**Usage**:
```bash
python debug/check_auth_status.py
```

### 3. debug/README.md

Documentation covering:
- Quick start guide
- Authentication methods
- Common issues and solutions
- Configuration details

### 4. debug/TROUBLESHOOTING.md

Comprehensive troubleshooting guide covering:
- GPT-5 model parameter errors
- Browser window not opening issue
- Azure CLI setup
- Device Code flow
- Permissions verification

## Authentication Flow

The UFO project now supports multiple authentication methods in this order:

1. **Azure CLI** (recommended for development)
   ```bash
   az login --tenant 5f8bc481-8908-47bf-9c84-c3ef37fe8c16
   ```

2. **Interactive Browser Broker** (Windows/macOS)
   - Uses Windows Authentication Broker (WAM) or macOS Keychain
   - May hang silently if broker is unavailable
   - 60-second timeout with automatic fallback

3. **Device Code** (most reliable fallback)
   - Manual browser login with code entry
   - Works in all environments
   - Used automatically if browser auth fails

## API Parameter Differences

| Parameter | GPT-4 | GPT-5 |
|-----------|-------|-------|
| Token limit | `max_tokens` | `max_completion_tokens` |
| Temperature | Any value (e.g., 0-2) | Only default (1) |
| Top-P | Any value (e.g., 0-1) | Only default (1) |

**Why?** GPT-5 models use complex multi-round reasoning internally that would be destabilized by external temperature control.

## Testing Steps

1. **Check authentication status**:
   ```bash
   python debug/check_auth_status.py
   ```

2. **Test Azure AD authentication and API access**:
   ```bash
   python debug/azure_ad_test.py
   ```

3. **Run UFO with GPT-5-mini**:
   ```bash
   python -m ufo --task "your task here"
   ```

## Success Indicators

When everything works correctly, you should see:

```
[OK] Successfully acquired token via Azure CLI (or Device Code)
  Token (first 50 chars): eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI...

[OK] AzureOpenAI client created successfully

[OK] SUCCESS! Chat completion received:
  Response: Hello
  Model: gpt-5-mini
  Usage: 7 prompt tokens, 1 completion tokens

[PASS] ALL TESTS PASSED!
```

## Required Packages

- `azure-identity` - Core authentication library
- `azure-identity-broker` - Optional, for enhanced browser authentication
- `msal` - Microsoft Authentication Library
- `openai` - OpenAI Python SDK (supports Azure OpenAI)

## Azure Permissions Required

Your Azure AD account must have one of these roles on the Azure OpenAI resource:

- **Cognitive Services OpenAI User** (for inference/chat)
- **Cognitive Services OpenAI Contributor** (full access)
- **Cognitive Services User** (general access)

## Files Modified

1. **ufo/llm/openai.py** - Azure AD scope handling + GPT-5 parameter support
2. **ufo/config/config.yaml** - Added Azure AD configuration with tenant ID
3. **ufo/config/config.yaml.template** - Added comprehensive examples
4. **ufo/config/config_prices.yaml** - Added GPT-5-mini pricing

## Files Created

1. **debug/azure_ad_test.py** - Comprehensive authentication test script
2. **debug/check_auth_status.py** - Quick status checker
3. **debug/README.md** - Debug tools documentation
4. **debug/TROUBLESHOOTING.md** - Troubleshooting guide
5. **debug/IMPLEMENTATION_SUMMARY.md** - This file

## Known Issues and Workarounds

### Issue: Interactive Browser Authentication Hangs

**Workaround**: The code now includes a 60-second timeout and automatically falls back to Device Code authentication.

### Issue: GPT-5 Parameter Errors

**Solution**: Code automatically detects GPT-5 models and uses correct parameters. No manual configuration needed.

## Future Considerations

1. **Model Detection**: Current detection uses simple string matching (`"gpt-5" in model.lower()`). Consider more robust version detection if needed.

2. **Reasoning Model Flag**: The code has a `REASONING_MODEL` flag that could be used for GPT-5 models, but currently they work without it due to the automatic detection.

3. **Temperature Configuration**: Since GPT-5 doesn't support custom temperature, consider documenting this in user-facing configuration guides.

4. **Token Cache Location**: Token cache files are stored in the current directory. Consider moving to a more permanent location (e.g., user's home directory).

## References

- [Azure OpenAI GPT-5 Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-5-models)
- [Azure Identity SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme)
- [Azure AD Authentication for Cognitive Services](https://learn.microsoft.com/en-us/azure/ai-services/authentication)
- [OpenAI Python SDK - Azure OpenAI](https://github.com/openai/openai-python#microsoft-azure-openai)
