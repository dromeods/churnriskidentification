# Databricks notebook source
# MAGIC %md
# MAGIC # Churn Risk Tracker - Databricks Edition
# MAGIC
# MAGIC A comprehensive system for tracking client renewal risks using Delta Lake tables.
# MAGIC
# MAGIC ## Quick Start
# MAGIC 1. Run the **Setup** section to initialize Delta Lake tables
# MAGIC 2. Run **Load Example Data** to see it in action
# MAGIC 3. Use the **Core Functions** to manage your renewals
# MAGIC
# MAGIC ## Key Features
# MAGIC - ✅ Track 2000+ at-risk renewals with Delta Lake
# MAGIC - ✅ Collaborative access for your entire team
# MAGIC - ✅ Rich visualizations and dashboards
# MAGIC - ✅ Integration with your data warehouse/CRM
# MAGIC - ✅ Automated weekly reports
# MAGIC - ✅ Action item tracking and progress monitoring

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup - Initialize Delta Lake Tables

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
from pyspark.sql.window import Window
import pandas as pd

# Initialize Spark session (already available in Databricks as 'spark')
# Set database name - change this to your preferred database
DATABASE_NAME = "churn_tracker"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
spark.sql(f"USE {DATABASE_NAME}")

print(f"✓ Using database: {DATABASE_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Define Table Schemas

# COMMAND ----------

# Create Clients table
spark.sql("""
CREATE TABLE IF NOT EXISTS clients (
    client_id BIGINT GENERATED ALWAYS AS IDENTITY,
    name STRING NOT NULL,
    account_id STRING NOT NULL,
    contract_value DECIMAL(12,2),
    renewal_date DATE,
    risk_level STRING,
    status STRING,
    account_owner STRING,
    notes STRING,
    created_date TIMESTAMP,
    last_updated TIMESTAMP
) USING DELTA
""")

# Add constraint for unique account_id (if not exists)
try:
    spark.sql("ALTER TABLE clients ADD CONSTRAINT unique_account_id UNIQUE(account_id)")
except:
    pass  # Constraint already exists

print("✓ Created clients table")

# COMMAND ----------

# Create Issues table
spark.sql("""
CREATE TABLE IF NOT EXISTS issues (
    issue_id BIGINT GENERATED ALWAYS AS IDENTITY,
    account_id STRING NOT NULL,
    issue_date TIMESTAMP,
    issue_category STRING,
    description STRING NOT NULL,
    severity STRING,
    status STRING,
    resolution STRING
) USING DELTA
""")

print("✓ Created issues table")

# COMMAND ----------

# Create Actions table
spark.sql("""
CREATE TABLE IF NOT EXISTS actions (
    action_id BIGINT GENERATED ALWAYS AS IDENTITY,
    account_id STRING NOT NULL,
    action_date TIMESTAMP,
    action_type STRING,
    description STRING NOT NULL,
    owner STRING,
    status STRING,
    due_date DATE,
    completed_date DATE
) USING DELTA
""")

print("✓ Created actions table")

# COMMAND ----------

# Create Weekly Reviews table
spark.sql("""
CREATE TABLE IF NOT EXISTS weekly_reviews (
    review_id BIGINT GENERATED ALWAYS AS IDENTITY,
    account_id STRING NOT NULL,
    week_start DATE,
    summary STRING,
    progress_status STRING,
    next_steps STRING,
    reviewed_by STRING,
    review_date TIMESTAMP
) USING DELTA
""")

print("✓ Created weekly_reviews table")
print("\n✅ All tables created successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Core Functions - Client Management

# COMMAND ----------

class ChurnTracker:
    """Main class for churn risk tracking in Databricks"""

    def __init__(self):
        self.database = DATABASE_NAME
        spark.sql(f"USE {self.database}")

    def add_client(self, name, account_id, contract_value, renewal_date,
                   risk_level, status="At Risk", account_owner="", notes=""):
        """Add a new at-risk client"""

        client_data = [(
            name,
            account_id,
            float(contract_value),
            renewal_date,
            risk_level,
            status,
            account_owner,
            notes,
            datetime.now(),
            datetime.now()
        )]

        columns = ["name", "account_id", "contract_value", "renewal_date",
                   "risk_level", "status", "account_owner", "notes",
                   "created_date", "last_updated"]

        df = spark.createDataFrame(client_data, columns)

        try:
            df.write.format("delta").mode("append").saveAsTable("clients")
            print(f"✓ Added client: {name} ({account_id})")
            return True
        except Exception as e:
            print(f"✗ Error adding client: {e}")
            return False

    def update_client(self, account_id, **kwargs):
        """Update client details"""

        allowed_fields = ['name', 'contract_value', 'renewal_date', 'risk_level',
                         'status', 'account_owner', 'notes']

        updates = []
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                if isinstance(value, str):
                    updates.append(f"{field} = '{value}'")
                else:
                    updates.append(f"{field} = {value}")

        if not updates:
            print("No valid fields to update")
            return

        updates.append(f"last_updated = current_timestamp()")
        update_clause = ", ".join(updates)

        spark.sql(f"""
            UPDATE clients
            SET {update_clause}
            WHERE account_id = '{account_id}'
        """)

        print(f"✓ Updated client: {account_id}")

    def add_issue(self, account_id, description, category="",
                  severity="Medium", status="Open"):
        """Add an issue for a client"""

        issue_data = [(
            account_id,
            datetime.now(),
            category,
            description,
            severity,
            status,
            None
        )]

        columns = ["account_id", "issue_date", "issue_category", "description",
                   "severity", "status", "resolution"]

        df = spark.createDataFrame(issue_data, columns)
        df.write.format("delta").mode("append").saveAsTable("issues")

        print(f"✓ Added issue for {account_id}")

    def add_action(self, account_id, action_type, description,
                   owner="", status="Pending", due_date=None):
        """Add an action item for a client"""

        action_data = [(
            account_id,
            datetime.now(),
            action_type,
            description,
            owner,
            status,
            due_date,
            None
        )]

        columns = ["account_id", "action_date", "action_type", "description",
                   "owner", "status", "due_date", "completed_date"]

        df = spark.createDataFrame(action_data, columns)
        df.write.format("delta").mode("append").saveAsTable("actions")

        print(f"✓ Added action for {account_id}")

    def update_action(self, action_id, status, completed_date=None):
        """Update action status"""

        if status == "Completed" and completed_date is None:
            completed_date = datetime.now().strftime("%Y-%m-%d")

        completed_clause = f", completed_date = '{completed_date}'" if completed_date else ""

        spark.sql(f"""
            UPDATE actions
            SET status = '{status}'{completed_clause}
            WHERE action_id = {action_id}
        """)

        print(f"✓ Updated action #{action_id}")

    def add_weekly_review(self, account_id, summary, progress_status,
                         next_steps="", reviewed_by=""):
        """Add a weekly review for a client"""

        # Get week start (Monday)
        today = datetime.now()
        week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")

        review_data = [(
            account_id,
            week_start,
            summary,
            progress_status,
            next_steps,
            reviewed_by,
            datetime.now()
        )]

        columns = ["account_id", "week_start", "summary", "progress_status",
                   "next_steps", "reviewed_by", "review_date"]

        df = spark.createDataFrame(review_data, columns)
        df.write.format("delta").mode("append").saveAsTable("weekly_reviews")

        print(f"✓ Added weekly review for {account_id}")

    def view_client(self, account_id):
        """View detailed client information"""

        # Get client details
        client = spark.sql(f"""
            SELECT * FROM clients
            WHERE account_id = '{account_id}'
        """).collect()

        if not client:
            print(f"Client '{account_id}' not found")
            return

        client = client[0]

        print("\n" + "="*80)
        print(f"CLIENT DETAILS: {client['name']}")
        print("="*80)
        print(f"Account ID:       {client['account_id']}")
        print(f"Contract Value:   ${client['contract_value']:,.2f}")
        print(f"Renewal Date:     {client['renewal_date']}")
        print(f"Risk Level:       {client['risk_level']}")
        print(f"Status:           {client['status']}")
        print(f"Account Owner:    {client['account_owner']}")
        print(f"Last Updated:     {client['last_updated']}")
        if client['notes']:
            print(f"Notes:            {client['notes']}")

        # Get issues
        print(f"\n{'-'*80}")
        print("ISSUES:")
        print(f"{'-'*80}")
        issues = spark.sql(f"""
            SELECT * FROM issues
            WHERE account_id = '{account_id}'
            ORDER BY issue_date DESC
        """)
        display(issues)

        # Get actions
        print(f"\n{'-'*80}")
        print("ACTIONS:")
        print(f"{'-'*80}")
        actions = spark.sql(f"""
            SELECT * FROM actions
            WHERE account_id = '{account_id}'
            ORDER BY action_date DESC
        """)
        display(actions)

        # Get weekly reviews
        print(f"\n{'-'*80}")
        print("RECENT WEEKLY REVIEWS:")
        print(f"{'-'*80}")
        reviews = spark.sql(f"""
            SELECT * FROM weekly_reviews
            WHERE account_id = '{account_id}'
            ORDER BY week_start DESC
            LIMIT 3
        """)
        display(reviews)

# Initialize tracker
tracker = ChurnTracker()
print("✓ ChurnTracker initialized")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Reporting & Analytics Functions

# COMMAND ----------

def show_dashboard():
    """Display comprehensive dashboard"""

    print("\n" + "="*80)
    print("CHURN RISK DASHBOARD")
    print("="*80)

    # Overall stats
    stats = spark.sql("""
        SELECT
            COUNT(*) as total_clients,
            SUM(CASE WHEN status = 'At Risk' THEN 1 ELSE 0 END) as at_risk,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END) as churned,
            SUM(CASE WHEN status = 'Renewed' THEN 1 ELSE 0 END) as renewed,
            SUM(contract_value) as total_value
        FROM clients
    """).collect()[0]

    print(f"\nOVERALL STATUS:")
    print(f"  Total Clients:     {stats['total_clients']}")
    print(f"  At Risk:           {stats['at_risk']}")
    print(f"  In Progress:       {stats['in_progress']}")
    print(f"  Resolved:          {stats['resolved']}")
    print(f"  Churned:           {stats['churned']}")
    print(f"  Renewed:           {stats['renewed']}")
    print(f"  Total Value:       ${stats['total_value']:,.2f}")

    # Risk breakdown visualization
    print("\n📊 RISK BREAKDOWN (Active Clients):")
    risk_df = spark.sql("""
        SELECT
            risk_level,
            COUNT(*) as client_count,
            SUM(contract_value) as total_value
        FROM clients
        WHERE status IN ('At Risk', 'In Progress')
        GROUP BY risk_level
        ORDER BY
            CASE risk_level
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
            END
    """)
    display(risk_df)

    # Upcoming renewals
    print("\n📅 UPCOMING RENEWALS (Next 30 days):")
    upcoming = spark.sql("""
        SELECT
            name,
            account_id,
            renewal_date,
            contract_value,
            risk_level,
            account_owner
        FROM clients
        WHERE renewal_date <= date_add(current_date(), 30)
        AND status NOT IN ('Churned', 'Renewed')
        ORDER BY renewal_date ASC
    """)
    display(upcoming)

    # Action items summary
    print("\n✅ ACTION ITEMS STATUS:")
    action_stats = spark.sql("""
        SELECT
            status,
            COUNT(*) as count
        FROM actions
        GROUP BY status
        ORDER BY count DESC
    """)
    display(action_stats)

# COMMAND ----------

def weekly_report():
    """Generate weekly report for review"""

    # Get week start (Monday)
    today = datetime.now()
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    week_end = (today - timedelta(days=today.weekday()) + timedelta(days=6)).strftime("%Y-%m-%d")

    print("\n" + "="*100)
    print(f"WEEKLY CHURN RISK REPORT: {week_start} to {week_end}")
    print("="*100)

    # High priority clients
    print("\n🔴 HIGH RISK CLIENTS:")
    high_risk = spark.sql("""
        SELECT
            c.name,
            c.account_id,
            c.renewal_date,
            datediff(c.renewal_date, current_date()) as days_to_renewal,
            c.contract_value,
            c.account_owner,
            COUNT(DISTINCT i.issue_id) as open_issues,
            COUNT(DISTINCT a.action_id) as pending_actions
        FROM clients c
        LEFT JOIN issues i ON c.account_id = i.account_id AND i.status IN ('Open', 'In Progress')
        LEFT JOIN actions a ON c.account_id = a.account_id AND a.status IN ('Pending', 'In Progress')
        WHERE c.risk_level = 'High'
        AND c.status IN ('At Risk', 'In Progress')
        GROUP BY c.name, c.account_id, c.renewal_date, c.contract_value, c.account_owner
        ORDER BY c.renewal_date ASC
    """)
    display(high_risk)

    # Clients needing review
    print("\n⚠️  CLIENTS NEEDING WEEKLY REVIEW:")
    needs_review = spark.sql(f"""
        SELECT
            c.name,
            c.account_id,
            c.risk_level,
            c.renewal_date,
            c.account_owner
        FROM clients c
        LEFT JOIN weekly_reviews wr ON c.account_id = wr.account_id AND wr.week_start = '{week_start}'
        WHERE c.status IN ('At Risk', 'In Progress')
        AND wr.review_id IS NULL
        ORDER BY
            CASE c.risk_level WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END,
            c.renewal_date
    """)
    display(needs_review)

    # Completed actions this week
    print("\n✅ COMPLETED ACTIONS THIS WEEK:")
    completed = spark.sql(f"""
        SELECT
            c.name,
            c.account_id,
            a.action_type,
            a.description,
            a.owner,
            a.completed_date
        FROM actions a
        JOIN clients c ON a.account_id = c.account_id
        WHERE a.completed_date >= '{week_start}'
        AND a.completed_date <= '{week_end}'
        ORDER BY a.completed_date DESC
    """)
    display(completed)

    # Pending/overdue actions
    print("\n📋 PENDING & OVERDUE ACTIONS:")
    pending = spark.sql(f"""
        SELECT
            c.name,
            c.account_id,
            a.action_type,
            a.description,
            a.owner,
            a.due_date,
            CASE
                WHEN a.due_date < current_date() THEN 'OVERDUE'
                WHEN a.due_date <= date_add(current_date(), 7) THEN 'DUE SOON'
                ELSE 'UPCOMING'
            END as urgency
        FROM actions a
        JOIN clients c ON a.account_id = c.account_id
        WHERE a.status IN ('Pending', 'In Progress')
        ORDER BY
            CASE urgency WHEN 'OVERDUE' THEN 1 WHEN 'DUE SOON' THEN 2 ELSE 3 END,
            a.due_date
    """)
    display(pending)

# COMMAND ----------

def list_clients(risk_level=None, status=None, days_to_renewal=None):
    """List clients with optional filters"""

    query = "SELECT * FROM clients WHERE 1=1"

    if risk_level:
        query += f" AND risk_level = '{risk_level}'"

    if status:
        query += f" AND status = '{status}'"

    if days_to_renewal:
        query += f" AND datediff(renewal_date, current_date()) <= {days_to_renewal}"

    query += " ORDER BY renewal_date ASC"

    df = spark.sql(query)

    # Add calculated column for days to renewal
    df = df.withColumn("days_to_renewal", datediff(col("renewal_date"), current_date()))

    display(df)

    # Show summary
    total_value = df.agg({"contract_value": "sum"}).collect()[0][0] or 0
    print(f"\n📊 Total clients: {df.count()} | Total contract value: ${total_value:,.2f}")

    return df

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Load Example Data

# COMMAND ----------

def load_example_data():
    """Load example data to demonstrate the system"""

    print("Loading example churn risk data...\n")

    # Example 1: High-risk client
    tracker.add_client(
        name="HealthFirst Medical Group",
        account_id="HF-2024-001",
        contract_value=750000,
        renewal_date=(datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
        risk_level="High",
        account_owner="Sarah Johnson",
        notes="Large enterprise account. CFO raised budget concerns in Q4 review."
    )

    tracker.add_issue("HF-2024-001", "Budget cuts due to hospital system merger",
                     "Commercial", "Critical")
    tracker.add_issue("HF-2024-001", "Integration issues with Epic EMR system",
                     "Technical", "High")

    tracker.add_action("HF-2024-001", "Meeting",
                      "Executive escalation with CEO and CFO",
                      "Sarah Johnson", "Pending",
                      (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))

    tracker.add_action("HF-2024-001", "Escalation",
                      "Engineering team to resolve Epic integration",
                      "Tech Team", "In Progress",
                      (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"))

    # Example 2: Medium-risk client making progress
    tracker.add_client(
        name="CareConnect Clinics",
        account_id="CC-2024-089",
        contract_value=180000,
        renewal_date=(datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        risk_level="Medium",
        status="In Progress",
        account_owner="Mike Chen",
        notes="Initially at high risk due to support issues. Now improving."
    )

    tracker.add_issue("CC-2024-089", "Slow response times from support team",
                     "Support", "Medium")

    tracker.add_action("CC-2024-089", "Call",
                      "Weekly check-in with practice manager",
                      "Mike Chen", "Completed")

    tracker.add_weekly_review("CC-2024-089",
                             "Assigned dedicated support rep. Response times improving.",
                             "Risk reduced from High to Medium. Client satisfied with changes.",
                             "Continue weekly check-ins. Monitor support metrics.")

    # Example 3: High-value client with pricing concerns
    tracker.add_client(
        name="Metro Health Partners",
        account_id="MHP-2023-234",
        contract_value=450000,
        renewal_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        risk_level="High",
        account_owner="Lisa Park",
        notes="Evaluating competitors. Price sensitive."
    )

    tracker.add_issue("MHP-2023-234", "Pricing 20% higher than competitor quotes",
                     "Pricing", "Critical")
    tracker.add_issue("MHP-2023-234", "Low utilization of premium features",
                     "Adoption", "Medium")

    tracker.add_action("MHP-2023-234", "Meeting",
                      "Business review to demonstrate ROI and value",
                      "Lisa Park", "Pending",
                      (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"))

    # Example 4: Low-risk client
    tracker.add_client(
        name="Wellness Medical Associates",
        account_id="WMA-2024-156",
        contract_value=95000,
        renewal_date=(datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        risk_level="Low",
        account_owner="Tom Williams",
        notes="Generally satisfied. Minor feature requests."
    )

    tracker.add_issue("WMA-2024-156", "Requesting mobile app improvements",
                     "Product", "Low")

    tracker.add_action("WMA-2024-156", "Email",
                      "Share product roadmap and upcoming mobile features",
                      "Tom Williams", "Completed")

    # Example 5: Churned client (historical)
    tracker.add_client(
        name="Summit Healthcare",
        account_id="SH-2023-087",
        contract_value=320000,
        renewal_date=(datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        risk_level="High",
        status="Churned",
        account_owner="Sarah Johnson",
        notes="Lost to competitor. Product limitations and price were factors."
    )

    tracker.add_issue("SH-2023-087", "Missing key reporting features vs competitors",
                     "Product", "Critical")
    tracker.add_issue("SH-2023-087", "Unable to match competitor pricing",
                     "Pricing", "High")

    print("\n✅ Example data loaded successfully!")
    print("\nNext steps:")
    print("  - Run show_dashboard() to see overview")
    print("  - Run list_clients() to see all clients")
    print("  - Run weekly_report() to generate report")
    print("  - Run tracker.view_client('HF-2024-001') to see details")

# Run to load example data
# load_example_data()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Visualization Helpers

# COMMAND ----------

def visualize_risk_by_value():
    """Visualize at-risk contract value by risk level"""

    df = spark.sql("""
        SELECT
            risk_level,
            status,
            SUM(contract_value) as total_value,
            COUNT(*) as client_count
        FROM clients
        WHERE status IN ('At Risk', 'In Progress')
        GROUP BY risk_level, status
        ORDER BY risk_level
    """)

    display(df)

def visualize_renewal_timeline():
    """Visualize renewals over time"""

    df = spark.sql("""
        SELECT
            DATE_TRUNC('month', renewal_date) as renewal_month,
            risk_level,
            COUNT(*) as client_count,
            SUM(contract_value) as total_value
        FROM clients
        WHERE status NOT IN ('Churned', 'Renewed')
        AND renewal_date >= current_date()
        AND renewal_date <= date_add(current_date(), 365)
        GROUP BY renewal_month, risk_level
        ORDER BY renewal_month, risk_level
    """)

    display(df)

def visualize_action_status():
    """Visualize action item completion"""

    df = spark.sql("""
        SELECT
            a.status,
            a.action_type,
            COUNT(*) as count,
            AVG(datediff(COALESCE(a.completed_date, current_date()), a.action_date)) as avg_days_to_complete
        FROM actions a
        GROUP BY a.status, a.action_type
        ORDER BY a.status, count DESC
    """)

    display(df)

def visualize_issues_by_category():
    """Visualize issues by category and severity"""

    df = spark.sql("""
        SELECT
            issue_category,
            severity,
            status,
            COUNT(*) as issue_count
        FROM issues
        GROUP BY issue_category, severity, status
        ORDER BY issue_count DESC
    """)

    display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Bulk Import from External Sources

# COMMAND ----------

def import_from_dataframe(df, source_name="external_source"):
    """
    Import clients from a Spark DataFrame or Pandas DataFrame

    Expected columns:
    - name
    - account_id
    - contract_value
    - renewal_date
    - risk_level
    - status (optional, defaults to 'At Risk')
    - account_owner (optional)
    - notes (optional)
    """

    # Convert pandas to Spark if needed
    if isinstance(df, pd.DataFrame):
        df = spark.createDataFrame(df)

    # Add default values and timestamps
    df = df.withColumn("status",
                       when(col("status").isNotNull(), col("status")).otherwise(lit("At Risk")))
    df = df.withColumn("account_owner",
                       when(col("account_owner").isNotNull(), col("account_owner")).otherwise(lit("")))
    df = df.withColumn("notes",
                       when(col("notes").isNotNull(), col("notes")).otherwise(lit("")))
    df = df.withColumn("created_date", current_timestamp())
    df = df.withColumn("last_updated", current_timestamp())

    # Write to Delta table
    df.write.format("delta").mode("append").saveAsTable("clients")

    count = df.count()
    print(f"✓ Imported {count} clients from {source_name}")

    return count

# Example: Import from CSV file
def import_from_csv(file_path):
    """Import clients from CSV file"""
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    return import_from_dataframe(df, source_name=file_path)

# Example: Import from existing table/view
def import_from_table(table_name, column_mapping=None):
    """
    Import clients from another table with optional column mapping

    column_mapping example:
    {
        'client_name': 'name',
        'acct_id': 'account_id',
        'arr': 'contract_value',
        'expiry_date': 'renewal_date',
        'risk': 'risk_level'
    }
    """
    df = spark.table(table_name)

    if column_mapping:
        for old_col, new_col in column_mapping.items():
            df = df.withColumnRenamed(old_col, new_col)

    return import_from_dataframe(df, source_name=table_name)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Quick Access Commands
# MAGIC
# MAGIC Use these cells for daily operations

# COMMAND ----------

# MAGIC %md
# MAGIC ### Daily Dashboard Check

# COMMAND ----------

# Run this every morning
show_dashboard()

# COMMAND ----------

# MAGIC %md
# MAGIC ### View High-Risk Clients

# COMMAND ----------

# Show all high-risk clients
list_clients(risk_level="High", status="At Risk")

# COMMAND ----------

# MAGIC %md
# MAGIC ### View Upcoming Renewals (30 days)

# COMMAND ----------

# Show clients renewing in next 30 days
list_clients(days_to_renewal=30)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate Weekly Report

# COMMAND ----------

# Run this every Monday
weekly_report()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Example Usage
# MAGIC
# MAGIC Uncomment and run these cells to see the system in action

# COMMAND ----------

# Load example data (run this once)
load_example_data()

# COMMAND ----------

# View dashboard
show_dashboard()

# COMMAND ----------

# View specific client
tracker.view_client("HF-2024-001")

# COMMAND ----------

# Add a new client
tracker.add_client(
    name="Your Client Name",
    account_id="YOUR-001",
    contract_value=200000,
    renewal_date="2026-06-30",
    risk_level="High",
    account_owner="Your Name",
    notes="Describe the risk situation"
)

# COMMAND ----------

# Add an issue
tracker.add_issue(
    account_id="YOUR-001",
    description="Main problem causing churn risk",
    category="Product",
    severity="High"
)

# COMMAND ----------

# Add an action item
tracker.add_action(
    account_id="YOUR-001",
    action_type="Meeting",
    description="Executive escalation call",
    owner="Your Name",
    due_date="2026-02-01"
)

# COMMAND ----------

# Add weekly review
tracker.add_weekly_review(
    account_id="YOUR-001",
    summary="Progress made this week",
    progress_status="Making headway on main issues",
    next_steps="Schedule follow-up meeting",
    reviewed_by="Your Name"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Advanced Analytics

# COMMAND ----------

# Churn prediction analysis
spark.sql("""
    SELECT
        risk_level,
        datediff(renewal_date, current_date()) as days_to_renewal,
        COUNT(*) as client_count,
        SUM(contract_value) as at_risk_value,
        AVG(contract_value) as avg_contract_value
    FROM clients
    WHERE status IN ('At Risk', 'In Progress')
    GROUP BY risk_level, datediff(renewal_date, current_date())
    ORDER BY days_to_renewal, risk_level
""").display()

# COMMAND ----------

# Success metrics - track resolution rates
spark.sql("""
    SELECT
        DATE_TRUNC('month', last_updated) as month,
        COUNT(CASE WHEN status = 'Renewed' THEN 1 END) as renewed,
        COUNT(CASE WHEN status = 'Churned' THEN 1 END) as churned,
        COUNT(CASE WHEN status IN ('At Risk', 'In Progress') THEN 1 END) as still_at_risk,
        SUM(CASE WHEN status = 'Renewed' THEN contract_value ELSE 0 END) as saved_revenue,
        SUM(CASE WHEN status = 'Churned' THEN contract_value ELSE 0 END) as lost_revenue
    FROM clients
    GROUP BY month
    ORDER BY month DESC
""").display()

# COMMAND ----------

# Account owner performance
spark.sql("""
    SELECT
        account_owner,
        COUNT(*) as total_clients,
        COUNT(CASE WHEN status = 'Renewed' THEN 1 END) as renewed,
        COUNT(CASE WHEN status = 'Churned' THEN 1 END) as churned,
        COUNT(CASE WHEN status IN ('At Risk', 'In Progress') THEN 1 END) as active,
        ROUND(100.0 * COUNT(CASE WHEN status = 'Renewed' THEN 1 END) /
              NULLIF(COUNT(CASE WHEN status IN ('Renewed', 'Churned') THEN 1 END), 0), 2) as save_rate_pct
    FROM clients
    WHERE account_owner != ''
    GROUP BY account_owner
    ORDER BY total_clients DESC
""").display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Scheduled Jobs Setup
# MAGIC
# MAGIC To automate weekly reports, set up a Databricks Job:
# MAGIC
# MAGIC 1. Go to Workflows → Create Job
# MAGIC 2. Schedule: Every Monday at 9am
# MAGIC 3. Task: Run the `weekly_report()` cell
# MAGIC 4. Notifications: Email report to your team
# MAGIC
# MAGIC Example code for automated email report:

# COMMAND ----------

def send_weekly_email_report():
    """
    Generate and send weekly report via email
    Configure in Databricks Jobs with email notifications
    """

    # Generate report
    weekly_report()

    # Export to CSV for email attachment
    high_risk = spark.sql("""
        SELECT * FROM clients
        WHERE risk_level = 'High'
        AND status IN ('At Risk', 'In Progress')
        ORDER BY renewal_date
    """)

    # Save to DBFS for email attachment
    high_risk.coalesce(1).write.mode("overwrite").csv("/tmp/weekly_high_risk_clients.csv", header=True)

    print("✓ Weekly report generated and saved")
    print("Configure Databricks Job email notifications to receive this report")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📚 Documentation & Help
# MAGIC
# MAGIC ### Quick Reference
# MAGIC
# MAGIC **Daily Commands:**
# MAGIC ```python
# MAGIC show_dashboard()                          # View overall metrics
# MAGIC list_clients(risk_level="High")          # Filter by risk
# MAGIC list_clients(days_to_renewal=30)         # Upcoming renewals
# MAGIC tracker.view_client("ACCOUNT-ID")        # Client details
# MAGIC ```
# MAGIC
# MAGIC **Weekly Commands:**
# MAGIC ```python
# MAGIC weekly_report()                          # Generate weekly report
# MAGIC tracker.add_weekly_review(...)           # Document review
# MAGIC tracker.update_action(id, "Completed")   # Update actions
# MAGIC ```
# MAGIC
# MAGIC **Add Data:**
# MAGIC ```python
# MAGIC tracker.add_client(...)                  # New at-risk client
# MAGIC tracker.add_issue(...)                   # Document issue
# MAGIC tracker.add_action(...)                  # Create action item
# MAGIC tracker.update_client(...)               # Update details
# MAGIC ```
# MAGIC
# MAGIC **Visualizations:**
# MAGIC ```python
# MAGIC visualize_risk_by_value()                # Risk/value breakdown
# MAGIC visualize_renewal_timeline()             # Timeline view
# MAGIC visualize_action_status()                # Action completion
# MAGIC visualize_issues_by_category()           # Issue analysis
# MAGIC ```
# MAGIC
# MAGIC **Bulk Import:**
# MAGIC ```python
# MAGIC import_from_csv("/path/to/file.csv")     # From CSV
# MAGIC import_from_table("table_name")          # From existing table
# MAGIC import_from_dataframe(df)                # From DataFrame
# MAGIC ```
# MAGIC
# MAGIC ### Data Schema
# MAGIC
# MAGIC **Risk Levels:** High, Medium, Low
# MAGIC **Status:** At Risk, In Progress, Resolved, Churned, Renewed
# MAGIC **Action Types:** Call, Email, Meeting, Escalation, Follow-up, Other
# MAGIC **Severities:** Critical, High, Medium, Low
# MAGIC
# MAGIC ### Next Steps
# MAGIC
# MAGIC 1. Run setup cells (already done if you ran from top)
# MAGIC 2. Load example data: `load_example_data()`
# MAGIC 3. Explore dashboard: `show_dashboard()`
# MAGIC 4. Import your real data using bulk import functions
# MAGIC 5. Set up scheduled job for weekly reports
