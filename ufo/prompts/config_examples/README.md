# UFO Configuration Examples

This folder contains example configurations for different use cases.

## How to Use

1. **Copy** the configuration that matches your needs
2. **Paste** into `ufo/config/config_dev.yaml`
3. **Restart** UFO for changes to take effect

## Available Configurations

### 1. `max_performance.yaml` - Maximum Speed & Minimum Cost
- **Use when:** Working with Office apps (Word, Excel, PowerPoint), cost-sensitive projects, repetitive tasks
- **Savings:** 60-70% faster, 80-90% lower vision costs
- **Trade-off:** No visual context for LLM (may fail on complex UI tasks)

**Key features:**
- No screenshots sent to LLM
- Maximum image compression
- Control filtering enabled
- API automation preferred

---

### 2. `balanced.yaml` - Best Overall Performance
- **Use when:** Mixed UI + API automation, moderate cost sensitivity
- **Savings:** 30-40% faster, 40-50% lower vision costs
- **Trade-off:** Some visual context (1 image per step)

**Key features:**
- 1 screenshot per step (concatenated)
- Good compression
- Smart control filtering
- API automation when available

---

### 3. `debug_full_visual.yaml` - Complete Debugging Info
- **Use when:** Debugging complex issues, research, understanding agent behavior
- **Savings:** None (maximum resource usage)
- **Trade-off:** Slowest, most expensive, largest logs

**Key features:**
- 2 screenshots per step
- Full UI tree dumps
- XML logs
- All controls shown

---

## Quick Comparison

| Feature | Max Performance | Balanced | Debug |
|---------|----------------|----------|-------|
| Screenshots to LLM | 0 | 1 | 2 |
| Images per 30-step task | 0 | 30 | 60 |
| Execution time (30 steps) | ~95s | ~160s | ~240s |
| Vision token cost* | $0.15 | $0.65 | $1.20 |
| Disk usage | 0.8MB | 3.5MB | 9MB |
| API automation | Yes | Yes | Yes |
| Good for debugging | No | Moderate | Yes |

*Estimated using GPT-4V pricing

---

## Customization

You can mix and match settings from different profiles. Here are the key toggles:

### Screenshot Control
```yaml
INCLUDE_LAST_SCREENSHOT: False  # Don't send to LLM (max savings)
CONCAT_SCREENSHOT: True         # 1 image instead of 2 (50% savings)
```

### Compression
```yaml
DEFAULT_PNG_COMPRESS_LEVEL: 9   # 0-9, higher = smaller files
```

### Control Filtering
```yaml
CONTROL_FILTER_TYPE: ["TEXT"]   # Only show relevant controls
```

### Performance
```yaml
SLEEP_TIME: 0.5                 # Faster step transitions
USE_APIS: True                  # Prefer native APIs
```

---

## Testing Your Configuration

After applying a configuration, test it with a simple task:

```bash
python ufo.py --task "Open Notepad and type 'Hello World'"
```

Check the logs to verify:
1. Screenshot count in `logs/<session>/action_screenshots/`
2. Execution time in the console output
3. Token usage in the session summary

---

## Troubleshooting

### Agent failing without screenshots
- Try `balanced.yaml` instead of `max_performance.yaml`
- Some tasks require visual context

### Still slow despite optimization
- Check if OmniParser is enabled: `CONTROL_BACKEND: ["uia"]` only
- Reduce control types: `CONTROL_LIST: ["Button", "Edit", "MenuItem"]`
- Check network latency to LLM API

### High costs despite configuration
- Verify config is loaded: check `INCLUDE_LAST_SCREENSHOT` in logs
- Ensure you're editing `config_dev.yaml`, not `config.yaml`
- Restart UFO after config changes

---

## Related Documentation

- [Performance Optimization Guide](../PERFORMANCE_OPTIMIZATION_GUIDE.md) - Detailed explanations
- [Main Config](../../config/config_dev.yaml) - Your active configuration

---

**Need help?** See the full optimization guide in `ufo/prompts/PERFORMANCE_OPTIMIZATION_GUIDE.md`
