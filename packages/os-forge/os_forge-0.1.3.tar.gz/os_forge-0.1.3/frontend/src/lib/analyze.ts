import type { DetectedOS, Level, RulesListResponse, RunResponse, RunResultItem, Severity } from "./types"

export function formatOS(os: DetectedOS) {
  const label = os.charAt(0).toUpperCase() + os.slice(1)
  return label
}

export function severityColor(sev: Severity) {
  switch (sev) {
    case "critical":
      return "bg-destructive/15 text-destructive"
    case "high":
      return "bg-amber-500/15 text-amber-600"
    case "medium":
      return "bg-blue-500/15 text-blue-600"
    default:
      return "bg-muted text-foreground/70"
  }
}

export function statusColor(status: RunResultItem["status"]) {
  switch (status) {
    case "pass":
      return "bg-emerald-500/15 text-emerald-600"
    case "fail":
      return "bg-amber-500/15 text-amber-600"
    case "error":
      return "bg-destructive/15 text-destructive"
    case "skipped":
      return "bg-muted text-foreground/60"
    default:
      return "bg-muted text-foreground/70"
  }
}

export function osMatches(itemOS: RulesListResponse["rules"][number]["os"], target: DetectedOS) {
  if (typeof itemOS === "string") return itemOS === target || (target === "linux" && itemOS === "linux")
  return itemOS.includes(target) || (target === "linux" && itemOS.includes("linux"))
}

export function filterRulesByOSAndLevel(rules: RulesListResponse["rules"], os: DetectedOS, level?: Level) {
  return rules.filter((r) => osMatches(r.os, os) && (!level || r.level.includes(level)))
}

export function runStats(run: RunResponse) {
  const byStatus = run.results.reduce<Record<string, number>>((acc, r) => {
    acc[r.status] = (acc[r.status] ?? 0) + 1
    return acc
  }, {})
  const criticalOpen = run.results.filter(
    (r) => r.severity === "critical" && (r.status === "fail" || r.status === "error"),
  ).length
  const highOpen = run.results.filter(
    (r) => r.severity === "high" && (r.status === "fail" || r.status === "error"),
  ).length
  return { byStatus, criticalOpen, highOpen }
}
