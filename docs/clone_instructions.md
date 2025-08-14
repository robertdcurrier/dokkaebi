# 🚀 DOKKAEBI Clone Instructions - Create New Projects in SECONDS!

**The SMART way to create new projects from DOKKAEBI's architecture!**

## 🔥 Why Clone Instead of Template?

DOKKAEBI is a **COMPLETE WORKING APPLICATION** with:
- 16 working API endpoints
- Professional web interface with tabs
- Model training/prediction system
- Real data providers
- Memory-bank system
- Everything TESTED and WORKING!

**Why rebuild from scratch when you can clone and modify?**

## 📋 Step-by-Step Clone Process

### 1. Clone the DOKKAEBI Directory

```bash
# Basic clone
cp -r /path/to/dokkaebi /path/to/NEW_PROJECT

# Example for a project called SKYNET
cp -r /Users/rdc/src/dokkaebi /Users/rdc/src/skynet

# Change to new directory
cd /Users/rdc/src/skynet
```

### 2. Clean Git History (Optional)

```bash
# Remove old git history if you want fresh start
rm -rf .git
git init
git add .
git commit -m "Initial commit from DOKKAEBI template"
```

### 3. Tell Claude Code What to Change

Open Claude Code in the new directory and say:

```
"Hey crew, update this cloned DOKKAEBI to be [PROJECT_NAME]:
- Domain: [Your domain - medical, sensors, logistics, etc.]
- Data type: [time-series, images, logs, etc.]
- Replace 'trading/market' terms with [your domain terms]
- Replace 'price/symbol' with [your data terms]
- Keep all functionality but adapt for [your use case]"
```

## 🎯 Example Clone Commands for Different Domains

### Example 1: Ocean Sensor Monitoring (POSEIDON)

```bash
cp -r /Users/rdc/src/dokkaebi /Users/rdc/src/poseidon
cd /Users/rdc/src/poseidon
```

Then tell Claude Code:
```
"Update this to be POSEIDON - ocean sensor monitoring:
- Replace 'trading' with 'sensor monitoring'
- Replace 'symbols' with 'sensor_ids'
- Replace 'price data' with 'sensor readings'
- Replace 'buy/sell signals' with 'anomaly alerts'
- Models detect anomalies instead of trading signals
- Keep using DuckDB for time-series storage"
```

### Example 2: Satellite Image Analysis (SKYNET)

```bash
cp -r /Users/rdc/src/dokkaebi /Users/rdc/src/skynet
cd /Users/rdc/src/skynet
```

Then tell Claude Code:
```
"Update this to be SKYNET - satellite image analysis:
- Replace 'trading' with 'image analysis'
- Replace 'symbols' with 'satellite_ids'
- Replace 'price data' with 'image tiles'
- Replace 'HebbNet' with 'CNN models'
- Models detect objects instead of trading signals
- Add S3 provider for image storage"
```

### Example 3: Medical Data Processing (HEALIX)

```bash
cp -r /Users/rdc/src/dokkaebi /Users/rdc/src/healix
cd /Users/rdc/src/healix
```

Then tell Claude Code:
```
"Update this to be HEALIX - medical data processing:
- Replace 'trading' with 'patient monitoring'
- Replace 'symbols' with 'patient_ids'
- Replace 'price data' with 'vital signs'
- Replace 'buy/sell' with 'risk levels'
- Models predict health risks instead of trades
- Add HIPAA compliance notes"
```

## 📝 What Claude Code Will Update

### 1. User Interface (`templates/index.html`)
- Page title and headers
- Tab names and labels
- Button text and descriptions
- Table column headers
- Activity feed messages

### 2. API Routes (`app/api/routes.py`)
- Endpoint URLs (keep structure, change names)
- Response model field names
- Function docstrings
- Log messages

### 3. Data Models (`app/models/schemas.py`)
- Pydantic model fields
- Validation rules for your domain
- Response/request schemas

### 4. Configuration (`app/core/config.py`)
- App name and description
- Environment variable names
- Default values

### 5. Documentation
- README.md with your project info
- Memory-bank domain knowledge
- API documentation strings

### 6. Provider Implementations (`src/data_processor/providers/`)
- Adapt for your data sources
- Update data fetching logic
- Modify caching strategy

## ✅ What STAYS THE SAME (The Gold!)

- **Project structure** - Already perfect
- **FastAPI setup** - Works immediately
- **Web interface layout** - Professional design
- **API endpoint patterns** - RESTful and clean
- **Model training flow** - Just works
- **Database architecture** - Optimized
- **Error handling** - Production-ready
- **Logging system** - Comprehensive
- **Memory-bank structure** - Critical for success

## 🎨 Customization Levels

### Level 1: Simple Rebrand (5 minutes)
- Just change text labels and names
- Keep all functionality identical
- Perfect for similar domains

### Level 2: Domain Adaptation (30 minutes)
- Update data models for your domain
- Modify API responses
- Adjust UI for your data types
- Add domain-specific validation

### Level 3: Full Customization (2 hours)
- Add new data providers
- Implement custom models
- Create domain-specific features
- Extend API with new endpoints

## 🚦 Quick Test After Cloning

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 3. Run the application
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 4. Open browser
open http://localhost:8000

# YOU HAVE A WORKING APP!
```

## 💡 Pro Tips

1. **Keep the memory-bank!** - Update it for your domain but keep the structure
2. **Don't break what works** - Change text/names before changing logic
3. **Test after each change** - The app should always run
4. **Use the tabs** - They're already wired up perfectly
5. **Keep the logging** - Just update the messages

## 🎯 The Bottom Line

**Cloning DOKKAEBI gives you:**
- ✅ Working application in SECONDS
- ✅ Professional architecture proven in production
- ✅ 2000+ lines of tested code
- ✅ UI that actually looks good
- ✅ API that actually works
- ✅ Models that actually train

**Why start from scratch when you can start from GOLD?**

## 📞 Getting Help

If Claude Code gets confused about what to change, be specific:
```
"In templates/index.html, replace all instances of:
- 'DOKKAEBI' with 'SKYNET'
- 'Trading Terminal' with 'Satellite Monitor'
- 'Download Market Data' with 'Fetch Satellite Images'
- But keep all the JavaScript functionality unchanged"
```

## 🔥 Example Success Story

Bob: "I need a sensor monitoring system"
1. Clone DOKKAEBI → POSEIDON (10 seconds)
2. Tell Claude Code to adapt it (2 minutes)
3. Run `uvicorn main:app` (instant)
4. **WORKING APP with 16 endpoints, models, and UI!**

Compare to starting from scratch: 2-3 days minimum!

---

**Remember: DOKKAEBI is battle-tested and WORKS. Clone it, adapt it, ship it!** 🚀

*"Why reinvent the wheel when you can just repaint it?"* - The Efficient Developer's Motto