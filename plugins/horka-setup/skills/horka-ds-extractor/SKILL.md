---
name: horka-ds-extractor
description: Extract and document a frontend project's design system into comprehensive Markdown files. Analyzes Tailwind config, CSS variables, component library (Shadcn, custom DS), neo-brutalism or any visual style, and generates a complete DS reference another AI or designer can use to reproduce the exact look and feel. Does NOT modify code or create Figma assets. Use when user says "extract design system", "document DS", "design system audit", "export design tokens", "DS documentation", "describe the design". Trigger on "design system", "DS", "design tokens", "extract styles".
argument-hint: optional output directory path (defaults to ./design-system/)
allowed-tools: Read, Write, Glob, Grep, Bash, AskUserQuestion
---

# Design System Extractor

Analyze a frontend codebase and generate comprehensive design system documentation in Markdown. The output must be precise enough for another AI or a designer to reproduce every visual detail without access to the source code.

## Scope

Extracts and documents visual design patterns. Does NOT:
- Modify source code or styles
- Create Figma files or design tool assets
- Implement or refactor components
- Document business logic or API contracts

## Phase 1: Detect Project Stack

Use Glob and Grep to identify the frontend framework and CSS approach:

1. **Package manager**: `package.json`, `bun.lockb`, `yarn.lock`, `pnpm-lock.yaml`
2. **Framework**: Vue/Nuxt (`nuxt.config`, `.vue` files), React/Next (`next.config`, `.tsx`), Svelte (`svelte.config`), Angular (`angular.json`)
3. **CSS approach**:
   - Tailwind: `tailwind.config.*`, `@theme` blocks in CSS, `@tailwind` directives
   - CSS-in-JS: `styled-components`, `emotion`, `@stitches`
   - Vanilla CSS/SASS: `*.scss`, `*.sass`, `*.css` with custom properties
   - CSS Modules: `*.module.css`
4. **Component library**: Shadcn (`components/ui/`), custom DS (`designSystem/`, `ds/`), Material UI, Vuetify, Radix
5. **Icon system**: Material Icons, Lucide, Heroicons, FontAwesome, custom SVGs

Report detected stack before proceeding. If detection is ambiguous, use `AskUserQuestion`.

## Phase 2: Extract Design Tokens

Read the theme/config files identified in Phase 1. Extract ALL of the following categories. For each token, document the **exact value** (hex, px, rem, oklch -- whatever the source uses).

### 2.1 Colors

Read Tailwind config, CSS custom properties, or theme files.

Extract and categorize:
- **Primary/Secondary** brand colors
- **Semantic colors**: success, warning, danger, info
- **Neutral scale**: grays, backgrounds, borders, text colors
- **Surface colors**: card backgrounds, page backgrounds, overlays
- **Domain-specific palettes**: status colors, platform colors, chart colors
- **Dark mode overrides** (if applicable)

Output as a table: `| Token name | Value | Usage |`

### 2.2 Typography

- Font families (with fallbacks)
- Font size scale (all named sizes with px/rem values AND line-heights)
- Font weight usage (which weights are used where)
- Special font features (variable fonts, icon fonts)

### 2.3 Spacing

- Spacing scale (all named values with px equivalents)
- Common padding patterns (cards, buttons, sections, inputs)
- Common gap patterns (flex/grid gaps)
- Container/layout padding (desktop vs mobile)

### 2.4 Border Radius

- Full radius scale with px values
- Document which radius is used most commonly and where

### 2.5 Borders

- Border widths used (1px, 2px, 3px, 4px...)
- Border colors
- Border styles (solid, dashed, etc.)
- Special border patterns (asymmetric borders, thicker on specific sides)

### 2.6 Shadows

- All shadow definitions (CSS values)
- Shadow naming/sizing scale
- Whether shadows use blur (soft) or solid offset (brutalist)
- Shadow offset patterns for different component sizes
- If using double-layer pattern (shadow div + content div), document the translate values

### 2.7 Z-Index

- Complete z-index hierarchy from lowest to highest

### 2.8 Animations & Transitions

- Named keyframe animations with descriptions
- Custom easing curves (cubic-bezier values)
- Transition durations and what they apply to
- Interaction states: hover, active, focus, disabled

### 2.9 Breakpoints & Responsive

- Breakpoint values
- Container max-widths
- Mobile-specific overrides

