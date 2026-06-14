# DESIGN.md v2.0 — Xenion

> Premium dark-first UI with atmospheric depth, spring physics, and intentional visual hierarchy.
> Linear/Raycast aesthetic for fashion brand campaign intelligence.

---

## 1. Design Philosophy

Xenion is now a **premium dark-mode dashboard** with:
- **Atmospheric depth**: Gradient meshes, subtle glow orbs, grain texture
- **Precision typography**: Geist Display for technology feel, Fraunces for warmth
- **Spring physics**: Motion library for tactile hover states, not PowerPoint CSS transitions
- **Broken grids**: Unequal layouts signal design intent, not template
- **One accent per theme**: Crimson on dark, Blue on light — no temperature mixing

---

## 2. Palette

### Dark Mode (Default)

| Name | Hex | Token | Role |
|------|-----|-------|------|
| Dark bg | `#0A0A0B` | `--dark-bg` | Page background |
| Dark elevated | `#111114` | `--dark-bg-elevated` | Card backgrounds |
| Dark subtle | `#18181B` | `--dark-bg-subtle` | Hover states |
| Dark border | `#27272A` | `--dark-border` | Borders |
| Fg | `#FAFAFA` | `--fg` | Primary text |
| Fg muted | `#A1A1AA` | `--fg-muted` | Secondary text |
| Fg subtle | `#71717A` | `--fg-subtle` | Tertiary text |
| Accent | `#DC2626` | `--accent` | Crimson - CTAs, highlights, active states |
| Accent dim | `#FECACA` | `--accent-dim` | Muted accent for backgrounds |
| Accent glow | `rgba(220,38,38,0.12)` | `--accent-glow` | Glow effects on active/hover |
| Success | `#22C55E` | `--success` | Success states |
| Warning | `#F97316` | `--warning` | Warning states |

### Light Mode

| Name | Hex | Token | Role |
|------|-----|-------|------|
| Light bg | `#FAFAFA` | `--light-bg` | Page background |
| Light elevated | `#FFFFFF` | `--light-bg-elevated` | Card backgrounds |
| Light border | `#E4E4E7` | `--light-border` | Borders |
| Accent | `#3B82F6` | `--accent-light` | Blue - CTAs, highlights |

### Cards

**Dark mode cards:**
```css
background: rgba(255, 255, 255, 0.02);
backdrop-filter: blur(8px);
border: 1px solid rgba(255, 255, 255, 0.06);
box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
```

**Top highlight line only — NO outer glows on cards (AI-tell)**

---

## 3. Typography

### Font Families

```css
--font-display: 'Geist', 'Inter', system-ui, sans-serif;  /* Wordmark, headings */
--font-serif: 'Fraunces', 'Lora', Georgia, serif;          /* Greeting moment only */
--font-ui: 'Inter', system-ui, sans-serif;                 /* All UI text */
```

### Usage Rules
- **Geist Display**: Wordmark "Xenion" in sidebar, page headings
- **Fraunces Italic**: Brand name in greeting (e.g., "Tana & Co."), campaign proposals — serif moment
- **Inter**: Everything else — body, labels, buttons, tables

### Type Scale

| Role | Size | Weight | Example |
|------|------|--------|---------|
| Display | 48px | 600 | Hero KPI metric |
| Heading | 24px | 600 | Page titles |
| Body | 15px | 400 | Prose, descriptions |
| Label | 13px | 500 | Section headers, uppercase |
| Caption | 12px | 400 | Timestamps, meta |

### Greeting Hierarchy
```tsx
// Dashboard header - split for contrast
<span className="text-base text-fg-muted">Good evening,</span>
<h1 className="font-serif text-[40px] italic text-fg">Tana & Co.</h1>
```

---

## 4. Background System

### Gradient Mesh (Dark Mode)

```css
.bg-mesh-dark {
  background: 
    radial-gradient(ellipse 100% 80% at 50% -30%, rgba(220, 38, 38, 0.06), transparent),
    radial-gradient(ellipse 80% 60% at 100% 100%, rgba(220, 38, 38, 0.03), transparent),
    #0A0A0B;
}
```

### Glow Orbs

```css
.glow-orb {
  width: 600px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(220, 38, 38, 0.12) 0%, transparent 70%);
  filter: blur(80px);
}
```

### Grain Overlay

```css
.grain {
  z-index: 1;  /* NOT 9999 */
  pointer-events: none;
  opacity: 0.025;
  /* SVG noise pattern */
}
```

### Dot Pattern (for sidebar backdrop)

```css
.bg-pattern-dots {
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 24px 24px;
}
```

---

## 5. Motion System

### Library
```bash
npm install motion
```

### Spring Hover Config
```tsx
const springConfig = { type: "spring", stiffness: 400, damping: 30 };

<motion.div
  whileHover={{ scale: 1.02, x: 4 }}
  transition={springConfig}
>
```

### Durations

