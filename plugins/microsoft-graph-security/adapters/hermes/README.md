# Hermes Agent adapter

This repository is an Agent Plugins v1 package. Hermes can validate the root manifest and discover the canonical `skills/` directory.

```bash
hermes plugins validate ./plugin
hermes plugins doctor ./plugin
```

Hermes plugin installation is intentionally not automated here. Use Hermes' own install/enable flow when you want to install it, and review the package first. The adapter adds no executable behavior and no user-level configuration.
