# Enhanced Security Features for OS Forge

This module provides comprehensive security scanning, monitoring, secrets management, and configuration management capabilities for OS Forge.

## Features

### 🔍 Vulnerability Scanner
- **Code Analysis**: Detects SQL injection, command injection, path traversal, and other vulnerabilities
- **Secret Detection**: Finds hardcoded passwords, API keys, and other sensitive data
- **Dependency Scanning**: Identifies vulnerable packages in requirements.txt and package.json
- **Multiple Output Formats**: JSON, HTML, and CSV reports
- **Pattern-based Detection**: Customizable vulnerability patterns

### 🔐 Secrets Manager
- **Secure Storage**: Encrypted secret storage using Fernet encryption
- **Access Control**: Track secret access with detailed logging
- **Automatic Rotation**: Support for secret rotation policies
- **Metadata Management**: Rich metadata for secrets including expiration and tags
- **Backup/Restore**: Export and import capabilities for disaster recovery

### 📊 Security Monitor
- **Real-time Monitoring**: System metrics, network activity, and file integrity monitoring
- **Threat Detection**: Automated threat detection based on multiple indicators
- **Alert System**: Configurable alerts with multiple notification channels
- **Log Analysis**: Automated analysis of system logs for security events
- **Statistics**: Comprehensive monitoring statistics and reporting

### ⚙️ Security Configuration
- **Policy Management**: Define and manage security policies
- **Baseline Management**: Create security baselines for different environments
- **Compliance Validation**: Validate system compliance against security baselines
- **Settings Management**: Centralized security settings configuration
- **Import/Export**: Configuration backup and sharing capabilities

## Installation

### Prerequisites
- Python 3.8+
- Required system packages (for monitoring):
  - `psutil` for system metrics
  - Network monitoring capabilities

### Install Dependencies
```bash
pip install -r security/enhanced/requirements.txt
```

### Core Dependencies
- `cryptography>=3.4.8` - For encryption and secure operations
- `pyyaml>=6.0` - For configuration file handling
- `psutil>=5.8.0` - For system monitoring

## Quick Start

### 1. Vulnerability Scanning
```bash
# Run comprehensive vulnerability scan
python -m security.enhanced.vulnerability_scanner --directory ./ --format html

# Scan specific directory with verbose output
python -m security.enhanced.vulnerability_scanner -d /path/to/code -v -f json -o scan_results.json
```

### 2. Secrets Management
```bash
# Store a secret
python -m security.enhanced.secrets_manager store "db_password" "my_secure_password" --description "Database password"

# Retrieve a secret
python -m security.enhanced.secrets_manager retrieve "db_password"

# List all secrets
python -m security.enhanced.secrets_manager list

# Rotate a secret
python -m security.enhanced.secrets_manager rotate "api_key"
```

### 3. Security Monitoring
```bash
# Start monitoring (runs continuously)
python -m security.enhanced.security_monitor start

# Check monitoring status
python -m security.enhanced.security_monitor status

# View recent events
python -m security.enhanced.security_monitor events --limit 20

# View recent alerts
python -m security.enhanced.security_monitor alerts --severity HIGH
```

### 4. Security Configuration
```bash
# List all policies
python -m security.enhanced.security_config policy list

# Show policy details
python -m security.enhanced.security_config policy show password_policy

# List all baselines
python -m security.enhanced.security_config baseline list

# Run compliance check
python -m security.enhanced.security_config compliance linux_server_strict
```

### 5. Integrated Security Operations
```bash
# Run comprehensive security scan
python -m security.enhanced.security_integration scan --directory ./ --format html

# Start integrated monitoring
python -m security.enhanced.security_integration monitor-start

# Generate security report
python -m security.enhanced.security_integration report security_report.html --format html
```

## Configuration

### Vulnerability Scanner Configuration
Create `vulnerability_scanner_config.yaml`:
```yaml
scan_directories: ["./"]
exclude_patterns:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/venv/**"
file_extensions: [".py", ".js", ".ts", ".yaml", ".yml", ".json"]
max_file_size: 10485760  # 10MB
enable_dependency_scan: true
enable_secret_scan: true
enable_code_analysis: true
```

### Secrets Manager Configuration
Create `secrets_manager_config.yaml`:
```yaml
secrets_directory: "./secrets"
encryption_algorithm: "fernet"
key_derivation_iterations: 100000
access_log_retention_days: 90
default_expiration_days: 90
rotation_policies:
  daily:
    interval: 1
    unit: "days"
  weekly:
    interval: 7
    unit: "days"
```

### Security Monitor Configuration
Create `security_monitor_config.yaml`:
```yaml
monitoring_enabled: true
max_events: 10000
max_alerts: 1000
monitoring_intervals:
  system_metrics: 30
  network_scan: 300
  file_integrity: 600
  log_analysis: 60
thresholds:
  cpu_usage: 80
  memory_usage: 85
  disk_usage: 90
  failed_logins: 5
log_files:
  - "/var/log/auth.log"
  - "/var/log/syslog"
```

## API Usage

### Python API Examples

#### Vulnerability Scanning
```python
from security.enhanced import VulnerabilityScanner

scanner = VulnerabilityScanner()
result = scanner.scan_directory("./")

print(f"Found {len(result.vulnerabilities)} vulnerabilities")
for vuln in result.vulnerabilities:
    print(f"{vuln.severity}: {vuln.title} in {vuln.file_path}")

# Export results
scanner.export_results(result, "json", "scan_results.json")
```

