# Nexus Terminal - Setup and Deployment Guide

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn package manager
- Google Gemini API key

## Quick Start

### 1. Clone and Navigate
```bash
cd /path/to/nexus-terminal
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
Create `.env.local` file in the root directory:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 4. Start Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Build and Production

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Backend Requirements

The application expects a backend service running at `http://localhost:8000` with the following endpoint:
- GET `/api/market` - Returns market data for all instruments

If the backend is not available, the application will fall back to simulated data from the dataService.

## Configuration Options

### Environment Variables
- `GEMINI_API_KEY`: Required for AI assistant functionality
- `VITE_PORT`: Port for development server (defaults to 3000)
- `VITE_HOST`: Host for development server (defaults to localhost)

### Configuration File (config.ts)
- `BACKEND_API_BASE`: Backend API base URL
- `AI_MODEL`: Gemini model to use (defaults to gemini-3-flash-preview)
- Polling intervals for different data types

## Development Scripts

### Available Scripts
- `npm run dev`: Start development server with hot reload
- `npm run build`: Create production build
- `npm run preview`: Serve production build locally for testing
- `npm run lint`: Lint code (if configured)
- `npm run type-check`: Type check (if using TypeScript)

## Folder Structure for Development

```
nexus-terminal/
├── public/                 # Static assets
├── src/                    # Source code
│   ├── components/         # Reusable UI components
│   ├── services/           # Business logic and API calls
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   ├── assets/             # Images, icons, styles
│   └── pages/              # Route components
├── .env.local             # Local environment variables
├── .gitignore             # Git ignore rules
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
└── vite.config.ts         # Vite build configuration
```

## Deployment Options

### Static Hosting
After running `npm run build`, the `dist/` folder contains static files that can be deployed to:
- Netlify
- Vercel
- GitHub Pages
- Any static hosting service

### Docker Deployment
Create a Dockerfile:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 8080
CMD ["npx", "serve", "-s", "dist"]
```

## Environment-Specific Configurations

### Development
- Hot module replacement enabled
- Source maps for debugging
- Verbose logging
- Port 3000 by default

### Production
- Code minification
- Dead code elimination
- Asset optimization
- Production-ready bundle

## Troubleshooting

### Common Issues

#### API Key Not Working
- Verify GEMINI_API_KEY is correctly set in `.env.local`
- Restart development server after changing environment variables
- Check that the environment variable is properly exposed in vite.config.ts

#### Backend Connection Issues
- Ensure backend service is running at configured URL
- Check CORS settings if backend is on different domain
- Verify network connectivity to backend

#### Build Failures
- Check for TypeScript errors
- Verify all dependencies are installed
- Clear node_modules and reinstall if needed

### Debugging Tips

#### Enable Verbose Logging
Add to browser console for debugging:
```javascript
localStorage.setItem('debug', 'nexus-terminal:*');
```

#### Check Network Requests
- Open DevTools Network tab
- Look for failed API requests
- Verify request URLs and headers

#### Performance Monitoring
- Use React DevTools for component performance
- Monitor bundle size with `npm run build --analyze`
- Check for unnecessary re-renders

## Testing

### Unit Tests
```bash
npm run test
```

### E2E Tests (if configured)
```bash
npm run test:e2e
```

## Maintenance

### Dependency Updates
```bash
npm outdated
npm update
```

### Security Audits
```bash
npm audit
npm audit fix
```

## CI/CD Pipeline

A typical CI/CD pipeline would include:
1. Code linting
2. Type checking
3. Unit tests
4. Build process
5. Security scanning
6. Deployment to staging
7. End-to-end tests
8. Deployment to production