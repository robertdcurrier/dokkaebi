# DOKKAEBI Startup Commands - CRITICAL OPERATIONAL KNOWLEDGE

**Last Updated:** August 24, 2025
**Status:** VERIFIED AND WORKING

## 🚀 PRIMARY STARTUP COMMAND

```bash
uvicorn main:app --reload
```

**NOT** `python main.py` - that's WRONG!

## Alternative Methods

### Using the convenience script:
```bash
./start_me.sh
```

### With specific host/port:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode (no auto-reload):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Common Mistakes to Avoid

❌ **WRONG:** `python main.py` - This will hang/timeout
❌ **WRONG:** `python -m main` - Not configured for this
❌ **WRONG:** `flask run` - This is FastAPI, not Flask

✅ **CORRECT:** `uvicorn main:app --reload`

## What Happens After Starting

1. Server starts on `http://localhost:8000`
2. Auto-reload enabled (watches for file changes)
3. FastAPI docs available at `http://localhost:8000/docs`
4. Terminal shows:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process [####] using statreload
   INFO:     Started server process [####]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

## Troubleshooting

### If port 8000 is already in use:
```bash
# Kill existing process
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn main:app --reload --port 8001
```

### If uvicorn not found:
```bash
pip install uvicorn
# or
pip install -r requirements.txt
```

## REMEMBER: Always use uvicorn, NOT python main.py!