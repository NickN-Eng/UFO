# Azure AD Authentication Debug Tool

This folder contains a debugging script to test Azure AD authentication for Azure OpenAI, using the same configuration as your UFO project.

## Files

- `azure_ad_test.py` - Main debugging script with detailed logging

## Quick Start

Run the test script:

```bash
python debug/azure_ad_test.py
```

## What This Script Tests

1. **Package Installation** - Verifies all required Azure Identity packages
2. **Authentication Method Detection** - Checks which auth methods are available
3. **Token Provider Creation** - Attempts to authenticate and get a token
4. **Azure OpenAI Connection** - Tests actual API call to your deployment
5. **Permissions Check** - Provides guidance on verifying Azure permissions

## Expected Output

The script will show detailed progress through each step:

```
████████████████████████████████████████████████████████████████████████████████
  AZURE AD AUTHENTICATION TEST FOR AZURE OPENAI
  Testing UFO Project Configuration
████████████████████████████████████████████████████████████████████████████████

Configuration:
  Tenant ID: 5f8bc481-8908-47bf-9c84-c3ef37fe8c16
  Endpoint: https://nicholasniem-9000-resource.cognitiveservices.azure.com/
  Model: gpt-5-mini
  ...

[Detailed step-by-step output with ✓ or ✗ for each test]
```

## Authentication Methods Tested

The script will try these methods in order:

1. **Azure CLI** (`az login`) - If Azure CLI is installed
2. **Interactive Browser** - Opens browser for login (Windows/macOS)
3. **Device Code** - Provides code for manual login

## Common Issues and Solutions

### Issue: "azure-identity package not installed"
**Solution:**
```bash
pip install azure-identity azure-identity-broker
```

### Issue: "Azure CLI authentication failed"
**Solution:**
```bash
az login --tenant 5f8bc481-8908-47bf-9c84-c3ef37fe8c16
```

### Issue: "AuthenticationError" or "PermissionDenied"
**Solution:**
- Go to Azure Portal → Your OpenAI Resource → Access Control (IAM)
- Ensure your account has "Cognitive Services OpenAI User" role

### Issue: "DeploymentNotFound" or "model 'gpt-5-mini' not found"
**Solution:**
- Go to Azure OpenAI Studio: https://oai.azure.com/
- Create a deployment named "gpt-5-mini" using the gpt-5-mini model

## Configuration

The script uses these settings (matching your UFO config):

```python
TENANT_ID = "5f8bc481-8908-47bf-9c84-c3ef37fe8c16"
AZURE_ENDPOINT = "https://nicholasniem-9000-resource.cognitiveservices.azure.com/"
API_VERSION = "2024-12-01-preview"
MODEL_DEPLOYMENT = "gpt-5-mini"
SCOPE_BASE = "https://cognitiveservices.azure.com"
```

## Success Indicators

If everything works, you'll see:

```
✅ ALL TESTS PASSED!

Your Azure AD authentication is working correctly.
The UFO project should now work with these credentials.
```

## Troubleshooting

If tests fail:

1. Check the specific step that failed
2. Review error messages carefully
3. Follow the "Azure Permissions Check" guidance
4. Verify your network can access Azure endpoints
5. Check that the deployment exists and is active

## Using with UFO

Once this test passes, your UFO configuration should work without issues. The authentication logic is identical to what UFO uses.

## Additional Resources

- [Azure OpenAI Authentication](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity)
- [Azure Identity SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme)
- [Azure CLI Installation](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
