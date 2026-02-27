# Mac Mouse Control

Control mouse cursor on macOS using `cliclick`. Essential for remote GUI automation via Screen Sharing or headless setups.

## Prerequisites

```bash
brew install cliclick
```

## Critical Rules

### 1. Always use easing (-e)
Without easing, the cursor "teleports" instantly — Screen Sharing won't see the movement.

```bash
# ❌ Bad - invisible movement
cliclick m:500,300

# ✅ Good - visible movement
cliclick -e 50 m:500,300
```

### 2. Always screenshot before clicking
Positions change based on window state, screen resolution, and app context. Never assume coordinates are stable.

```bash
# Screenshot with cursor visible
/usr/sbin/screencapture -C /tmp/screen.png
```

### 3. Coordinate scaling
On scaled displays (e.g., Retina, or custom scaling like 39%), cliclick coordinates differ from visual coordinates.

**Formula:** `cliclick_coord ≈ visual_coord × scale_factor`

Example with 39% scale: `cliclick_x ≈ visual_x × 1.3`

## Commands

| Command | Description |
|---------|-------------|
| `cliclick -e 50 m:X,Y` | Move cursor to X,Y with easing |
| `cliclick c:X,Y` | Click at X,Y |
| `cliclick dc:X,Y` | Double-click at X,Y |
| `cliclick rc:X,Y` | Right-click at X,Y |
| `cliclick p` | Print current cursor position |
| `cliclick t:"text"` | Type text |
| `cliclick kp:return` | Press Return key |

## Workflow

1. **Screenshot** the current screen state
   ```bash
   /usr/sbin/screencapture -C /tmp/screen.png
   ```

2. **Analyze** the screenshot to find target coordinates (visual)

3. **Calculate** cliclick coordinates (apply scale factor if needed)

4. **Move** with easing
   ```bash
   cliclick -e 50 m:X,Y
   ```

5. **Verify** position (optional screenshot)

6. **Click**
   ```bash
   cliclick c:X,Y
   ```

## Tips

- **Easing value:** 50 is a good default. Higher = slower/smoother.
- **Chaining:** `cliclick -e 50 m:X,Y && sleep 0.5 && cliclick c:X,Y`
- **Debugging:** Use `cliclick -m verbose` to see what's happening
- **Restore position:** Use `-r` flag to return cursor to original position after

## Common Issues

| Problem | Solution |
|---------|----------|
| Cursor doesn't visually move | Add `-e 50` (easing) |
| Clicks land in wrong spot | Screenshot first, recalculate coords |
| Screen Sharing shows no movement | Easing is required for remote viewing |

## Example: Click a toolbar button

```bash
# 1. Screenshot
/usr/sbin/screencapture -C /tmp/screen.png

# 2. Analyze screenshot, find button at visual (990, 81)

# 3. Apply scale factor (1.3x for 39% scale)
# Target: 990 × 1.3 = 1287, 81 × 1.3 = 105

# 4. Move and click
cliclick -e 50 m:1287,105 && sleep 0.3 && cliclick c:1287,105
```
