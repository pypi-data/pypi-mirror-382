OS Forge
========

Minimal commands to install and use on Linux and Windows.

Installation
------------

```bash
pip install os-forge
```

CLI Help
--------

```bash
os-forge --help
```

Common Commands
---------------

```bash
# Show system info
os-forge info

# Run checks (no changes)
os-forge check --level basic --dry-run

# Start API server
os-forge server

# Generate reports
os-forge report
os-forge pdf-report
```

Windows
-------

Use from an elevated PowerShell or Command Prompt:

```powershell
pip install os-forge
os-forge --help
os-forge info
```

Notes
-----

- Commands and behavior are the same on Linux and Windows.
- For full documentation, run `os-forge --help`.


