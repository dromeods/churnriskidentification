# Churn Risk Tracker

A powerful tool for managing and tracking client renewal risks at scale. Perfect for renewal teams managing hundreds or thousands of at-risk clients.

**Available in two versions:**
- **CLI Version** (this file) - Simple command-line tool with local SQLite database
- **Databricks Version** - Enterprise-grade solution with Delta Lake, visualizations, and team collaboration

👉 **For 2000+ renewals, we recommend the [Databricks version](DATABRICKS_GUIDE.md)** for better scalability, collaboration, and automation.

---

## 🎯 What This Solves

As a renewals leader managing 2000+ clients, you need:
- ✅ **Systematic documentation** of at-risk clients
- ✅ **Action item tracking** for each client
- ✅ **Weekly review workflow** to monitor progress
- ✅ **Dashboard visibility** into all renewals
- ✅ **Risk prioritization** to focus on high-value accounts

This tool provides all of that through a simple command-line interface with a local database.

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**

2. **Make the script executable:**
```bash
chmod +x churn_tracker.py
```

3. **Run your first command:**
```bash
python3 churn_tracker.py dashboard
```

That's it! The database will be created automatically on first use.

### Basic Workflow

**1. Add at-risk clients:**
```bash
python3 churn_tracker.py add-client \
  --name "Acme Healthcare" \
  --account-id "ACME-001" \
  --value 250000 \
  --renewal-date "2026-03-15" \
  --risk High \
  --owner "Sarah Johnson" \
  --notes "Concerned about recent product issues"
```

**2. Document issues:**
```bash
python3 churn_tracker.py add-issue ACME-001 \
  --description "Experiencing slow report generation times" \
  --category "Performance" \
  --severity High
```

**3. Track action items:**
```bash
python3 churn_tracker.py add-action ACME-001 \
  --type Meeting \
  --description "Executive escalation call with CTO" \
  --owner "Sarah Johnson" \
  --due "2026-01-20"
```

**4. View client details:**
```bash
python3 churn_tracker.py view ACME-001
```

**5. Check your dashboard:**
```bash
python3 churn_tracker.py dashboard
```

**6. Generate weekly report:**
```bash
python3 churn_tracker.py weekly-report
```

## 📚 Complete Command Reference

### Client Management

**Add a new at-risk client:**
```bash
python3 churn_tracker.py add-client \
  --name "Client Name" \
  --account-id "UNIQUE-ID" \
  --value 100000 \
  --renewal-date "2026-06-30" \
  --risk [High|Medium|Low] \
  --status "At Risk" \
  --owner "Account Manager Name" \
  --notes "Any relevant context"
```

**Update existing client:**
```bash
python3 churn_tracker.py update-client ACCOUNT-ID \
  --risk High \
  --status "In Progress" \
  --notes "Updated status after call"
```

**List all clients:**
```bash
python3 churn_tracker.py list
```

**Filter by risk level:**
```bash
python3 churn_tracker.py list --risk High
```

**Filter by status:**
```bash
python3 churn_tracker.py list --status "At Risk"
```

**Show clients renewing in next 30 days:**
```bash
python3 churn_tracker.py list --days 30
```

**View detailed client information:**
```bash
python3 churn_tracker.py view ACCOUNT-ID
```

### Issue Tracking

**Add an issue:**
```bash
python3 churn_tracker.py add-issue ACCOUNT-ID \
  --description "Description of the issue" \
  --category "Product|Support|Pricing|Other" \
  --severity [Critical|High|Medium|Low]
```

### Action Items

**Add an action item:**
```bash
python3 churn_tracker.py add-action ACCOUNT-ID \
  --type [Call|Email|Meeting|Escalation|Follow-up|Other] \
  --description "What needs to be done" \
  --owner "Person responsible" \
  --status [Pending|In Progress|Completed|Blocked] \
  --due "2026-01-30"
```

**Update action status:**
```bash
python3 churn_tracker.py update-action ACTION-ID --status Completed
```

### Weekly Reviews

**Add a weekly review:**
```bash
python3 churn_tracker.py add-review ACCOUNT-ID \
  --summary "This week's progress summary" \
  --progress "Status update" \
  --next-steps "What we'll do next week" \
  --reviewed-by "Your Name"
```

### Reports & Analytics

**Dashboard overview:**
```bash
python3 churn_tracker.py dashboard
```

