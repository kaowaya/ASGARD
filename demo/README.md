# ASGARD Demo Frontend

[English] | [简体中文](README_CN.md)

## Overview

The ASGARD Demo Frontend showcases the intelligent battery analysis capabilities of the ASGARD system. This single-page application provides an interactive demonstration of BAS (Battery Analysis Skills) orchestration, case studies, and real-time data analysis.

## Features

### 1. Home Page (首页)
- Product introduction and value proposition
- Key benefits and competitive advantages
- Call-to-action buttons
- Responsive bento-grid layout
- Performance metrics showcase

### 2. Skills Library (技能库)
- **6 Tiers**: L0-L5 organized by complexity
- **67+ BAS Skills**: Complete skill ecosystem covering:
  - L0: Foundation utilities
  - L1: Basic data operations
  - L2: Single-battery diagnostics
  - L3: Multi-battery analysis
  - L4: Fleet-level insights
  - L5: Strategic optimization
- **Three-Level Navigation**: Tier → Skills → Detail
- **Interactive Cards**: Click to explore detailed information
- **Filter & Search**: Quick skill discovery

### 3. Agent Orchestration (Agent编排)
- **Interactive Chat**: Natural language interface for describing analysis needs
- **Dynamic DAG**: Real-time workflow visualization with node-edge graphs
- **Smart Planning**: Automatic skill orchestration based on user intent
- **Example Prompts**: Quick-start scenarios for common tasks
- **Conversation History**: Full context tracking

### 4. Data Analysis (分析)
- **Drag & Drop Upload**: Easy data import (CSV, JSON)
- **Interactive Visualizations**:
  - Voltage-time line charts with zooming
  - Temperature heatmaps with color gradients
  - Risk radar charts with multi-dimensional analysis
- **AI Insights**: Diagnostic summary and actionable recommendations
- **Responsive Charts**: Auto-resize on window resize

### 5. Case Studies (案例)
- **Real-World Examples**:
  - Huanggang ESS Station (黄冈储能站)
  - Fleet Vehicle Management (车队管理)
- **Technical Details**: Complete DAG visualization and BAS adoption plans
- **Traceability**: Root cause analysis and actionable recommendations
- **Performance Metrics**: Before/after comparisons

## Screenshots

> *Screenshots will be added in production deployment*

## Usage

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ASGARD/.worktrees/demo-frontend
   ```

2. **Start a local server**:
   ```bash
   # Using Python 3
   python -m http.server 8000

   # Or using Node.js
   npx serve demo

   # Or using PHP
   php -S localhost:8000
   ```

3. **Open in browser**:
   ```
   http://localhost:8000/
   ```

### Quick Start Without Server

Simply open `demo/index.html` directly in your browser. No server required for basic functionality.

### Navigation

Use the top navigation bar to switch between 5 main sections:
- **首页** (Home) - Product overview and value proposition
- **技能库** (Skills) - Explore 67+ BAS skills across 6 tiers
- **Agent编排** (Planner) - Interactive orchestration chat interface
- **分析** (Analysis) - Upload and analyze battery data
- **案例** (Cases) - Real-world case studies with technical details

## Tech Stack

- **Frontend**: Pure HTML5 + JavaScript ES6+ (no framework)
- **Styling**: Tailwind CSS 3.4 (CDN)
- **Icons**: Font Awesome 6.5 (CDN)
- **Charts**: Apache ECharts 5.4 (CDN)
- **Build**: None required (pure static HTML)
- **Bundling**: Single-file architecture for simplicity

## Browser Support

- ✓ Chrome 90+ (recommended)
- ✓ Safari 14+
- ✓ Firefox 88+
- ✓ Edge 90+
- ✓ Mobile browsers (iOS Safari 14+, Chrome Mobile)
- ✓ Tablet browsers (iPad OS 14+, Android tablets)

## Development

### File Structure
```
demo/
├── index.html          # Main application (all code in one file)
├── README.md           # English documentation
├── README_CN.md        # Chinese documentation
└── DEPLOYMENT.md       # Deployment guide
```

### Key Features
- **Zero build process**: No npm, no webpack, no bundling
- **No dependencies**: All libraries loaded via CDN
- **Single-file architecture**: All HTML/CSS/JS in one file
- **Responsive design**: Mobile-first approach with Tailwind
- **Accessible**: ARIA labels, semantic HTML, keyboard navigation
- **Performance optimized**: Debounce handlers, lazy loading

### Code Organization
- **HTML**: Semantic structure with sections for each feature
- **CSS**: Tailwind utility classes with custom styles in `<style>`
- **JavaScript**: Modular functions with clear separation of concerns
  - State management (simple object-based)
  - UI rendering (separate functions per component)
  - Event handling (delegated where possible)
  - Chart initialization (ECharts instances)

## Performance

- **Initial Load**: <2 seconds (with CDN caching)
- **Lighthouse Score**: Target >90 (Performance, Accessibility, Best Practices)
- **Mobile Optimized**: Touch targets ≥44px, readable font sizes ≥16px
- **Chart Optimization**: Debounced resize handlers (300ms)
- **Bundle Size**: ~50KB (HTML + inline CSS/JS)

## Accessibility

- **ARIA Labels**: All interactive elements properly labeled
- **Keyboard Navigation**: Full keyboard support (Tab, Enter, Space)
- **Screen Reader**: Semantic HTML and live regions for dynamic content
- **Color Contrast**: WCAG AA compliant (4.5:1 for text)
- **Focus Indicators**: Visible focus states on all interactive elements

## Architecture

### Single-File Philosophy
Following Occam's Razor principle, this demo uses a single-file architecture:
- **Simplicity**: No build tools, no dependency management
- **Portability**: One file contains everything
- **Maintainability**: Clear code organization with comments
- **Performance**: Zero build time, instant deployment

### State Management
Simple object-based state with manual reactivity:
```javascript
const state = {
  currentTab: 'home',
  selectedTier: null,
  selectedSkill: null,
  chatMessages: [],
  analysisData: null
};
```

### Component Architecture
Functional decomposition with clear responsibilities:
- `renderHome()`: Home page rendering
- `renderSkills()`: Skills library rendering
- `renderPlanner()`: Agent orchestration rendering
- `renderAnalysis()`: Data analysis rendering
- `renderCases()`: Case studies rendering

## Troubleshooting

### Charts not displaying
- Check browser console for JavaScript errors
- Verify ECharts CDN is accessible (check network tab)
- Ensure container div has explicit height
- Try clearing browser cache

### Styles not loading
- Verify Tailwind CDN is accessible
- Check network connection
- Try hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

### Mobile display issues
- Clear browser cache
- Test in incognito mode
- Check viewport meta tag is present
- Verify responsive breakpoints in Tailwind config

## Future Enhancements

- [ ] Add dark mode toggle
- [ ] Implement real backend API integration
- [ ] Add more chart types (scatter, box plot)
- [ ] Export analysis reports as PDF
- [ ] Multi-language support (beyond EN/CN)
- [ ] PWA capabilities (offline support)
- [ ] Advanced filtering in skills library

## License

[Specify license]

## Contact

[Add contact information]

## Documentation

- [Implementation Plan](../docs/plans/2026-03-14-asgardo-demo-implementation.md)
- [Design Document](../docs/plans/2026-03-14-asgardo-demo-design.md)
- [Deployment Guide](DEPLOYMENT.md)