Before proceeding to Phase 3, consult `references/extraction-checklist.md` to verify all token categories have been covered. Check off each item as extracted.

## Phase 3: Analyze Components

For each component in the design system directory:

1. **Read the component file** (.vue, .tsx, .jsx, .svelte)
2. **Read its types/props** definition
3. **Read associated CSS** (scoped, module, or global)

For each component, follow the template in `references/component-template.md`. Include structure (ASCII diagram), visual specs table, variants, sizes, interactive states, and props.

**Example** (ButtonDS):
```
## ButtonDS
### Visual Specs
| Property | Value |
|----------|-------|
| Border | 2px solid black |
| Border-radius | 2px (--radius-xs) |
| Shadow | Double-layer: bg-black div + translate(-8px, -8px) |
### Variants
| Variant | Background | Text |
|---------|-----------|------|
| primary | #AE7AFF | white |
| ghost | white | black |
```

### Priority Order for Components

Analyze in this order (most foundational first):
1. Buttons
2. Inputs / Form controls
3. Cards
4. Tags / Badges
5. Modals / Dialogs
6. Tooltips
7. Dropdowns / Menus
8. Tables
9. Tabs
10. Progress indicators
11. Toasts / Notifications
12. Navigation (sidebar, navbar, breadcrumb)
13. Skeletons / Loaders
14. Separators / Dividers
15. Any remaining components

## Phase 4: Identify Visual Style Patterns

After analyzing tokens and components, identify and document the **overarching design style**:

### Style Detection Checklist

- **Neo-brutalism**: thick borders (2-4px), solid offset shadows (no blur), minimal border-radius, high contrast, bold typography, double-layer shadow pattern, spring easing on interactions
- **Glassmorphism**: backdrop-blur, transparency, subtle borders, frosted glass effect
- **Neumorphism**: inset shadows, soft extruded shapes, monochromatic
- **Material Design**: elevation shadows with blur, 4dp/8dp grid, ripple effects
- **Flat/Minimal**: no shadows, thin borders or none, clean spacing
- **Custom/Hybrid**: describe the specific combination

Document the signature visual patterns:
- What makes this DS visually distinctive?
- What are the recurring micro-interactions?
- Are there playful/decorative elements (random rotations, mascot icons, etc.)?

## Phase 5: Document Layout Patterns

Read layout files and several page-level components to document:

- Page layout structure (sidebar + content, etc.)
- Grid systems used
- Content container widths and padding
- Section spacing patterns
- Responsive behavior

## Phase 6: Generate Output

Create the following files in the output directory:

### File 1: `DESIGN_SYSTEM_OVERVIEW.md`
- Detected tech stack
- Visual style identification with key characteristics
- Color palette (complete tables)
- Typography scale
- Spacing scale
- Border radius scale
- Z-index hierarchy
- Breakpoints

### File 2: `DESIGN_TOKENS.md`
- Every CSS custom property / Tailwind token with exact values
- Organized by category (colors, spacing, typography, shadows, etc.)
- Dark mode overrides if applicable

### File 3: `COMPONENTS.md`
- Every component with full specs (structure, variants, sizes, states, props)
- ASCII diagrams for complex structures
- Interaction behaviors documented

### File 4: `LAYOUT_AND_PATTERNS.md`
- Page layout structure
- Navigation patterns
- Common page patterns
- Responsive behavior
- Animation/transition catalog

### File 5: `STYLE_GUIDE.md`
- The "how to build like this" summary
- Key principles (e.g., "always use 2px borders", "shadows are solid offset, never blur")
- Common class combinations / utility patterns
- Do's and Don'ts with examples

## Output Rules

- Use **exact values** from source code -- never approximate or round
- Include the **source file path** for each extracted value (e.g., `tailwind.css:81`)
- Use tables for token lists, not prose
- Use ASCII diagrams for component structures
- Include code snippets (CSS/HTML) for complex patterns
- Every spec must be verifiable by reading the referenced source file
- If a value uses a CSS function (oklch, calc, var), include both the function AND the computed result where possible

## Error Handling

- **No design system directory found**: Search for component patterns in `components/`, `src/components/`, `app/components/`. Use `AskUserQuestion` if nothing found
- **No Tailwind/CSS config**: Look for inline styles, CSS-in-JS theme objects, SASS variables
- **Incomplete component**: Document what exists, flag missing specs with `[TODO: not found in source]`
- **Mixed styling approaches**: Document all approaches found, note which is primary