Shows:
- Overall status breakdown
- Risk level distribution
- Upcoming renewals (30 days)
- Action item summary
- Open issues count

**Weekly report:**
```bash
python3 churn_tracker.py weekly-report
```

Shows:
- High-risk clients requiring attention
- Clients needing weekly review
- Completed actions this week
- Pending/overdue actions

**Previous week's report:**
```bash
python3 churn_tracker.py weekly-report --week-offset -1
```

**Export data to JSON:**
```bash
python3 churn_tracker.py export --output my_export.json
```

## 💡 Recommended Workflow for Managing 2000+ Renewals

### Daily Routine (5-10 minutes)

1. **Check dashboard for overview:**
```bash
python3 churn_tracker.py dashboard
```

2. **Review high-risk clients:**
```bash
python3 churn_tracker.py list --risk High --status "At Risk"
```

3. **Check clients renewing soon:**
```bash
python3 churn_tracker.py list --days 30
```

### Weekly Review (30-60 minutes)

1. **Generate weekly report:**
```bash
python3 churn_tracker.py weekly-report
```

2. **For each high-risk client, add weekly review:**
```bash
python3 churn_tracker.py add-review ACCOUNT-ID \
  --summary "Progress this week" \
  --progress "Current status" \
  --next-steps "Actions for next week"
```

3. **Update action items:**
```bash
python3 churn_tracker.py update-action ACTION-ID --status Completed
```

4. **Add new actions as needed:**
```bash
python3 churn_tracker.py add-action ACCOUNT-ID --type Follow-up --description "..."
```

### When Adding New At-Risk Clients

1. **Add the client with all details:**
```bash
python3 churn_tracker.py add-client --name "..." --account-id "..." --value ... --renewal-date "..." --risk High
```

2. **Document all known issues:**
```bash
python3 churn_tracker.py add-issue ACCOUNT-ID --description "..." --severity High
python3 churn_tracker.py add-issue ACCOUNT-ID --description "..." --severity Medium
```

3. **Create initial action plan:**
```bash
python3 churn_tracker.py add-action ACCOUNT-ID --type Call --description "Initial assessment call"
python3 churn_tracker.py add-action ACCOUNT-ID --type Meeting --description "Stakeholder meeting"
```

### When Client Status Changes

**Client shows improvement:**
```bash
python3 churn_tracker.py update-client ACCOUNT-ID --status "In Progress" --risk Medium
```

**Issue resolved:**
```bash
python3 churn_tracker.py update-client ACCOUNT-ID --status Resolved
```

**Client churned:**
```bash
python3 churn_tracker.py update-client ACCOUNT-ID --status Churned
```

**Client renewed:**
```bash
python3 churn_tracker.py update-client ACCOUNT-ID --status Renewed
```

## 📊 Data Structure

The tool uses SQLite database with four main tables:

### Clients
- Basic info (name, account ID, contract value)
- Renewal date
- Risk level (High/Medium/Low)
- Status (At Risk/In Progress/Resolved/Churned/Renewed)
- Account owner
- Notes

### Issues
- Issue description
- Category and severity
- Status tracking
- Resolution notes

### Actions
- Action type (Call, Email, Meeting, etc.)
- Description and owner
- Status and due dates
- Completion tracking

### Weekly Reviews
- Weekly summary
- Progress status
- Next steps
- Review history

## 🔧 Advanced Usage

### Bulk Import

You can import clients from a CSV file using a simple Python script:

```python
import csv
import subprocess

with open('clients.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cmd = [
            'python3', 'churn_tracker.py', 'add-client',
            '--name', row['name'],
            '--account-id', row['account_id'],
            '--value', row['value'],
            '--renewal-date', row['renewal_date'],
            '--risk', row['risk'],
            '--owner', row.get('owner', '')
        ]
        subprocess.run(cmd)
```

### Integration with Other Tools

**Export to spreadsheet for executive review:**
```bash
python3 churn_tracker.py export --output weekly_export.json
# Then import JSON into Google Sheets/Excel
```

**Automated weekly reports via cron:**
```bash
# Add to crontab for Monday 9am reports
0 9 * * 1 cd /path/to/tracker && python3 churn_tracker.py weekly-report > weekly_report_$(date +\%Y\%m\%d).txt
```

### Multiple Team Members

The database file `churn_tracker.db` can be:
- Stored in a shared folder (Dropbox, Google Drive)
- Committed to a private Git repository
- Synced via any file sync service

