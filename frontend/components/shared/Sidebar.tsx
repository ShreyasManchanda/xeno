'use client'

import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, useReducedMotion, type Transition } from "motion/react"
import { LayoutDashboard, Users, Target, Megaphone } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/customers", label: "Customers", icon: Users },
  { href: "/segments", label: "Segments", icon: Target },
  { href: "/campaigns", label: "Campaigns", icon: Megaphone },
]

export function Sidebar() {
  const pathname = usePathname()
  const shouldReduceMotion = useReducedMotion()
  
  const isActive = (href: string) => {
    if (href === "/") return pathname === "/"
    return pathname.startsWith(href)
  }

  const springConfig: Transition = { type: "spring", stiffness: 400, damping: 30 }
  const hoverAnimation = shouldReduceMotion ? {} : { scale: 1.02, x: 4 }

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 sidebar-glass flex flex-col">
      <div className="p-5 pt-6">
        <Link href="/" className="block">
          <span className="font-display text-xl font-semibold text-fg tracking-tight">Xenion</span>
        </Link>
        <div className="accent-line mt-2 w-12" />
      </div>
      
      <nav className="flex-1 px-3 py-4">
        <div className="mb-3">
          <span className="text-[11px] font-medium uppercase tracking-wider text-fg-muted px-3">
            CAMPAIGNS
          </span>
        </div>
        <ul className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.href)
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="block"
                >
                  <motion.div
                    whileHover={hoverAnimation}
                    transition={springConfig}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-[15px] font-medium transition-colors duration-150",
                      active
                        ? "bg-white/[0.08] text-fg border-l-2 border-accent"
                        : "text-fg-muted hover:text-fg hover:bg-white/[0.04]"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </motion.div>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-white/[0.06]">
        <span className="text-xs text-fg-subtle">Tana &amp; Co. CRM</span>
      </div>
    </aside>
  )
}
