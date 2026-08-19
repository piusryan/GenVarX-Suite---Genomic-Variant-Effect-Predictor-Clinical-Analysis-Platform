# 🚀 GenVarX - Complete Setup & Run Guide

## ⚡ Quick Start (30 seconds)

### Terminal 1 - Backend (Port 8000)
```bash
uvicorn app.main:app --port 8000 --reload
```

### Terminal 2 - Frontend (Port 5173)
```bash
npm run dev
```

### Open Browser
```
http://localhost:5173
```

---

## 🔧 System Requirements

- **Python** 3.11+ (installed and working)
- **Node.js** 18+ (with npm)
- **Git** (optional, for version control)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

### Verify Installation
```bash
# Check Python
python --version

# Check Node.js
node --version
npm --version
```

---

## 📋 Step-by-Step Setup

### 1️⃣ Clone or Navigate to Project

```bash
# If cloned from git
cd genvarx

# Or just navigate to project directory
```

### 2️⃣ Install Backend Dependencies

The backend uses FastAPI which requires Python packages. Check `requirements.txt`:

```bash
# View requirements
cat requirements.txt

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Install Frontend Dependencies

```bash
# Install npm packages
npm install

# This will take 2-3 minutes
```

---

## 🎯 Running the Application

### Option A: Two Terminal Windows (Recommended)

**Terminal 1 - Backend Server**
```bash
uvicorn app.main:app --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Terminal 2 - Frontend Development Server**
```bash
npm run dev
```

Expected output:
```
VITE v8.1.5  ready in 246 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Option B: Single Terminal (Requires `tmux` or similar)

```bash
# Start backend in background
uvicorn app.main:app --port 8000 --reload &

# Start frontend
npm run dev
```

---

## 🌐 Access the Application

1. **Open your browser**
2. **Navigate to:** `http://localhost:5173`
3. **You should see:** GenVarX Suite interface

---

## ✅ Verify Everything is Working

### Check Backend Health
```bash
# In another terminal, run:
curl http://127.0.0.1:8000/health

# Expected response:
# {"status":"online","service":"GenVarX Engine"}
```

### Check Frontend Build
```bash
# Frontend should be accessible at:
# http://localhost:5173
```

---

## 🧪 Test the Full Workflow

1. **Enter Variant Coordinate:** `17:43044295:G:A` (BRCA1 example)
2. **Click:** "Analyze Variant"
3. **You should see:**
   - DNA strand visualization (2D)
   - 3D protein structure (interactive)
   - Disease associations
   - Conservation scores

---

## 📊 What Each Module Does

### Variant Module
- Analyzes genomic variants
- Shows impact prediction
- Displays DNA visualization
- Shows 3D protein structure
- Lists disease associations

### Disease Association Module
- Resolves rsID from variant
- Queries GWAS Catalog
- Shows trait associations
- Displays p-values

### Drug Discovery Module
- Searches ChEMBL compounds
- Shows drug properties
- Displays molecular structures
- Lists bioactivities

---

## 🎨 Features Overview

### Visualizations
✅ **2D DNA Strand** - Shows what changed in the DNA
✅ **3D Protein Structure** - Interactive model of protein with mutation highlighted
✅ **Info Panels** - Educational labels and explanations
✅ **Color Coding** - Blue (normal), Red (mutation)

### Functionality
✅ **Variant Annotation** - Via Ensembl VEP
✅ **Clinical Data** - Via ClinVar
✅ **Disease Links** - Via GWAS Catalog
✅ **Drug Targets** - Via ChEMBL
✅ **Conservation** - BLOSUM62 scoring
✅ **Domain Analysis** - Motif disruption detection
✅ **Phenotypes** - HPO integration

---

## 🛠️ Configuration

### Backend Configuration

**Port Changes:**
- Edit the `uvicorn` command above
- Change `--port 8000` to your desired port
- Update `.env.local` in frontend accordingly

### Frontend Configuration

**API URL:**
- Edit `.env.local`:
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Port Changes:**
- Edit `vite.config.js` for custom port

---

## 📚 Project Structure

```
genvarx/
├── app/                          # Backend (FastAPI)
│   ├── main.py                   # API endpoints
│   ├── models.py                 # Data models
│   └── services/                 # External services
│       ├── vep_service.py        # Variant Effect Prediction
│       ├── clinvar_service.py    # ClinVar integration
│       ├── gwas_service.py       # GWAS Catalog
│       ├── chembl_local_service.py # ChEMBL search
│       ├── hpo_service.py        # Phenotypes
│       ├── conservation_service.py # BLOSUM scoring
│       └── motif_service.py      # Domain analysis
├── src/                          # Frontend (React)
│   ├── App.jsx                   # Main component
│   ├── main.jsx                  # Entry point
│   └── components/               # React components
│       ├── VariantVisualizer.jsx # 2D DNA visualization
│       └── AdvancedProtein3D.jsx # 3D protein structure
├── data/                         # Datasets
│   └── datasets/
│       ├── chembl/               # ChEMBL compounds
│       ├── hpo/                  # HPO phenotypes
│       ├── clinvar/              # ClinVar variants
│       └── reference/            # Reference genomes
└── docs/                         # Documentation

```

---

## 🔍 API Endpoints