Just ensure only one person edits at a time to avoid conflicts.

## 📈 Tips for Scale (2000+ Clients)

1. **Prioritize ruthlessly** - Focus on high-risk, high-value accounts first
2. **Use filters heavily** - Don't try to view all 2000 at once
3. **Automate weekly reviews** - Set aside dedicated time blocks
4. **Delegate with owners** - Assign account owners and track their progress
5. **Track patterns** - Use export feature to analyze common issues
6. **Regular cleanup** - Move resolved/renewed clients to appropriate status

## ❓ FAQ

**Q: Can multiple people use this simultaneously?**
A: Yes, but they need to share the database file. Consider using Git or cloud sync.

**Q: How do I back up my data?**
A: Simply copy the `churn_tracker.db` file. You can also use `export` command.

**Q: Can I run this on Windows?**
A: Yes! Python 3 works on Windows. Just use `python churn_tracker.py` instead of `python3`.

**Q: Do I need to install anything?**
A: No! It uses only Python standard library (included with Python 3).

**Q: How do I find an action ID to update it?**
A: Use `view ACCOUNT-ID` to see all actions with their IDs.

**Q: Can I delete clients or actions?**
A: Not via CLI currently. You can connect to the SQLite DB directly or update status to "Churned" to hide them.

## 🆘 Getting Help

For issues or questions:
1. Check the command help: `python3 churn_tracker.py COMMAND --help`
2. Review this README
3. Check the example usage below

## 📝 Example Session

Here's a complete example workflow:

```bash
# Monday morning - check your dashboard
python3 churn_tracker.py dashboard

# Add a new at-risk client
python3 churn_tracker.py add-client \
  --name "HealthTech Solutions" \
  --account-id "HTS-2024-156" \
  --value 500000 \
  --renewal-date "2026-04-15" \
  --risk High \
  --owner "Mike Chen" \
  --notes "CFO expressed budget concerns"

# Document the issues
python3 churn_tracker.py add-issue HTS-2024-156 \
  --description "Budget constraints due to company restructuring" \
  --category "Commercial" \
  --severity Critical

python3 churn_tracker.py add-issue HTS-2024-156 \
  --description "Low user adoption in East region" \
  --category "Product" \
  --severity High

# Create action plan
python3 churn_tracker.py add-action HTS-2024-156 \
  --type Meeting \
  --description "Executive business review with CFO and CTO" \
  --owner "Mike Chen" \
  --due "2026-01-25"

python3 churn_tracker.py add-action HTS-2024-156 \
  --type Call \
  --description "Call with East region manager to discuss adoption" \
  --owner "Sarah Park" \
  --due "2026-01-22"

# View the complete client profile
python3 churn_tracker.py view HTS-2024-156

# A week later - update progress
python3 churn_tracker.py add-review HTS-2024-156 \
  --summary "Had productive call with regional manager. Identified training gap." \
  --progress "Making progress on user adoption. Budget still uncertain." \
  --next-steps "Executive meeting scheduled. Prepare ROI analysis."

python3 churn_tracker.py update-action 1 --status Completed

# Check who needs attention this week
python3 churn_tracker.py weekly-report

# Filter to see just high-risk cases
python3 churn_tracker.py list --risk High

# Export for executive review
python3 churn_tracker.py export --output monthly_review.json
```

## 🎉 You're Ready!

Start tracking your at-risk renewals systematically. Good luck turning those accounts around!

---

## 🚀 Want More Power? Try Databricks!

For managing 2000+ renewals with your team, consider the **Databricks version**:

✅ **Better for scale** - Handle thousands of clients with Spark + Delta Lake
✅ **Better collaboration** - Multiple team members working simultaneously
✅ **Better visualizations** - Rich charts, graphs, and dashboards
✅ **Better automation** - Scheduled jobs, automated reports, email alerts
✅ **Better integration** - Connect to CRM, data warehouse, BI tools

**See [DATABRICKS_GUIDE.md](DATABRICKS_GUIDE.md) for full setup instructions.**

Migration is easy:
```bash
# Export from CLI
python3 churn_tracker.py export --output migration.json

# Import to Databricks (see guide)
# Takes just a few minutes!
```

---

**Pro tip:** Bookmark these key commands for daily use:
- `python3 churn_tracker.py dashboard`
- `python3 churn_tracker.py list --risk High`
- `python3 churn_tracker.py weekly-report`
