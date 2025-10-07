import type React from "react"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Shield, Lock, FileCheck, RotateCcw, Terminal, Gauge } from "lucide-react"
import { TerminalDemo } from "@/components/terminal-demo"
import { SiteHeader } from "@/components/site-header"
import MagicBento from "@/components/MagicBento"

export default function Page() {
  return (
    <main className="relative min-h-screen w-full bg-white">
      <div
        className="fixed inset-0 z-0"
        style={{
          backgroundImage: `
            linear-gradient(to right, #e5e7eb 1px, transparent 1px),
            linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
          `,
          backgroundSize: "40px 40px",
        }}
      />

      <div className="relative z-10">
        <SiteHeader />

        <section className="relative mx-auto max-w-5xl px-6 pt-32 pb-20 text-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-black/5 px-4 py-1.5 text-sm font-light text-black">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-black opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-black"></span>
              </span>
              CIS-Aligned Security Framework
            </div>

            <h1 className="mt-8 text-balance text-5xl sm:text-6xl lg:text-7xl font-extralight tracking-tight text-black">
              Automate OS Security <span className="font-light">Hardening</span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-pretty text-lg font-light leading-relaxed text-black/60">
              Enterprise-grade hardening for Windows, Ubuntu, and CentOS. Assess, enforce, and report against security
              baselines with audit-ready logs.
            </p>

            <div className="mt-10 flex items-center justify-center gap-4">
              <Link href="/dashboard">
                <Button size="lg" className="px-8 py-6 text-base font-light bg-black text-white hover:bg-black/90">
                  Get Started
                </Button>
              </Link>
              <Link href="#features">
                <Button
                  variant="outline"
                  size="lg"
                  className="px-8 py-6 text-base font-light border-black/20 hover:bg-black/5 bg-transparent"
                >
                  Explore Features
                </Button>
              </Link>
            </div>

            <div className="mt-12 flex items-center justify-center gap-3 text-sm font-light text-black/60">
              <span className="rounded-full border border-black/10 bg-white px-4 py-1.5">Windows 10/11</span>
              <span className="rounded-full border border-black/10 bg-white px-4 py-1.5">Ubuntu 20.04+</span>
              <span className="rounded-full border border-black/10 bg-white px-4 py-1.5">CentOS 7+</span>
            </div>
          </div>
        </section>

        <section className="relative mx-auto max-w-7xl px-6 py-20">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
            <div>
              <h2 className="text-balance text-3xl sm:text-4xl font-extralight text-black">
                Simple CLI, Powerful Results
              </h2>
              <p className="mt-4 text-pretty text-lg font-light leading-relaxed text-black/60">
                Run comprehensive security assessments and apply hardening profiles with simple command-line
                instructions. No complex configuration required.
              </p>
              <div className="mt-8 space-y-4">
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5">
                    <div className="h-2 w-2 rounded-full bg-black" />
                  </div>
                  <div>
                    <h3 className="font-normal text-black">Assess Security Posture</h3>
                    <p className="text-sm font-light text-black/60">
                      Scan your system against CIS benchmarks in seconds
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5">
                    <div className="h-2 w-2 rounded-full bg-black" />
                  </div>
                  <div>
                    <h3 className="font-normal text-black">Enforce Hardening</h3>
                    <p className="text-sm font-light text-black/60">Apply security profiles with a single command</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5">
                    <div className="h-2 w-2 rounded-full bg-black" />
                  </div>
                  <div>
                    <h3 className="font-normal text-black">Real-time Feedback</h3>
                    <p className="text-sm font-light text-black/60">
                      See results instantly with detailed status updates
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <TerminalDemo />
            </div>
          </div>
        </section>

        <section id="features" className="relative mx-auto max-w-7xl px-6 py-20">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-extralight text-black">Core Features</h2>
            <p className="mt-4 text-lg font-light text-black/60">Everything you need for comprehensive OS security</p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon={<Gauge className="h-6 w-6" />}
              title="One-Click Assessment"
              description="Modular security engine with basic, moderate, and strict hardening levels tailored to your OS."
            />
            <FeatureCard
              icon={<FileCheck className="h-6 w-6" />}
              title="Compliance Reports"
              description="Generate PDF/HTML reports with severity ratings, timestamps, and full audit trails."
            />
            <FeatureCard
              icon={<RotateCcw className="h-6 w-6" />}
              title="Safe Rollback"
              description="Restore previous configurations anytime with stored snapshots and version control."
            />
            <FeatureCard
              icon={<Lock className="h-6 w-6" />}
              title="Annexure A/B Parameters"
              description="Apply industry-standard security parameters aligned with CIS benchmarks."
            />
            <FeatureCard
              icon={<Terminal className="h-6 w-6" />}
              title="CLI & GUI Options"
              description="Automate via command-line or use the intuitive dashboard for manual control."
            />
            <FeatureCard
              icon={<Shield className="h-6 w-6" />}
              title="Cross-Platform"
              description="Unified security framework across Windows, Ubuntu, and CentOS environments."
            />
          </div>
        </section>

        <section id="platforms" className="relative mx-auto max-w-7xl px-6 py-20">
          <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-center">
            <div>
              <h2 className="text-balance text-3xl sm:text-4xl font-extralight text-black">
                Why Security Hardening Matters
              </h2>
              <p className="mt-4 text-pretty text-lg font-light leading-relaxed text-black/60">
                Modern operating systems ship with defaults that prioritize usability over security. Misconfigurations,
                exposed services, and weak access controls create vulnerabilities that attackers exploit daily.
              </p>
              <div className="mt-8 space-y-4">
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5">
                    <div className="h-2 w-2 rounded-full bg-black" />
                  </div>
                  <div>
                    <h3 className="font-normal text-black">Consistent Baselines</h3>
                    <p className="text-sm font-light text-black/60">
                      Maintain uniform security posture across all systems
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5">
                    <div className="h-2 w-2 rounded-full bg-black" />
                  </div>
                  <div>
                    <h3 className="font-normal text-black">Audit-Ready</h3>
                    <p className="text-sm font-light text-black/60">
                      Comprehensive logs and reports for compliance verification
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black/5">
                    <div className="h-2 w-2 rounded-full bg-black" />
                  </div>
                  <div>
                    <h3 className="font-normal text-black">Reduce Risk</h3>
                    <p className="text-sm font-light text-black/60">Eliminate manual errors and configuration drift</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="rounded-2xl border border-black/10 bg-white p-8 shadow-lg">
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-light text-black/60">Security Score</span>
                    <span className="text-2xl font-light text-black">94%</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-black/5">
                    <div className="h-full rounded-full bg-black" style={{ width: "94%" }} />
                  </div>
                  <div className="grid grid-cols-3 gap-4 pt-4">
                    <div className="text-center">
                      <div className="text-2xl font-light text-black">156</div>
                      <div className="text-xs font-light text-black/60">Checks Passed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-light text-black">8</div>
                      <div className="text-xs font-light text-black/60">Warnings</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-light text-black">2</div>
                      <div className="text-xs font-light text-black/60">Critical</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="relative mx-auto max-w-7xl px-6 py-20">
          <div className="rounded-2xl border border-black/10 bg-white p-12 text-center shadow-lg">
            <h2 className="text-balance text-3xl sm:text-4xl font-extralight text-black">
              Ready to Secure Your Infrastructure?
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-pretty text-lg font-light text-black/60">
              Start hardening your systems today with enterprise-grade security automation.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/dashboard">
                <Button size="lg" className="px-8 py-6 text-base font-light bg-black text-white hover:bg-black/90">
                  Access Dashboard
                </Button>
              </Link>
              <Button
                variant="outline"
                size="lg"
                className="px-8 py-6 text-base font-light border-black/20 hover:bg-black/5 bg-transparent"
              >
                View Documentation
              </Button>
            </div>
          </div>
        </section>

        <footer className="border-t border-black/10 bg-white/50">
          <div className="mx-auto max-w-7xl px-6 py-12">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-black" />
                <span className="text-sm font-light text-black">OS Forge</span>
              </div>
              <p className="text-sm font-light text-black/60">© 2025 OS Forge. Enterprise Security Automation.</p>
            </div>
          </div>
        </footer>
      </div>
    </main>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="group relative rounded-xl border border-black/10 bg-white p-6 shadow-sm transition-all hover:border-black/30 hover:shadow-lg">
      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-black/5 text-black transition-colors group-hover:bg-black group-hover:text-white">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-normal text-black">{title}</h3>
      <p className="mt-2 text-sm font-light leading-relaxed text-black/60">{description}</p>
    </div>
  )
}
