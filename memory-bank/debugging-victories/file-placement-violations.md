# File Placement Violations - SOLVED

## The Problem (August 12, 2025)
Multiple violations of file placement rules:
1. Test files being created in root directory
2. Documentation (.md files) being created in root
3. Agents (Viper, Repo) not following the rules

## Root Cause
Memory bank rules existed but weren't being communicated to agents via Task tool prompts.

## The Solution

### 1. Updated CLAUDE.md with ABSOLUTE RULE
```
**🚨 ABSOLUTE RULE: NEVER TAKE ANY ACTIONS WITHOUT CHECKING THE MEMORY-BANK FIRST 🚨**
```

### 2. Created MANDATORY AGENT HANDOFF PROTOCOL
When using Task tool:
- ALWAYS include file location rules in the prompt
- Copy memory bank rules INTO agent prompt
- Check agent output before presenting to Bob

### 3. Created MANDATORY-CHECKLIST.md
Checklist to review before EVERY action

## Verification Test
Tested with Viper creating test_textual_import.py:
- ✅ Rules were included in prompt
- ✅ Viper acknowledged rules
- ✅ File created in correct location (sandbox/)

## Files That Were Misplaced and Fixed
- `test_simple.py` → moved to sandbox/
- `demo_scanner.py` → moved to sandbox/
- `main.py` → moved to sandbox/old_main.py
- `config.py` → moved to sandbox/old_config.py
- `FIRE_GOBLIN_README.md` → moved to docs/
- `run_fire_goblin_textual.py` → moved to sandbox/

## Key Learning
Memory bank rules must be ACTIVELY INJECTED into agent prompts, not passively stored.