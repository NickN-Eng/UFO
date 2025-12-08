# Fix Missing RAG Configuration Keys in config.yaml

## Problem
UFO application crashes with `KeyError: 'RAG_OFFLINE_DOCS'` when trying to create an AppAgent. The error occurs because the [ufo/config/config.yaml](../ufo/config/config.yaml) is missing RAG-related configuration keys that the code expects.

## Root Cause
The [ufo/config/config.yaml](../ufo/config/config.yaml) file only contains:
- Agent configurations (HOST_AGENT, APP_AGENT, EVALUATION_AGENT, BACKUP_AGENT)
- GPT parameters (MAX_TOKENS, MAX_RETRY, TEMPERATURE, TOP_P, TIMEOUT)
- REASONING_EFFORT parameter

But it's missing the RAG configuration section that exists in [config.yaml.template](../ufo/config/config.yaml.template):
- RAG_OFFLINE_DOCS
- RAG_OFFLINE_DOCS_RETRIEVED_TOPK
- RAG_ONLINE_SEARCH
- BING_API_KEY
- RAG_ONLINE_SEARCH_TOPK
- RAG_ONLINE_RETRIEVED_TOPK
- RAG_EXPERIENCE
- RAG_EXPERIENCE_RETRIEVED_TOPK
- RAG_DEMONSTRATION
- RAG_DEMONSTRATION_RETRIEVED_TOPK
- RAG_DEMONSTRATION_COMPLETION_N

The code in app_agent.py:475 tries to access `configs["RAG_OFFLINE_DOCS"]` and crashes when the key doesn't exist.

## Solution
Add the missing RAG configuration section to [ufo/config/config.yaml](../ufo/config/config.yaml) after the REASONING_EFFORT parameter. Copy the exact configuration from config.yaml.template with default values:

```yaml
### For RAG

## RAG Configuration for the offline docs
RAG_OFFLINE_DOCS: False  # Whether to use the offline RAG.
RAG_OFFLINE_DOCS_RETRIEVED_TOPK: 1  # The topk for the offline retrieved documents

## RAG Configuration for the Bing search
BING_API_KEY: "YOUR_BING_SEARCH_API_KEY"  # The Bing search API key
RAG_ONLINE_SEARCH: False  # Whether to use the online search for the RAG.
RAG_ONLINE_SEARCH_TOPK: 5  # The topk for the online search
RAG_ONLINE_RETRIEVED_TOPK: 1 # The topk for the online retrieved documents

## RAG Configuration for experience
RAG_EXPERIENCE: False  # Whether to use the RAG from its self-experience.
RAG_EXPERIENCE_RETRIEVED_TOPK: 5  # The topk for the offline retrieved documents

## RAG Configuration for demonstration
RAG_DEMONSTRATION: False  # Whether to use the RAG from its user demonstration.
RAG_DEMONSTRATION_RETRIEVED_TOPK: 5  # The topk for the offline retrieved documents
RAG_DEMONSTRATION_COMPLETION_N: 3  # The number of completion choices for the demonstration result
```

## Files to Modify
- **ufo/config/config.yaml** - Add missing RAG configuration section after line 62 (after REASONING_EFFORT parameter)

## Implementation Steps
1. Read the complete RAG configuration section from config.yaml.template
2. Append the RAG configuration section to config.yaml after the REASONING_EFFORT parameter
3. Ensure proper YAML formatting and indentation
4. Keep all RAG features disabled by default (False values)

## Expected Result
After adding the RAG configuration:
- UFO application will start successfully
- AppAgent creation will not crash with KeyError
- All RAG features will be disabled by default (can be enabled if needed)
- The application will proceed to execute user requests (like "open microsoft word and type hello world")

## Notes
- This is a simple configuration addition, not a code change
- All RAG features will be disabled (False) by default, so no additional setup is required
- The BING_API_KEY can remain as placeholder "YOUR_BING_SEARCH_API_KEY" since RAG_ONLINE_SEARCH is False
