# Solutions for Azure OpenAI 429 Rate Limit Errors

## 1. How to Reduce Request Frequency (Request Pacing)

UFO already has a built-in delay mechanism between steps. You can control this with the `SLEEP_TIME` parameter:

### Option A: Use Existing SLEEP_TIME Config

**Location:** `ufo/config/config_dev.yaml` or `ufo/config/config.yaml`

```yaml
SLEEP_TIME: 1  # The sleep time in seconds between each step
```

**To reduce 429 errors, increase this value:**

```yaml
SLEEP_TIME: 2  # Adds 2 seconds between each agent step (reduces from ~2-3 req/sec to ~0.5 req/sec)
```

**Where it's used:** [ufo/agents/processors/basic.py:288](ufo/agents/processors/basic.py#L288)
```python
def update_status(self) -> None:
    """Update the status of the session."""
    self.agent.step += 1
    self.agent.status = self.status

    if self.status != self._agent_status_manager.FINISH.value:
        time.sleep(configs["SLEEP_TIME"])  # <-- Delay happens here
```

### Option B: Add Request-Level Pacing (More Advanced)

If you need finer control, you can add a delay directly in the LLM call function:

**Location:** [ufo/llm/llm_call.py:69-78](ufo/llm/llm_call.py#L69-L78)

Add this at the top of the `get_completions` function:

```python
import time

def get_completions(
    messages,
    agent: str = "APP",
    use_backup_engine: bool = True,
    n: int = 1,
    configs=configs,
) -> Tuple[list, float]:
    # Add a small delay before each API request to avoid burst detection
    time.sleep(0.4)  # 400ms delay = ~2.5 requests/sec max

    # ... rest of the function
```

**Recommended delay calculation for your limits:**
- Your limit: 150 RPM = 2.5 requests/sec
- Safe rate: 2.0 requests/sec (with buffer)
- Delay needed: 1 / 2.0 = **0.5 seconds (500ms)**

### Which Option to Use?

| Approach | When to Use | Pros | Cons |
|----------|------------|------|------|
| **SLEEP_TIME** | Best for most cases | Simple, already exists, controls overall pacing | Delays entire workflow, not just API calls |
| **Request-level delay** | Need precise API rate control | Precise control over API rate | Requires code modification |

**Recommendation:** Start with increasing `SLEEP_TIME` to 2-3 seconds. This is the simplest solution.

---

## 2. How to View Token Size of Each Request

Yes! UFO logs token usage and costs for every API call. Here's how to view it:

### Where Token Usage is Logged

UFO creates detailed logs in the `logs/` directory. Each session gets its own folder.

**Log files created:**
- `response.log` - Contains all agent responses with token costs
- `request.log` - Contains all requests sent to the API
- `output.md` - Human-readable summary

### Viewing Token Usage

**Example from your logs:**

Location: `logs/etabs2/response.log`

Each line is a JSON object with token cost information:

```json
{
  "Agent": "HostAgent",
  "Cost": 0.004574750000000001,  // <-- Token cost for this request
  "Step": 0,
  "time_cost": {
    "get_response": 26.368384838104248  // Time spent on API call
  },
  "total_time_cost": 28.348694801330566
}
```

### How to Analyze Token Usage

**Method 1: View in Real-Time**
```bash
# Watch the response log as it's created
tail -f logs/<session_name>/response.log
```

**Method 2: Calculate Total Cost**
```bash
# Extract all costs from the log (Windows PowerShell)
Get-Content logs/etabs2/response.log | ConvertFrom-Json | Select-Object -ExpandProperty Cost | Measure-Object -Sum
```

**Method 3: Create a Simple Analysis Script**

Create `analyze_costs.py` in the UFO root directory:

```python
import json
import sys
from pathlib import Path

def analyze_token_costs(log_file):
    """Analyze token costs from a response log file"""
    total_cost = 0
    request_count = 0
    costs = []

    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    data = json.loads(line)
                    cost = data.get('Cost', 0)
                    agent = data.get('Agent', 'Unknown')
                    step = data.get('Step', -1)

                    if cost > 0:
                        costs.append({
                            'step': step,
                            'agent': agent,
                            'cost': cost
                        })
                        total_cost += cost
                        request_count += 1
                except json.JSONDecodeError:
                    continue

    print(f"\\n{'='*60}")
    print(f"Token Cost Analysis for: {log_file}")
    print(f"{'='*60}\\n")
    print(f"Total API Requests: {request_count}")
    print(f"Total Cost: ${total_cost:.6f}")
    print(f"Average Cost per Request: ${total_cost/request_count if request_count > 0 else 0:.6f}\\n")

    if costs:
        print("Per-Request Breakdown:")
        print(f"{'Step':<6} {'Agent':<15} {'Cost ($)':<12}")
        print("-" * 35)
        for item in costs:
            print(f"{item['step']:<6} {item['agent']:<15} ${item['cost']:<12.6f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_costs.py logs/<session_name>/response.log")
        sys.exit(1)

    log_file = sys.argv[1]
    if not Path(log_file).exists():
        print(f"Error: File not found: {log_file}")
        sys.exit(1)

    analyze_token_costs(log_file)
```

**Usage:**
```bash
python analyze_costs.py logs/etabs2/response.log
```

**Output example:**
```
============================================================
Token Cost Analysis for: logs/etabs2/response.log
============================================================

Total API Requests: 1
Total Cost: $0.004575
Average Cost per Request: $0.004575

Per-Request Breakdown:
Step   Agent           Cost ($)
-----------------------------------
0      HostAgent       $0.004575
```

### Understanding the Cost Values

The `Cost` field in the logs represents the **estimated cost in USD** based on:
- Prompt tokens (input)
- Completion tokens (output)
- Model pricing from your config

**Note:** This is calculated from actual token usage reported by the API response, NOT the estimated tokens used for rate limiting. This is why you see low costs even when hitting rate limits.

### Where Cost Calculation Happens

**Code location:** [ufo/llm/openai.py:178-190](ufo/llm/openai.py#L178-L190)

```python
usage = response.usage
prompt_tokens = usage.prompt_tokens
completion_tokens = usage.completion_tokens

cost = self.get_cost_estimator(
    self.api_type, model, self.prices, prompt_tokens, completion_tokens
)

return [response.choices[0].message.content], cost
```

This shows the **actual tokens consumed** after the request completes, which is different from the **estimated tokens** Azure uses for rate limiting.

---

## Quick Reference

### To Fix 429 Errors:

1. **Increase SLEEP_TIME** in config:
   ```yaml
   SLEEP_TIME: 2  # Start with 2 seconds
   ```

2. **View token usage** in logs:
   ```bash
   cat logs/<session_name>/response.log
   ```

3. **Monitor rate**:
   - With SLEEP_TIME: 2 seconds → ~0.5 requests/sec (safe!)
   - Without SLEEP_TIME → Multiple requests/sec (causes 429!)

### Key Files:
- **Config:** `ufo/config/config.yaml` or `ufo/config/config_dev.yaml`
- **Logs:** `logs/<session_name>/response.log`
- **Cost calculation:** `ufo/llm/openai.py:178-190`
- **Delay implementation:** `ufo/agents/processors/basic.py:288`
