import type { SystemInfoResponse, RulesListResponse, RunResponse } from "./types"

export const systemInfoDemo: SystemInfoResponse = {
  message: "OS Forge - Multi-Platform System Hardening Tool",
  detected_os: "windows",
  available_rules: 17,
  rule_counts: { basic: 7, moderate: 13, strict: 16 },
}

export const rulesListDemo: RulesListResponse = {
  rules: [
    {
      id: "WIN-001",
      description: "Check if Guest account is disabled",
      os: "windows",
      severity: "high",
      level: ["basic", "moderate", "strict"],
      check: 'powershell -Command "Get-LocalUser -Name Guest | Select-Object -ExpandProperty Enabled"',
      remediate: 'powershell -Command "Disable-LocalUser -Name Guest"',
      rollback: 'powershell -Command "Enable-LocalUser -Name Guest"',
      expected: "False",
    },
    {
      id: "WIN-002",
      description: "Check Windows Firewall status",
      os: "windows",
      severity: "critical",
      level: ["basic", "moderate", "strict"],
      check: 'powershell -Command "Get-NetFirewallProfile -Profile Domain | Select-Object -ExpandProperty Enabled"',
      remediate: 'powershell -Command "Set-NetFirewallProfile -Profile Domain -Enabled True"',
      rollback: 'powershell -Command "Set-NetFirewallProfile -Profile Domain -Enabled False"',
      expected: "True",
    },
    {
      id: "WIN-004",
      description: "Check Windows Defender real-time protection",
      os: "windows",
      severity: "critical",
      level: ["basic", "moderate", "strict"],
      check: 'powershell -Command "Get-MpPreference | Select-Object -ExpandProperty DisableRealtimeMonitoring"',
      remediate: 'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false"',
      rollback: 'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
      expected: "False",
    },
    {
      id: "WIN-005",
      description: "Check UAC setting",
      os: "windows",
      severity: "high",
      level: ["basic", "moderate", "strict"],
      check:
        'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD | findstr "0x1"',
      remediate:
        'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 1 /f',
      rollback:
        'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 0 /f',
      expected: "0x1",
    },
    {
      id: "LIN-001",
      description: "Check if SSH root login is disabled",
      os: ["ubuntu", "centos", "linux"],
      severity: "high",
      level: ["basic", "moderate", "strict"],
      check: 'grep "^PermitRootLogin" /etc/ssh/sshd_config || echo "PermitRootLogin yes"',
      remediate:
        'sudo sed -i "s/^PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config && sudo systemctl reload ssh',
      rollback:
        'sudo sed -i "s/^PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config && sudo systemctl reload ssh',
      expected: "PermitRootLogin no",
    },
    {
      id: "LIN-002",
      description: "Check if UFW firewall is enabled",
      os: ["ubuntu", "linux"],
      severity: "high",
      level: ["basic", "moderate", "strict"],
      check: 'sudo ufw status | grep "Status:" | cut -d" " -f2',
      remediate: "sudo ufw --force enable",
      rollback: "sudo ufw --force disable",
      expected: "active",
    },
    {
      id: "LIN-004",
      description: "Check SSH Protocol version",
      os: ["ubuntu", "centos", "linux"],
      severity: "high",
      level: ["basic", "moderate", "strict"],
      check: 'grep "^Protocol" /etc/ssh/sshd_config | cut -d" " -f2 || echo "2"',
      remediate: 'echo "Protocol 2" | sudo tee -a /etc/ssh/sshd_config && sudo systemctl reload ssh',
      rollback: 'sudo sed -i "/^Protocol 2/d" /etc/ssh/sshd_config && sudo systemctl reload ssh',
      expected: "2",
    },
  ],
  count: 7,
}

export const runResultsDemo: RunResponse = {
  status: "completed",
  dry_run: true,
  level: "basic",
  results: [
    {
      rule_id: "WIN-001",
      description: "Check if Guest account is disabled",
      severity: "high",
      status: "pass",
      old_value: "False",
      new_value: "False",
      error: null,
    },
    {
      rule_id: "WIN-002",
      description: "Check Windows Firewall status",
      severity: "critical",
      status: "pass",
      old_value: "True",
      new_value: "True",
      error: null,
    },
    {
      rule_id: "WIN-004",
      description: "Check Windows Defender real-time protection",
      severity: "critical",
      status: "pass",
      old_value: "False",
      new_value: "False",
      error: null,
    },
    {
      rule_id: "WIN-005",
      description: "Check UAC setting",
      severity: "high",
      status: "fail",
      old_value: "EnableLUA    REG_DWORD    0x1",
      new_value: "EnableLUA    REG_DWORD    0x1",
      error: null,
    },
    {
      rule_id: "LIN-001",
      description: "Check if SSH root login is disabled",
      severity: "high",
      status: "error",
      old_value: null,
      new_value: null,
      error:
        'Security validation failed: Command not allowed: grep "^PermitRootLogin" /etc/ssh/sshd_config || echo "PermitRootLogin yes"',
    },
    {
      rule_id: "LIN-002",
      description: "Check if UFW firewall is enabled",
      severity: "high",
      status: "error",
      old_value: null,
      new_value: null,
      error: 'Security validation failed: Command not allowed: sudo ufw status | grep "Status:" | cut -d" " -f2',
    },
    {
      rule_id: "LIN-004",
      description: "Check SSH Protocol version",
      severity: "high",
      status: "error",
      old_value: null,
      new_value: null,
      error:
        'Security validation failed: Command not allowed: grep "^Protocol" /etc/ssh/sshd_config | cut -d" " -f2 || echo "2"',
    },
  ],
  summary: {
    total: 7,
    passed: 3,
    failed: 1,
    errors: 3,
  },
}

export const reportLinksDemo = {
  html: "/report",
  pdf: "/report/pdf",
  history: "/history",
}
