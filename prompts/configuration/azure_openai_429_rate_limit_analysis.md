# Analysis: 429 Rate Limit Error in APP_AGENT

## Error Overview

**Error Message:**
```
The API request of APP_AGENT failed: OpenAI API request exceeded rate limit: Error code: 429 - {'error': {'code': '429', 'message': 'Rate limit is exceeded. Try again in 60 seconds.'}}.
```

## Error Flow in UFO Codebase

The error originates from:
1. **ufo\llm\openai.py:208-210** - Catches `openai.RateLimitError` and re-raises with formatted message
2. **ufo\llm\llm_call.py:81-89** - Catches the exception and attempts to switch to BACKUP_AGENT

Current configuration (from config.yaml):
- Using **Azure AD authentication** with **gpt-5-mini** model
- **MAX_RETRY: 3** and **TIMEOUT: 60** seconds
- All agents (APP_AGENT, HOST_AGENT, BACKUP_AGENT) use the same deployment: `gpt-5-mini-ufo`

## WHY YOU'RE GETTING 429 ERRORS DESPITE BEING WELL BELOW LIMITS

**Your Quota:**
- 150,000 TPM (Tokens per minute)
- 150 RPM (Requests per minute)

**Your Actual Usage:**
- Only 16k tokens consumed

**The Problem: Azure Uses ESTIMATED Tokens, Not Actual Tokens**

Azure OpenAI doesn't use your actual token consumption for rate limiting. Instead, it uses **estimated tokens at request time**:

### How Rate Limiting Really Works

1. **At Request Time**: Azure estimates tokens based on your `max_tokens` parameter
   - Your config: `MAX_TOKENS: 2000`
   - Each request reserves: (input_tokens + 2000) against your TPM quota
   - This happens BEFORE the request completes

2. **If max_tokens is Missing**: Azure assumes the **entire model context window** (8K-128K tokens depending on model)
   - This causes massive overestimation
   - Can consume your quota in just a few requests

3. **Burst Detection in 1-5 Second Windows**:
   - Azure enforces limits over **sub-minute intervals** (1-5 seconds)
   - Recommendation: Keep under **30 requests/second** and **~5,100 tokens/second**
   - Your 150K TPM = 2,500 TPS average, but burst limits are stricter
   - Users report getting 429 errors with as few as **4 requests per second**

### Example Calculation

If you sent 10 requests in quick succession:
- Estimated tokens per request: ~1,000 (input) + 2,000 (max_tokens) = 3,000 tokens
- Total estimated in burst: 10 × 3,000 = **30,000 tokens**
- In a 1-second window: This equals **30,000 TPS**
- This exceeds the recommended ~5,100 TPS burst limit
- Result: **429 error** even though actual usage is only 16k tokens

### Key Quote from Microsoft Documentation

> "TPM rate limits are based on the maximum number of tokens that are estimated to be processed by a request at the time the request is received, and it isn't the same as the token count used for billing, which is computed after all processing is completed."

This means your actual 16k token consumption is irrelevant for rate limiting - what matters is the estimated reservation at request time.

## Root Causes of the 429 Error

Based on research of Azure OpenAI rate limiting in 2025:

### 1. Request Burst Pattern (Most Likely)
Azure OpenAI evaluates rate limits over **1-10 second windows**, not just the full minute. Even if your total requests per minute (RPM) is within limits, **bursts of requests** can trigger rate limiting. The system expects requests to be **evenly distributed** over the minute.

**Why this happens:**
- The rate limit expects requests to be evenly distributed over a one-minute period
- If this average flow isn't maintained, requests may receive a 429 response even though the limit isn't met when measured over the course of a minute
- Example: A 60 RPM limit means approximately 1 request per second. If you send 10 requests in 1 second, you'll get rate limited even though 10 < 60

### 2. Tokens Per Minute (TPM) Limit
Azure OpenAI has separate limits for:
- **Requests Per Minute (RPM)** - Number of API calls
- **Tokens Per Minute (TPM)** - Total tokens processed (input + output)

The TPM rate limit is based on the **maximum estimated tokens** at the time the request is received, not actual usage.

With `MAX_TOKENS: 2000` in your config, each request can consume up to 2000 tokens in the output alone, plus input tokens.

### 3. Quota Tier Limitations
Your deployment's quota tier determines your rate limits. The "Try again in 60 seconds" message indicates a **standard minute-based rate limit**, not a quota exhaustion (which would show a different error).

### 4. Shared Deployment Usage
If multiple applications or agents are using the same deployment (`gpt-5-mini-ufo`), their requests are **aggregated** against the same rate limit.

