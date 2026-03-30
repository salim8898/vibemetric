# Known Issues & Future Enhancements

## Critical Issues

None currently.

## Known Limitations

### 1. Squash Merge Workflows (Velocity Analyzer)

**Status:** Not Implemented  
**Priority:** Medium  
**Affects:** Velocity Analyzer accuracy  

**Problem:**
Teams that use squash merge workflows will see inaccurate velocity measurements. When a PR with 14 commits over 2 weeks gets squashed into 1 commit, it appears as a massive velocity spike on the merge day.

**Example:**
```
Developer works for 2 weeks:
- 14 commits in feature branch (not visible in main)
- Day 14: Squash merge → 1 commit with 700 lines

Current behavior: Detects as 700 lines/day (WRONG)
Expected behavior: Should be 50 lines/day (700 / 14 days)
```

**Impact:**
- False positives: Normal work appears as AI-assisted spikes
- False negatives: Real AI adoption hidden in squash commits
- Affects teams using GitHub/GitLab squash merge strategy

**Solution:**
Implement PR-based velocity analysis:
1. Detect squash merge commits (>500 lines, many files, "squash" in message)
2. Fetch PR metadata from GitHub/GitLab API
3. Calculate velocity using PR timeline (merged_at - created_at)
4. Hybrid approach: regular commits + PR-based for squash merges

**Workaround:**
For now, velocity analyzer works best with:
- Merge commit workflows
- Rebase workflows
- Teams that don't squash PRs

**Implementation Plan:**
- Phase 1: Add squash merge detection (30 min)
- Phase 2: GitHub/GitLab API integration (2-3 hours)
- Phase 3: PR-based velocity calculation (1-2 hours)
- Phase 4: Hybrid analysis mode (1 hour)

**Estimated Effort:** 4-6 hours  
**Target:** After Phase 1 core features complete

---

## Future Enhancements

### 2. Multi-Repository Analysis

**Status:** Not Planned for Phase 1  
**Priority:** Low  

Analyze velocity across multiple repositories for a single developer.

### 3. Team Velocity Aggregation

**Status:** Not Planned for Phase 1  
**Priority:** Medium  

Aggregate velocity metrics across entire team, not just individual developers.

### 4. Velocity Trend Visualization

**Status:** Not Planned for Phase 1  
**Priority:** Low  

Generate charts showing velocity over time with AI adoption markers.

### 5. Commit Message Analysis

**Status:** Not Planned for Phase 1  
**Priority:** Low  

Analyze commit messages for AI-generated patterns (e.g., overly formal, consistent style).

---

## Resolved Issues

None yet.

---

**Last Updated:** March 20, 2026
