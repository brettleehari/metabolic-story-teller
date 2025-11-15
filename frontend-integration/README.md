# Frontend Integration Files

Ready-to-use files for connecting **metabolic-story-teller** (or any frontend) to the GlucoLens backend.

## 📦 Files Included

### Core Integration
- **`typescript-types.ts`** - TypeScript type definitions for all API models
- **`api-client.js`** - Complete API client with all endpoints
- **`react-hooks.js`** - React custom hooks (optional, for React apps)

### Configuration
- **`.env.frontend.example`** - Environment variable template for your frontend
- **`api-config.example.js`** - API configuration helper

## 🚀 Quick Setup

### Step 1: Copy Files to Your Frontend

```bash
# Copy all files to your frontend
cp frontend-integration/* /path/to/metabolic-story-teller/src/api/
```

Or copy individually:

```bash
# For TypeScript projects
cp typescript-types.ts /path/to/metabolic-story-teller/src/api/types.ts

# API client (works with any framework)
cp api-client.js /path/to/metabolic-story-teller/src/api/client.js

# React hooks (React projects only)
cp react-hooks.js /path/to/metabolic-story-teller/src/api/hooks.js

# Configuration
cp api-config.example.js /path/to/metabolic-story-teller/src/config/api.js
cp .env.frontend.example /path/to/metabolic-story-teller/.env
```

### Step 2: Update Environment Variables

Edit `.env` in your frontend:

```bash
# For Vite
VITE_API_URL=http://localhost:8000/api/v1

# For Next.js
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# For Create React App
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Step 3: Update Backend CORS

In `glucolens/backend/.env`:

```bash
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Restart backend:
```bash
cd glucolens
docker-compose restart api
```

## 📖 Usage Examples

### Basic API Call

```javascript
import GlucoLensAPI from './api/client';

const api = new GlucoLensAPI();

// Get glucose readings
const readings = await api.getGlucoseReadings({ limit: 100 });
console.log(readings);
```

### React Component

```jsx
import { useGlucoseReadings } from './api/hooks';

function GlucoseChart() {
  const { readings, loading, error } = useGlucoseReadings({ limit: 288 });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {readings.map(r => (
        <div key={r.id}>
          {r.timestamp}: {r.value} mg/dL
        </div>
      ))}
    </div>
  );
}
```

### Vue.js

```vue
<script setup>
import { ref, onMounted } from 'vue';
import GlucoLensAPI from './api/client';

const api = new GlucoLensAPI();
const dashboard = ref(null);

onMounted(async () => {
  dashboard.value = await api.getDashboard(7);
});
</script>

<template>
  <div v-if="dashboard">
    <h1>Avg Glucose: {{ dashboard.avg_glucose }}</h1>
    <p>Time in Range: {{ dashboard.time_in_range_percent }}%</p>
  </div>
</template>
```

### Next.js

```typescript
// app/api/glucose/route.ts
import { NextResponse } from 'next/server';
import GlucoLensAPI from '@/lib/api/client';

export async function GET() {
  const api = new GlucoLensAPI();
  const readings = await api.getGlucoseReadings({ limit: 100 });
  return NextResponse.json(readings);
}
```

## 🔧 Framework-Specific Setup

### React (Vite)

```bash
# Install (no extra deps needed!)
npm install

# Create .env
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Import in src/main.tsx or App.tsx
import GlucoLensAPI from './api/client';
```

### Next.js

```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Use in components or API routes
import GlucoLensAPI from '@/lib/api/client';
```

### Vue 3

```bash
# Create .env
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Use in composables
import GlucoLensAPI from '@/api/client';
```

### Angular

```bash
# Create environment.ts
export const environment = {
  apiUrl: 'http://localhost:8000/api/v1'
};

# Create service
import { Injectable } from '@angular/core';
import GlucoLensAPI from './api/client';

@Injectable({ providedIn: 'root' })
export class GlucoLensService {
  private api = new GlucoLensAPI();

  async getReadings() {
    return this.api.getGlucoseReadings();
  }
}
```

## 🎯 Available API Methods

### Glucose
- `getGlucoseReadings(params)` - Get glucose readings
- `createGlucoseReading(reading)` - Create single reading
- `bulkUploadGlucose(readings)` - Bulk upload

### Sleep
- `createSleepData(sleep)` - Log sleep session

### Activities
- `createActivity(activity)` - Log activity

### Meals
- `createMeal(meal)` - Log meal

### Insights
- `getCorrelations(limit)` - Get correlations
- `getPatterns(limit)` - Get patterns
- `getDashboard(days)` - Get dashboard summary
- `triggerAnalysis()` - Trigger ML analysis

## 🐛 Troubleshooting

### CORS Errors

Add your frontend URL to `backend/.env`:
```bash
ALLOWED_ORIGINS=http://localhost:3000
```

### TypeScript Errors

Make sure `typescript-types.ts` is in your project and imported:
```typescript
import type { GlucoseReading, DashboardSummary } from './api/types';
```

### Environment Variables Not Loading

**Vite**: Variables must start with `VITE_`
**Next.js**: Variables must start with `NEXT_PUBLIC_`
**CRA**: Variables must start with `REACT_APP_`

## 📚 Full Documentation

See [`FRONTEND_INTEGRATION.md`](../FRONTEND_INTEGRATION.md) for complete integration guide.

---

**Ready to integrate! 🚀**
