# Databricks Churn Risk Tracker - Setup Guide

This guide shows you how to use the Churn Risk Tracker in Databricks with Delta Lake tables.

## 🎯 Why Databricks?

The Databricks version is **significantly better** for managing 2000+ renewals:

| Feature | CLI Version | Databricks Version |
|---------|-------------|-------------------|
| **Collaboration** | Single user (shared file) | ✅ Multiple users simultaneously |
| **Scalability** | Good for 100s | ✅ Excellent for 1000s+ |
| **Visualizations** | Text-based | ✅ Rich charts and graphs |
| **Data Integration** | Manual import | ✅ Connect to CRM, data warehouse |
| **Performance** | SQLite | ✅ Spark + Delta Lake |
| **Scheduling** | Manual cron | ✅ Built-in job scheduler |
| **Sharing Reports** | Export files | ✅ Share notebooks, dashboards |
| **Version Control** | Git commits | ✅ Git + notebook versioning |

## 📥 Setup Instructions

### Step 1: Import the Notebook (5 minutes)

1. **Download the notebook file:**
   - File: `databricks_churn_tracker.py`

2. **Import into Databricks:**
   - Go to your Databricks workspace
   - Click **Workspace** → **Users** → **[Your Name]**
   - Click **⋮** (menu) → **Import**
   - Select the file: `databricks_churn_tracker.py`
   - Click **Import**

3. **Attach to a cluster:**
   - Open the imported notebook
   - Click the cluster dropdown at the top
   - Select an existing cluster or create a new one
   - Any cluster works - even the smallest size is fine

### Step 2: Initialize Tables (2 minutes)

1. **Run Setup Cells:**
   - Find section **"1. Setup - Initialize Delta Lake Tables"**
   - Click **Run All** for that section
   - You should see: ✓ Created clients table, etc.

2. **Verify Tables Created:**
   ```sql
   %sql
   SHOW TABLES IN churn_tracker;
   ```

   You should see:
   - clients
   - issues
   - actions
   - weekly_reviews

### Step 3: Load Example Data (1 minute)

1. **Find section "4. Load Example Data"**

2. **Run the cell:**
   ```python
   load_example_data()
   ```

3. **View the dashboard:**
   ```python
   show_dashboard()
   ```

You should see 5 example clients with issues, actions, and reviews!

### Step 4: Explore the Features (5 minutes)

**View All Clients:**
```python
list_clients()
```

**Filter by Risk:**
```python
list_clients(risk_level="High")
```

**View Client Details:**
```python
tracker.view_client("HF-2024-001")
```

**Generate Weekly Report:**
```python
weekly_report()
```

**Create Visualizations:**
```python
visualize_risk_by_value()
visualize_renewal_timeline()
```

## 🚀 Daily Workflow in Databricks

### Every Morning (5 minutes)

Open your notebook and run:

```python
# Quick dashboard check
show_dashboard()

# High-risk clients
list_clients(risk_level="High", status="At Risk")

# Upcoming renewals
list_clients(days_to_renewal=30)
```

### Every Monday (30-60 minutes)

```python
# Generate weekly report
weekly_report()
```

Then for each high-priority client:

```python
# Add weekly review
tracker.add_weekly_review(
    account_id="CLIENT-ID",
    summary="What happened this week",
    progress_status="Current status and improvements",
    next_steps="Actions for next week",
    reviewed_by="Your Name"
)

# Update completed actions
tracker.update_action(action_id=123, status="Completed")

# Add new actions as needed
tracker.add_action(
    account_id="CLIENT-ID",
    action_type="Meeting",
    description="Follow-up call scheduled",
    owner="Team Member",
    due_date="2026-02-01"
)
```

### Adding New At-Risk Clients

```python
# Add the client
tracker.add_client(
    name="Client Name",
    account_id="UNIQUE-ID",
    contract_value=250000,
    renewal_date="2026-06-30",
    risk_level="High",
    account_owner="Account Manager Name",
    notes="Context about why they're at risk"
)

# Document issues
tracker.add_issue(
    account_id="UNIQUE-ID",
    description="Main issue causing churn risk",
    category="Product",
    severity="Critical"
)

tracker.add_issue(
    account_id="UNIQUE-ID",
    description="Secondary concern",
    category="Pricing",
    severity="High"
)

# Create action plan
tracker.add_action(
    account_id="UNIQUE-ID",
    action_type="Meeting",
    description="Executive escalation meeting",
    owner="Sales Leader",
    due_date="2026-01-30"
)
```

