export type DetectedOS = "windows" | "ubuntu" | "centos" | "linux" | "macos" | "unknown"

export interface SystemInfoResponse {
  message: string
  detected_os: DetectedOS
  available_rules: number
  rule_counts: Record<"basic" | "moderate" | "strict", number>
}

export type Severity = "low" | "medium" | "high" | "critical"
export type Level = "basic" | "moderate" | "strict"

export interface RuleItem {
  id: string
  description: string
  os: DetectedOS | DetectedOS[] | "windows" | "linux" // payload can be mixed
  severity: Severity
  level: Level[]
  check: string
  remediate: string
  rollback: string
  expected: string
}

export interface RulesListResponse {
  rules: RuleItem[]
  count: number
}

export type ResultStatus = "pass" | "fail" | "error" | "skipped" | "unknown"

export interface RunResultItem {
  rule_id: string
  description: string
  severity: Severity
  status: ResultStatus
  old_value: string | null
  new_value: string | null
  error: string | null
}

export interface RunResponse {
  status: "completed" | "running" | "failed"
  dry_run: boolean
  level: Level
  results: RunResultItem[]
  summary: {
    total: number
    passed: number
    failed: number
    errors: number
  }
}
