# MVP2 Phase 2: Advanced ML Models (PCMCI & STUMPY)

**Causal Discovery and Pattern Detection with Advanced ML**

---

## 🎯 What's New

### PCMCI Causal Discovery
Discover time-lagged causal relationships in your health data.

**Examples:**
- "Sleep 1 day ago → Average glucose today" (r=-0.45, p<0.01)
- "Exercise → Glucose variability" (r=-0.32, p<0.05)
- "Carb intake → Glucose spike 2 hours later"

### STUMPY Pattern Detection
Find recurring patterns and anomalies in glucose data.

**Examples:**
- Recurring morning patterns (occurs 15 times)
- Weekend vs weekday patterns
- Anomalous glucose spikes

---

## 🚀 New API Endpoints

### 1. Causal Graph
```bash
GET /api/v1/insights/advanced/causal-graph?lookback_days=90
Authorization: Bearer <token>
```

**Response:**
```json
{
  "method": "PCMCI",
  "causal_links": [
    {
      "from": "sleep_hours",
      "to": "avg_glucose",
      "lag": 0,
      "strength": -0.45,
      "p_value": 0.001,
      "confidence": "high"
    },
    {
      "from": "exercise_minutes",
      "to": "glucose_variability",
      "lag": 1,
      "strength": -0.32,
      "p_value": 0.03,
      "confidence": "medium"
    }
  ],
  "causal_graph": {
    "nodes": [
      {"id": "sleep_hours", "label": "sleep_hours"},
      {"id": "avg_glucose", "label": "avg_glucose"}
    ],
    "edges": [
      {
        "source": "sleep_hours",
        "target": "avg_glucose",
        "label": "same day",
        "strength": -0.45,
        "confidence": "high"
      }
    ]
  },
  "variables": ["sleep_hours", "exercise_minutes", "carbs_grams", "avg_glucose"],
  "tau_max": 7,
  "sample_size": 85
}
```

### 2. Recurring Patterns
```bash
GET /api/v1/insights/advanced/recurring-patterns?lookback_days=90
Authorization: Bearer <token>
```

**Response:**
```json
{
  "method": "STUMPY Matrix Profile",
  "window_size_hours": 24,
  "patterns_found": 3,
  "patterns": [
    {
      "pattern_id": 1,
      "occurrences": 15,
      "example_dates": ["2025-01-01", "2025-01-08", "2025-01-15"],
      "pattern_summary": {
        "mean": 120.5,
        "std": 15.2,
        "min": 95.0,
        "max": 145.0,
        "duration_hours": 24
      },
      "description": "Pattern occurs 15 times with avg glucose 120.5 mg/dL"
    }
  ],
  "total_data_points": 25920
}
```

### 3. Anomalies
```bash
GET /api/v1/insights/advanced/anomalies?lookback_days=30
Authorization: Bearer <token>
```

**Response:**
```json
{
  "method": "STUMPY Discord Discovery",
  "window_size_hours": 24,
  "anomalies_found": 3,
  "anomalies": [
    {
      "anomaly_id": 1,
      "timestamp": "2025-01-15T14:30:00Z",
      "date": "2025-01-15",
      "time": "14:30:00",
      "severity": "high",
      "pattern_summary": {
        "mean": 235.0,
        "std": 45.2,
        "min": 180.0,
        "max": 310.0
      },
      "description": "Anomalous pattern on 2025-01-15 at 14:30:00 (severity: high)"
    }
  ],
  "total_data_points": 8640
}
```

### 4. Top Causes
```bash
GET /api/v1/insights/advanced/top-causes/avg_glucose?lookback_days=90
Authorization: Bearer <token>
```

**Response:**
```json
{
  "target_variable": "avg_glucose",
  "top_causes": [
    {
      "cause": "sleep_hours",
      "lag_days": 0,
      "strength": -0.45,
      "p_value": 0.001,
      "confidence": "high",
      "interpretation": "Sleep Hours on the same day decreases avg glucose"
    },
    {
      "cause": "carbs_grams",
      "lag_days": 0,
      "strength": 0.38,
      "p_value": 0.005,
      "confidence": "high",
      "interpretation": "Carbs Grams on the same day increases avg glucose"
    }
  ],
  "explanation": "Top factors that influence avg glucose based on causal analysis of the last 90 days."
}
```

### 5. Trigger ML Analysis
```bash
POST /api/v1/insights/advanced/trigger
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "ml_analysis_queued",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Advanced ML analysis started. Check back in a few minutes."
}
```

---

## 📊 How It Works

### PCMCI Algorithm

1. **Collects Data**: Fetches daily aggregates (sleep, exercise, meals, glucose)
2. **Tests Dependencies**: For each variable pair at different time lags (0-7 days)
3. **Conditions on Confounders**: Removes spurious correlations
4. **Finds Causal Links**: Outputs significant relationships with p-values

**Advantages:**
- Time-lag analysis ("yesterday's sleep → today's glucose")
- Distinguishes causation from correlation
- Statistical significance testing

### STUMPY Matrix Profile

1. **Computes Similarity**: Calculates distance between all subsequences
2. **Finds Motifs**: Identifies patterns that repeat frequently
3. **Detects Discords**: Finds patterns that are unusually different
4. **Clusters Days**: Groups similar days together

**Advantages:**
- Fast pattern discovery
- Works with noisy data
- No training required (unsupervised)

---

