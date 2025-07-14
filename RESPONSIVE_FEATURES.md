# Terminal UI Responsive Features

## Overview

The SpaceTraders Terminal UI has been enhanced with responsive design features to ensure it scales properly with the terminal window and prevents content from spilling over the edges.

## Key Improvements

### 1. Scrollable Containers
- All widgets now use `ScrollableContainer` to handle content overflow
- Content that exceeds terminal height will scroll vertically
- Prevents UI from becoming unusable in small terminals
- Affected widgets: Dashboard, Ships, Contracts, Agent, Shipyard

### 2. Responsive Text Truncation
- **Ship symbols**: Truncated to 12 characters (+ "..." if longer)
- **Waypoint symbols**: Show last 20 characters for relevance
- **System symbols**: Show last 15 characters
- **Component names**: Truncated to 15 characters (+ "..." if longer)
- **Dashboard text**: "Headquarters" → "HQ" for space saving

### 3. Responsive Button Sizing
- **"Navigate"** → **"Nav"** (8 chars → 3 chars)
- **"Refuel"** → **"Fuel"** (6 chars → 4 chars) 
- **"Automate"** → **"Auto"** (8 chars → 4 chars)
- CSS constraints: `min-width: 6`, `max-width: 10` for ship buttons

### 4. Terminal Resize Handling
- Added `on_resize()` event handler in main application
- Automatically refreshes display when terminal is resized
- All widgets adapt to new terminal dimensions
- Re-renders content to fit new screen size

### 5. CSS Responsive Classes
- `height: auto` for flexible sizing
- `min-height` settings for minimum usable space
- Responsive scrollable containers (`.dashboard-scrollable`, `.ships-scrollable`, etc.)
- Flexible button sizing constraints

## Technical Implementation

### Widget Structure
```python
# Before (Non-Responsive)
yield Container(
    content,
    classes="static-content"
)

# After (Responsive)
yield ScrollableContainer(
    Container(
        content,
        classes="responsive-content"
    ),
    classes="widget-scrollable"
)
```

### Text Truncation Logic
```python
# Ship symbol truncation
ship_symbol = ship.symbol[:12] + "..." if len(ship.symbol) > 15 else ship.symbol

# Waypoint symbol truncation (show end for relevance)
waypoint_symbol = waypoint_symbol[-20:] if len(waypoint_symbol) > 20 else waypoint_symbol
```

### CSS Responsive Classes
```css
/* Scrollable containers */
.dashboard-scrollable, .ships-scrollable, .contracts-scrollable {
    scrollbar-background: #313244;
    scrollbar-color: #89b4fa;
    height: 100%;
}

/* Responsive sizing */
.dashboard-stats {
    height: auto;
    min-height: 5;
}

/* Responsive buttons */
.ship-button {
    min-width: 6;
    max-width: 10;
}
```

## Testing

### Manual Testing
1. Run the application: `python main.py`
2. Resize your terminal window to different sizes
3. Switch between tabs (Dashboard, Ships, Contracts, Agent, Shipyard)
4. Verify content scrolls instead of overflowing
5. Check that long text is properly truncated

### Automated Testing
```bash
# Run all tests
python test_terminal_ui.py

# Run responsive behavior tests
python test_responsive_behavior.py
```

## Expected Behavior

### Small Terminal (80x24)
- Content fits within terminal bounds
- Long text is truncated with "..." indicators
- Buttons remain usable and properly sized
- Vertical scrolling available for overflow content

### Large Terminal (120x40)
- Content expands to use available space
- More information displayed without truncation
- Scrolling still available for very long content
- UI remains proportional and usable

### Terminal Resize
- UI automatically adapts to new dimensions
- Content re-renders to fit new screen size
- No content spills over terminal edges
- Smooth transition during resize

## Browser Support

The responsive features are built using the Textual framework and work in any terminal that supports:
- Unicode characters
- Color display
- Terminal resizing events
- Scrolling functionality

## Troubleshooting

### Issue: Content Still Overflows
- Check that `ScrollableContainer` is properly wrapping content
- Verify CSS classes are applied correctly
- Ensure terminal supports scrolling

### Issue: Text Not Truncating
- Verify truncation logic is applied in widget code
- Check character limits are appropriate for your use case
- Ensure responsive classes are loaded

### Issue: Terminal Resize Not Working
- Verify `on_resize()` handler is implemented
- Check that widgets are properly re-rendering
- Ensure terminal emulator supports resize events

## Future Enhancements

- Dynamic text truncation based on terminal width
- Adaptive column layouts for wide terminals
- Touch/mobile-friendly navigation
- High-DPI terminal support
- Theme-based responsive adjustments