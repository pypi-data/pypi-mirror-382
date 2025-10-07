"""
Windows-specific hardening rules for OS Forge

Contains comprehensive Windows hardening rules based on:
- CIS Benchmarks for Windows
- NIST Guidelines
- Microsoft Security Baselines
- Common Windows vulnerabilities
"""

from typing import Dict, List, Any
from enum import Enum


class WindowsRuleCategory(str, Enum):
    """Categories for Windows hardening rules"""
    USER_ACCOUNT_CONTROL = "user_account_control"
    WINDOWS_FIREWALL = "windows_firewall"
    WINDOWS_DEFENDER = "windows_defender"
    GROUP_POLICY = "group_policy"
    REGISTRY_SECURITY = "registry_security"
    SERVICE_MANAGEMENT = "service_management"
    NETWORK_SECURITY = "network_security"
    BITLOCKER = "bitlocker"
    AUDIT_LOGGING = "audit_logging"
    WINDOWS_UPDATE = "windows_update"
    REMOTE_ACCESS = "remote_access"
    SYSTEM_CONFIGURATION = "system_configuration"


def get_windows_hardening_rules() -> List[Dict[str, Any]]:
    """
    Get comprehensive list of Windows hardening rules
    
    Returns:
        List of rule dictionaries
    """
    return [
        # User Account Control Rules
        {
            "id": "WIN-UAC-001",
            "description": "Enable User Account Control (UAC)",
            "category": WindowsRuleCategory.USER_ACCOUNT_CONTROL,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "EnableLUA" | Select-Object -ExpandProperty EnableLUA',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "EnableLUA" -Value 1',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "EnableLUA" -Value 0',
            "expected": "1",
            "rationale": "UAC prevents unauthorized system changes and malware execution"
        },
        
        {
            "id": "WIN-UAC-002",
            "description": "Set UAC to always notify",
            "category": WindowsRuleCategory.USER_ACCOUNT_CONTROL,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "ConsentPromptBehaviorAdmin" | Select-Object -ExpandProperty ConsentPromptBehaviorAdmin',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "ConsentPromptBehaviorAdmin" -Value 2',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" -Name "ConsentPromptBehaviorAdmin" -Value 5',
            "expected": "2",
            "rationale": "Maximum UAC protection requires admin consent for all elevation requests"
        },
        
        # Windows Firewall Rules
        {
            "id": "WIN-FW-001",
            "description": "Enable Windows Firewall for all profiles",
            "category": WindowsRuleCategory.WINDOWS_FIREWALL,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "command",
            "check": 'netsh advfirewall show allprofiles | findstr "State"',
            "remediate_type": "command",
            "remediate": 'netsh advfirewall set allprofiles state on',
            "rollback_type": "command",
            "rollback": 'netsh advfirewall set allprofiles state off',
            "expected": "ON",
            "rationale": "Windows Firewall provides essential network security"
        },
        
        {
            "id": "WIN-FW-002",
            "description": "Block inbound connections by default",
            "category": WindowsRuleCategory.WINDOWS_FIREWALL,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "command",
            "check": 'netsh advfirewall show allprofiles | findstr "Inbound"',
            "remediate_type": "command",
            "remediate": 'netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound',
            "rollback_type": "command",
            "rollback": 'netsh advfirewall set allprofiles firewallpolicy allowinbound,allowoutbound',
            "expected": "BlockInbound",
            "rationale": "Blocking inbound connections by default reduces attack surface"
        },
        
        # Windows Defender Rules
        {
            "id": "WIN-DEF-001",
            "description": "Enable Windows Defender real-time protection",
            "category": WindowsRuleCategory.WINDOWS_DEFENDER,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-MpPreference | Select-Object -ExpandProperty DisableRealtimeMonitoring',
            "remediate_type": "powershell",
            "remediate": 'Set-MpPreference -DisableRealtimeMonitoring $false',
            "rollback_type": "powershell",
            "rollback": 'Set-MpPreference -DisableRealtimeMonitoring $true',
            "expected": "False",
            "rationale": "Real-time protection prevents malware execution"
        },
        
        {
            "id": "WIN-DEF-002",
            "description": "Enable Windows Defender cloud protection",
            "category": WindowsRuleCategory.WINDOWS_DEFENDER,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-MpPreference | Select-Object -ExpandProperty MAPSReporting',
            "remediate_type": "powershell",
            "remediate": 'Set-MpPreference -MAPSReporting 2',
            "rollback_type": "powershell",
            "rollback": 'Set-MpPreference -MAPSReporting 0',
            "expected": "2",
            "rationale": "Cloud protection provides enhanced threat detection"
        },
        
        {
            "id": "WIN-DEF-003",
            "description": "Enable Windows Defender automatic sample submission",
            "category": WindowsRuleCategory.WINDOWS_DEFENDER,
            "os": ["windows"],
            "severity": "low",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-MpPreference | Select-Object -ExpandProperty SubmitSamplesConsent',
            "remediate_type": "powershell",
            "remediate": 'Set-MpPreference -SubmitSamplesConsent 2',
            "rollback_type": "powershell",
            "rollback": 'Set-MpPreference -SubmitSamplesConsent 0',
            "expected": "2",
            "rationale": "Sample submission helps improve threat detection"
        },
        
        # Group Policy Rules
        {
            "id": "WIN-GP-001",
            "description": "Disable guest account",
            "category": WindowsRuleCategory.GROUP_POLICY,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-LocalUser -Name "Guest" | Select-Object -ExpandProperty Enabled',
            "remediate_type": "powershell",
            "remediate": 'Disable-LocalUser -Name "Guest"',
            "rollback_type": "powershell",
            "rollback": 'Enable-LocalUser -Name "Guest"',
            "expected": "False",
            "rationale": "Guest account provides unauthorized access to the system"
        },
        
        {
            "id": "WIN-GP-002",
            "description": "Disable SMBv1 protocol",
            "category": WindowsRuleCategory.GROUP_POLICY,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol | Select-Object -ExpandProperty State',
            "remediate_type": "powershell",
            "remediate": 'Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart',
            "rollback_type": "powershell",
            "rollback": 'Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart',
            "expected": "Disabled",
            "rationale": "SMBv1 has known security vulnerabilities"
        },
        
        {
            "id": "WIN-GP-003",
            "description": "Disable SMBv2 client",
            "category": WindowsRuleCategory.GROUP_POLICY,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" -Name "RequireSecuritySignature" | Select-Object -ExpandProperty RequireSecuritySignature',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" -Name "RequireSecuritySignature" -Value 1',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" -Name "RequireSecuritySignature" -Value 0',
            "expected": "1",
            "rationale": "Requiring security signatures prevents man-in-the-middle attacks"
        },
        
        # Registry Security Rules
        {
            "id": "WIN-REG-001",
            "description": "Disable Windows Script Host",
            "category": WindowsRuleCategory.REGISTRY_SECURITY,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows Script Host\\Settings" -Name "Enabled" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Enabled',
            "remediate_type": "powershell",
            "remediate": 'New-Item -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows Script Host\\Settings" -Force; Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows Script Host\\Settings" -Name "Enabled" -Value 0',
            "rollback_type": "powershell",
            "rollback": 'Remove-Item -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows Script Host\\Settings" -Recurse -Force',
            "expected": "0",
            "rationale": "Disabling WSH prevents malicious script execution"
        },
        
        {
            "id": "WIN-REG-002",
            "description": "Disable AutoRun for all drives",
            "category": WindowsRuleCategory.REGISTRY_SECURITY,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" -Name "NoDriveTypeAutoRun" | Select-Object -ExpandProperty NoDriveTypeAutoRun',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" -Name "NoDriveTypeAutoRun" -Value 255',
            "rollback_type": "powershell",
            "rollback": 'Remove-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" -Name "NoDriveTypeAutoRun"',
            "expected": "255",
            "rationale": "Disabling AutoRun prevents malware from executing from removable drives"
        },
        
        # Service Management Rules
        {
            "id": "WIN-SVC-001",
            "description": "Disable Telnet service",
            "category": WindowsRuleCategory.SERVICE_MANAGEMENT,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-Service -Name "Telnet" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Status',
            "remediate_type": "powershell",
            "remediate": 'Stop-Service -Name "Telnet" -ErrorAction SilentlyContinue; Set-Service -Name "Telnet" -StartupType Disabled -ErrorAction SilentlyContinue',
            "rollback_type": "powershell",
            "rollback": 'Set-Service -Name "Telnet" -StartupType Manual -ErrorAction SilentlyContinue',
            "expected": "Stopped",
            "rationale": "Telnet transmits credentials in plain text"
        },
        
        {
            "id": "WIN-SVC-002",
            "description": "Disable Remote Registry service",
            "category": WindowsRuleCategory.SERVICE_MANAGEMENT,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-Service -Name "RemoteRegistry" | Select-Object -ExpandProperty StartType',
            "remediate_type": "powershell",
            "remediate": 'Set-Service -Name "RemoteRegistry" -StartupType Disabled',
            "rollback_type": "powershell",
            "rollback": 'Set-Service -Name "RemoteRegistry" -StartupType Manual',
            "expected": "Disabled",
            "rationale": "Remote Registry allows unauthorized access to registry"
        },
        
        # Network Security Rules
        {
            "id": "WIN-NET-001",
            "description": "Disable NetBIOS over TCP/IP",
            "category": WindowsRuleCategory.NETWORK_SECURITY,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-NetAdapterBinding -ComponentID ms_tcpip6 | Where-Object {$_.Name -like "*NetBIOS*"} | Select-Object -ExpandProperty Enabled',
            "remediate_type": "powershell",
            "remediate": 'Disable-NetAdapterBinding -Name "*" -ComponentID ms_tcpip6',
            "rollback_type": "powershell",
            "rollback": 'Enable-NetAdapterBinding -Name "*" -ComponentID ms_tcpip6',
            "expected": "False",
            "rationale": "NetBIOS over TCP/IP can leak system information"
        },
        
        {
            "id": "WIN-NET-002",
            "description": "Disable LLMNR (Link-Local Multicast Name Resolution)",
            "category": WindowsRuleCategory.NETWORK_SECURITY,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\DNSClient" -Name "EnableMulticast" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty EnableMulticast',
            "remediate_type": "powershell",
            "remediate": 'New-Item -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\DNSClient" -Force; Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\DNSClient" -Name "EnableMulticast" -Value 0',
            "rollback_type": "powershell",
            "rollback": 'Remove-Item -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\DNSClient" -Recurse -Force',
            "expected": "0",
            "rationale": "LLMNR can be used for DNS poisoning attacks"
        },
        
        # BitLocker Rules
        {
            "id": "WIN-BIT-001",
            "description": "Enable BitLocker for system drive",
            "category": WindowsRuleCategory.BITLOCKER,
            "os": ["windows"],
            "severity": "high",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-BitLockerVolume -MountPoint "C:" | Select-Object -ExpandProperty VolumeStatus',
            "remediate_type": "powershell",
            "remediate": 'Enable-BitLocker -MountPoint "C:" -EncryptionMethod XtsAes256 -UsedSpaceOnly',
            "rollback_type": "powershell",
            "rollback": 'Disable-BitLocker -MountPoint "C:"',
            "expected": "FullyEncrypted",
            "rationale": "BitLocker protects data in case of physical theft"
        },
        
        {
            "id": "WIN-BIT-002",
            "description": "Configure BitLocker to use TPM + PIN",
            "category": WindowsRuleCategory.BITLOCKER,
            "os": ["windows"],
            "severity": "medium",
            "level": ["strict"],
            "check_type": "powershell",
            "check": 'Get-BitLockerVolume -MountPoint "C:" | Select-Object -ExpandProperty KeyProtector',
            "remediate_type": "powershell",
            "remediate": 'Add-BitLockerKeyProtector -MountPoint "C:" -TpmAndPinProtector',
            "rollback_type": "powershell",
            "rollback": 'Remove-BitLockerKeyProtector -MountPoint "C:" -KeyProtectorId (Get-BitLockerVolume -MountPoint "C:").KeyProtector[0].KeyProtectorId',
            "expected": "TpmAndPin",
            "rationale": "TPM + PIN provides stronger authentication than TPM alone"
        },
        
        # Audit Logging Rules
        {
            "id": "WIN-AUDIT-001",
            "description": "Enable audit logon events",
            "category": WindowsRuleCategory.AUDIT_LOGGING,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'auditpol /get /category:"Logon/Logoff" | findstr "Logon"',
            "remediate_type": "command",
            "remediate": 'auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable',
            "rollback_type": "command",
            "rollback": 'auditpol /set /category:"Logon/Logoff" /success:disable /failure:disable',
            "expected": "Success and Failure",
            "rationale": "Audit logging helps track security events"
        },
        
        {
            "id": "WIN-AUDIT-002",
            "description": "Enable audit object access",
            "category": WindowsRuleCategory.AUDIT_LOGGING,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'auditpol /get /category:"Object Access" | findstr "Object Access"',
            "remediate_type": "command",
            "remediate": 'auditpol /set /category:"Object Access" /success:enable /failure:enable',
            "rollback_type": "command",
            "rollback": 'auditpol /set /category:"Object Access" /success:disable /failure:disable',
            "expected": "Success and Failure",
            "rationale": "Object access auditing tracks file and registry access"
        },
        
        # Windows Update Rules
        {
            "id": "WIN-UPD-001",
            "description": "Enable automatic Windows updates",
            "category": WindowsRuleCategory.WINDOWS_UPDATE,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "NoAutoUpdate" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty NoAutoUpdate',
            "remediate_type": "powershell",
            "remediate": 'New-Item -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Force; Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "NoAutoUpdate" -Value 0',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "NoAutoUpdate" -Value 1',
            "expected": "0",
            "rationale": "Automatic updates keep system patched with security fixes"
        },
        
        {
            "id": "WIN-UPD-002",
            "description": "Configure Windows Update to install updates automatically",
            "category": WindowsRuleCategory.WINDOWS_UPDATE,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "AUOptions" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty AUOptions',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "AUOptions" -Value 4',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" -Name "AUOptions" -Value 2',
            "expected": "4",
            "rationale": "Automatic installation ensures critical updates are applied promptly"
        },
        
        # Remote Access Rules
        {
            "id": "WIN-RDP-001",
            "description": "Enable Network Level Authentication for RDP",
            "category": WindowsRuleCategory.REMOTE_ACCESS,
            "os": ["windows"],
            "severity": "high",
            "level": ["basic", "moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "UserAuthentication" | Select-Object -ExpandProperty UserAuthentication',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "UserAuthentication" -Value 1',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "UserAuthentication" -Value 0',
            "expected": "1",
            "rationale": "NLA prevents RDP brute force attacks"
        },
        
        {
            "id": "WIN-RDP-002",
            "description": "Set RDP encryption level to High",
            "category": WindowsRuleCategory.REMOTE_ACCESS,
            "os": ["windows"],
            "severity": "medium",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "MinEncryptionLevel" | Select-Object -ExpandProperty MinEncryptionLevel',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "MinEncryptionLevel" -Value 3',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -Name "MinEncryptionLevel" -Value 1',
            "expected": "3",
            "rationale": "High encryption level protects RDP sessions from eavesdropping"
        },
        
        # System Configuration Rules
        {
            "id": "WIN-SYS-001",
            "description": "Disable Windows Error Reporting",
            "category": WindowsRuleCategory.SYSTEM_CONFIGURATION,
            "os": ["windows"],
            "severity": "low",
            "level": ["moderate", "strict"],
            "check_type": "powershell",
            "check": 'Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" -Name "Disabled" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Disabled',
            "remediate_type": "powershell",
            "remediate": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" -Name "Disabled" -Value 1',
            "rollback_type": "powershell",
            "rollback": 'Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting" -Name "Disabled" -Value 0',
            "expected": "1",
            "rationale": "Disabling error reporting prevents potential information leakage"
        },
        
        {
            "id": "WIN-SYS-002",
            "description": "Disable Windows Search indexing",
            "category": WindowsRuleCategory.SYSTEM_CONFIGURATION,
            "os": ["windows"],
            "severity": "low",
            "level": ["strict"],
            "check_type": "powershell",
            "check": 'Get-Service -Name "WSearch" | Select-Object -ExpandProperty StartType',
            "remediate_type": "powershell",
            "remediate": 'Set-Service -Name "WSearch" -StartupType Disabled',
            "rollback_type": "powershell",
            "rollback": 'Set-Service -Name "WSearch" -StartupType Automatic',
            "expected": "Disabled",
            "rationale": "Disabling search indexing reduces system resource usage and attack surface"
        }
    ]


def get_rules_by_category(category: WindowsRuleCategory) -> List[Dict[str, Any]]:
    """
    Get rules filtered by category
    
    Args:
        category: Rule category to filter by
        
    Returns:
        List of rules in the specified category
    """
    all_rules = get_windows_hardening_rules()
    return [rule for rule in all_rules if rule.get('category') == category]


def get_rules_by_severity(severity: str) -> List[Dict[str, Any]]:
    """
    Get rules filtered by severity
    
    Args:
        severity: Severity level to filter by
        
    Returns:
        List of rules with the specified severity
    """
    all_rules = get_windows_hardening_rules()
    return [rule for rule in all_rules if rule.get('severity') == severity]


def get_rules_by_level(level: str) -> List[Dict[str, Any]]:
    """
    Get rules filtered by hardening level
    
    Args:
        level: Hardening level to filter by
        
    Returns:
        List of rules for the specified level
    """
    all_rules = get_windows_hardening_rules()
    return [rule for rule in all_rules if level in rule.get('level', [])]