### Updating Client Status

```python
# Update risk level
tracker.update_client("CLIENT-ID", risk_level="Medium")

# Update status
tracker.update_client("CLIENT-ID", status="In Progress")

# Update multiple fields
tracker.update_client(
    "CLIENT-ID",
    risk_level="Low",
    status="Resolved",
    notes="Issues resolved, client satisfied"
)
```

## 📊 Creating Dashboards

Databricks makes it easy to create shareable dashboards:

### Method 1: SQL Dashboards

1. Create a new SQL query:
   ```sql
   SELECT
       risk_level,
       status,
       COUNT(*) as client_count,
       SUM(contract_value) as total_value
   FROM churn_tracker.clients
   GROUP BY risk_level, status
   ```

2. Click **Add Visualization**
3. Choose chart type (bar, pie, etc.)
4. Click **Add to Dashboard** → **Create New Dashboard**

### Method 2: Notebook Dashboards

1. In your notebook, click **View** → **Dashboard**
2. Arrange cells with visualizations
3. Hide code, show only outputs
4. Share the dashboard link with your team

### Recommended Visualizations

**Executive Dashboard:**
- Total at-risk value by risk level (bar chart)
- Renewal timeline next 6 months (line chart)
- Status breakdown (pie chart)
- Top 10 at-risk clients by value (table)

**Operations Dashboard:**
- Clients needing review this week (table)
- Overdue actions by owner (table)
- Open issues by category (bar chart)
- Action completion rate (gauge)

## 🔄 Bulk Import Your Real Data

### Method 1: From CSV File

Upload your CSV to DBFS, then:

```python
# Import from CSV
import_from_csv("/dbfs/FileStore/my_clients.csv")
```

CSV format:
```csv
name,account_id,contract_value,renewal_date,risk_level,account_owner,notes
Acme Corp,ACME-001,250000,2026-06-15,High,Sarah Johnson,Budget concerns
```

### Method 2: From Existing Databricks Table

If you have client data in another table:

```python
# Direct import with column mapping
import_from_table(
    "salesforce.accounts",
    column_mapping={
        'account_name': 'name',
        'sfdc_id': 'account_id',
        'arr': 'contract_value',
        'renewal_date': 'renewal_date',
        'health_score': 'risk_level'  # You'll need to map scores to High/Medium/Low
    }
)
```

### Method 3: From CRM/Data Warehouse

```python
# Example: Import from Salesforce via Databricks connector
sf_accounts = spark.table("salesforce.at_risk_accounts")

# Transform to match our schema
clients_df = sf_accounts.select(
    col("Name").alias("name"),
    col("AccountId").alias("account_id"),
    col("ARR__c").alias("contract_value"),
    col("RenewalDate__c").alias("renewal_date"),
    when(col("HealthScore__c") < 40, "High")
        .when(col("HealthScore__c") < 70, "Medium")
        .otherwise("Low").alias("risk_level"),
    col("AccountOwner").alias("account_owner"),
    col("ChurnReason__c").alias("notes")
)

# Import
import_from_dataframe(clients_df, source_name="Salesforce")
```

### Method 4: Incremental Sync

Set up a scheduled job to sync new at-risk clients daily:

```python
def sync_from_crm():
    """Daily sync of at-risk accounts from CRM"""

    # Get existing account IDs
    existing = spark.table("churn_tracker.clients").select("account_id")

    # Get current at-risk accounts from CRM
    crm_at_risk = spark.table("salesforce.at_risk_accounts")

    # Find new at-risk accounts
    new_at_risk = crm_at_risk.join(
        existing,
        crm_at_risk.AccountId == existing.account_id,
        "left_anti"
    )

    # Transform and import
    if new_at_risk.count() > 0:
        # Transform to our schema
        clients_df = transform_crm_data(new_at_risk)

        # Import
        count = import_from_dataframe(clients_df, source_name="CRM Daily Sync")

        print(f"✓ Synced {count} new at-risk clients from CRM")
    else:
        print("No new at-risk clients today")

# Schedule this to run daily
```

## ⏰ Automated Weekly Reports

Set up a Databricks Job to send weekly reports automatically:

### Setup Instructions:

1. **Create a Job:**
   - Go to **Workflows** → **Create Job**
   - Name: "Weekly Churn Risk Report"

2. **Configure Task:**
   - Task type: Notebook
   - Notebook path: /Users/[your-email]/databricks_churn_tracker
   - Cluster: Choose existing or create new

