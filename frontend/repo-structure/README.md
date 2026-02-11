# Nexus Terminal - Repo Structure Documentation

This document provides a comprehensive overview of the Nexus Terminal project structure.

## Project Overview

Nexus Terminal is a Bloomberg-style financial dashboard featuring real-time stock simulations, interactive charting, live public chat, and context-aware AI analysis powered by Gemini.

## Directory Structure

```
nexus-terminal/
├── .gitignore                 # Git ignore rules
├── App.tsx                   # Main application component
├── README.md                 # Project documentation
├── config.ts                 # Configuration settings
├── index.html                # HTML entry point
├── index.tsx                 # React DOM entry point
├── metadata.json             # Application metadata
├── package.json              # Project dependencies and scripts
├── package-lock.json         # Dependency lock file
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite build configuration
├── components/               # React UI components
│   ├── AIAssistant.tsx       # AI assistant chat interface
│   ├── Auth.tsx             # Authentication component
│   ├── Button.tsx           # Reusable button component
│   ├── MacroDashboard.tsx   # Macro economic dashboard
│   ├── PublicChat.tsx       # Public chat interface
│   └── StockChart.tsx       # Interactive stock chart
├── services/                 # Business logic and API services
│   ├── dataService.ts       # Data generation and simulation
│   ├── geminiService.ts     # AI service integration
│   ├── marketDataService.ts # Market data fetching
│   ├── storage.ts           # Local storage and persistence
│   └── t12Service.ts        # Twelve Data API integration
├── types.ts                  # Type definitions
└── .env.local                # Environment variables (not committed)
```

## Key Components

### Core Application Files
- **App.tsx**: Main application component managing state, routing, and global data
- **index.tsx**: React DOM mounting point
- **index.html**: HTML template with Tailwind CSS and font imports
- **config.ts**: Centralized configuration for API endpoints and settings

### Component Architecture
- **Auth.tsx**: User authentication system
- **StockChart.tsx**: Interactive charting component using Recharts
- **PublicChat.tsx**: Real-time public chat functionality
- **AIAssistant.tsx**: Gemini-powered AI assistant interface
- **MacroDashboard.tsx**: Macro-economic instrument dashboard

### Service Layer
- **marketDataService.ts**: Handles market data fetching from backend
- **geminiService.ts**: AI integration with Google's Gemini
- **dataService.ts**: Simulated market data generation
- **storage.ts**: Client-side storage and persistence
- **t12Service.ts**: Twelve Data API integration (deprecated/local)

### Configuration
- **vite.config.ts**: Build configuration with environment variable setup
- **tsconfig.json**: TypeScript compilation settings
- **package.json**: Dependencies and scripts

## Technology Stack

- **Framework**: React 19.x
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom theme
- **Icons**: Lucide React
- **Charts**: Recharts
- **AI Integration**: Google GenAI (Gemini)
- **Language**: TypeScript

## Environment Variables

The application expects the following environment variables:
- `GEMINI_API_KEY`: Google Gemini API key for AI features

## Scripts

- `npm run dev`: Start development server
- `npm run build`: Build production bundle
- `npm run preview`: Preview production build

## Features

1. **Real-time Market Data**: Live stock quotes and charts
2. **Interactive Charts**: Time-series visualization with selection
3. **AI Assistant**: Context-aware financial analysis powered by Gemini
4. **Agentic Vision**: Visual chart analysis using Gemini 3 Flash vision capabilities
5. **Public Chat**: Real-time trading community discussion
6. **Macro Dashboard**: Economic indicators and instruments
7. **Authentication**: User session management