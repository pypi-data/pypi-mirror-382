'use client';

import React, { useState, useEffect } from 'react';
import {
  Shield,
  Server,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Download,
  RotateCcw,
  LayoutDashboard,
  ClipboardList,
  FileText,
  History,
  Loader2,
  ChevronDown
} from 'lucide-react';
import axios from 'axios';
import Link from 'next/link';


interface SystemInfo {
  message: string;
  detected_os: string;
  available_rules: number;
}

interface RuleResult {
  rule_id: string;
  description: string;
  severity: string;
  status: string;
  old_value?: string;
  new_value?: string;
  error?: string;
}

interface ExecutionResult {
  status: string;
  dry_run: boolean;
  level: string;
  results: RuleResult[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    errors: number;
  };
}

interface RollbackOption {
  rule_id: string;
  description: string;
  last_applied: string;
  current_status: string;
}

interface ApiRule {
  id: string;
  description: string;
  os: string | string[];
  severity: string;
  level: string[];
}

type Tab = 'dashboard' | 'security_check' | 'rule_library' | 'reports' | 'rollback';



const StatCard = ({ title, value, icon: Icon }: { title: string; value: string | number; icon: React.ElementType }) => (
  <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
      </div>
      <div className="bg-gray-100 rounded-full p-2">
        <Icon className="h-6 w-6 text-gray-500" />
      </div>
    </div>
  </div>
);

