# UI/UX Redesign - Developer Guide & Customization

## Quick Start

The StudentLabs UI has been completely redesigned with a Scite.ai-inspired aesthetic. All changes are in:
- `frontend/index.html` - HTML structure and layout
- `frontend/styles.css` - Complete styling redesign

No JavaScript changes required - existing functionality preserved.

---

## CSS Variables Reference

### Colors
All colors are defined as CSS variables in the `:root` selector:

```css
:root {
    /* Primary Color System */
    --primary-color: #2563eb;        /* Main blue color */
    --primary-dark: #1d4ed8;         /* Darker blue for hover */
    --primary-light: #3b82f6;        /* Lighter blue for variants */
    
    /* Background Colors */
    --bg-color: #ffffff;             /* Main background (white) */
    --bg-secondary: #f9fafb;         /* Secondary background */
    --bg-tertiary: #f3f4f6;          /* Tertiary background */
    
    /* Text Colors */
    --text-primary: #111827;         /* Primary text (dark) */
    --text-secondary: #6b7280;       /* Secondary text (muted) */
    --text-tertiary: #9ca3af;        /* Tertiary text (light) */
    
    /* UI Elements */
    --border-color: #e5e7eb;         /* Borders */
    --success-color: #10b981;        /* Success states */
    --error-color: #ef4444;          /* Error states */
    --warning-color: #f59e0b;        /* Warning states */
    
    /* Shadows */
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

### Using Variables
```css
.button {
    background: var(--primary-color);
    color: white;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
}

button:hover {
    background: var(--primary-dark);
}
```

---

## Customization Guide

### 1. Change Primary Color

To change the primary blue to another color:

```css
:root {
    --primary-color: #YOUR_COLOR;      /* Main color */
    --primary-dark: #YOUR_DARKER;      /* 15-20% darker */
    --primary-light: #YOUR_LIGHTER;    /* 15-20% lighter */
}
```

**Example - Change to Green:**
```css
--primary-color: #16a34a;      /* Green */
--primary-dark: #15803d;       /* Dark green */
--primary-light: #4ade80;      /* Light green */
```

### 2. Change Background Color

To switch from white to a different background:

```css
:root {
    --bg-color: #Your_color;
    --bg-secondary: #Your_lighter_shade;
    --bg-tertiary: #Your_even_lighter_shade;
}
```

**Example - Light Gray Background:**
```css
--bg-color: #f5f5f5;
--bg-secondary: #fafafa;
--bg-tertiary: #f0f0f0;
```

### 3. Change Text Color

To adjust text colors for better contrast:

```css
:root {
    --text-primary: #Your_dark_color;
    --text-secondary: #Your_medium_color;
    --text-tertiary: #Your_light_color;
}
```

### 4. Adjust Shadows

To make shadows more or less prominent:

```css
:root {
    /* Lighter shadows */
    --shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 2px 4px rgba(0, 0, 0, 0.05);
    
    /* Or heavier shadows */
    --shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    --shadow-md: 0 8px 16px rgba(0, 0, 0, 0.15);
}
```

### 5. Adjust Spacing

Global spacing adjustments:

```css
.page-wrapper {
    padding: 2rem;  /* Change from default 2rem */
}

.section {
    margin-bottom: 3rem;  /* Change from 3rem */
}

.stats-container {
    gap: 1.5rem;  /* Change from 1.5rem */
}
```

---

## Component Customization

### Button Variants

Current button styles:
```css
.btn-primary          /* Blue background */
.btn-secondary        /* Gray background */
.btn-text             /* Text only (no background) */
.btn-large            /* Larger padding */
.btn-small            /* Smaller padding */
```

**Add a new variant:**
```css
.btn-success {
    background: var(--success-color);
    color: white;
}

.btn-success:hover {
    background: #059669;  /* Darker green */
}
```

### Card Styling

Customize card appearance:

```css
.stat-tile {
    background: white;           /* Change background */
    border: 1px solid #e5e7eb;  /* Change border */
    border-radius: 12px;        /* Adjust roundness */
    padding: 1.75rem;           /* Change padding */
}

.stat-tile:hover {
    box-shadow: var(--shadow-lg);  /* Hover effect */
}
```

### Form Elements

Customize inputs and forms:

```css
.form-group input {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.75rem 1rem;
}

.form-group input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
```

---

## Typography Customization

### Font Family
```css
body {
    font-family: 'Your Font', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Or use Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
    font-family: 'Inter', sans-serif;
}
```

### Font Sizes
Adjust heading sizes:

```css
.page-header h1 {
    font-size: 2.5rem;  /* Change from 2rem */
}

.section-header h2 {
    font-size: 1.75rem;  /* Change from 1.5rem */
}
```

### Line Height
```css
body {
    line-height: 1.7;  /* Change from 1.6 */
}

h1, h2, h3 {
    line-height: 1.3;  /* Tighter for headings */
}
```

---

## Layout Customization

### Max Width
Change the maximum content width:

```css
.nav-container {
    max-width: 1600px;  /* Change from 1400px */
}

.page-wrapper {
    max-width: 1600px;  /* Change from 1400px */
}
```

### Navigation Height
Adjust top nav height:

```css
.top-nav {
    padding: 1.25rem 2rem;  /* Change from default */
}
```

### Grid Columns
Adjust responsive grid:

```css
.stats-container {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.projects-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}
```

---

## Responsive Breakpoints

Current breakpoints in media queries:

```css
@media (max-width: 768px) {  /* Tablet */
    /* Changes for tablet/small */
}

