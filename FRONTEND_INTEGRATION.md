# Frontend Integration Guide

Connect your **metabolic-story-teller** frontend to the GlucoLens backend.

---

## 🚀 Quick Start

### 1. Update Backend CORS Settings

The backend needs to allow requests from your frontend. Update `backend/.env`:

```bash
# Add your frontend URL to ALLOWED_ORIGINS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:4200
```

Common frontend ports:
- **React (CRA)**: 3000
- **Next.js**: 3000
- **Vite**: 5173
- **Angular**: 4200
- **Vue**: 8080

### 2. Copy Integration Files to Your Frontend

```bash
# From glucolens directory
cp frontend-integration/* /path/to/metabolic-story-teller/src/api/
```

Files provided:
- `typescript-types.ts` - TypeScript type definitions
- `api-client.js` - API client class
- `react-hooks.js` - React custom hooks (if using React)

### 3. Install Required Dependencies

```bash
cd /path/to/metabolic-story-teller

# No additional dependencies needed! Uses native fetch API
# Optional: If using TypeScript
npm install -D @types/node
```

### 4. Configure API Base URL

Create a `.env` file in your frontend:

```bash
# For React/Next.js
VITE_API_URL=http://localhost:8000/api/v1
# OR
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
# OR
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## 📦 Using the API Client

### JavaScript/TypeScript

```javascript
import GlucoLensAPI from './api/api-client';

const api = new GlucoLensAPI('http://localhost:8000/api/v1');

// Get glucose readings
const readings = await api.getGlucoseReadings({ limit: 100 });

// Upload glucose reading
await api.createGlucoseReading({
  timestamp: new Date().toISOString(),
  value: 95.0,
  source: 'manual'
});

// Get dashboard data
const dashboard = await api.getDashboard(7); // 7 days
```

### React Components

```jsx
import { useGlucoseReadings, useDashboard } from './api/react-hooks';