## Critical Issue in Current Setup

**Problem:** APP_AGENT and BACKUP_AGENT use the **same deployment** (`gpt-5-mini-ufo`)

**Impact:**
- When APP_AGENT hits the rate limit, the fallback to BACKUP_AGENT will also hit the same limit immediately
- This makes the backup mechanism ineffective
- Both agents share the same TPM and RPM quota

## Solutions

### Immediate Actions (PRIORITIZED FOR YOUR SITUATION)

1. **Add Request Pacing/Delay Between Calls** ⭐ MOST IMPORTANT
   - **Problem**: You're likely sending requests in bursts that exceed the 1-5 second window limits
   - **Solution**: Add delays between API calls (minimum 33ms between requests for 30 req/sec)
   - **Implementation**: Add a sleep/delay in your request loop
   - **Calculation**: With 150 RPM = 2.5 req/sec safe rate, add 400ms delays between requests
   - This is likely the primary cause of your 429 errors

2. **Reduce MAX_TOKENS to Actual Needs** ⭐ VERY IMPORTANT
   - **Current**: MAX_TOKENS: 2000 (reserves 2000 tokens per request)
   - **Reality**: If your responses are typically much shorter, you're wasting quota
   - **Recommendation**: Analyze your actual response lengths and set MAX_TOKENS accordingly
   - **Example**: If responses average 500 tokens, set MAX_TOKENS: 800 (with buffer)
   - **Impact**: This directly reduces estimated token reservation per request

3. **Check for Concurrent Usage**
   - Verify no other applications/users are hitting the same `gpt-5-mini-ufo` deployment
   - Check Azure Monitor/Metrics for the deployment to see actual request patterns
   - Look for unexpected traffic from other sources

4. **Create a separate deployment for BACKUP_AGENT**
   - Deploy another instance of gpt-5-mini with a different name (e.g., `gpt-5-mini-backup`)
   - Allocate separate quota to this deployment
   - Update BACKUP_AGENT configuration to use the new deployment
   - This makes the fallback mechanism actually work

### Long-term Solutions

1. **Optimize MAX_TOKENS**
   - Current setting: 2000 tokens
   - Consider reducing this if your use case doesn't need that many tokens
   - This will help with TPM limits

2. **Request quota increase**
   - Through Azure Portal, request higher TPM/RPM limits
   - Justify based on your usage patterns

3. **Monitor usage patterns**
   - Use Azure OpenAI Studio to monitor:
     - Request patterns over time
     - Token usage
     - Rate limit hits
   - Identify peak usage times and optimize accordingly

4. **Implement retry logic with exponential backoff**
   - Current implementation in openai.py uses the OpenAI client's built-in retry
   - Consider adding application-level retry with exponential backoff
   - Example: Wait 1s, then 2s, then 4s between retries

5. **Consider request queuing**
   - Implement a queue system to smooth out request bursts
   - Process requests at a steady rate to avoid triggering burst detection

## Understanding the "Try again in 60 seconds" Message

This message means:
- You've hit the **per-minute rate limit** for your deployment
- The limit resets on a rolling 60-second window
- This is **not** a quota exhaustion (which would require adding credits)
- This is **throttling** to prevent overuse

Common confusion:
- Some users report seeing "Try again in 86400 seconds" (24 hours), which indicates a different type of limit
- Your error shows 60 seconds, which is the standard RPM/TPM limit

## Code References

### Error Handling in openai.py
```python
# ufo\llm\openai.py:208-210
except openai.RateLimitError as e:
    # Handle rate limit error, e.g. wait or log
    raise Exception(f"OpenAI API request exceeded rate limit: {e}")
```

### Fallback Logic in llm_call.py
```python
# ufo\llm\llm_call.py:81-89
except Exception as e:
    if use_backup_engine:
        print_with_color(f"The API request of {agent_type} failed: {e}.", "red")
        print_with_color(f"Switching to use the backup engine...", "yellow")
        return get_completions(
            messages, agent="backup", use_backup_engine=False, n=n
        )
    else:
        raise e
```

## Recommended Configuration Changes

### Option 1: Create Separate Backup Deployment
```yaml
BACKUP_AGENT: {
  VISUAL_MODE: True,
  API_TYPE: "azure_ad",
  API_BASE: "https://uk-buildings-llm-exploration-oai.cognitiveservices.azure.com/",
  API_VERSION: "2024-12-01-preview",
  API_MODEL: "gpt-5-mini",
  API_DEPLOYMENT_ID: "gpt-5-mini-backup", # Different deployment
  AAD_TENANT_ID: "c8823c91-be81-4f89-b024-6c3dd789c106",
  AAD_API_SCOPE: "https://cognitiveservices.azure.com/.default",
  AAD_API_SCOPE_BASE: "https://cognitiveservices.azure.com",
  AAD_AUTH_METHOD: "device_code"
}
```

