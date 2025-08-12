# MANDATORY MEMORY BANK CHECKLIST - CHECK BEFORE EVERY ACTION

## BEFORE CREATING ANY FILE:
- [ ] Check: Is this test/demo code? → Goes in sandbox/
- [ ] Check: Is this documentation? → Goes in docs/
- [ ] Check: Is this production code? → Only then can it go in root or src/

## BEFORE USING TASK TOOL:
- [ ] Have I read critical-rules.md?
- [ ] Have I copied relevant rules into the agent prompt?
- [ ] Did I explicitly tell the agent WHERE to put files?

## BEFORE ANSWERING BOB'S QUESTIONS:
- [ ] Check: Have we seen this problem before? → Check debugging-victories/
- [ ] Check: What's the current state? → Check current-state/
- [ ] Check: Are there special rules? → Check domain-knowledge/

## CRITICAL RULES TO ALWAYS INCLUDE IN AGENT PROMPTS:
1. "ALL test/demo code MUST go in sandbox/ directory"
2. "ALL documentation MUST go in docs/ directory"  
3. "Root directory is for PRODUCTION CODE ONLY"
4. "Check memory-bank/domain-knowledge/critical-rules.md for all rules"

## FAILURE CONSEQUENCES:
- Bob loses trust
- Work gets redone
- Time wasted
- Project chaos

## THE GOLDEN RULE:
**MEMORY BANK FIRST, ACTION SECOND - NO EXCEPTIONS**