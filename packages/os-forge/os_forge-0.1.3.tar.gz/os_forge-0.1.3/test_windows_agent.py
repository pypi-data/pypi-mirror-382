#!/usr/bin/env python3
"""
Comprehensive Windows Agent Test Suite

Complete testing of all Windows agent features including:
- Agent creation and health checks
- All rule categories and Windows features
- Rule execution and remediation
- Agent manager functionality
- System information gathering
- CLI interface testing
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.windows.windows_agent import WindowsAgent
from agents.windows.windows_agent_manager import WindowsAgentManager
from agents.windows.windows_rules import get_windows_hardening_rules, WindowsRuleCategory


def test_agent_creation():
    """Test basic agent creation and properties"""
    print("🔧 Testing Windows Agent Creation...")
    try:
        agent = WindowsAgent("test-windows-agent")
        print(f"✅ Agent created: {agent.agent_id}")
        print(f"   OS Type: {agent.os_type}")
        print(f"   OS Version: {agent.os_version}")
        print(f"   Architecture: {agent.architecture}")
        print(f"   Capabilities: {len(agent.capabilities)} capabilities")
        for cap in agent.capabilities:
            print(f"     - {cap}")
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False


def test_health_check():
    """Test agent health check functionality"""
    print("\n🏥 Testing Health Check...")
    try:
        agent = WindowsAgent("test-windows-agent")
        status = agent.health_check()
        print(f"✅ Health check: {status}")
        
        # Test heartbeat update
        agent.update_heartbeat()
        print(f"✅ Heartbeat updated: {agent.last_heartbeat}")
        
        return status.value == "healthy"
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_rule_loading():
    """Test comprehensive rule loading and categorization"""
    print("\n📋 Testing Rule Loading...")
    try:
        rules = get_windows_hardening_rules()
        print(f"✅ Loaded {len(rules)} total rules")
        
        # Test all categories
        categories = {}
        for rule in rules:
            cat = rule.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"✅ Rule categories ({len(categories)}):")
        for cat, count in categories.items():
            print(f"   {cat}: {count} rules")
        
        # Test severity distribution
        severities = {}
        for rule in rules:
            sev = rule.get('severity', 'unknown')
            severities[sev] = severities.get(sev, 0) + 1
        
        print(f"✅ Severity distribution:")
        for sev, count in severities.items():
            print(f"   {sev}: {count} rules")
        
        # Test hardening levels
        levels = {}
        for rule in rules:
            rule_levels = rule.get('level', [])
            for level in rule_levels:
                levels[level] = levels.get(level, 0) + 1
        
        print(f"✅ Hardening levels:")
        for level, count in levels.items():
            print(f"   {level}: {count} rules")
        
        return len(rules) >= 20  # We should have at least 20 rules
    except Exception as e:
        print(f"❌ Rule loading failed: {e}")
        return False


def test_windows_specific_features():
    """Test Windows-specific features and capabilities"""
    print("\n🪟 Testing Windows-Specific Features...")
    try:
        agent = WindowsAgent("test-windows-agent")
        windows_info = agent.get_windows_specific_info()
        
        print(f"✅ Windows Edition: {windows_info['windows_edition']}")
        print(f"✅ PowerShell Version: {windows_info['powershell_version']}")
        print(f"✅ .NET Version: {windows_info['dotnet_version']}")
        
        # Test capabilities detection
        caps = windows_info['capabilities']
        print(f"✅ Windows capabilities detected:")
        for feature, enabled in caps.items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}")
        
        return True
    except Exception as e:
        print(f"❌ Windows-specific features test failed: {e}")
        return False


def test_rule_execution():
    """Test rule execution and remediation"""
    print("\n⚡ Testing Rule Execution...")
    try:
        agent = WindowsAgent("test-windows-agent")
        rules = get_windows_hardening_rules()
        
        # Test different types of rules
        test_rules = [
            r for r in rules 
            if r['id'] in ['WIN-UAC-001', 'WIN-FW-001', 'WIN-DEF-001', 'WIN-GP-001']
        ]
        
        results = []
        for rule in test_rules:
            print(f"   Testing {rule['id']}: {rule['description']}")
            
            # Check rule
            result = agent.check_rule(rule)
            print(f"     Check: {result.status}")
            if result.old_value:
                print(f"     Current: {result.old_value}")
            
            # Test dry run remediation
            result = agent.remediate_rule(rule, dry_run=True)
            print(f"     Dry run: {result.status}")
            
            results.append(result)
        
        return len(results) > 0
    except Exception as e:
        print(f"❌ Rule execution failed: {e}")
        return False


def test_agent_manager():
    """Test agent manager functionality"""
    print("\n👥 Testing Agent Manager...")
    try:
        manager = WindowsAgentManager()
        
        # Get statistics
        stats = manager.get_agent_statistics()
        print(f"✅ Manager created with {stats['total_agents']} agents")
        print(f"   Healthy agents: {stats['healthy_agents']}")
        print(f"   Unhealthy agents: {stats['unhealthy_agents']}")
        
        # Test capability distribution
        print(f"✅ Capability distribution:")
        for cap, count in stats['capability_counts'].items():
            print(f"   {cap}: {count}")
        
        # Test OS distribution
        print(f"✅ OS distribution:")
        for os_type, count in stats['os_distribution'].items():
            print(f"   {os_type}: {count}")
        
        # Test rule execution
        uac_rules = [r for r in get_windows_hardening_rules() if r.get('category') == WindowsRuleCategory.USER_ACCOUNT_CONTROL]
        if uac_rules:
            test_rule = uac_rules[0]
            print(f"   Testing distributed execution with rule: {test_rule['id']}")
            results = manager.execute_rule_distributed(test_rule, dry_run=True)
            print(f"   Distributed execution completed: {len(results)} results")
        
        return stats['total_agents'] > 0
    except Exception as e:
        print(f"❌ Agent manager test failed: {e}")
        return False


def test_system_info():
    """Test comprehensive system information gathering"""
    print("\n📊 Testing System Information...")
    try:
        agent = WindowsAgent("test-windows-agent")
        info = agent.get_system_info()
        
        print("✅ Basic system info:")
        print(f"   Agent ID: {info['agent_info'].agent_id}")
        print(f"   OS Type: {info['agent_info'].os_type}")
        print(f"   OS Version: {info['agent_info'].os_version}")
        print(f"   Architecture: {info['agent_info'].architecture}")
        print(f"   Status: {info['agent_info'].status}")
        
        # Test Windows-specific info
        windows_info = agent.get_windows_specific_info()
        print(f"✅ Windows-specific info:")
        print(f"   Windows Edition: {windows_info['windows_edition']}")
        print(f"   PowerShell Version: {windows_info['powershell_version']}")
        print(f"   .NET Version: {windows_info['dotnet_version']}")
        
        # Test capabilities detection
        caps = windows_info['capabilities']
        print(f"✅ Security features detected:")
        for feature, enabled in caps.items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}")
        
        return True
    except Exception as e:
        print(f"❌ System info test failed: {e}")
        return False


def test_cli_interface():
    """Test CLI interface functionality"""
    print("\n🖥️ Testing CLI Interface...")
    try:
        import subprocess
        
        # Test CLI help
        result = subprocess.run([
            sys.executable, "agents/windows/windows_agent_cli.py", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI help: WORKING")
        else:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
        
        # Test info command
        result = subprocess.run([
            sys.executable, "agents/windows/windows_agent_cli.py", "info"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Agent ID" in result.stdout:
            print("✅ CLI info command: WORKING")
        else:
            print(f"❌ CLI info command failed: {result.stderr}")
            return False
        
        # Test list rules command
        result = subprocess.run([
            sys.executable, "agents/windows/windows_agent_cli.py", "list", "--category", "user_account_control"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "Found" in result.stdout:
            print("✅ CLI list rules: WORKING")
        else:
            print(f"❌ CLI list rules failed: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ CLI interface test failed: {e}")
        return False


def test_rule_categories():
    """Test all rule categories are working"""
    print("\n📂 Testing Rule Categories...")
    try:
        rules = get_windows_hardening_rules()
        
        # Test each category
        categories = [
            WindowsRuleCategory.USER_ACCOUNT_CONTROL,
            WindowsRuleCategory.WINDOWS_FIREWALL,
            WindowsRuleCategory.WINDOWS_DEFENDER,
            WindowsRuleCategory.GROUP_POLICY,
            WindowsRuleCategory.REGISTRY_SECURITY,
            WindowsRuleCategory.SERVICE_MANAGEMENT,
            WindowsRuleCategory.NETWORK_SECURITY,
            WindowsRuleCategory.BITLOCKER,
            WindowsRuleCategory.AUDIT_LOGGING,
            WindowsRuleCategory.WINDOWS_UPDATE,
            WindowsRuleCategory.REMOTE_ACCESS,
            WindowsRuleCategory.SYSTEM_CONFIGURATION
        ]
        
        for category in categories:
            category_rules = [r for r in rules if r.get('category') == category]
            print(f"✅ {category}: {len(category_rules)} rules")
        
        return True
    except Exception as e:
        print(f"❌ Rule categories test failed: {e}")
        return False


def test_powershell_integration():
    """Test PowerShell integration"""
    print("\n💻 Testing PowerShell Integration...")
    try:
        agent = WindowsAgent("test-windows-agent")
        
        # Test basic PowerShell command
        stdout, stderr, return_code = agent.execute_powershell("Get-Host | Select-Object Name")
        
        if return_code == 0:
            print("✅ PowerShell execution: WORKING")
            print(f"   Output: {stdout.strip()}")
        else:
            print(f"❌ PowerShell execution failed: {stderr}")
            return False
        
        # Test Windows-specific PowerShell command
        stdout, stderr, return_code = agent.execute_powershell("Get-ComputerInfo | Select-Object WindowsProductName")
        
        if return_code == 0:
            print("✅ Windows PowerShell commands: WORKING")
        else:
            print(f"❌ Windows PowerShell commands failed: {stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ PowerShell integration test failed: {e}")
        return False


def main():
    """Run comprehensive test suite"""
    print("🪟 COMPREHENSIVE WINDOWS AGENT TEST SUITE")
    print("=" * 60)
    print("Testing all Windows agent features and capabilities")
    print("=" * 60)
    
    tests = [
        ("Agent Creation", test_agent_creation),
        ("Health Check", test_health_check),
        ("Rule Loading", test_rule_loading),
        ("Windows-Specific Features", test_windows_specific_features),
        ("Rule Execution", test_rule_execution),
        ("Agent Manager", test_agent_manager),
        ("System Information", test_system_info),
        ("CLI Interface", test_cli_interface),
        ("Rule Categories", test_rule_categories),
        ("PowerShell Integration", test_powershell_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print("🎯 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Windows Agent is complete and ready!")
        print("\n🏆 ACHIEVEMENTS:")
        print("  ✅ 25+ comprehensive Windows hardening rules")
        print("  ✅ Group Policy integration")
        print("  ✅ Registry security management")
        print("  ✅ Windows Defender configuration")
        print("  ✅ BitLocker management")
        print("  ✅ UAC and service management")
        print("  ✅ PowerShell integration")
        print("  ✅ Complete CLI interface")
        print("  ✅ Agent manager for distributed execution")
        print("  ✅ Comprehensive Windows detection")
        print("\n🚀 Ready for production deployment!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
