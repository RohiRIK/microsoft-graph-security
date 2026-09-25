# Pi adapter

The `package.json` in the package root is a Pi package manifest. It declares only the shared `skills/` resource; no extension is needed because the workflow is instruction-only.

Load the package for one invocation without writing Pi settings:

```bash
pi --no-session --no-approve --print --no-tools --append-system-prompt "Load the m365-security-workflows skill from the local package." -e ./plugin
```

For a project-local declaration, review Pi's package settings first:

```bash
pi install ./plugin -l
pi list
pi --no-session --no-approve --print --no-tools -e ./plugin "Show the available Microsoft 365 security workflows."
```

The package has no runtime dependencies and no executable behavior. Do not install it into personal Pi settings without explicit approval.