3. **Add Parameters (optional):**
   ```json
   {
     "week_offset": 0,
     "send_email": true
   }
   ```

4. **Set Schedule:**
   - Cron: `0 9 * * 1` (Every Monday at 9am)
   - Or use UI: "Weekly on Monday at 9:00 AM"

5. **Configure Email Notifications:**
   - On Success: Send email to your team
   - Attach report output

6. **Create Email Report Cell:**

```python
# Add this cell to your notebook
def generate_email_report():
    """Generate formatted report for email"""

    print("="*80)
    print("WEEKLY CHURN RISK REPORT")
    print("="*80)

    # Run weekly report
    weekly_report()

    # Export high-risk clients to CSV for attachment
    high_risk = spark.sql("""
        SELECT
            name,
            account_id,
            contract_value,
            renewal_date,
            account_owner,
            datediff(renewal_date, current_date()) as days_to_renewal
        FROM churn_tracker.clients
        WHERE risk_level = 'High'
        AND status IN ('At Risk', 'In Progress')
        ORDER BY renewal_date
    """)

    # Save for email attachment
    output_path = "/dbfs/FileStore/reports/weekly_high_risk.csv"
    high_risk.coalesce(1).write.mode("overwrite").csv(output_path, header=True)

    print(f"\n✓ Report saved to: {output_path}")

# Run when job executes
# generate_email_report()
```

## 🔐 Access Control & Collaboration

### Share with Your Team:

1. **Share the Notebook:**
   - Click **Permissions** button in notebook
   - Add team members with "Can Run" or "Can Edit" permissions

2. **Share the Dashboard:**
   - Create dashboard from notebook
   - Share dashboard link (read-only)
   - Team can view live data without editing

3. **Table Permissions:**
   ```sql
   -- Grant read access to renewals team
   GRANT SELECT ON DATABASE churn_tracker TO `renewals_team`;

   -- Grant write access to managers
   GRANT ALL PRIVILEGES ON DATABASE churn_tracker TO `renewals_managers`;
   ```

### Multi-User Best Practices:

- **Use account_owner field** to assign clients to team members
- **Filter by owner** for individual views:
  ```python
  list_clients(status="At Risk")  # Filter in SQL by account_owner
  ```

- **Weekly review workflow:**
  - Each manager reviews their clients
  - Updates tracked by `reviewed_by` field
  - Central dashboard shows overall progress

## 📈 Advanced Analytics

### Churn Prediction Analysis:

```python
# Analyze patterns in churned clients
churned_analysis = spark.sql("""
    SELECT
        risk_level,
        AVG(contract_value) as avg_contract_value,
        COUNT(*) as churned_count,
        COLLECT_LIST(account_id) as churned_accounts
    FROM churn_tracker.clients
    WHERE status = 'Churned'
    GROUP BY risk_level
""")

display(churned_analysis)
```

### Success Metrics:

```python
# Track your save rate over time
success_metrics = spark.sql("""
    SELECT
        DATE_TRUNC('month', last_updated) as month,
        COUNT(CASE WHEN status = 'Renewed' THEN 1 END) as saved,
        COUNT(CASE WHEN status = 'Churned' THEN 1 END) as lost,
        ROUND(100.0 * COUNT(CASE WHEN status = 'Renewed' THEN 1 END) /
              NULLIF(COUNT(*), 0), 2) as save_rate_pct,
        SUM(CASE WHEN status = 'Renewed' THEN contract_value END) as revenue_saved,
        SUM(CASE WHEN status = 'Churned' THEN contract_value END) as revenue_lost
    FROM churn_tracker.clients
    WHERE status IN ('Renewed', 'Churned')
    GROUP BY month
    ORDER BY month DESC
""")

display(success_metrics)
```

### Team Performance:

```python
# Track account owner performance
owner_performance = spark.sql("""
    SELECT
        account_owner,
        COUNT(*) as total_clients,
        COUNT(CASE WHEN status = 'Renewed' THEN 1 END) as wins,
        COUNT(CASE WHEN status = 'Churned' THEN 1 END) as losses,
        ROUND(100.0 * COUNT(CASE WHEN status = 'Renewed' THEN 1 END) /
              NULLIF(COUNT(CASE WHEN status IN ('Renewed', 'Churned') THEN 1 END), 0), 2) as win_rate_pct
    FROM churn_tracker.clients
    WHERE account_owner != ''
    GROUP BY account_owner
    ORDER BY total_clients DESC
""")

display(owner_performance)
```

