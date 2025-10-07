"""
Linux-specific hardening rules for OS Forge

Contains comprehensive Linux hardening rules based on:
- CIS Benchmarks
- NIST Guidelines
- Security best practices
- Common vulnerabilities
"""

from typing import Dict, List, Any
from enum import Enum


class LinuxRuleCategory(str, Enum):
    """Categories for Linux hardening rules"""
    SSH_SECURITY = "ssh_security"
    FIREWALL = "firewall"
    USER_MANAGEMENT = "user_management"
    FILE_PERMISSIONS = "file_permissions"
    KERNEL_SECURITY = "kernel_security"
    SERVICE_MANAGEMENT = "service_management"
    NETWORK_SECURITY = "network_security"
    LOGGING = "logging"
    PACKAGE_MANAGEMENT = "package_management"
    SYSTEM_CONFIGURATION = "system_configuration"
    CONTAINER_SECURITY = "container_security"
    RHEL_SPECIFIC = "rhel_specific"
    APPARMOR_SELINUX = "apparmor_selinux"


def get_linux_hardening_rules() -> List[Dict[str, Any]]:
    """
    Get comprehensive list of Linux hardening rules
    
    Returns:
        List of rule dictionaries
    """
    return [
        # SSH Security Rules
        {
            "id": "LIN-SSH-001",
            "description": "Disable SSH root login",
            "category": LinuxRuleCategory.SSH_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'grep "^PermitRootLogin" /etc/ssh/sshd_config || echo "PermitRootLogin yes"',
            "remediate": 'sudo sed -i "s/^PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "rollback": 'sudo sed -i "s/^PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "expected": "PermitRootLogin no",
            "rationale": "Prevents direct root login via SSH, reducing attack surface"
        },
        
        {
            "id": "LIN-SSH-002",
            "description": "Set SSH protocol version to 2",
            "category": LinuxRuleCategory.SSH_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'grep "^Protocol" /etc/ssh/sshd_config || echo "Protocol 1"',
            "remediate": 'echo "Protocol 2" | sudo tee -a /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "rollback": 'sudo sed -i "/^Protocol 2/d" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "expected": "Protocol 2",
            "rationale": "SSH Protocol 1 has known security vulnerabilities"
        },
        
        {
            "id": "LIN-SSH-003",
            "description": "Disable SSH password authentication",
            "category": LinuxRuleCategory.SSH_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'grep "^PasswordAuthentication" /etc/ssh/sshd_config || echo "PasswordAuthentication yes"',
            "remediate": 'sudo sed -i "s/^PasswordAuthentication.*/PasswordAuthentication no/" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "rollback": 'sudo sed -i "s/^PasswordAuthentication.*/PasswordAuthentication yes/" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "expected": "PasswordAuthentication no",
            "rationale": "Key-based authentication is more secure than passwords"
        },
        
        {
            "id": "LIN-SSH-004",
            "description": "Set SSH idle timeout",
            "category": LinuxRuleCategory.SSH_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'grep "^ClientAliveInterval" /etc/ssh/sshd_config || echo "ClientAliveInterval 0"',
            "remediate": 'echo "ClientAliveInterval 300" | sudo tee -a /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "rollback": 'sudo sed -i "/^ClientAliveInterval 300/d" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "expected": "ClientAliveInterval 300",
            "rationale": "Prevents idle SSH sessions from staying open indefinitely"
        },
        
        # Firewall Rules
        {
            "id": "LIN-FW-001",
            "description": "Enable UFW firewall",
            "category": LinuxRuleCategory.FIREWALL,
            "os": ["linux", "ubuntu"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'sudo ufw status | grep "Status:" | cut -d" " -f2 || echo "inactive"',
            "remediate": 'sudo ufw --force enable',
            "rollback": 'sudo ufw --force disable',
            "expected": "active",
            "rationale": "Firewall provides essential network security"
        },
        
        {
            "id": "LIN-FW-002",
            "description": "Enable firewalld (RHEL/CentOS)",
            "category": LinuxRuleCategory.FIREWALL,
            "os": ["centos", "rhel"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'sudo systemctl is-active firewalld || echo "inactive"',
            "remediate": 'sudo systemctl enable firewalld && sudo systemctl start firewalld',
            "rollback": 'sudo systemctl stop firewalld && sudo systemctl disable firewalld',
            "expected": "active",
            "rationale": "Firewall provides essential network security"
        },
        
        # User Management Rules
        {
            "id": "LIN-USER-001",
            "description": "Set minimum password length",
            "category": LinuxRuleCategory.USER_MANAGEMENT,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'grep "^minlen" /etc/security/pwquality.conf | cut -d"=" -f2 | tr -d " " || echo "8"',
            "remediate": 'echo "minlen = 12" | sudo tee -a /etc/security/pwquality.conf',
            "rollback": 'sudo sed -i "/^minlen = 12/d" /etc/security/pwquality.conf',
            "expected": "12",
            "rationale": "Longer passwords are more secure"
        },
        
        {
            "id": "LIN-USER-002",
            "description": "Set password complexity requirements",
            "category": LinuxRuleCategory.USER_MANAGEMENT,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'grep "^dcredit" /etc/security/pwquality.conf | cut -d"=" -f2 | tr -d " " || echo "0"',
            "remediate": 'echo "dcredit = -1" | sudo tee -a /etc/security/pwquality.conf && echo "ucredit = -1" | sudo tee -a /etc/security/pwquality.conf && echo "lcredit = -1" | sudo tee -a /etc/security/pwquality.conf && echo "ocredit = -1" | sudo tee -a /etc/security/pwquality.conf',
            "rollback": 'sudo sed -i "/^[duol]credit = -1/d" /etc/security/pwquality.conf',
            "expected": "-1",
            "rationale": "Complex passwords are harder to crack"
        },
        
        # Kernel Security Rules
        {
            "id": "LIN-KERNEL-001",
            "description": "Enable ASLR (Address Space Layout Randomization)",
            "category": LinuxRuleCategory.KERNEL_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "high",
            "level": ["moderate", "strict"],
            "check": 'sysctl kernel.randomize_va_space | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "kernel.randomize_va_space = 2" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/kernel.randomize_va_space = 2/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "2",
            "rationale": "ASLR makes buffer overflow attacks more difficult"
        },
        
        {
            "id": "LIN-KERNEL-002",
            "description": "Disable core dumps for SUID programs",
            "category": LinuxRuleCategory.KERNEL_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["strict"],
            "check": 'sysctl fs.suid_dumpable | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "fs.suid_dumpable = 0" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/fs.suid_dumpable = 0/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "0",
            "rationale": "Prevents sensitive information from being written to core dumps"
        },
        
        {
            "id": "LIN-KERNEL-003",
            "description": "Disable IP forwarding",
            "category": LinuxRuleCategory.KERNEL_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'sysctl net.ipv4.ip_forward | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "net.ipv4.ip_forward = 0" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/net.ipv4.ip_forward = 0/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "0",
            "rationale": "Prevents system from acting as a router unless needed"
        },
        
        # Service Management Rules
        {
            "id": "LIN-SVC-001",
            "description": "Disable unnecessary services",
            "category": LinuxRuleCategory.SERVICE_MANAGEMENT,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'systemctl is-enabled telnet.socket 2>/dev/null || echo "disabled"',
            "remediate": 'sudo systemctl disable telnet.socket 2>/dev/null || true',
            "rollback": 'sudo systemctl enable telnet.socket 2>/dev/null || true',
            "expected": "disabled",
            "rationale": "Reduces attack surface by disabling unused services"
        },
        
        {
            "id": "LIN-SVC-002",
            "description": "Disable X11 forwarding in SSH",
            "category": LinuxRuleCategory.SERVICE_MANAGEMENT,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "low",
            "level": ["moderate", "strict"],
            "check": 'grep "^X11Forwarding" /etc/ssh/sshd_config || echo "X11Forwarding yes"',
            "remediate": 'sudo sed -i "s/^X11Forwarding.*/X11Forwarding no/" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "rollback": 'sudo sed -i "s/^X11Forwarding.*/X11Forwarding yes/" /etc/ssh/sshd_config && sudo systemctl reload sshd',
            "expected": "X11Forwarding no",
            "rationale": "X11 forwarding can be a security risk if not properly configured"
        },
        
        # File Permission Rules
        {
            "id": "LIN-FILE-001",
            "description": "Set secure permissions on /etc/passwd",
            "category": LinuxRuleCategory.FILE_PERMISSIONS,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'stat -c "%a" /etc/passwd 2>/dev/null || echo "000"',
            "remediate": 'sudo chmod 644 /etc/passwd',
            "rollback": 'sudo chmod 644 /etc/passwd',
            "expected": "644",
            "rationale": "Prevents unauthorized modification of user account information"
        },
        
        {
            "id": "LIN-FILE-002",
            "description": "Set secure permissions on /etc/shadow",
            "category": LinuxRuleCategory.FILE_PERMISSIONS,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'stat -c "%a" /etc/shadow 2>/dev/null || echo "000"',
            "remediate": 'sudo chmod 640 /etc/shadow',
            "rollback": 'sudo chmod 640 /etc/shadow',
            "expected": "640",
            "rationale": "Protects password hashes from unauthorized access"
        },
        
        # Network Security Rules
        {
            "id": "LIN-NET-001",
            "description": "Disable unused network protocols",
            "category": LinuxRuleCategory.NETWORK_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "low",
            "level": ["strict"],
            "check": 'lsmod | grep dccp || echo "not_loaded"',
            "remediate": 'echo "install dccp /bin/true" | sudo tee -a /etc/modprobe.d/dccp.conf',
            "rollback": 'sudo rm -f /etc/modprobe.d/dccp.conf',
            "expected": "not_loaded",
            "rationale": "Reduces attack surface by disabling unused protocols"
        },
        
        {
            "id": "LIN-NET-002",
            "description": "Disable IP source routing",
            "category": LinuxRuleCategory.NETWORK_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'sysctl net.ipv4.conf.all.accept_source_route | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "net.ipv4.conf.all.accept_source_route = 0" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/net.ipv4.conf.all.accept_source_route = 0/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "0",
            "rationale": "Prevents IP source routing attacks"
        },
        
        # Logging Rules
        {
            "id": "LIN-LOG-001",
            "description": "Enable audit logging",
            "category": LinuxRuleCategory.LOGGING,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'systemctl is-active auditd 2>/dev/null || echo "inactive"',
            "remediate": 'sudo systemctl enable auditd && sudo systemctl start auditd',
            "rollback": 'sudo systemctl stop auditd && sudo systemctl disable auditd',
            "expected": "active",
            "rationale": "Audit logging helps track security events"
        },
        
        # Package Management Rules
        {
            "id": "LIN-PKG-001",
            "description": "Enable automatic security updates",
            "category": LinuxRuleCategory.PACKAGE_MANAGEMENT,
            "os": ["ubuntu"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'grep "^APT::Periodic::Unattended-Upgrade" /etc/apt/apt.conf.d/20auto-upgrades | cut -d"\\"" -f2 || echo "0"',
            "remediate": 'echo "APT::Periodic::Unattended-Upgrade \\"1\\";" | sudo tee -a /etc/apt/apt.conf.d/20auto-upgrades',
            "rollback": 'sudo sed -i "/APT::Periodic::Unattended-Upgrade/d" /etc/apt/apt.conf.d/20auto-upgrades',
            "expected": "1",
            "rationale": "Keeps system updated with security patches"
        },
        
        {
            "id": "LIN-PKG-002",
            "description": "Remove unnecessary packages",
            "category": LinuxRuleCategory.PACKAGE_MANAGEMENT,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "low",
            "level": ["moderate", "strict"],
            "check": 'dpkg -l | grep -E "^(telnet|rsh|rlogin)" | wc -l || echo "0"',
            "remediate": 'sudo apt-get remove -y telnet rsh-client rlogin 2>/dev/null || true',
            "rollback": 'sudo apt-get install -y telnet rsh-client rlogin 2>/dev/null || true',
            "expected": "0",
            "rationale": "Removes potentially insecure network tools"
        },
        
        # RHEL/CentOS Specific Rules
        {
            "id": "LIN-RHEL-001",
            "description": "Enable automatic security updates (RHEL/CentOS)",
            "category": LinuxRuleCategory.RHEL_SPECIFIC,
            "os": ["centos", "rhel"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check": 'systemctl is-enabled dnf-automatic.timer 2>/dev/null || echo "disabled"',
            "remediate": 'sudo systemctl enable dnf-automatic.timer && sudo systemctl start dnf-automatic.timer',
            "rollback": 'sudo systemctl stop dnf-automatic.timer && sudo systemctl disable dnf-automatic.timer',
            "expected": "enabled",
            "rationale": "Keeps RHEL/CentOS systems updated with security patches"
        },
        
        {
            "id": "LIN-RHEL-002",
            "description": "Configure SELinux enforcing mode",
            "category": LinuxRuleCategory.APPARMOR_SELINUX,
            "os": ["centos", "rhel"],
            "severity": "high",
            "level": ["moderate", "strict"],
            "check": 'getenforce 2>/dev/null || echo "Disabled"',
            "remediate": 'sudo setenforce 1 && echo "SELINUX=enforcing" | sudo tee /etc/selinux/config',
            "rollback": 'sudo setenforce 0 && echo "SELINUX=permissive" | sudo tee /etc/selinux/config',
            "expected": "Enforcing",
            "rationale": "SELinux provides mandatory access control for enhanced security"
        },
        
        {
            "id": "LIN-RHEL-003",
            "description": "Remove unnecessary RHEL/CentOS packages",
            "category": LinuxRuleCategory.RHEL_SPECIFIC,
            "os": ["centos", "rhel"],
            "severity": "low",
            "level": ["moderate", "strict"],
            "check": 'rpm -qa | grep -E "(telnet|rsh|rlogin)" | wc -l || echo "0"',
            "remediate": 'sudo dnf remove -y telnet rsh rlogin 2>/dev/null || true',
            "rollback": 'sudo dnf install -y telnet rsh rlogin 2>/dev/null || true',
            "expected": "0",
            "rationale": "Removes potentially insecure network tools"
        },
        
        # AppArmor/SELinux Advanced Rules
        {
            "id": "LIN-APPARMOR-001",
            "description": "Enable AppArmor (Ubuntu/Debian)",
            "category": LinuxRuleCategory.APPARMOR_SELINUX,
            "os": ["ubuntu", "debian"],
            "severity": "high",
            "level": ["moderate", "strict"],
            "check": 'aa-status 2>/dev/null | head -1 || echo "AppArmor is not enabled"',
            "remediate": 'sudo systemctl enable apparmor && sudo systemctl start apparmor',
            "rollback": 'sudo systemctl stop apparmor && sudo systemctl disable apparmor',
            "expected": "apparmor module is loaded",
            "rationale": "AppArmor provides mandatory access control for Ubuntu/Debian"
        },
        
        {
            "id": "LIN-APPARMOR-002",
            "description": "Set AppArmor profiles to enforce mode",
            "category": LinuxRuleCategory.APPARMOR_SELINUX,
            "os": ["ubuntu", "debian"],
            "severity": "medium",
            "level": ["strict"],
            "check": 'aa-status 2>/dev/null | grep "enforce" | wc -l || echo "0"',
            "remediate": 'sudo aa-enforce /etc/apparmor.d/* 2>/dev/null || true',
            "rollback": 'sudo aa-complain /etc/apparmor.d/* 2>/dev/null || true',
            "expected": "1",
            "rationale": "Enforces AppArmor profiles for maximum security"
        },
        
        # Advanced Kernel Security Rules
        {
            "id": "LIN-KERNEL-004",
            "description": "Disable IPv6 if not needed",
            "category": LinuxRuleCategory.KERNEL_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "low",
            "level": ["strict"],
            "check": 'sysctl net.ipv6.conf.all.disable_ipv6 | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "net.ipv6.conf.all.disable_ipv6 = 1" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/net.ipv6.conf.all.disable_ipv6 = 1/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "1",
            "rationale": "Reduces attack surface if IPv6 is not needed"
        },
        
        {
            "id": "LIN-KERNEL-005",
            "description": "Enable SYN flood protection",
            "category": LinuxRuleCategory.KERNEL_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'sysctl net.ipv4.tcp_syncookies | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "net.ipv4.tcp_syncookies = 1" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/net.ipv4.tcp_syncookies = 1/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "1",
            "rationale": "Protects against SYN flood attacks"
        },
        
        # Advanced Systemd Security Rules
        {
            "id": "LIN-SYSTEMD-001",
            "description": "Set systemd service security options",
            "category": LinuxRuleCategory.SERVICE_MANAGEMENT,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["strict"],
            "check": 'systemctl show ssh | grep "NoNewPrivileges" | cut -d"=" -f2 || echo "no"',
            "remediate": 'sudo systemctl edit ssh --drop-in=override.conf && echo "[Service]\nNoNewPrivileges=yes" | sudo tee /etc/systemd/system/ssh.service.d/override.conf && sudo systemctl daemon-reload',
            "rollback": 'sudo rm -f /etc/systemd/system/ssh.service.d/override.conf && sudo systemctl daemon-reload',
            "expected": "yes",
            "rationale": "Prevents services from gaining new privileges"
        },
        
        # Container Security Rules
        {
            "id": "LIN-CONTAINER-001",
            "description": "Secure Docker daemon configuration",
            "category": LinuxRuleCategory.CONTAINER_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "high",
            "level": ["moderate", "strict"],
            "check": 'grep "tcp://" /etc/docker/daemon.json 2>/dev/null || echo "not_configured"',
            "remediate": 'echo "{\"hosts\": [\"unix:///var/run/docker.sock\"]}" | sudo tee /etc/docker/daemon.json && sudo systemctl restart docker',
            "rollback": 'sudo rm -f /etc/docker/daemon.json && sudo systemctl restart docker',
            "expected": "not_configured",
            "rationale": "Disables Docker daemon TCP socket for security"
        },
        
        {
            "id": "LIN-CONTAINER-002",
            "description": "Enable Docker content trust",
            "category": LinuxRuleCategory.CONTAINER_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["strict"],
            "check": 'echo $DOCKER_CONTENT_TRUST || echo "0"',
            "remediate": 'echo "export DOCKER_CONTENT_TRUST=1" | sudo tee -a /etc/environment',
            "rollback": 'sudo sed -i "/export DOCKER_CONTENT_TRUST=1/d" /etc/environment',
            "expected": "1",
            "rationale": "Ensures only signed images can be pulled"
        },
        
        # Advanced Network Security Rules
        {
            "id": "LIN-NET-003",
            "description": "Disable ICMP redirects",
            "category": LinuxRuleCategory.NETWORK_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'sysctl net.ipv4.conf.all.accept_redirects | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "net.ipv4.conf.all.accept_redirects = 0" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/net.ipv4.conf.all.accept_redirects = 0/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "0",
            "rationale": "Prevents ICMP redirect attacks"
        },
        
        {
            "id": "LIN-NET-004",
            "description": "Enable reverse path filtering",
            "category": LinuxRuleCategory.NETWORK_SECURITY,
            "os": ["linux", "ubuntu", "centos"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check": 'sysctl net.ipv4.conf.all.rp_filter | cut -d"=" -f2 | tr -d " "',
            "remediate": 'echo "net.ipv4.conf.all.rp_filter = 1" | sudo tee -a /etc/sysctl.conf && sudo sysctl -p',
            "rollback": 'sudo sed -i "/net.ipv4.conf.all.rp_filter = 1/d" /etc/sysctl.conf && sudo sysctl -p',
            "expected": "1",
            "rationale": "Prevents IP spoofing attacks"
        }
    ]


def get_rules_by_category(category: LinuxRuleCategory) -> List[Dict[str, Any]]:
    """
    Get rules filtered by category
    
    Args:
        category: Rule category to filter by
        
    Returns:
        List of rules in the specified category
    """
    all_rules = get_linux_hardening_rules()
    return [rule for rule in all_rules if rule.get('category') == category]


def get_rules_by_severity(severity: str) -> List[Dict[str, Any]]:
    """
    Get rules filtered by severity
    
    Args:
        severity: Severity level to filter by
        
    Returns:
        List of rules with the specified severity
    """
    all_rules = get_linux_hardening_rules()
    return [rule for rule in all_rules if rule.get('severity') == severity]


def get_rules_by_level(level: str) -> List[Dict[str, Any]]:
    """
    Get rules filtered by hardening level
    
    Args:
        level: Hardening level to filter by
        
    Returns:
        List of rules for the specified level
    """
    all_rules = get_linux_hardening_rules()
    return [rule for rule in all_rules if level in rule.get('level', [])]
