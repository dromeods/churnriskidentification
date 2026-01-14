#!/usr/bin/env python3
"""
Migration Script: CLI SQLite to Databricks Delta Lake

This script helps you migrate your data from the CLI version (SQLite)
to the Databricks version (Delta Lake).

Usage:
1. Export from CLI: python3 churn_tracker.py export --output export.json
2. Upload export.json to Databricks
3. Run this script in a Databricks notebook
"""

import json
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime


def migrate_cli_to_databricks(json_file_path, database_name="churn_tracker"):
    """
    Migrate data from CLI export to Databricks Delta Lake

    Args:
        json_file_path: Path to JSON export from CLI version
        database_name: Databricks database name (default: churn_tracker)
    """

    print("="*80)
    print("CLI to Databricks Migration Tool")
    print("="*80)

    # Read JSON export
    print(f"\n📂 Reading export file: {json_file_path}")

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    clients_data = data.get('clients', [])
    export_date = data.get('export_date', 'Unknown')

    print(f"✓ Found {len(clients_data)} clients (exported: {export_date})")

    if len(clients_data) == 0:
        print("❌ No clients found in export file")
        return

    # Use Databricks database
    spark.sql(f"USE {database_name}")
    print(f"✓ Using database: {database_name}")

    # Prepare data for import
    clients_list = []
    issues_list = []
    actions_list = []
    reviews_list = []

    for client in clients_data:
        # Client data
        client_row = {
            'name': client.get('name'),
            'account_id': client.get('account_id'),
            'contract_value': float(client.get('contract_value', 0)) if client.get('contract_value') else None,
            'renewal_date': client.get('renewal_date'),
            'risk_level': client.get('risk_level'),
            'status': client.get('status'),
            'account_owner': client.get('account_owner', ''),
            'notes': client.get('notes', ''),
            'created_date': client.get('created_date'),
            'last_updated': client.get('last_updated')
        }
        clients_list.append(client_row)

        # Issues
        for issue in client.get('issues', []):
            issue_row = {
                'account_id': client.get('account_id'),
                'issue_date': issue.get('issue_date'),
                'issue_category': issue.get('issue_category', ''),
                'description': issue.get('description'),
                'severity': issue.get('severity'),
                'status': issue.get('status'),
                'resolution': issue.get('resolution')
            }
            issues_list.append(issue_row)

        # Actions
        for action in client.get('actions', []):
            action_row = {
                'account_id': client.get('account_id'),
                'action_date': action.get('action_date'),
                'action_type': action.get('action_type'),
                'description': action.get('description'),
                'owner': action.get('owner', ''),
                'status': action.get('status'),
                'due_date': action.get('due_date'),
                'completed_date': action.get('completed_date')
            }
            actions_list.append(action_row)

        # Weekly reviews
        for review in client.get('weekly_reviews', []):
            review_row = {
                'account_id': client.get('account_id'),
                'week_start': review.get('week_start'),
                'summary': review.get('summary'),
                'progress_status': review.get('progress_status'),
                'next_steps': review.get('next_steps', ''),
                'reviewed_by': review.get('reviewed_by', ''),
                'review_date': review.get('week_start')  # Use week_start as review_date
            }
            reviews_list.append(review_row)

    # Import clients
    print(f"\n📊 Importing {len(clients_list)} clients...")
    if clients_list:
        clients_df = spark.createDataFrame(clients_list)
        clients_df.write.format("delta").mode("append").saveAsTable("clients")
        print(f"✓ Imported {len(clients_list)} clients")

    # Import issues
    print(f"📊 Importing {len(issues_list)} issues...")
    if issues_list:
        issues_df = spark.createDataFrame(issues_list)
        issues_df.write.format("delta").mode("append").saveAsTable("issues")
        print(f"✓ Imported {len(issues_list)} issues")

    # Import actions
    print(f"📊 Importing {len(actions_list)} actions...")
    if actions_list:
        actions_df = spark.createDataFrame(actions_list)
        actions_df.write.format("delta").mode("append").saveAsTable("actions")
        print(f"✓ Imported {len(actions_list)} actions")

    # Import reviews
    print(f"📊 Importing {len(reviews_list)} weekly reviews...")
    if reviews_list:
        reviews_df = spark.createDataFrame(reviews_list)
        reviews_df.write.format("delta").mode("append").saveAsTable("weekly_reviews")
        print(f"✓ Imported {len(reviews_list)} weekly reviews")

    print("\n" + "="*80)
    print("✅ Migration completed successfully!")
    print("="*80)
    print("\nNext steps:")
    print("1. Verify data: show_dashboard()")
    print("2. Check clients: list_clients()")
    print("3. Delete CLI database if migration successful")
    print("\n")

    # Show summary
    print("Migration Summary:")
    print(f"  Clients:        {len(clients_list)}")
    print(f"  Issues:         {len(issues_list)}")
    print(f"  Actions:        {len(actions_list)}")
    print(f"  Weekly Reviews: {len(reviews_list)}")
    print("="*80)


def verify_migration(database_name="churn_tracker"):
    """Verify migration was successful"""

    spark.sql(f"USE {database_name}")

    print("\n" + "="*80)
    print("Migration Verification")
    print("="*80)

    # Count records
    clients_count = spark.table("clients").count()
    issues_count = spark.table("issues").count()
    actions_count = spark.table("actions").count()
    reviews_count = spark.table("weekly_reviews").count()

    print(f"\n✓ Clients:        {clients_count}")
    print(f"✓ Issues:         {issues_count}")
    print(f"✓ Actions:        {actions_count}")
    print(f"✓ Weekly Reviews: {reviews_count}")

    # Sample data check
    print("\nSample Client Data:")
    spark.sql("SELECT name, account_id, risk_level, status FROM clients LIMIT 5").show()

    print("="*80)


# DATABRICKS NOTEBOOK USAGE:
# Uncomment and run the following in Databricks notebook

# COMMAND ----------

# # Upload your export.json file to DBFS first
# # Then run migration
# migrate_cli_to_databricks("/dbfs/FileStore/churn_export.json")

# COMMAND ----------

# # Verify the migration
# verify_migration()

# COMMAND ----------

# # View imported data
# show_dashboard()


# STANDALONE SCRIPT USAGE (for testing locally):
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("\nCLI to Databricks Migration Script")
        print("="*50)
        print("\nUsage:")
        print("  python3 migrate_to_databricks.py export.json")
        print("\nThis script is meant to be run in a Databricks notebook.")
        print("For Databricks usage, see DATABRICKS_GUIDE.md")
        sys.exit(1)

    # For local testing only - shows what would be migrated
    json_file = sys.argv[1]

    print("\n" + "="*80)
    print("Migration Preview (Local Mode)")
    print("="*80)
    print("\nThis preview shows what would be migrated to Databricks.")
    print("To actually migrate, upload this script to Databricks and run there.\n")

    with open(json_file, 'r') as f:
        data = json.load(f)

    clients_data = data.get('clients', [])
    print(f"Clients to migrate: {len(clients_data)}")

    total_issues = sum(len(c.get('issues', [])) for c in clients_data)
    total_actions = sum(len(c.get('actions', [])) for c in clients_data)
    total_reviews = sum(len(c.get('weekly_reviews', [])) for c in clients_data)

    print(f"Issues to migrate: {total_issues}")
    print(f"Actions to migrate: {total_actions}")
    print(f"Weekly reviews to migrate: {total_reviews}")

    print("\n✓ Preview complete. Upload to Databricks to run actual migration.")
    print("="*80)
