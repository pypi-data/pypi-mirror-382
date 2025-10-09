---
name: Plugin Idea
about: Suggest an idea for a community plugin
title: '[PLUGIN] '
labels: ['plugin-idea', 'community']
assignees: ''
---

## Plugin Overview

**Plugin Name**: (e.g., openfinops-plugin-oracle-cloud)
**Plugin Type**: (Telemetry, Attribution, Recommendation, Dashboard, Integration)
**Author**: (Your name/organization)
**Status**: (Idea, In Development, Published)

## Description

Brief description of what the plugin does and why it's useful.

## Use Cases

Who would use this plugin and what problems does it solve?

1. Use case 1
2. Use case 2
3. Use case 3

## Features

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3

## Technical Approach

How would this plugin work technically?

### Data Sources
- Source 1
- Source 2

### Required APIs
- API 1
- API 2

### Configuration
```yaml
plugin_config:
  setting1: value
  setting2: value
```

## Example Usage

```python
from openfinops.plugins import registry

# Load plugin
plugin = registry.load_plugin("my-plugin", config={
    "api_key": "...",
})

# Use plugin
result = plugin.collect_telemetry()
```

## Dependencies

- Python package 1
- Python package 2
- External service requirements

## Documentation Plan

- [ ] README with installation instructions
- [ ] Configuration guide
- [ ] Usage examples
- [ ] API reference

## Timeline

When do you plan to build/publish this?

- [ ] Week 1-2: Design and planning
- [ ] Week 3-4: Implementation
- [ ] Week 5-6: Testing and documentation
- [ ] Week 7: Publication

## Support

Are you willing to maintain this plugin?

- [ ] Yes, I will maintain it
- [ ] Looking for co-maintainers
- [ ] This is just an idea (someone else should build it)

## Related Plugins

Are there similar plugins or integrations?

- Plugin 1
- Plugin 2

---

### Notes

(Additional context or questions)