All endpoints are at `http://127.0.0.1:8000`

### Health Check
```
GET /health
```

### Analyze Variant
```
POST /api/annotate
{
  "variant": "17:43044295:G:A"
}
```

### Get GWAS Associations
```
POST /api/gwas
{
  "variant": "17:43044295:G:A"
}
```

### Search Compounds
```
GET /api/compounds?query=selinexor&limit=20
```

### Get Compound Details
```
GET /api/compounds/CHEMBL237500
```

### Get Phenotypes
```
POST /api/phenotypes
{
  "variant": "Breast Cancer"
}
```

### Analyze Motif
```
POST /api/motif-analysis?gene_symbol=BRCA1&ref_aa=D&alt_aa=V&protein_position=100
```

### Conservation Score
```
GET /api/conservation-score?ref_aa=D&alt_aa=V
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
# If Windows:
netstat -ano | findstr :8000

# If Mac/Linux:
lsof -i :8000

# Try different port:
uvicorn app.main:app --port 8001 --reload
# Then update .env.local
```

### Frontend won't start
```bash
# Clear node_modules and reinstall
rm -r node_modules package-lock.json
npm install

# Then run again
npm run dev
```

### "CORS error" or "Cannot reach backend"
```bash
# Check .env.local has correct URL:
cat .env.local
# Should have: VITE_API_BASE_URL=http://127.0.0.1:8000

# Verify backend is running:
curl http://127.0.0.1:8000/health
```

### Build errors
```bash
# Clear build cache
rm -r dist/

# Rebuild
npm run build
```

---

## 📈 Performance Tips

### For Development
- Keep `--reload` flag on backend for auto-restart
- Use hot-reload on frontend (automatic with `npm run dev`)
- Keep browser DevTools open to debug issues

### For Production
```bash
# Build frontend
npm run build

# Run backend without reload
uvicorn app.main:app --port 8000 --workers 4

# Serve frontend from dist/ folder
# Use nginx, Apache, or similar
```

---

## 📝 Example Variants

Try these for testing:

| Gene  | Variant            | Type          |
|-------|-------------------|---------------|
| BRCA1 | 17:43044295:G:A   | Pathogenic    |
| BRCA2 | 13:32316462:G:A   | Pathogenic    |
| TP53  | 17:7673802:C:T    | Pathogenic    |

---

## 🎓 Testing Workflow

1. **Start Backend**
   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```

2. **Start Frontend**
   ```bash
   npm run dev
   ```

3. **Navigate to** `http://localhost:5173`

4. **Try Variant Analysis**
   - Enter: `17:43044295:G:A`
   - Click: `Analyze Variant`
   - Wait for results

5. **Explore Visualizations**
   - See DNA 2D strand
   - See 3D protein model
   - Interact: Drag to rotate
   - Interact: Scroll to zoom
   - Interact: Click Pause

6. **Try Other Modules**
   - Disease Association
   - Drug Discovery

---

## 💡 Development Workflow

### Making Changes

**Backend Changes:**
1. Edit file in `app/` or `app/services/`
2. Backend auto-reloads (if `--reload` flag used)
3. Test with `curl` or frontend

**Frontend Changes:**
1. Edit file in `src/`
2. Frontend auto-reloads
3. See changes immediately in browser

### Debugging

**Backend:**
```python
# Add print statements
print(f"Variant: {variant}")

# Or use logging
import logging
logger = logging.getLogger()
logger.info(f"Processing variant: {variant}")
```

**Frontend:**
```javascript
// Browser console
console.log("Data:", data);
console.error("Error:", error);

// React DevTools
// Install React DevTools extension
```

---

## 🚀 Deployment (Future)

When ready to deploy:

1. **Build Frontend**
   ```bash
   npm run build
   ```

2. **Deploy Backend** (e.g., Heroku, AWS, DigitalOcean)
   ```bash
   # Set environment variables
   # Configure database
   # Run: uvicorn app.main:app --port $PORT
   ```

3. **Deploy Frontend** (e.g., Vercel, Netlify)
   ```bash
   # Push to GitHub
   # Connect to Vercel/Netlify
   # Auto-deploy from main branch
   ```

---

## 📞 Support

**Not working?**
1. Check backend: `curl http://127.0.0.1:8000/health`
2. Check frontend: `http://localhost:5173` in browser
3. Check `.env.local` has correct API URL
4. Check no port conflicts (ports 5173 and 8000)
5. Try restarting both servers

---

## ✨ What's Next?

After running:
- Experiment with different variants
- Try different modules
- Explore the visualizations
- Read the documentation
- Consider enhancements

---

## 📄 Documentation Files

- `README.md` - Project overview
- `PROJECT_STRUCTURE.md` - Architecture
- `DATASETS_GUIDE.md` - Data information
- `VISUALIZATION_GUIDE.md` - Visualization details
- `3D_VISUALIZATION.md` - 3D model details
- `3D_COMPLETE.txt` - 3D status

---

## ✅ Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`, `npm install`)
- [ ] `.env.local` has correct API URL
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Browser open to `http://localhost:5173`
- [ ] Variant analysis working
- [ ] Visualizations rendering
- [ ] 3D model interactive

---

**🎉 You're ready to go! Happy analyzing!**