@media (max-width: 480px) {  /* Mobile */
    /* Changes for mobile */
}
```

**Add new breakpoint:**
```css
@media (max-width: 1024px) {  /* Small desktop */
    /* Your customizations */
}

@media (min-width: 1920px) {  /* Large desktop */
    /* Your customizations */
}
```

---

## Dark Mode Implementation (Optional)

To add dark mode support:

```css
@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: #0f172a;
        --bg-secondary: #1e293b;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --border-color: #475569;
    }
}
```

Or with a class:

```css
body.dark-mode {
    --bg-color: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
}
```

```javascript
// Add toggle button
document.getElementById('dark-toggle').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});
```

---

## Animation Customization

### Button Transitions
```css
.btn {
    transition: all 0.2s;  /* Change from 0.2s */
}

.btn:hover {
    transform: translateY(0);  /* Add or remove */
}
```

### Slide-in Animation
```css
@keyframes slideIn {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast {
    animation: slideIn 0.3s ease;  /* Adjust duration */
}
```

### Spin Animation
```css
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.spinner {
    animation: spin 1s linear infinite;  /* 1s rotation */
}
```

---

## Accessibility Customization

### Increase Text Contrast
```css
:root {
    --text-primary: #000000;      /* Pure black */
    --text-secondary: #333333;    /* Darker gray */
}
```

### Larger Font Sizes
```css
body {
    font-size: 18px;  /* Change from 16px base */
}

h1 {
    font-size: 2.5rem;  /* Larger headings */
}
```

### Improve Focus States
```css
*:focus-visible {
    outline: 3px solid var(--primary-color);
    outline-offset: 2px;
}
```

---

## Examples

### Example 1: Green Theme
```css
/* Change primary color to green */
:root {
    --primary-color: #16a34a;
    --primary-dark: #15803d;
    --primary-light: #4ade80;
    --success-color: #22c55e;
}
```

### Example 2: Dark Mode
```css
@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: #1a1a1a;
        --bg-secondary: #2d2d2d;
        --text-primary: #ffffff;
        --text-secondary: #d1d5db;
        --border-color: #404040;
    }
}
```

### Example 3: High Contrast
```css
:root {
    --text-primary: #000000;
    --text-secondary: #404040;
    --border-color: #000000;
}

.btn-primary {
    border: 2px solid #000000;
}
```

### Example 4: Compact Layout
```css
.page-wrapper {
    padding: 1rem;
}

.stats-container {
    gap: 1rem;
}

.section-header {
    font-size: 1.25rem;
}
```

---

## Testing Your Changes

After customizing the CSS:

1. **Visual Testing**
   ```bash
   # View in browser
   open frontend/index.html
   ```

2. **Responsive Testing**
   ```bash
   # Test at different sizes
   # 480px (mobile)
   # 768px (tablet)
   # 1024px (desktop)
   # 1920px (large desktop)
   ```

3. **Color Contrast Testing**
   - Use online tools: WebAIM Contrast Checker
   - Verify 4.5:1 minimum for text
   - Verify 3:1 for graphics

4. **Performance Testing**
   - Check rendering performance
   - Verify no layout shifts
   - Test animations smoothness

---

## Common CSS Patterns

### Flexbox Layout
```css
.container {
    display: flex;
    gap: 1rem;
    align-items: center;
    justify-content: space-between;
}
```

### Grid Layout
```css
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}
```

### Text Truncation
```css
.text-truncate {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
```

### Smooth Transitions
```css
.interactive {
    transition: all 0.2s ease;
}
```

---

## Browser DevTools Tips

### Inspect Variables
```javascript
// In browser console
getComputedStyle(document.documentElement).getPropertyValue('--primary-color')
```

### Change Variables Temporarily
```javascript
// In browser console
document.documentElement.style.setProperty('--primary-color', '#ff0000')
```

### Toggle Classes
```javascript
// In browser console
document.body.classList.toggle('dark-mode')
```

---

## Version Control

When making changes:
```bash
# Create a feature branch
git checkout -b feature/custom-theme

# Commit your changes
git add frontend/styles.css
git commit -m "feat: customize color theme to green"

# Push to remote
git push origin feature/custom-theme

# Create Pull Request for review
```

---

## Support & Resources

- **CSS Reference**: https://developer.mozilla.org/en-US/docs/Web/CSS
- **Color Tools**: https://coolors.co, https://color-hex.com
- **Design Inspiration**: https://scite.ai
- **Accessibility**: https://www.w3.org/WAI/WCAG21/quickref/

---

## Troubleshooting

### Variables Not Working
- Check syntax: `var(--variable-name)`
- Ensure CSS is reloaded (hard refresh)
- Check browser support (most modern browsers)

### Colors Look Wrong
- Check color hex codes
- Verify RGB/HSL values
- Test in different browsers
- Check for browser extensions affecting colors

### Layout Broken
- Check media query breakpoints
- Verify flexbox/grid syntax
- Clear browser cache
- Test in incognito mode

### Performance Issues
- Reduce animation complexity
- Optimize media queries
- Check shadow complexity
- Profile with DevTools

---

**Last Updated**: [Current Date]
**Guide Version**: 1.0
**Status**: Complete ✅
