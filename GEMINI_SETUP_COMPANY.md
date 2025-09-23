# Setting Up Gemini API on Company Google Account

## Step-by-Step Guide for Company Account Setup with Separate Billing

### Prerequisites
- Admin access to your company Google Workspace account
- Ability to create new Google Cloud projects
- Access to company billing information

---

## Step 1: Create a Dedicated Google Cloud Project

1. **Log into your company Google account**
   - Use your company email (e.g., yourname@company.com)
   - Make sure you're NOT logged into your personal account

2. **Go to Google Cloud Console**
   - Navigate to: https://console.cloud.google.com
   - You should see your company's organization at the top

3. **Create a new project specifically for the trading bot**
   ```
   Click "Select a project" dropdown → "NEW PROJECT"

   Project name: btc-trading-bot-prod (or similar)
   Organization: [Your Company]
   Location: [Your Company Folder/Organization]

   Click "CREATE"
   ```

---

## Step 2: Set Up Separate Billing Account

This ensures costs are tracked separately from other company projects:

1. **Navigate to Billing**
   ```
   Menu (☰) → Billing → Manage billing accounts
   ```

2. **Create a new billing sub-account** (recommended for cost tracking)
   ```
   Click "CREATE ACCOUNT" or "Add billing account"

   Account name: Trading Bot - AI Services
   Country: [Your Country]
   Currency: USD (or your preference)
   ```

3. **Add payment method**
   - Use a company credit card designated for this project
   - Or use the main company payment method if sub-accounts aren't needed

4. **Link the billing account to your project**
   ```
   Go to: Menu → Billing → Link a billing account
   Select: "Trading Bot - AI Services" (or your main company billing)
   Click: "SET ACCOUNT"
   ```

---

## Step 3: Enable Gemini API (Generative AI)

1. **Enable the API**
   ```
   Menu → APIs & Services → Library
   Search: "Generative Language API" or "Gemini"
   Click on: Generative Language API
   Click: "ENABLE"
   ```

2. **Wait for API activation** (usually instant, but can take 2-3 minutes)

---

## Step 4: Create API Credentials

1. **Generate API Key**
   ```
   Menu → APIs & Services → Credentials
   Click: "+ CREATE CREDENTIALS" → "API key"
   ```

2. **Secure the API key immediately**
   ```
   Click: "RESTRICT KEY" (important!)

   Application restrictions:
   - None (for server use)

   API restrictions:
   - Select: "Restrict key"
   - Choose: "Generative Language API"

   Click: "SAVE"
   ```

3. **Copy your API key**
   - Copy the key immediately
   - Store it securely

---

## Step 5: Configure Quotas (Important!)

Since your company account has payment history, you should get higher quotas automatically, but let's verify:

1. **Check current quotas**
   ```
   Menu → APIs & Services → Quotas
   Filter: Generative Language API
   ```

2. **Look for these quotas:**
   - `Generate content requests per minute` - Should be 1000+ for paid
   - `Generate content requests per day` - Should be 100,000+ for paid

3. **If quotas are still low, request increase:**
   ```
   Click on the quota name
   Click: "EDIT QUOTAS"
   Enter new limit: 10000 (or desired amount)
   Provide justification: "Production trading bot requiring real-time market analysis"
   Click: "SUBMIT REQUEST"
   ```

---

## Step 6: Set Up Budget Alerts (Recommended)

Prevent unexpected charges:

1. **Create a budget**
   ```
   Menu → Billing → Budgets & alerts
   Click: "CREATE BUDGET"

   Name: Trading Bot AI Budget
   Projects: Select your btc-trading-bot-prod project
   Services: All services (or specifically Generative Language API)
   ```

2. **Set budget amount**
   ```
   Budget type: Specified amount
   Target amount: $100/month (adjust as needed)

   Alert thresholds:
   - 50% ($50)
   - 90% ($90)
   - 100% ($100)

   Email alerts to: your-email@company.com
   ```

---

## Step 7: Update Your Bot Configuration

1. **Update the .env file on your local machine:**
   ```bash
   # Replace with your new company API key
   GEMINI_API_KEY=your-new-company-api-key-here
   ```

2. **Test the new API key locally:**
   ```bash
   cd /Users/benorbe/Documents/Coding\ Projects/btc-bot
   python verify_gemini_quota.py
   ```

3. **If successful, update on VPS:**
   ```bash
   # SSH to VPS
   ssh root@5.223.55.219

   # Update .env file
   nano /root/trading/btc-bot/.env
   # Replace GEMINI_API_KEY with new one

   # Restart the AI lab
   pkill -f ai_trading_lab_enhanced.py
   python ai_trading_lab_enhanced.py &
   ```

---

## Step 8: Verify Everything Works

1. **Check API usage in Google Cloud Console**
   ```
   Menu → APIs & Services → Metrics
   Select: Generative Language API

   You should see requests coming through
   ```

2. **Monitor initial costs**
   ```
   Menu → Billing → Reports
   Filter by: Project = btc-trading-bot-prod

   Gemini 2.5 Flash costs:
   - $0.075 per 1M input tokens
   - $0.30 per 1M output tokens
   - Very affordable for your use case
   ```

---

## Troubleshooting

### If you still see quota errors:

1. **Verify billing is active:**
   ```
   Menu → Billing → Overview
   Status should show: "Active"
   ```

2. **Check organization policies:**
   - Some company accounts have org-level restrictions
   - Contact your Google Workspace admin if needed

3. **Wait for propagation:**
   - New billing accounts can take 15-30 minutes to fully activate
   - Quota increases can take up to 24 hours

### If you need to track costs separately:

1. **Use labels for cost allocation:**
   ```
   Menu → Billing → Reports
   Click: "Configure labels"
   Add label: project=trading-bot
   ```

2. **Export billing data:**
   ```
   Menu → Billing → Billing export
   Set up BigQuery export for detailed analysis
   ```

---

## Security Best Practices

1. **Never commit the API key to git**
   - Keep it in .env file only
   - .env is already in .gitignore

2. **Rotate keys periodically**
   - Every 3-6 months
   - Immediately if exposed

3. **Monitor usage regularly**
   - Set up alerts for unusual activity
   - Review logs weekly

4. **Use service accounts for production** (optional but recommended)
   - More secure than API keys
   - Better for automation

---

## Expected Quotas with Company Account

With your company's established billing history, you should get:

- **Requests per minute**: 1,000-10,000
- **Requests per day**: 100,000-1,000,000
- **No throttling** for normal usage
- **Priority support** if issues arise

This is MORE than enough for your trading bot which makes ~720 requests/day (1 per 2 minutes).

---

## Next Steps After Setup

1. Test the new API key with verify_gemini_quota.py
2. Update both local and VPS environments
3. Monitor for 24 hours to ensure no quota issues
4. Set up billing alerts to track costs
5. Document the API key securely in your company's password manager

---

## Cost Estimation

For your trading bot running 24/7:
- ~720 API calls/day
- ~21,600 calls/month
- Estimated cost: $5-20/month (depending on prompt complexity)

This is negligible compared to your company's existing Google Cloud spending.