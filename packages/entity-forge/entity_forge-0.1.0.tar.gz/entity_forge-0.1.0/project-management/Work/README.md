# Work Directory - Transient Workspace

This directory contains **temporary** development artifacts that become obsolete after code is merged.

## Lifecycle Policy

### During Development
Create freely in these subdirectories:
- `sessions/` - Daily session notes and progress
- `planning/` - Feature planning and design documents
- `analysis/` - Code analysis and investigation notes

### After Commit
- Promote important insights to ADRs or Background/
- Delete implementation details (they're in git history)

### After Merge to Develop
**Clean slate** - Delete all session files:
```bash
cd /workspace/project-management/Work
rm -rf sessions/*
rm -rf planning/*  # Keep only active WIP
rm -rf analysis/*  # Keep only if ADR not yet written
```

## Retention Policy
Maximum 1-2 sprints of history (2-4 weeks)

## Philosophy
Work/ is Claude's scratchpad during development. After code is committed:
1. **Promote**: Move valuable insights to ADRs or Background
2. **Prune**: Delete transient notes (implementation details live in git)

This keeps project-management/ focused on permanent, high-value documentation.

---
_This directory is intentionally temporary. Don't commit long-term docs here._