### Option 2: Reduce MAX_TOKENS
```yaml
MAX_TOKENS: 1000  # Reduced from 2000 to help with TPM limits
```

### Option 3: Increase Timeout for Retry
```yaml
TIMEOUT: 120  # Increased from 60 to allow for retry delays
```

## References

### General 429 Error Resources
- [How can I solve 429: 'Too Many Requests' errors? | OpenAI Help Center](https://help.openai.com/en/articles/5955604-how-can-i-solve-429-too-many-requests-errors)
- [Azure OpenAI Error 429 - Request Below Rate Limit - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/1693832/azure-openai-error-429-request-below-rate-limit)
- [Getting error:429 rate limit exceeded error when trying azure open ai API calls from python - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/1855030/getting-error-429-rate-limit-exceeded-error-when-t)
- [OpenAI API Quota Exceeded Error: Complete 2025 Solutions Guide – LaoZhang-AI](https://blog.laozhang.ai/api-guides/openai-quota-error-fix/)

### Burst Detection and Short Window Limits
- [Why is my Azure OpenAI deployment returning HTTP 429 "Too Many Requests" even with low usage? - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/5600421/why-is-my-azure-openai-deployment-returning-http-4)
- [OpenAI request hit 429 when rate limit is not reached - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/2283452/openai-request-hit-429-when-rate-limit-is-not-reac)
- [Getting RateLimitError for using Azure OpenAI services while being well below the limit - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/1193897/getting-ratelimiterror-for-using-azure-openai-serv)
- [Azure OpenAI Users Experience 429 Rate-Limit Errors Despite Staying Under Limits | AI News](https://opentools.ai/news/azure-openai-users-experience-429-rate-limit-errors-despite-staying-under-limits)

### Token Estimation and Rate Limit Calculation
- [Azure OpenAI in Microsoft Foundry Models Quotas and Limits - Microsoft Foundry | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/quotas-limits?view=foundry-classic)
- [Understanding API Rate Limits: Best Practices for Azure OpenAI | by Akshay Ruplag | Medium](https://medium.com/@ruplagakshay/understanding-api-rate-limits-best-practices-for-azure-openai-de889a604863)
- [What explains the significant discrepancy between Azure OpenAI API's reported "remaining tokens" and my actual token consumption? - Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/2276520/what-explains-the-significant-discrepancy-between)
- [A Guide to Azure OpenAI Service's Rate Limits and Monitoring · Clemens Siebler's Blog](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/)

### Quota Management
- [Manage Azure OpenAI in Microsoft Foundry Models quota - Microsoft Foundry | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/quota?view=foundry-classic)
- [Azure API Management policy reference - azure-openai-token-limit | Microsoft Learn](https://learn.microsoft.com/en-us/azure/api-management/azure-openai-token-limit-policy)

## Summary: Why 16k Tokens Triggered 429 with 150K TPM Limit

**The Core Issue**: Azure OpenAI uses **estimated tokens** (based on `max_tokens` parameter) for rate limiting, not your actual token consumption.

**Your Situation**:
- Quota: 150K TPM, 150 RPM
- Actual usage: 16k tokens
- Config: MAX_TOKENS: 2000

**What Happened**:
1. Each request reserves ~(input + 2000) tokens for rate limiting
2. If you sent multiple requests quickly (e.g., 10 requests in 2 seconds):
   - Estimated reservation: 10 × ~3000 = 30,000 tokens
   - In a 2-second window: 15,000 TPS
   - This exceeds the burst limit of ~5,100 TPS
   - Result: 429 error
3. Your actual 16k token usage is **irrelevant** - Azure throttles based on estimated reservation

**Most Likely Culprit**: **Request bursts** in short time windows (1-5 seconds), not the per-minute average.

**Primary Solutions**:
1. Add delays between API calls (400ms recommended for your limits)
2. Reduce MAX_TOKENS to match actual needs
3. Check for concurrent usage on the same deployment

## Next Steps

1. **Implement request pacing** - Add 400ms delay between API calls (highest priority)
2. **Analyze actual response lengths** - Reduce MAX_TOKENS if possible
3. Check your current quota allocation and usage patterns in Azure Portal
4. Create a separate backup deployment so fallback mechanism works
5. Monitor Azure metrics to identify peak burst patterns
6. Consider requesting quota increase if legitimate usage needs require it
