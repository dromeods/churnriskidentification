# Quick Start Guide

Get up and running with Churn Risk Tracker in 5 minutes!

## Step 1: Test the Installation (30 seconds)

```bash
# Make the script executable
chmod +x churn_tracker.py

# Run your first command
python3 churn_tracker.py dashboard
```

You should see an empty dashboard. Perfect! The database was created automatically.

## Step 2: Try with Example Data (2 minutes)

Load realistic example data to explore the tool:

```bash
# Load example clients
python3 example_setup.py

# View the dashboard
python3 churn_tracker.py dashboard

# See all clients
python3 churn_tracker.py list

# View detailed info for one client
python3 churn_tracker.py view HF-2024-001

# Generate weekly report
python3 churn_tracker.py weekly-report
```

## Step 3: Add Your First Real Client (2 minutes)

Now add one of your actual at-risk clients:

```bash
python3 churn_tracker.py add-client \
  --name "YOUR CLIENT NAME" \
  --account-id "UNIQUE-ID-001" \
  --value 250000 \
  --renewal-date "2026-03-30" \
  --risk High \
  --owner "Your Name" \
  --notes "Brief context about the risk"
```

Document an issue:

```bash
python3 churn_tracker.py add-issue UNIQUE-ID-001 \
  --description "Main issue causing churn risk" \
  --severity High
```

Add an action item:

```bash
python3 churn_tracker.py add-action UNIQUE-ID-001 \
  --type Meeting \
  --description "Executive escalation call" \
  --owner "Your Name" \
  --due "2026-01-25"
```

View your client:

```bash
python3 churn_tracker.py view UNIQUE-ID-001
```

## Step 4: Daily Workflow

### Every Morning (5 minutes)

```bash
# Check high-risk clients
python3 churn_tracker.py list --risk High

# See upcoming renewals (next 30 days)
python3 churn_tracker.py list --days 30

# View dashboard
python3 churn_tracker.py dashboard
```

### Every Monday (30 minutes)

```bash
# Generate weekly report
python3 churn_tracker.py weekly-report

# For each high-priority client, add weekly review:
python3 churn_tracker.py add-review CLIENT-ID \
  --summary "What happened this week" \
  --progress "Current status" \
  --next-steps "What's next"

# Update completed actions
python3 churn_tracker.py update-action ACTION-ID --status Completed
```

### As Situations Change

```bash
# Update risk level
python3 churn_tracker.py update-client CLIENT-ID --risk Medium

# Update status
python3 churn_tracker.py update-client CLIENT-ID --status "In Progress"

# Add new action
python3 churn_tracker.py add-action CLIENT-ID \
  --type Call \
  --description "Follow-up call" \
  --due "2026-02-01"
```

## Step 5: Bulk Import (Optional)

If you have many clients to import:

```bash
# Create a CSV template
python3 bulk_import_template.py --create-template

# Edit import_template.csv with your data

# Import all clients
python3 bulk_import_template.py import_template.csv
```

## Key Commands to Remember

| What You Want | Command |
|--------------|---------|
| Overall view | `python3 churn_tracker.py dashboard` |
| High-risk clients | `python3 churn_tracker.py list --risk High` |
| Client details | `python3 churn_tracker.py view CLIENT-ID` |
| Weekly report | `python3 churn_tracker.py weekly-report` |
| Add client | `python3 churn_tracker.py add-client --name "..." --account-id "..." --value ... --renewal-date "..." --risk High` |
| Add action | `python3 churn_tracker.py add-action CLIENT-ID --type Meeting --description "..."` |
| Update status | `python3 churn_tracker.py update-client CLIENT-ID --status "In Progress"` |

## Pro Tips

1. **Use descriptive account IDs** - Make them easy to remember (e.g., "ACME-2024-001" not "12345")

2. **Filter aggressively** - Don't try to view all 2000 clients at once
   ```bash
   python3 churn_tracker.py list --risk High --status "At Risk"
   python3 churn_tracker.py list --days 30
   ```

3. **Set a weekly review time** - Block 30-60 minutes every Monday morning

4. **Export for presentations**
   ```bash
   python3 churn_tracker.py export --output weekly_export.json
   ```

5. **Bookmark key commands** - Save them in a text file for quick copy/paste

## Troubleshooting

**"Command not found"**
- Make sure you're in the churn risk tracker directory
- Use `python3` not `python`

**"No module named sqlite3"**
- Your Python installation is missing sqlite3 (rare)
- Try reinstalling Python or use a different Python version

**"Client already exists"**
- Each account_id must be unique
- Use `update-client` instead of `add-client`

**Want to start fresh?**
```bash
# Delete the database to start over
rm churn_tracker.db

# Database will be recreated on next command
python3 churn_tracker.py dashboard
```

## Next Steps

- Read the full [README.md](README.md) for complete documentation
- Set up bulk import if you have many existing at-risk clients
- Customize the workflow to match your team's process
- Consider syncing the database file to cloud storage for backup

---

**You're all set!** Start tracking those at-risk renewals systematically. 🎯