#### Secrets Management
```python
from security.enhanced import SecretsManager

manager = SecretsManager()

# Store a secret
manager.store_secret(
    name="api_key",
    value="sk-1234567890abcdef",
    description="OpenAI API Key",
    expires_in_days=90,
    tags=["api", "external"]
)

# Retrieve a secret
api_key = manager.retrieve_secret("api_key")

# List secrets
secrets = manager.list_secrets()
for secret in secrets:
    print(f"{secret['name']}: {secret['description']}")
```

#### Security Monitoring
```python
from security.enhanced import SecurityMonitor

monitor = SecurityMonitor()

# Start monitoring
monitor.start_monitoring()

# Get statistics
stats = monitor.get_statistics()
print(f"Events: {stats['events_total']}, Alerts: {stats['alerts_total']}")

# Get recent events
events = monitor.get_events(limit=10)
for event in events:
    print(f"{event['event_type']}: {event['message']}")
```

#### Security Configuration
```python
from security.enhanced import SecurityConfigManager, SecurityPolicy

config_manager = SecurityConfigManager()

# Get all policies
policies = config_manager.get_enabled_policies()
for policy in policies:
    print(f"{policy.name}: {policy.description}")

# Validate compliance
system_state = {
    "min_length": 12,
    "require_uppercase": True,
    "firewall_enabled": True
}
compliance = config_manager.validate_compliance("linux_server_strict", system_state)
print(f"Compliance: {compliance['compliance_percentage']:.1f}%")
```

#### Integrated Security Operations
```python
from security.enhanced import SecurityIntegration

integration = SecurityIntegration()

# Run comprehensive scan
results = integration.run_comprehensive_security_scan()
print(f"Security Score: {results['summary']['security_score']}")

# Start monitoring
integration.start_security_monitoring()

# Generate report
integration.export_security_report("security_report.html", "html")
```

## Security Policies

### Default Policies Included

1. **Password Security Policy**
   - Minimum length requirements
   - Character complexity requirements
   - Password history and aging

2. **Network Security Policy**
   - Firewall configuration
   - Service restrictions
   - Port management

3. **System Hardening Policy**
   - User account security
   - Service management
   - Kernel security features

4. **Data Protection Policy**
   - Encryption requirements
   - Access controls
   - Data classification

5. **Application Security Policy**
   - Input validation
   - Output encoding
   - Security headers

### Default Baselines Included

1. **Linux Server - Strict**: Comprehensive security for production Linux servers
2. **Linux Server - Moderate**: Balanced security for development/staging servers
3. **Windows Server - Strict**: Enterprise Windows server security
4. **Windows Workstation - Moderate**: Standard workstation security
5. **Docker Container**: Container-specific security requirements

## Monitoring and Alerting

### Supported Alert Types
- **System Metrics**: CPU, memory, disk usage alerts
- **Network Activity**: Suspicious connections, port scans
- **Authentication**: Failed login attempts, privilege escalation
- **File Integrity**: Unauthorized file modifications
- **Threat Detection**: Automated threat pattern recognition

### Notification Channels
- **Email**: SMTP-based email notifications
- **Webhook**: HTTP POST to custom endpoints
- **Slack**: Direct Slack channel notifications

### Alert Rules
- Configurable thresholds and time windows
- Multiple severity levels (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Customizable actions per alert type

## Compliance and Reporting

### Supported Frameworks
- **NIST**: National Institute of Standards and Technology guidelines
- **CIS**: Center for Internet Security benchmarks
- **ISO 27001**: Information security management standards

### Report Formats
- **JSON**: Machine-readable format for integration
- **HTML**: Human-readable reports with charts and graphs
- **CSV**: Spreadsheet-compatible format

### Compliance Scoring
- Automatic compliance percentage calculation
- Policy-by-policy compliance validation
- Overall security score assessment
- Detailed remediation recommendations

## Security Considerations

### Encryption
- All secrets are encrypted using Fernet (AES 128 in CBC mode)
- Key derivation uses PBKDF2 with SHA-256
- Configurable iteration count for key derivation

### Access Control
- Detailed access logging for all secret operations
- Configurable access retention policies
- Audit trail for compliance requirements

### Data Protection
- No sensitive data stored in plain text
- Secure deletion capabilities
- Backup encryption support

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Install missing dependencies
pip install cryptography pyyaml psutil

# For optional features
pip install bandit safety semgrep
```

#### Permission Errors
```bash
# Ensure proper file permissions
chmod 600 security/secrets/.key
chmod 755 security/enhanced/
```

#### Configuration Issues
```bash
# Validate configuration files
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

### Debug Mode
```bash
# Enable verbose logging
export PYTHONPATH=.
python -m security.enhanced.vulnerability_scanner -v
```

## Contributing

### Adding New Vulnerability Patterns
1. Edit `vulnerability_scanner.py`
2. Add patterns to `_load_vulnerability_patterns()`
3. Include remediation advice in `_get_remediation()`

### Adding New Security Policies
1. Edit `security_config.py`
2. Add policy to `_initialize_default_policies()`
3. Define policy rules and validation logic

### Adding New Monitoring Capabilities
1. Edit `security_monitor.py`
2. Add monitoring function
3. Create corresponding alert rules

## License

This module is part of OS Forge and follows the same license terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration examples
3. Consult the API documentation
4. Open an issue in the OS Forge repository (policy-guard)