## 🧪 Usage Examples

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"
headers = {"Authorization": f"Bearer {access_token}"}

# Get causal graph
response = requests.get(
    f"{API_URL}/insights/advanced/causal-graph",
    params={"lookback_days": 90},
    headers=headers
)
causal_data = response.json()

# Print top causes
for link in causal_data["causal_links"][:5]:
    print(f"{link['from']} → {link['to']} (lag={link['lag']}d): r={link['strength']:.2f}")

# Get recurring patterns
response = requests.get(
    f"{API_URL}/insights/advanced/recurring-patterns",
    headers=headers
)
patterns = response.json()

for pattern in patterns["patterns"]:
    print(f"Pattern {pattern['pattern_id']}: occurs {pattern['occurrences']} times")

# Get anomalies
response = requests.get(
    f"{API_URL}/insights/advanced/anomalies",
    params={"lookback_days": 30},
    headers=headers
)
anomalies = response.json()

for anomaly in anomalies["anomalies"]:
    print(f"Anomaly on {anomaly['date']} at {anomaly['time']}: {anomaly['severity']}")
```

### Frontend Integration

```javascript
const api = new GlucoLensAPI();
api.setToken(accessToken);

// Get causal graph
const causalData = await api.request('/insights/advanced/causal-graph?lookback_days=90');

// Visualize causal graph (using vis.js or D3.js)
const network = new vis.Network(container, {
  nodes: causalData.causal_graph.nodes,
  edges: causalData.causal_graph.edges
}, options);

// Get recurring patterns
const patterns = await api.request('/insights/advanced/recurring-patterns');

// Display patterns
patterns.patterns.forEach(pattern => {
  console.log(`Pattern ${pattern.pattern_id}: ${pattern.description}`);
});

// Trigger ML analysis
const analysis = await api.request('/insights/advanced/trigger', { method: 'POST' });
console.log(`Analysis queued: ${analysis.task_id}`);
```

---

## 🔬 Background Tasks

Advanced ML analysis runs automatically:

**Scheduled Tasks (Celery Beat):**
```python
# Weekly on Sunday at midnight
'run-ml-analysis': {
    'task': 'app.tasks_ml.run_ml_analysis_for_all_users',
    'schedule': crontab(hour=0, minute=0, day_of_week=0),
}
```

**Manual Trigger:**
```bash
# Via API
POST /api/v1/insights/advanced/trigger

# Via Celery
celery -A app.tasks_ml call app.tasks_ml.run_full_ml_analysis --args='["<user_id>"]'
```

---

## 📦 Dependencies

Both PCMCI and STUMPY work with fallback methods if libraries aren't available:

**PCMCI (Tigramite):**
- If available: Uses full PCMCI algorithm
- Fallback: Time-lagged Pearson correlation

**STUMPY:**
- If available: Uses matrix profile algorithm
- Fallback: Simple correlation-based pattern detection

**Install libraries:**
```bash
pip install tigramite stumpy
```

---

## 🎨 Visualization Ideas

### Causal Graph
```javascript
// Using vis.js
const nodes = new vis.DataSet(causalData.causal_graph.nodes);
const edges = new vis.DataSet(
  causalData.causal_graph.edges.map(edge => ({
    ...edge,
    label: `${edge.strength > 0 ? '+' : ''}${edge.strength.toFixed(2)}`,
    color: edge.strength > 0 ? 'green' : 'red',
    width: Math.abs(edge.strength) * 5
  }))
);

const network = new vis.Network(container, { nodes, edges }, {
  physics: { enabled: true },
  edges: { arrows: 'to' }
});
```

### Pattern Timeline
```javascript
// Using Chart.js
const patternChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: pattern.example_dates,
    datasets: [{
      label: `Pattern ${pattern.pattern_id}`,
      data: pattern.pattern_values,
      borderColor: 'blue',
      fill: false
    }]
  }
});
```

---

## 📈 Performance

**PCMCI Analysis:**
- 90 days of data: ~5-10 seconds
- Runs once per week per user
- Results cached for 7 days

**STUMPY Pattern Detection:**
- 90 days of CGM data (25,920 readings): ~30-60 seconds
- Runs once per week per user
- Results cached for 7 days

---

## 🔧 Configuration

Update `backend/.env`:

```bash
# ML Settings
PCMCI_MIN_DATA_POINTS=30
PATTERN_DISCOVERY_MIN_DAYS=14

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## 🐛 Troubleshooting

**PCMCI not finding causal links?**
- Check data quality (missing values)
- Ensure at least 30 days of clean data
- Adjust `alpha_level` (default 0.05)

**STUMPY taking too long?**
- Reduce `window_size_hours` (default 24)
- Reduce `lookback_days`
- Use fallback method

**Task not running?**
- Check Celery worker is running: `docker-compose logs celery_worker`
- Verify Redis connection
- Check task queue: `celery -A app.tasks_ml inspect active`

---

## 📚 References

- **PCMCI**: [Tigramite Documentation](https://github.com/jakobrunge/tigramite)
- **STUMPY**: [STUMPY Documentation](https://stumpy.readthedocs.io/)
- **Matrix Profile**: [UCR Matrix Profile](https://www.cs.ucr.edu/~eamonn/MatrixProfile.html)

---

**Phase 2 Complete!** 🎉

Next: Phase 3 (WebSocket Alerts) or Phase 4 (Frontend Dashboard)?