| Element | Duration | Easing |
|---------|----------|--------|
| Button press (:active) | 100ms | ease-out |
| Card hover lift | 200ms | spring |
| Entrance animation | 400-500ms | `[0.16, 1, 0.3, 1]` |
| Stagger delay | 80ms per item | - |

### Reduced Motion

```tsx
import { useReducedMotion } from "motion/react";

const shouldReduceMotion = useReducedMotion();
const hoverAnimation = shouldReduceMotion ? {} : { scale: 1.02 };
```

---

## 6. Components

### 6.1 Sidebar

```css
Background: rgba(255, 255, 255, 0.03)
Backdrop-filter: blur(24px)
Border-right: 1px solid rgba(255, 255, 255, 0.06)

Wordmark: Geist Display, 20px, 600, #FAFAFA
Accent line: 2px height, gradient from #DC2626 to transparent, width 48px, under wordmark

Nav items:
  - Spring hover: scale 1.02, x 4
  - Active state: bg-white/[0.08], text-fg, border-l-2 border-accent
  - Inactive: text-fg-muted, hover:text-fg
```

### 6.2 KPI Cards (Broken Grid)

```tsx
// One hero card - col-span-2, row-span-2
// Others subordinate - col-span-1

<motion.div className="col-span-2 row-span-2 card-glass p-6">
  {/* Hero: Avg Read Rate - largest > text-display */}
</motion.div>

<motion.div className="col-span-1 card-glass p-5">
  {/* Subordinate metrics */}
</motion.div>
```

**Staggered entrance:**
```tsx
transition={{ delay: index * 0.08, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
```

### 6.3 Buttons

**Primary (Accent fill):**
```css
Background: var(--accent) /* #DC2626 */
Text: white
Radius: 9999px
Padding: 10px 24px
Shadow: 0px 0px 40px -10px rgba(220, 38, 38, 0.3)
Active: scale(0.97), 100ms
```

**Secondary (Ghost):**
```css
Background: transparent
Border: 1px solid rgba(255, 255, 255, 0.2)
Hover: bg-white/[0.06], border-white/[0.3]
```

### 6.4 Status Badges

```tsx
// Semantic colors for status
const badgeStyles = {
  read: "bg-accent/10 text-accent",
  running: "bg-accent/10 text-accent animate-pulse",
  completed: "bg-success/10 text-success",
  failed: "bg-red-500/10 text-red-400",
  default: "bg-white/[0.06] text-fg-muted",
};
```

### 6.5 Nudge Cards (Visual Priority)

```tsx
// First card: heavier, more padding, larger title
// Subsequent cards: compact, less visible
// NOT three identical rectangles

<NudgeCard index={0} nudge={nudge} />  // isHero=true, p-6
<NudgeCard index={1} nudge={nudge} />  // p-4
<NudgeCard index={2} nudge={nudge} />  // p-4
```

---

## 7. Component CSS Classes

### Card Glass
```css
.card-glass {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
```

### Top Highlight
```css
.top-highlight {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
```

### Sidebar Glass
```css
.sidebar-glass {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(24px);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}
```

### Accent Line
```css
.accent-line {
  height: 2px;
  background: linear-gradient(90deg, #DC2626, rgba(220, 38, 38, 0.3));
  border-radius: 1px;
}
```

---

## 8. Do's and Don'ts

### Do
- Use spring physics for hover states (sidebar nav, cards)
- Break grids with one visually dominant element
- Use top highlight lines on cards, not outer glows
- Keep one accent color per theme (crimson dark / blue light)
- Use surface contrast for KPI card differentiation, not amber tints
- Put accent line under wordmark in sidebar, not on active nav

### Don't
- Use outer glow shadows on cards (AI-tell)
- Mix cool and warm accent colors in the same theme
- Make all KPI cards the same size (template look)
- Use `transition` for hover effects — use spring physics
- Put grain overlay at z-index 9999 (blocks modals)

---

## 9. Implementation Notes

### Grain z-index
```css
/* WRONG */
.grain { z-index: 9999; }

/* CORRECT */
.grain { z-index: 1; pointer-events: none; }
```

### Light Mode Consistency
Light mode cards get the same top-highlight treatment:
```css
box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
```

### Active Nav Indicator
Use 2px left border in accent color, NOT accent line:
```css
.active-nav {
  border-l-2 border-accent;  /* 2px solid accent */
  bg-white/[0.08];
}
```

---

## 10. Tailwind Config Reference

```typescript
// tailwind.config.ts
colors: {
  dark: {
    bg: "#0A0A0B",
    "bg-elevated": "#111114",
    "bg-subtle": "#18181B",
    border: "#27272A",
  },
  accent: {
    DEFAULT: "#DC2626",
    dim: "#FECACA",
    glow: "rgba(220, 38, 38, 0.12)",
  },
  fg: {
    DEFAULT: "#FAFAFA",
    muted: "#A1A1AA",
    subtle: "#71717A",
  },
}
```

---

## 11. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v2.0 | Jun 2026 | Complete redesign: dark mode, motion, new palette, broken grids |
| v1.0 | Jun 2026 | Initial design system |
