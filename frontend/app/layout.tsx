import type { Metadata } from "next"
import { Inter, Fraunces } from "next/font/google"
import "./globals.css"
import { Sidebar } from "@/components/shared/Sidebar"
import { ThemeProvider } from "@/components/shared/ThemeProvider"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-ui",
  weight: ["400", "500", "600"],
})

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-serif",
  weight: ["400"],
  style: ["normal", "italic"],
})

export const metadata: Metadata = {
  title: "Xenion - AI-Native CRM",
  description: "Campaign intelligence for fashion brands",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} ${fraunces.variable}`}>
        <ThemeProvider>
          <div className="grain" aria-hidden="true" />
          <div className="flex min-h-screen bg-mesh-dark bg-pattern-dots">
            <Sidebar />
            <main className="flex-1 ml-60">
              <div className="max-w-[1280px] mx-auto p-8">
                {children}
              </div>
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}
