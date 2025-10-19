# Roadmap

## Future Vision: Adaptive Self-Optimizing Trading System

**Status:** Research complete, implementation planned for post-Oct 28 analysis

See [ADAPTIVE_TRADING_SYSTEM.md](ADAPTIVE_TRADING_SYSTEM.md) for full details.

**Quick Summary:**
- Auto-detect strategy degradation and pause underperforming live strategies
- Continuously discover new strategies (genetic algorithms or mining)
- 3 Live bots (real money) + 7 Testing bots (dry-run) with auto-rotation
- Monthly performance-based rotation between Live and Testing pools
- Incremental build: 6-8 months, 60-85 hours development time

**Why This Matters:**
- Protects capital by detecting failures within days (not weeks/months)
- Continuous R&D lab: 10-20 new strategies tested per month
- "Set it and forget it" operation with automated oversight
- Even 1 discovered strategy at 5-10% annual return pays for itself

**Next Steps (After Oct 28):**
1. Analyze current 6-bot test results
2. Pick top 3 strategies → designate as "Live" pool
3. Convert bottom 3 → "Testing" pool (dry-run mode)
4. Decision point: Start Phase 1 (auto-pause system, 2-3 weeks) or continue manual testing
5. Build incrementally over 6-8 months with validation at each phase

**VPS Upgrade Path:**
- Current: 4GB RAM, 6 bots, €13/month
- Phase 2: 8GB RAM, 10 bots (3 live + 7 test), €25/month
- Optional: 16GB RAM, 20 bots (3 live + 17 test), €45/month

---

## Current Roadmap (2025)

- [ ] Dry-run parity checks vs exchange data
- [ ] Simple hedge leg (optional)
- [ ] Daily PnL snapshot & weekly summary
- [ ] Backtest harness (subset of endpoints)
- [ ] Safety: per-symbol risk caps, kill switches
