# Travel Planner India - Frontend

Next.js 16 frontend for the Travel Planner India application.

## Tech Stack

- **Next.js 16.1.3** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Styling
- **date-fns** - Date utilities

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                    # Next.js app router pages
│   ├── page.tsx           # Homepage
│   ├── results/           # Search results
│   ├── journey/           # Journey details
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── LocationSearch.tsx
│   ├── JourneyCard.tsx
│   └── ...
├── lib/                   # Utility functions
│   ├── api.ts            # API client
│   └── utils.ts          # Helper functions
├── types/                 # TypeScript types
└── public/               # Static assets
```

## Build for Production

```bash
npm run build
npm start
```

## API Integration

The frontend communicates with the backend API at `http://localhost:8000` by default.

### Endpoints

- `GET /api/v1/search` - Search for journeys
- `GET /api/v1/locations` - Search for locations
- `GET /api/v1/journeys/{id}` - Get journey details