## 🛠 Maintenance & Backups

### Backup Your Data:

```python
# Export all data to cloud storage
backup_path = "s3://your-bucket/churn-tracker-backup/"

# Backup all tables
for table in ["clients", "issues", "actions", "weekly_reviews"]:
    spark.table(f"churn_tracker.{table}").write.mode("overwrite").parquet(f"{backup_path}{table}")

print("✓ Backup completed")
```

### Archive Old Clients:

```python
# Move old resolved/churned clients to archive
spark.sql("""
    CREATE TABLE IF NOT EXISTS churn_tracker.clients_archive
    USING DELTA
    AS SELECT * FROM churn_tracker.clients WHERE 1=0
""")

spark.sql("""
    INSERT INTO churn_tracker.clients_archive
    SELECT * FROM churn_tracker.clients
    WHERE status IN ('Renewed', 'Churned')
    AND last_updated < date_sub(current_date(), 90)
""")

spark.sql("""
    DELETE FROM churn_tracker.clients
    WHERE status IN ('Renewed', 'Churned')
    AND last_updated < date_sub(current_date(), 90)
""")
```

### Optimize Tables:

```python
# Run monthly to optimize Delta Lake tables
spark.sql("OPTIMIZE churn_tracker.clients")
spark.sql("OPTIMIZE churn_tracker.actions")
spark.sql("OPTIMIZE churn_tracker.issues")
spark.sql("OPTIMIZE churn_tracker.weekly_reviews")

print("✓ Tables optimized")
```

## 💡 Tips for Managing 2000+ Renewals

### 1. Use Partitioning for Performance

```sql
-- Recreate clients table with partitioning by renewal month
CREATE TABLE churn_tracker.clients_partitioned
USING DELTA
PARTITIONED BY (renewal_month)
AS
SELECT
    *,
    DATE_TRUNC('month', renewal_date) as renewal_month
FROM churn_tracker.clients
```

### 2. Create Materialized Views

```python
# Create aggregated view for faster dashboard
spark.sql("""
    CREATE OR REPLACE VIEW churn_tracker.dashboard_summary AS
    SELECT
        risk_level,
        status,
        COUNT(*) as client_count,
        SUM(contract_value) as total_value,
        AVG(contract_value) as avg_value
    FROM churn_tracker.clients
    GROUP BY risk_level, status
""")
```

### 3. Set Up Alerts

```python
# Alert on high-value clients at risk
high_value_alerts = spark.sql("""
    SELECT * FROM churn_tracker.clients
    WHERE contract_value > 500000
    AND risk_level = 'High'
    AND status = 'At Risk'
""")

if high_value_alerts.count() > 0:
    print("⚠️  ALERT: High-value clients at risk!")
    display(high_value_alerts)
```

## 🎓 Training Your Team

### Quick Start for Team Members:

1. Share the notebook (read-only)
2. Show them the key cells:
   - Dashboard view
   - Their clients filter
   - How to add weekly reviews

### For Managers:

Give edit access and train on:
- Adding new at-risk clients
- Updating client status
- Running weekly reports
- Creating custom filters

### For Executives:

Share dashboard with:
- Overall metrics
- High-risk client list
- Save/churn rates
- Team performance

## ❓ FAQ

**Q: Can I use this with the CLI version?**
A: Yes! Both use similar data models. You can export from CLI and import to Databricks.

**Q: What if I already have client data in Salesforce?**
A: Use the bulk import functions to sync from your CRM. Set up daily sync job.

**Q: How do I share reports with executives who don't use Databricks?**
A: Create a SQL dashboard and share the public link, or schedule email reports.

**Q: Can multiple people edit the same client?**
A: Yes! Delta Lake handles concurrent writes. Last update wins.

**Q: How do I migrate from CLI to Databricks?**
A: Export CLI data to JSON, convert to DataFrame, import using `import_from_dataframe()`.

**Q: What's the cost?**
A: Depends on your Databricks plan. For 2000 clients, very minimal compute/storage costs.

## 🎉 You're Ready!

The Databricks version gives you:
- ✅ Scalability for 2000+ renewals
- ✅ Team collaboration
- ✅ Automated reports
- ✅ Rich visualizations
- ✅ Data integration

Start with the example data, then import your real clients and start tracking systematically!

---

**Need help?** Check the notebook documentation or reach out to your Databricks admin.
