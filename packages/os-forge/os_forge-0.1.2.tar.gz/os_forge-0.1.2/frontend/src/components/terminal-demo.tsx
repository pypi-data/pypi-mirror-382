"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"

export function TerminalDemo() {
  const [currentLine, setCurrentLine] = useState(0)

  const lines = [
    { type: "prompt", text: "C:\\>" },
    { type: "command", text: "secureos assess --level moderate" },
    { type: "output", text: "🔍 Scanning system configuration..." },
    { type: "output", text: "✓ Firewall rules: PASS" },
    { type: "output", text: "✓ Password policy: PASS" },
    { type: "output", text: "⚠ SSH configuration: WARNING" },
    { type: "output", text: "✓ File permissions: PASS" },
    { type: "prompt", text: "C:\\>" },
    { type: "command", text: "secureos enforce --profile cis-level-1" },
    { type: "output", text: "🔒 Applying security hardening..." },
    { type: "output", text: "✓ 156 checks applied successfully" },
  ]

  useEffect(() => {
    if (currentLine < lines.length) {
      const timer = setTimeout(() => {
        setCurrentLine(currentLine + 1)
      }, 800)
      return () => clearTimeout(timer)
    }
  }, [currentLine, lines.length])

  return (
    <div className="relative w-full rounded-xl border border-black/10 bg-[#0a0a0a] p-6 font-mono text-sm shadow-2xl">
      {/* Terminal Header */}
      <div className="mb-4 flex items-center gap-2">
        <div className="h-3 w-3 rounded-full bg-red-500" />
        <div className="h-3 w-3 rounded-full bg-yellow-500" />
        <div className="h-3 w-3 rounded-full bg-green-500" />
        <span className="ml-2 text-xs text-gray-500">secureos-terminal</span>
      </div>

      {/* Terminal Content */}
      <div className="space-y-2">
        {lines.slice(0, currentLine).map((line, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className={
              line.type === "prompt"
                ? "text-white inline"
                : line.type === "command"
                  ? "text-blue-400 inline ml-1"
                  : line.text.includes("✓")
                    ? "text-green-400"
                    : line.text.includes("⚠")
                      ? "text-yellow-400"
                      : "text-gray-300"
            }
          >
            {line.text}
          </motion.div>
        ))}
        {currentLine < lines.length && (
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ duration: 0.8, repeat: Number.POSITIVE_INFINITY }}
            className="inline-block h-4 w-2 bg-blue-400"
          />
        )}
      </div>
    </div>
  )
}
