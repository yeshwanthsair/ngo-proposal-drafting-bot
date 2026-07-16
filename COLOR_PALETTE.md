# NGO Proposal Drafting Bot - Color Palette

## 🎨 Official Color Scheme

### Primary Colors (NGO/Environmental Theme)
```
Primary Green:      #2E7D32  RGB(46, 125, 50)
Primary Light:      #4CAF50  RGB(76, 175, 80)
Primary Dark:       #1B5E20  RGB(27, 94, 32)
```

### Secondary Colors (Trust & Professionalism)
```
Secondary Blue:     #1976D2  RGB(25, 118, 210)
Secondary Light:    #1565C0  RGB(21, 101, 192)
Secondary Dark:     #0D47A1  RGB(13, 71, 161)
```

### Accent Colors (Energy & Action)
```
Accent Orange:      #FF6F00  RGB(255, 111, 0)
Accent Light:       #F57C00  RGB(245, 124, 0)
Accent Dark:        #E65100  RGB(230, 81, 0)
```

### Status Colors
```
Success Green:      #4CAF50  RGB(76, 175, 80)
Warning Orange:     #FFA726  RGB(255, 167, 38)
Danger Red:         #EF5350  RGB(239, 83, 80)
```

### Neutral Colors
```
Background Light:   #F5F7FA  RGB(245, 247, 250)
Card White:         #FFFFFF  RGB(255, 255, 255)
Text Dark:          #1A1A1A  RGB(26, 26, 26)
Text Light:         #666666  RGB(102, 102, 102)
Border Gray:        #E0E0E0  RGB(224, 224, 224)
```

---

## 📍 Color Usage by Component

### Sidebar
- **Background**: Gradient (Primary Green → Primary Dark)
- **Text**: White
- **Stats Cards**: Semi-transparent white overlay

### Page Headers
- **Chat**: Green gradient
- **Proposal**: Blue gradient
- **Upload**: Orange gradient
- **Knowledge Base**: Purple gradient
- **Admin**: Red gradient

### Buttons
- **Primary**: Blue gradient
- **Secondary**: Orange gradient
- **Danger**: Red gradient

### Status Boxes
- **Info**: Blue background + left border
- **Success**: Green background + left border
- **Warning**: Orange background + left border
- **Error**: Red background + left border

### Cards & Metrics
- **Background**: White
- **Border**: Light gray
- **Shadow**: Subtle black (5% opacity)

### Input Fields
- **Border**: Light gray (default)
- **Border**: Green (focus)
- **Shadow**: Green (focus, 10% opacity)

---

## 🎯 Gradient Combinations

### Primary Gradient (Green)
```css
background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
```

### Secondary Gradient (Blue)
```css
background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
```

### Accent Gradient (Orange)
```css
background: linear-gradient(135deg, #FF6F00 0%, #F57C00 100%);
```

### Purple Gradient (Knowledge Base)
```css
background: linear-gradient(135deg, #7B1FA2 0%, #6A1B9A 100%);
```

### Red Gradient (Admin)
```css
background: linear-gradient(135deg, #C62828 0%, #B71C1C 100%);
```

---

## 🌈 Light Backgrounds (for info boxes)

### Green Light
```css
background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
border-left: 4px solid #4CAF50;
color: #1B5E20;
```

### Blue Light
```css
background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
border-left: 4px solid #1976D2;
color: #0D47A1;
```

### Orange Light
```css
background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
border-left: 4px solid #FF9800;
color: #E65100;
```

### Red Light
```css
background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
border-left: 4px solid #C62828;
color: #B71C1C;
```

---

## 💡 Design Principles

1. **Consistency**: Same colors used across all pages
2. **Hierarchy**: Darker shades for primary, lighter for secondary
3. **Accessibility**: High contrast ratios (WCAG AA compliant)
4. **Professionalism**: Green for NGO/environmental theme
5. **Trust**: Blue for secondary actions
6. **Energy**: Orange for calls-to-action
7. **Clarity**: Clear status indicators with color coding

---

## 🔄 Hover States

All interactive elements have hover effects:
- **Buttons**: Darker gradient + shadow elevation
- **Cards**: Subtle shadow increase
- **Expanders**: Light green background
- **Links**: Underline + color change

---

## 📱 Responsive Design

Colors remain consistent across:
- Desktop (wide layout)
- Tablet (medium layout)
- Mobile (single column)

---

## ✅ Accessibility Checklist

- [x] Color contrast ratio ≥ 4.5:1 for text
- [x] Not relying on color alone for information
- [x] Semantic HTML structure
- [x] Clear visual hierarchy
- [x] Readable font sizes (min 14px)
- [x] Sufficient spacing between elements

---

**Color Palette Version**: 1.0  
**Last Updated**: May 2026  
**Status**: Production Ready ✅
