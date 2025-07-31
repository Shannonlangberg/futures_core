# Futures Core Frontend

Modern React frontend for Futures Core with a clean, glowing design.

## Features

- 🎨 **Modern UI**: Clean, glowing design with Tailwind CSS
- 📱 **Responsive**: Works on desktop, tablet, and mobile
- 🧭 **Sidebar Navigation**: Collapsible sidebar with all main pages
- 📊 **Dashboard**: Interactive stat cards with + expansion functionality
- ⚡ **Fast**: Built with Vite for rapid development

## Pages

- **Dashboard** (`/dashboard`): Main stats overview with filters
- **Log Stats** (`/`): Stat logging interface
- **Pulse** (`/heartbeat`): Real-time church activity monitor
- **Passport** (`/journey`): Member journey tracking
- **Users** (`/users`): User management
- **Campuses** (`/campuses`): Campus management

## Tech Stack

- **React 18** - UI framework
- **React Router DOM** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Heroicons** - Beautiful SVG icons
- **Vite** - Fast build tool

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Development

The app runs on `http://localhost:3000` and proxies API calls to the Flask backend on `http://localhost:5001`.

## Structure

```
src/
├── components/
│   └── MainLayout.jsx    # Shared layout with sidebar
├── pages/
│   ├── Dashboard.jsx      # Main dashboard with stat cards
│   ├── LogStats.jsx       # Stat logging page
│   ├── Pulse.jsx          # Real-time monitoring
│   ├── Passport.jsx       # Member journeys
│   ├── Users.jsx          # User management
│   └── Campuses.jsx       # Campus management
├── App.jsx                # Main app with routing
├── main.jsx              # Entry point
└── index.css             # Global styles
```

## Design System

- **Colors**: Slate gray palette with blue/purple accents
- **Typography**: Inter font family
- **Effects**: Glass morphism, subtle glows, smooth transitions
- **Layout**: Responsive grid system with sidebar navigation

## Backend Integration

The frontend connects to the existing Flask backend:
- API calls are proxied to `http://localhost:5001`
- Preserves all existing backend logic and routing
- Maintains + button functionality for stat card expansion 