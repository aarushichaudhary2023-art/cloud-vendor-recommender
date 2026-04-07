# ☁️ Cloud Vendor Recommendation System
## Complete Setup & Deployment Guide

---

## 📁 Project Structure

```
cloud-vendor-recommender/
├── frontend/
│   └── index.html          ← Single-file frontend (HTML + CSS + JS)
├── backend/
│   ├── app.py              ← Flask REST API
│   ├── requirements.txt    ← Python dependencies
│   └── Procfile            ← For Heroku/Render deployment
├── docker-compose.yml      ← Run everything with Docker
├── Dockerfile.backend      ← Backend container
└── README.md               ← This file
```

---

## 🔧 LOCAL DEVELOPMENT SETUP

### Prerequisites
- Python 3.9+
- Node.js (optional, only if you want a local dev server for frontend)
- Git

### Step 1: Clone / Set Up
```bash
git clone <your-repo-url>
cd cloud-vendor-recommender
```

### Step 2: Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Backend running at: http://localhost:5000
```

### Step 3: Frontend Setup (No build needed!)
Open `frontend/index.html` directly in your browser.

To use the live backend, edit `index.html` line 1 of the `<script>`:
```js
const API_BASE = "http://localhost:5000";
```

> **Note**: The frontend has a built-in demo mode fallback — it works even without the backend running.

---

## 🐳 DOCKER DEPLOYMENT (Recommended)

### Create `Dockerfile.backend`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
```

### Create `docker-compose.yml`:
```yaml
version: "3.9"
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped

  frontend:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./frontend:/usr/share/nginx/html:ro
    restart: unless-stopped
```

### Run with Docker:
```bash
docker-compose up --build -d

# Frontend: http://localhost:8080
# Backend:  http://localhost:5000
# Docs:     http://localhost:5000/api/health
```

---

## 🌐 FREE CLOUD DEPLOYMENT

---

### Option A: Render (Backend) + GitHub Pages (Frontend) — RECOMMENDED FREE

#### Backend → Render (Free)
1. Push code to GitHub
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3
5. Click "Create Web Service"
6. Copy your Render URL: `https://your-app.onrender.com`

#### Frontend → GitHub Pages
1. In `frontend/index.html`, update:
   ```js
   const API_BASE = "https://your-app.onrender.com";
   ```
2. Push `frontend/` to a GitHub repo
3. Go to repo Settings → Pages → Source: Deploy from `main` branch `/frontend`
4. Live at: `https://yourusername.github.io/your-repo/`

---

### Option B: Heroku (Backend)
```bash
cd backend
heroku login
heroku create cloud-vendor-api
git init && git add . && git commit -m "init"
heroku git:remote -a cloud-vendor-api
git push heroku main
# Live at: https://cloud-vendor-api.herokuapp.com
```

---

### Option C: Netlify (Frontend only — demo mode)
```bash
# Install Netlify CLI
npm install -g netlify-cli

cd frontend
netlify deploy --prod --dir=.
# Live at: https://random-name.netlify.app
```

---

### Option D: AWS Free Tier (Full deployment)

#### EC2 Instance Setup:
```bash
# 1. Launch EC2 t2.micro (Amazon Linux 2) — free tier
# 2. Open ports 22 (SSH), 80 (HTTP), 5000 (API) in Security Group

# SSH into instance:
ssh -i your-key.pem ec2-user@<your-ec2-ip>

# Install dependencies:
sudo yum update -y
sudo yum install python3 python3-pip git nginx -y

# Clone & run backend:
git clone <your-repo>
cd cloud-vendor-recommender/backend
pip3 install -r requirements.txt
gunicorn app:app --bind 0.0.0.0:5000 --daemon

# Serve frontend with nginx:
sudo cp -r /home/ec2-user/cloud-vendor-recommender/frontend/* /usr/share/nginx/html/
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 📡 API REFERENCE

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/health` | GET | Health check |
| `GET /api/vendors` | GET | List all vendors |
| `POST /api/recommend` | POST | Get recommendations |
| `POST /api/compare` | POST | Compare specific vendors |

### POST /api/recommend — Sample Request:
```json
{
  "workload": {
    "compute_size": "medium",
    "compute_hours": 730,
    "storage_gb": 100,
    "network_gb": 50,
    "db_instances": 1,
    "db_size": "small"
  },
  "max_budget": 500,
  "required_compliance": ["HIPAA", "SOC2"],
  "needs_ml": true,
  "needs_kubernetes": false,
  "needs_serverless": true,
  "cost_weight": 0.2,
  "reliability_weight": 0.2,
  "performance_weight": 0.15,
  "security_weight": 0.15,
  "support_weight": 0.1,
  "innovation_weight": 0.1,
  "compliance_weight": 0.1
}
```

### Sample Response:
```json
{
  "success": true,
  "top_pick": "aws",
  "recommendations": [...],
  "analysis": {
    "summary": "Amazon Web Services is the best fit...",
    "reasoning": [...],
    "trade_offs": [...]
  }
}
```

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                    User's Browser                   │
│                  (index.html / SPA)                 │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP POST /api/recommend
                      ▼
┌─────────────────────────────────────────────────────┐
│               Flask REST API (Python)               │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Scoring     │  │ Cost Calc    │  │ Analysis  │  │
│  │ Engine      │  │ Engine       │  │ Generator │  │
│  └─────────────┘  └──────────────┘  └───────────┘  │
│           │               │               │         │
│           └───────────────┴───────────────┘         │
│                           │                         │
│              ┌────────────▼───────────┐             │
│              │   Vendor Database      │             │
│              │ AWS / GCP / Azure / DO │             │
│              └────────────────────────┘             │
└─────────────────────────────────────────────────────┘
```

---

## 📊 SCORING ALGORITHM

The recommendation score is computed as a **weighted sum**:

```
Score = Σ (criterion_score × user_weight) + feature_bonus

Where:
- criterion_score = vendor's normalized rating (0-10)
- user_weight     = user-defined priority (sums to 1.0)
- feature_bonus   = +0.5 for ML match, +0.3 for K8s match, etc.
- cost_score      = 10 - (monthly_cost / budget) × 5
```

---

## 🧪 TESTING THE API

```bash
# Health check
curl http://localhost:5000/api/health

# Get recommendation
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "workload": {"compute_size": "medium", "compute_hours": 730, "storage_gb": 100, "network_gb": 50},
    "max_budget": 500,
    "cost_weight": 0.25,
    "reliability_weight": 0.25,
    "security_weight": 0.2,
    "performance_weight": 0.15,
    "support_weight": 0.1,
    "innovation_weight": 0.05,
    "compliance_weight": 0.0
  }'
```

---

## 📈 PERFORMANCE OPTIMIZATION

1. **Cache vendor data** with Redis (add `flask-caching` + `redis` to requirements.txt)
2. **Rate limiting** with `flask-limiter`
3. **CORS** already configured; restrict to your frontend domain in production
4. **CDN**: Serve `index.html` via Cloudflare Free for global edge caching

---

## ✅ ASSESSMENT CHECKLIST

| Criterion | Status |
|-----------|--------|
| Working implementation | ✅ Flask API + HTML frontend |
| Source code | ✅ app.py + index.html |
| Architecture diagram | ✅ In this README |
| Setup instructions | ✅ This file |
| Deployment options | ✅ Render, Heroku, AWS, Docker |
| Performance analysis | ✅ Scoring algorithm documented |
| Demo mode (no backend) | ✅ Built-in fallback |

---

*Built for Cloud Computing Course Project — Cloud Vendor Recommendation System*
