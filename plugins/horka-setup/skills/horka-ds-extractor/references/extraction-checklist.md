# Design System Extraction Checklist

Use this checklist to ensure completeness. Every item must be either documented or explicitly marked as N/A.

## Tokens Checklist

### Colors
- [ ] Primary color(s) with hex/oklch values
- [ ] Secondary color(s)
- [ ] Semantic: success, warning, danger, info
- [ ] Neutral scale (grays)
- [ ] Background colors (page, card, overlay)
- [ ] Text colors (primary, secondary, muted, inverse)
- [ ] Border/line colors
- [ ] Domain-specific palettes (if any)
- [ ] Dark mode overrides (if any)
- [ ] Chart/data visualization colors (if any)

### Typography
- [ ] Font family (primary + fallbacks)
- [ ] Font family (secondary/brand, if different)
- [ ] Icon font (if any)
- [ ] Heading sizes (h1-h6 with line-heights)
- [ ] Body text sizes (with line-heights)
- [ ] Font weights used and where
- [ ] Letter-spacing / tracking values
- [ ] Variable font settings (if applicable)

### Spacing
- [ ] Named spacing scale (xs through xxxl or similar)
- [ ] Button padding per size
- [ ] Card padding
- [ ] Input padding
- [ ] Section/page padding
- [ ] Gap values (flex/grid)
- [ ] Container padding (desktop vs mobile)

### Border Radius
- [ ] Full radius scale with values
- [ ] Most common radius identified
- [ ] Special cases (pill, circle)

### Borders
- [ ] Standard border width
- [ ] Emphasis border width (if different)
- [ ] Border color(s)
- [ ] Asymmetric border patterns (if any)

### Shadows
- [ ] Shadow scale (sm, md, lg or similar)
- [ ] Shadow type: blur-based or solid-offset
- [ ] Shadow direction (bottom-right, top-left, etc.)
- [ ] If double-layer: translate values per component size
- [ ] Hover shadow changes
- [ ] Active/pressed shadow changes

### Z-Index
- [ ] Complete hierarchy documented

### Animations
- [ ] Named keyframe animations
- [ ] Custom easing curves (cubic-bezier values)
- [ ] Transition durations per context
- [ ] Hover transitions
- [ ] Enter/exit transitions (modals, dropdowns, toasts)

### Breakpoints
- [ ] All breakpoint values
- [ ] Container max-widths per breakpoint

## Components Checklist

For EACH component, verify:
- [ ] DOM structure (ASCII diagram)
- [ ] All visual specs (border, radius, shadow, bg, padding)
- [ ] All variants with visual differences
- [ ] All sizes with dimensions
- [ ] Interactive states (hover, active, focus, disabled)
- [ ] Props/API documented
- [ ] Animation/transition behavior

### Component Coverage
- [ ] Button
- [ ] Input / Textarea
- [ ] Checkbox / Radio / Toggle
- [ ] Select / Dropdown
- [ ] Card
- [ ] Tag / Badge
- [ ] Modal / Dialog
- [ ] Confirm Dialog
- [ ] Tooltip
- [ ] Dropdown Menu
- [ ] Table
- [ ] Tabs
- [ ] Progress Bar
- [ ] Toast / Notification
- [ ] Sidebar / Navigation
- [ ] Top Bar / Header
- [ ] Breadcrumb
- [ ] Pagination
- [ ] Skeleton / Loader
- [ ] Separator / Divider
- [ ] Info Box / Alert
- [ ] Avatar
- [ ] Footer

## Layout Checklist
- [ ] Overall page structure documented
- [ ] Sidebar dimensions and behavior
- [ ] Content area dimensions
- [ ] Grid/flex patterns
- [ ] Responsive breakpoint behavior

## Style Identity Checklist
- [ ] Visual style named and described
- [ ] Key distinguishing characteristics listed
- [ ] Recurring micro-interactions documented
- [ ] Decorative/playful elements noted
- [ ] Do's and Don'ts with examples