function Dashboard() {
  const { dashboard, loading, error } = useDashboard(7);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h1>Average Glucose: {dashboard.avg_glucose} mg/dL</h1>
      <h2>Time in Range: {dashboard.time_in_range_percent}%</h2>

      <h3>Top Correlations</h3>
      {dashboard.top_correlations.map(corr => (
        <div key={corr.id}>
          {corr.factor_x} → {corr.factor_y}: {corr.correlation_coefficient}
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
import GlucoLensAPI from './api/api-client';

const api = new GlucoLensAPI('http://localhost:8000/api/v1');
const readings = ref([]);

onMounted(async () => {
  readings.value = await api.getGlucoseReadings({ limit: 100 });
});
</script>

<template>
  <div v-for="reading in readings" :key="reading.id">
    {{ reading.timestamp }}: {{ reading.value }} mg/dL
  </div>
</template>
```

---

## 🔌 API Endpoints Reference

### Glucose

```javascript
// Get readings
api.getGlucoseReadings({
  start: '2025-01-01T00:00:00Z',
  end: '2025-01-15T00:00:00Z',
  limit: 1000
});

// Create single reading
api.createGlucoseReading({
  timestamp: '2025-01-15T08:00:00Z',
  value: 95.0,
  source: 'dexcom_g7'
});

// Bulk upload
api.bulkUploadGlucose([
  { timestamp: '2025-01-15T08:00:00Z', value: 95.0 },
  { timestamp: '2025-01-15T08:05:00Z', value: 98.0 }
]);
```

### Sleep

```javascript
api.createSleepData({
  date: '2025-01-15',
  sleep_start: '2025-01-14T23:00:00Z',
  sleep_end: '2025-01-15T07:00:00Z',
  duration_minutes: 480,
  quality_score: 8.5,
  source: 'apple_watch'
});
```

### Activities

```javascript
api.createActivity({
  timestamp: '2025-01-15T18:00:00Z',
  activity_type: 'running',
  duration_minutes: 45,
  intensity: 'moderate',
  calories_burned: 350
});
```

### Meals

```javascript
api.createMeal({
  timestamp: '2025-01-15T12:00:00Z',
  meal_type: 'lunch',
  carbs_grams: 60.0,
  protein_grams: 30.0,
  fat_grams: 20.0,
  calories: 500
});
```

### Insights

```javascript
// Get correlations
const correlations = await api.getCorrelations(10);

// Get patterns
const patterns = await api.getPatterns(10);

// Get dashboard summary
const dashboard = await api.getDashboard(7); // 7 days

// Trigger ML analysis
await api.triggerAnalysis();
```

---

## 🎨 Example Components

### Glucose Chart Component

```jsx
import { useGlucoseReadings } from './api/react-hooks';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

function GlucoseChart() {
  const { readings, loading } = useGlucoseReadings({ limit: 288 }); // 24 hours

  if (loading) return <div>Loading...</div>;

  const chartData = readings.map(r => ({
    time: new Date(r.timestamp).toLocaleTimeString(),
    glucose: r.value
  }));

  return (
    <LineChart width={800} height={400} data={chartData}>
      <XAxis dataKey="time" />
      <YAxis domain={[50, 200]} />
      <Tooltip />
      <Line type="monotone" dataKey="glucose" stroke="#8884d8" />
    </LineChart>
  );
}
```

### Insights Display

```jsx
function InsightsPanel() {
  const [correlations, setCorrelations] = useState([]);
  const [patterns, setPatterns] = useState([]);

  useEffect(() => {
    async function loadInsights() {
      const api = new GlucoLensAPI();
      const [corr, patt] = await Promise.all([
        api.getCorrelations(5),
        api.getPatterns(5)
      ]);
      setCorrelations(corr);
      setPatterns(patt);
    }
    loadInsights();
  }, []);

  return (
    <div>
      <h2>Correlations</h2>
      {correlations.map(c => (
        <div key={c.id} className="correlation-card">
          <strong>{c.factor_x}</strong> affects <strong>{c.factor_y}</strong>
          <br />
          Strength: {(c.correlation_coefficient * 100).toFixed(0)}%
          <br />
          Confidence: {c.confidence_level}
        </div>
      ))}

      <h2>Patterns</h2>
      {patterns.map(p => (
        <div key={p.id} className="pattern-card">
          {p.description}
          <br />
          Confidence: {(p.confidence * 100).toFixed(0)}%
        </div>
      ))}
    </div>
  );
}
```

---

## 🔧 Environment Setup

### Development

```bash
# 1. Start backend
cd glucolens
docker-compose up -d

# 2. Generate sample data (optional)
docker-compose exec api python scripts/generate_sample_data.py --days 90

# 3. Start frontend
cd ../metabolic-story-teller
npm install
npm run dev
```

### Production

Update API URLs in your frontend `.env`:

```bash
VITE_API_URL=https://api.glucolens.com/api/v1
```

Update backend CORS:

```bash
# backend/.env
ALLOWED_ORIGINS=https://metabolic-story-teller.com,https://www.metabolic-story-teller.com
```

---

## 🐛 Troubleshooting

### CORS Errors

**Problem**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**: Add your frontend URL to `backend/.env`:
```bash
ALLOWED_ORIGINS=http://localhost:3000
```

Restart backend:
```bash
docker-compose restart api
```

### API Not Found (404)

**Problem**: `GET http://localhost:8000/api/v1/glucose/readings 404`

**Solution**: Check backend is running:
```bash
docker-compose ps
curl http://localhost:8000/health
```

### Authentication Errors (Future)

MVP1 uses a mock user. In MVP2 with authentication:

```javascript
const api = new GlucoLensAPI('http://localhost:8000/api/v1', {
  getToken: () => localStorage.getItem('auth_token')
});
```

---

## 📊 Data Flow

```
┌─────────────────┐
│   Frontend      │
│  (metabolic-    │
│   story-teller) │
└────────┬────────┘
         │ HTTP Requests
         │
┌────────▼────────┐
│  FastAPI        │
│  Backend        │
│  (glucolens)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  TimescaleDB    │
│  + Redis        │
└─────────────────┘
```

---

## 🚀 Next Steps

1. **Copy integration files** to your frontend
2. **Update backend CORS** with your frontend URL
3. **Test API connection** with a simple fetch:
   ```javascript
   fetch('http://localhost:8000/health')
     .then(r => r.json())
     .then(console.log);
   ```
4. **Build your UI** using the provided hooks and client
5. **Deploy** both backend and frontend

---

## 📞 Support

- **Backend API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

**Ready to connect! 🔗**

Share your metabolic-story-teller frontend code or structure, and I can provide more specific integration steps!
