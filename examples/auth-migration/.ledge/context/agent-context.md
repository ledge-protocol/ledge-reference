# Agent Context

## Human Intent
Replace Clerk with BetterAuth.

## Accepted Knowledge
Authentication migration is not complete.

## Evidence
Remaining Clerk references were found in:

- src/auth/provider.ts
- src/middleware.ts

## Corrected Assumptions
Do not assume authentication migration is complete.
Do not assume all Clerk references have been removed.

## Current Drift Risk
The codebase may still contain Clerk-specific imports, middleware, or auth provider usage.

## Agent Guidance
Before implementing new authentication changes:

1. Search for remaining Clerk references.
2. Prefer BetterAuth-compatible changes.
3. Do not mark the migration complete without evidence.
4. Produce evidence for any claim about migration completion.

