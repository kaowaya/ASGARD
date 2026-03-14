# ASGARD Demo - Deployment Guide

[English] | [简体中文](README_CN.md)

## Overview

The ASGARD Demo is a pure static HTML application with zero build process. It can be deployed to any static hosting service or web server.

## Deployment Options

### Option 1: GitHub Pages (Recommended)

Free hosting for public repositories with automatic HTTPS.

#### Steps:

1. **Push to GitHub repository**:
   ```bash
   git push origin feature/demo-frontend
   ```

2. **Enable GitHub Pages**:
   - Go to repository **Settings** → **Pages**
   - **Source**: Deploy from a branch
   - **Branch**: `feature/demo-frontend` / `demo` folder
   - **Save**

3. **Access your demo**:
   ```
   https://<username>.github.io/<repo>/demo/
   ```

#### Pros:
- Free hosting
- Automatic HTTPS
- Custom domain support
- Easy setup

#### Cons:
- Build time ~1-2 minutes
- Limited to public repositories (free tier)

---

### Option 2: Netlify

Fast deployment with automatic HTTPS and custom domains.

#### Steps:

1. **Connect repository** to Netlify dashboard

2. **Configure build settings**:
   - **Build command**: (leave empty)
   - **Publish directory**: `demo`
   - **Branch**: `feature/demo-frontend`

3. **Deploy**: Automatic on push to configured branch

#### Access:
```
https://<random-name>.netlify.app
```

#### Pros:
- Instant deployment (<30 seconds)
- Automatic HTTPS
- Free custom domains
- Form handling (if needed later)
- Deploy previews for pull requests

#### Cons:
- Netlify branding on free tier (removable)

---

### Option 3: Vercel

Next.js creators' platform with excellent performance.

#### Steps:

1. **Import project** in Vercel dashboard

2. **Configure settings**:
   - **Framework Preset**: Other
   - **Root Directory**: `./demo`
   - **Build Command**: (leave empty)
   - **Output Directory**: `.`

3. **Deploy**: Automatic on push

#### Access:
```
https://<project-name>.vercel.app
```

#### Pros:
- Global edge network
- Automatic HTTPS
- Fast deployments
- Analytics (free tier)

#### Cons:
- Build time ~1 minute

---

### Option 4: Static File Server

Deploy to any web server with file access.

#### Using Python:

```bash
# Python 3
cd demo
python -m http.server 8000

# Access at http://localhost:8000
```

#### Using Node.js:

```bash
# Install serve globally
npm install -g serve

# Serve demo folder
serve demo

# Access at http://localhost:3000
```

#### Using Nginx:

```nginx
server {
    listen 80;
    server_name demo.asgard.com;
    root /path/to/demo;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### Using Apache:

```apache
<VirtualHost *:80>
    ServerName demo.asgard.com
    DocumentRoot /path/to/demo

    <Directory /path/to/demo>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

---

## Build Process

**No build required!**

This is a pure static HTML application with zero build steps:
- No `npm install` needed
- No bundling with webpack
- No transpilation with Babel
- Just open `index.html` in a browser

### Why No Build Process?

Following **Occam's Razor principle**:
- Simplicity: No dependency management
- Performance: No build time
- Portability: Single file contains everything
- Maintainability: Clear code organization

---

## Environment Variables

**None required.**

The application runs entirely client-side with no backend dependencies:
- No API keys
- No database connections
- No server-side rendering
- No build-time configuration

All data is hardcoded or user-provided (via file upload).

---

## Custom Domain Setup

### GitHub Pages

1. **Add CNAME file** in `demo/` folder:
   ```
   demo.asgard.com
   ```

2. **Configure DNS** at your domain provider:
   - **Type**: CNAME
   - **Name**: demo (or subdomain)
   - **Value**: `<username>.github.io`

3. **Wait** for DNS propagation (up to 48 hours)

### Netlify

1. **Add domain** in Netlify dashboard:
   - **Domain settings** → **Add custom domain**

2. **Configure DNS**:
   - Netlify provides DNS records to add

3. **Automatic HTTPS** provisioned by Netlify

### Vercel

1. **Add domain** in Vercel dashboard:
   - **Settings** → **Domains** → **Add**

2. **Configure DNS**:
   - Vercel provides DNS records to add

3. **Automatic HTTPS** provisioned by Vercel

---

## Troubleshooting

### Charts Not Displaying

**Symptoms**: Empty chart containers, console errors

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify ECharts CDN is accessible (check Network tab)
3. Ensure container div has explicit height in CSS
4. Try clearing browser cache (Ctrl+Shift+R / Cmd+Shift+R)
5. Check internet connection (CDN requires connectivity)

### Fonts Not Loading

**Symptoms**: Icons appear as squares, wrong font

**Solutions**:
1. Check Font Awesome CDN accessibility
2. Verify network connection
3. Use browser DevTools Network tab to check font requests
4. Consider using local fonts as fallback
5. Check for ad blockers blocking CDNs

