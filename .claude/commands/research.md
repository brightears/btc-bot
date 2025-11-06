# Research Checkpoint - Automated Market Analysis

Run the appropriate research analysis based on current date and previous reports.

## Your Task

**Determine what analysis to run:**

1. **Check today's date** and day of week
2. **Check what reports exist** in `research/market_regime/`
3. **Determine analysis frequency needed:**
   - **Daily**: If no report for today exists → run @binance-market-regime-analyst
   - **Weekly**: If today is Sunday (or 7+ days since last weekly check) → run weekly sprint
   - **Monthly**: If today is first Sunday of month → run full 5-agent analysis

## Analysis Types

### Daily (Default)
**Prompt for agent:**
```
Run daily market regime analysis for [TODAY'S DATE].

Analyze:
- Current BTC/USDT and ETH/USDT prices
- 30-day volatility metrics
- Market regime classification (Ranging/Trending/Low Vol/High Uncertainty)
- Deployment recommendation (Deploy/Wait/DCA)

Generate report: research/market_regime/YYYY-MM-DD.md

Be brutally honest. If conditions are bad for grid bots, say so clearly.
```

**Output to user:**
- Market regime status
- Deploy / Wait / DCA recommendation
- Key metrics (BTC price, volatility, trend)

### Weekly (Sundays or on request)
**Invoke multiple agents:**
1. @binance-market-regime-analyst: 7-day trend analysis
2. @binance-grid-optimizer: Optimal grid parameters (if ranging)
3. @binance-risk-guardian: Risk baseline

**Output to user:**
- Market regime (last 7 days)
- Grid bot parameters (if suitable)
- Risk assessment
- Deploy / Wait recommendation with specific parameters

### Monthly (First Sunday of month)
**Invoke ALL 5 agents:**
1. @binance-market-regime-analyst: 30-day comprehensive analysis
2. @binance-grid-optimizer: Full parameter optimization
3. @binance-portfolio-allocator: Allocation research (50/50 vs 60/40 vs 70/30)
4. @binance-bot-validator: Validate any proposed configurations
5. @binance-risk-guardian: Complete risk baseline

**Output to user:**
- Complete research report (all 5 dimensions)
- Portfolio allocation recommendation
- Deployment decision with full parameters
- Risk limits and stop-losses

## Decision Logic

```
IF today is first Sunday of month:
  → Run MONTHLY analysis (all 5 agents)

ELSE IF today is Sunday OR 7+ days since last weekly:
  → Run WEEKLY analysis (3 agents)

ELSE IF no report exists for today:
  → Run DAILY analysis (1 agent)

ELSE:
  → Show latest report summary + "Next checkpoint: [date]"
```

## Output Format

Always provide:
1. **Analysis Type**: Daily / Weekly / Monthly
2. **Market Regime**: Current classification
3. **Recommendation**: Deploy / Wait / DCA (with reasoning)
4. **Key Metrics**: BTC/ETH prices, volatility, trend
5. **Next Checkpoint**: When to run next analysis
6. **Action Items**: What user should do (if anything)

## Important Reminders

- Be brutally honest (we learned from Freqtrade failure)
- Never recommend deployment in trending markets
- Only suggest grid bots in ranging conditions
- Include risk warnings prominently
- Reference report file paths for details

## Context Awareness

Check these before running analysis:
- Date of last market regime report
- Current market conditions (from last report)
- Any major market events in news
- Time since last deployment recommendation

Use this context to provide smart, timely analysis.