const SeverityBadge = ({ severity }: { severity: string }) => {
  const styles = {
    critical: 'bg-red-100 text-red-800 border-red-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200',
    default: 'bg-gray-100 text-gray-800 border-gray-200'
  };
  const style = styles[severity.toLowerCase() as keyof typeof styles] || styles.default;
  return (
    <span className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${style}`}>
      {severity.toUpperCase()}
    </span>
  );
};

const StatusIcon = ({ status }: { status: string }) => {
  switch (status) {
    case 'pass': return <CheckCircle className="h-5 w-5 text-green-500" />;
    case 'fail': return <XCircle className="h-5 w-5 text-red-500" />;
    case 'error': return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    default: return <AlertTriangle className="h-5 w-5 text-gray-400" />;
  }
};



export default function Dashboard() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [executionResults, setExecutionResults] = useState<ExecutionResult | null>(null);
  const [rollbackOptions, setRollbackOptions] = useState<RollbackOption[]>([]);
  const [allRules, setAllRules] = useState<ApiRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedLevel, setSelectedLevel] = useState<'basic' | 'moderate' | 'strict'>('basic');
  const [dryRun, setDryRun] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());


  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchSystemInfo();
    fetchRollbackOptions();
    fetchAllRules();
  }, []);

  const toggleRowExpansion = (ruleId: string) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(ruleId)) {
        newSet.delete(ruleId);
      } else {
        newSet.add(ruleId);
      }
      return newSet;
    });
  };

  const fetchSystemInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE}/`);
      setSystemInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch system info:', error);
    }
  };

  const fetchRollbackOptions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/rollback/available`);
      setRollbackOptions(response.data.rollback_options || []);
    } catch (error) {
      console.error('Failed to fetch rollback options:', error);
    }
  };

  const fetchAllRules = async () => {
    try {
      const response = await axios.get(`${API_BASE}/rules`);
      setAllRules(response.data.rules || []);
    } catch (error) {
      console.error('Failed to fetch all rules:', error);
    }
  };

  const executeHardening = async () => {
    setLoading(true);
    setExecutionResults(null);
    try {
      const response = await axios.post(
        `${API_BASE}/run?level=${selectedLevel}&dry_run=${dryRun}`,
        {},
        { headers: { 'Authorization': 'Bearer dev-key-change-in-production' } }
      );
      setExecutionResults(response.data);
      fetchRollbackOptions();
    } catch (error) {
      console.error('Failed to execute hardening:', error);
    } finally {
      setLoading(false);
    }
  };

  const rollbackRule = async (ruleId: string) => {
    try {
      await axios.post(`${API_BASE}/rollback/${ruleId}`);
      fetchRollbackOptions();
      alert(`Successfully rolled back rule ${ruleId}`);
    } catch (error) {
      console.error('Failed to rollback rule:', error);
      alert(`Failed to rollback rule ${ruleId}`);
    }
  };

  const SidebarItem = ({ id, label, icon: Icon }: { id: Tab, label: string, icon: React.ElementType }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center w-full px-4 py-2.5 text-sm font-medium rounded-md transition-colors ${
        activeTab === id
          ? 'bg-gray-900 text-white'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }`}
    >
      <Icon className="h-5 w-5 mr-3" />
      <span>{label}</span>
    </button>
  );

  const renderContent = () => {
    switch (activeTab) {
        case 'dashboard':
            return (
                <div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <StatCard title="Detected OS" value={systemInfo?.detected_os || '...'} icon={Server} />
                        <StatCard title="Available Rules" value={systemInfo?.available_rules || 0} icon={Shield} />
                        <StatCard title="Rollback Options" value={rollbackOptions.length} icon={History} />
                    </div>
                    {executionResults ? (
                        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Latest Scan Results</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                                <div>
                                    <p className="text-3xl font-bold text-gray-800">{executionResults.summary.total}</p>
                                    <p className="text-sm text-gray-500">Total Checks</p>
                                </div>
                                <div>
                                    <p className="text-3xl font-bold text-green-600">{executionResults.summary.passed}</p>
                                    <p className="text-sm text-gray-500">Passed</p>
                                </div>
                                <div>
                                    <p className="text-3xl font-bold text-red-600">{executionResults.summary.failed}</p>
                                    <p className="text-sm text-gray-500">Failed</p>
                                </div>
                                <div>
                                    <p className="text-3xl font-bold text-yellow-600">{executionResults.summary.errors}</p>
                                    <p className="text-sm text-gray-500">Errors</p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center bg-white border border-gray-200 rounded-lg py-12 px-6 shadow-sm">
                            <ClipboardList className="mx-auto h-12 w-12 text-gray-400" />
                            <h3 className="mt-2 text-lg font-medium text-gray-900">No results yet</h3>
                            <p className="mt-1 text-sm text-gray-500">Run a security check to see the latest results.</p>
                        </div>
                    )}
                </div>
            );
        case 'security_check':
            return (
                <div className="space-y-8">
                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-6">Security Hardening Configuration</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Hardening Level</label>
                                <select value={selectedLevel} onChange={(e) => setSelectedLevel(e.target.value as any)} className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                    <option value="basic">Basic</option>
                                    <option value="moderate">Moderate</option>
                                    <option value="strict">Strict</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Execution Mode</label>
                                <select value={dryRun ? 'dry_run' : 'apply'} onChange={(e) => setDryRun(e.target.value === 'dry_run')} className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                    <option value="dry_run">Dry Run (Safe)</option>
                                    <option value="apply">Apply Changes</option>
                                </select>
                            </div>
                            <div className="flex items-end">
                                <button onClick={executeHardening} disabled={loading} className="w-full flex justify-center items-center bg-gray-800 hover:bg-gray-700 disabled:bg-gray-400 text-white font-semibold py-2.5 px-4 rounded-md transition-colors">
                                    {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Run Security Check'}
                                </button>
                            </div>
                        </div>
                    </div>
                    {loading && !executionResults && (
                      <div className="text-center py-12">
                        <Loader2 className="mx-auto h-10 w-10 text-gray-500 animate-spin" />
                        <p className="mt-4 text-gray-600">Running security check...</p>
                      </div>
                    )}
                    {executionResults && (
                        <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                            <div className="p-6 border-b">
                                <h3 className="text-lg font-semibold text-gray-900">
                                    Scan Results <span className="text-sm font-normal text-gray-500">({executionResults.dry_run ? 'Dry Run' : 'Changes Applied'})</span>
                                </h3>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rule ID</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                                            <th className="px-6 py-3 w-[50px]"></th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {executionResults.results.map((result) => (
                                          <React.Fragment key={result.rule_id}>
                                            <tr>
                                                <td className="px-6 py-4 whitespace-nowrap"><StatusIcon status={result.status} /></td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-700">{result.rule_id}</td>
                                                <td className="px-6 py-4 text-sm text-gray-600">{result.description}</td>
                                                <td className="px-6 py-4 whitespace-nowrap"><SeverityBadge severity={result.severity} /></td>
                                                <td className="px-6 py-4">
                                                  <button onClick={() => toggleRowExpansion(result.rule_id)} className="text-gray-400 hover:text-gray-600">
                                                    <ChevronDown className={`h-5 w-5 transition-transform ${expandedRows.has(result.rule_id) ? 'rotate-180' : ''}`} />
                                                  </button>
                                                </td>
                                            </tr>
                                            {expandedRows.has(result.rule_id) && (
                                              <tr key={`${result.rule_id}-details`}>
                                                <td colSpan={5} className="p-0">
                                                  <div className="p-4 bg-gray-50">
                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                                                      {result.old_value != null && (
                                                        <div>
                                                          <p className="font-semibold text-gray-600 mb-1">Current Value</p>
                                                          <code className="block bg-gray-200 text-gray-800 p-2 rounded-md whitespace-pre-wrap font-mono">{result.old_value || 'N/A'}</code>
                                                        </div>
                                                      )}
                                                      {result.new_value != null && (
                                                        <div>
                                                          <p className="font-semibold text-gray-600 mb-1">Recommended Value</p>
                                                          <code className="block bg-gray-200 text-gray-800 p-2 rounded-md whitespace-pre-wrap font-mono">{result.new_value || 'N/A'}</code>
                                                        </div>
                                                      )}
                                                    </div>
                                                    {result.error && (
                                                      <div className="mt-4">
                                                        <p className="font-semibold text-red-600 mb-1">Error Details</p>
                                                        <code className="block bg-red-50 text-red-800 p-2 rounded-md whitespace-pre-wrap font-mono text-xs">{result.error}</code>
                                                      </div>
                                                    )}
                                                  </div>
                                                </td>
                                              </tr>
                                            )}
                                          </React.Fragment>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            );
        case 'rule_library':
            return (
                <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                    <div className="p-6 border-b">
                        <h3 className="text-lg font-semibold text-gray-900">Available Rule Library</h3>
                        <p className="text-sm text-gray-500 mt-1">List of all security rules available for the detected OS.</p>
                    </div>
                     <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rule ID</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Levels</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {allRules.length > 0 ? allRules.map((rule) => (
                                    <tr key={rule.id}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-700">{rule.id}</td>
                                        <td className="px-6 py-4 text-sm text-gray-600">{rule.description}</td>
                                        <td className="px-6 py-4 whitespace-nowrap"><SeverityBadge severity={rule.severity} /></td>
                                        <td className="px-6 py-4 text-sm text-gray-500 space-x-2">
                                            {rule.level.map(l => <span key={l} className="capitalize bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md text-xs">{l}</span>)}
                                        </td>
                                    </tr>
                                )) : (
                                  <tr><td colSpan={4} className="text-center py-8 text-gray-500">Loading rules...</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            );
        case 'reports':
            return (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">PDF Report</h3>
                      <p className="text-sm text-gray-600 mb-6">Download a professional PDF compliance report with executive summary and detailed results.</p>
                      <button onClick={() => window.open(`${API_BASE}/report/pdf`, '_blank')} className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-700 text-white font-semibold py-2.5 px-4 rounded-md transition-colors">
                          <Download className="h-5 w-5" />
                          <span>Download PDF</span>
                      </button>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">HTML Report</h3>
                      <p className="text-sm text-gray-600 mb-6">View an interactive web-based compliance report with detailed analysis in a new tab.</p>
                      <button onClick={() => window.open(`${API_BASE}/report`, '_blank')} className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-md transition-colors">
                          <Download className="h-5 w-5" />
                          <span>View HTML Report</span>
                      </button>
                  </div>
                </div>
            );
        case 'rollback':
            return (
                <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                    <div className="p-6 border-b">
                        <h3 className="text-lg font-semibold text-gray-900">Rollback Management</h3>
                        <p className="text-sm text-gray-500 mt-1">Revert specific security rules to their previous state.</p>
                    </div>
                    {rollbackOptions.length > 0 ? (
                         <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rule ID</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Applied</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {rollbackOptions.map((option) => (
                                        <tr key={option.rule_id}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-700">{option.rule_id}</td>
                                            <td className="px-6 py-4 text-sm text-gray-600">{option.description}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(option.last_applied).toLocaleString()}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right">
                                                <button onClick={() => rollbackRule(option.rule_id)} className="flex items-center space-x-2 bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-3 rounded-md transition-colors text-sm">
                                                    <RotateCcw className="h-4 w-4" />
                                                    <span>Rollback</span>
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="text-center py-12 px-6">
                            <History className="mx-auto h-12 w-12 text-gray-400" />
                            <h3 className="mt-2 text-lg font-medium text-gray-900">No Rollback Options</h3>
                            <p className="mt-1 text-sm text-gray-500">No applied changes are available for rollback.</p>
                        </div>
                    )}
                </div>
            );
      default: return null;
    }
  };

  const pageTitles: Record<Tab, string> = {
    dashboard: "Dashboard Overview",
    security_check: "Security Check",
    rule_library: "Rule Library",
    reports: "Compliance Reports",
    rollback: "Rollback Management"
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col">
        <Link href="/"><div className="flex items-center gap-2 px-4 mb-8">
          <Shield className="h-8 w-8 text-gray-800" />
          <h1 className="text-xl font-bold text-gray-900">OS Forge</h1>
        </div></Link>
        
        <nav className="flex flex-col space-y-2">
            <SidebarItem id="dashboard" label="Dashboard" icon={LayoutDashboard} />
            <SidebarItem id="security_check" label="Security Check" icon={ClipboardList} />
            <SidebarItem id="rule_library" label="Rule Library" icon={FileText} />
            <SidebarItem id="reports" label="Reports" icon={FileText} />
            <SidebarItem id="rollback" label="Rollback" icon={History} />
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <h1 className="text-2xl font-bold text-gray-900">{pageTitles[activeTab]}</h1>
              {systemInfo && (
                 <div className="flex items-center text-sm text-gray-600 bg-gray-100 px-3 py-1.5 rounded-md">
                    <Server className="h-4 w-4 mr-2" />
                    <span className='capitalize font-medium'>{systemInfo.detected_os}</span>
                 </div>
              )}
            </div>
          </div>
        </header>

        <main className="p-6 lg:p-8">
            {renderContent()}
        </main>
      </div>
    </div>
  );
}