### Mobile Display Issues

**Symptoms**: Layout broken on mobile, text too small

**Solutions**:
1. Clear browser cache
2. Test in incognito/private mode
3. Check viewport meta tag is present:
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   ```
4. Verify responsive breakpoints in Tailwind config
5. Test on real device (not just DevTools emulation)

### CORS Errors

**Symptoms**: File uploads fail, console shows CORS errors

**Solutions**:
1. This demo runs entirely client-side (no CORS issues)
2. If using local server, ensure CORS headers are set:
   ```python
   # Python http.server with CORS
   from http.server import HTTPServer, SimpleHTTPRequestHandler
   import sys

   class CORSRequestHandler(SimpleHTTPRequestHandler):
       def end_headers(self):
           self.send_header('Access-Control-Allow-Origin', '*')
           super().end_headers()

   HTTPServer(('', 8000), CORSRequestHandler).serve_forever()
   ```

### Slow Loading

**Symptoms**: Page takes >5 seconds to load

**Solutions**:
1. Check internet connection (CDN dependencies)
2. Use browser DevTools to identify bottlenecks
3. Consider serving CDN libraries locally
4. Enable compression on web server (gzip/brotli)
5. Use CDN caching headers

---

## Testing Checklist

Before deploying to production, verify:

### Functionality
- [ ] All 5 tabs load correctly
- [ ] Skills library navigation works (Tier → Skill → Detail)
- [ ] Agent chat accepts input and displays DAG
- [ ] File upload works (drag & drop)
- [ ] Charts render on desktop viewport
- [ ] Charts render on mobile viewport
- [ ] Case studies display correctly
- [ ] All navigation links work

### Cross-Browser
- [ ] Chrome (latest version)
- [ ] Safari (latest version)
- [ ] Firefox (latest version)
- [ ] Edge (latest version)
- [ ] Mobile Safari (iOS 14+)
- [ ] Mobile Chrome (Android 10+)

### Performance
- [ ] Initial load <2 seconds
- [ ] Lighthouse Performance score >90
- [ ] Lighthouse Accessibility score >90
- [ ] Lighthouse Best Practices score >90
- [ ] No console errors
- [ ] All images/icons load

### Accessibility
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Screen reader announces content
- [ ] Color contrast meets WCAG AA
- [ ] Touch targets ≥44px on mobile
- [ ] Focus indicators visible

### Responsive
- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)
- [ ] Mobile landscape (667x375)

---

## Performance Optimization

### CDN Caching

The application uses CDN libraries with long cache headers:
- Tailwind CSS: 1 year cache
- ECharts: 1 year cache
- Font Awesome: 1 year cache

### Compression

Enable compression on your web server:

**Nginx**:
```nginx
gzip on;
gzip_types text/html text/css application/javascript;
gzip_min_length 1000;
```

**Apache**:
```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/css application/javascript
</IfModule>
```

### Minification

For production, consider minifying the inline JavaScript:
- Use tools like [jscompress.com](https://jscompress.com)
- Or add build step with terser

---

## Version History

### v0.1.0 (2026-03-14)
- Initial release
- 5 main features implemented:
  - Home page with value proposition
  - Skills library with 67+ BAS skills
  - Agent orchestration with chat interface
  - Data analysis with interactive charts
  - Case studies with DAG visualization
- Responsive design (mobile-first)
- Accessibility features (ARIA, keyboard nav)
- Performance optimizations (debounce, lazy loading)
- Zero build process
- Single-file architecture

---

## Local Testing

Before deploying, test locally:

### 1. Start Local Server
```bash
cd demo
python -m http.server 8000
```

### 2. Open in Browser
```
http://localhost:8000
```

### 3. Run Lighthouse Audit
1. Open Chrome DevTools (F12)
2. Go to **Lighthouse** tab
3. Select **Performance**, **Accessibility**, **Best Practices**
4. Click **Analyze page load**
5. Target scores >90

### 4. Test on Mobile
1. Open Chrome DevTools
2. Click **Device Toolbar** (Ctrl+Shift+M / Cmd+Shift+M)
3. Test different devices:
   - iPhone 12 Pro (390x844)
   - iPad (768x1024)
   - Desktop (1920x1080)

---

## Continuous Deployment

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Demo

on:
  push:
    branches: [feature/demo-frontend]
    paths: [demo/**]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./demo
```

### Netlify/Vercel

Both platforms offer automatic deployment on git push - no configuration needed beyond initial setup.

---

## Support

For deployment issues:
1. Check this guide's troubleshooting section
2. Review browser console for errors
3. Test locally first to isolate the issue
4. Check hosting provider's status page

---

## Next Steps

After successful deployment:
1. Share the URL with stakeholders
2. Monitor performance with hosting provider analytics
3. Gather feedback from users
4. Plan v0.2.0 enhancements based on feedback
5. Consider adding backend API integration
