#!/usr/bin/env python3
"""
Example setup script - Creates sample data to get started quickly
Run this to populate the tracker with example at-risk clients
"""

import subprocess
import sys
from datetime import datetime, timedelta


def run_command(cmd):
    """Run a churn tracker command"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)


def setup_example_data():
    """Create example clients with realistic scenarios"""

    print("\n" + "="*80)
    print("Setting up example churn risk data...")
    print("="*80 + "\n")

    # Calculate dates
    today = datetime.now()

    # Example 1: High-risk client with multiple issues
    print("📊 Adding high-risk client: HealthFirst Medical Group")
    run_command([
        'python3', 'churn_tracker.py', 'add-client',
        '--name', 'HealthFirst Medical Group',
        '--account-id', 'HF-2024-001',
        '--value', '750000',
        '--renewal-date', (today + timedelta(days=45)).strftime('%Y-%m-%d'),
        '--risk', 'High',
        '--owner', 'Sarah Johnson',
        '--notes', 'Large enterprise account. CFO raised budget concerns in Q4 review.'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'HF-2024-001',
        '--description', 'Budget cuts due to hospital system merger',
        '--category', 'Commercial',
        '--severity', 'Critical'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'HF-2024-001',
        '--description', 'Integration issues with Epic EMR system',
        '--category', 'Technical',
        '--severity', 'High'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-action', 'HF-2024-001',
        '--type', 'Meeting',
        '--description', 'Executive escalation with CEO and CFO',
        '--owner', 'Sarah Johnson',
        '--due', (today + timedelta(days=7)).strftime('%Y-%m-%d')
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-action', 'HF-2024-001',
        '--type', 'Escalation',
        '--description', 'Engineering team to resolve Epic integration',
        '--owner', 'Tech Team',
        '--status', 'In Progress',
        '--due', (today + timedelta(days=14)).strftime('%Y-%m-%d')
    ])

    # Example 2: Medium-risk client making progress
    print("\n📊 Adding medium-risk client: CareConnect Clinics")
    run_command([
        'python3', 'churn_tracker.py', 'add-client',
        '--name', 'CareConnect Clinics',
        '--account-id', 'CC-2024-089',
        '--value', '180000',
        '--renewal-date', (today + timedelta(days=60)).strftime('%Y-%m-%d'),
        '--risk', 'Medium',
        '--status', 'In Progress',
        '--owner', 'Mike Chen',
        '--notes', 'Initially at high risk due to support issues. Now improving.'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'CC-2024-089',
        '--description', 'Slow response times from support team',
        '--category', 'Support',
        '--severity', 'Medium'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-action', 'CC-2024-089',
        '--type', 'Call',
        '--description', 'Weekly check-in with practice manager',
        '--owner', 'Mike Chen',
        '--status', 'Completed'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-review', 'CC-2024-089',
        '--summary', 'Assigned dedicated support rep. Response times improving.',
        '--progress', 'Risk reduced from High to Medium. Client satisfied with changes.',
        '--next-steps', 'Continue weekly check-ins. Monitor support metrics.'
    ])

    # Example 3: High-value client with pricing concerns
    print("\n📊 Adding high-risk client: Metro Health Partners")
    run_command([
        'python3', 'churn_tracker.py', 'add-client',
        '--name', 'Metro Health Partners',
        '--account-id', 'MHP-2023-234',
        '--value', '450000',
        '--renewal-date', (today + timedelta(days=30)).strftime('%Y-%m-%d'),
        '--risk', 'High',
        '--owner', 'Lisa Park',
        '--notes', 'Evaluating competitors. Price sensitive.'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'MHP-2023-234',
        '--description', 'Pricing 20% higher than competitor quotes',
        '--category', 'Pricing',
        '--severity', 'Critical'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'MHP-2023-234',
        '--description', 'Low utilization of premium features',
        '--category', 'Adoption',
        '--severity', 'Medium'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-action', 'MHP-2023-234',
        '--type', 'Meeting',
        '--description', 'Business review to demonstrate ROI and value',
        '--owner', 'Lisa Park',
        '--due', (today + timedelta(days=5)).strftime('%Y-%m-%d')
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-action', 'MHP-2023-234',
        '--type', 'Other',
        '--description', 'Prepare custom pricing proposal',
        '--owner', 'Sales Ops',
        '--status', 'Pending'
    ])

    # Example 4: Low-risk client with minor issues
    print("\n📊 Adding low-risk client: Wellness Medical Associates")
    run_command([
        'python3', 'churn_tracker.py', 'add-client',
        '--name', 'Wellness Medical Associates',
        '--account-id', 'WMA-2024-156',
        '--value', '95000',
        '--renewal-date', (today + timedelta(days=90)).strftime('%Y-%m-%d'),
        '--risk', 'Low',
        '--owner', 'Tom Williams',
        '--notes', 'Generally satisfied. Minor feature requests.'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'WMA-2024-156',
        '--description', 'Requesting mobile app improvements',
        '--category', 'Product',
        '--severity', 'Low'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-action', 'WMA-2024-156',
        '--type', 'Email',
        '--description', 'Share product roadmap and upcoming mobile features',
        '--owner', 'Tom Williams',
        '--status', 'Completed'
    ])

    # Example 5: Recently churned client (for historical tracking)
    print("\n📊 Adding churned client: Summit Healthcare (historical)")
    run_command([
        'python3', 'churn_tracker.py', 'add-client',
        '--name', 'Summit Healthcare',
        '--account-id', 'SH-2023-087',
        '--value', '320000',
        '--renewal-date', (today - timedelta(days=15)).strftime('%Y-%m-%d'),
        '--risk', 'High',
        '--status', 'Churned',
        '--owner', 'Sarah Johnson',
        '--notes', 'Lost to competitor. Product limitations and price were factors.'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'SH-2023-087',
        '--description', 'Missing key reporting features vs competitors',
        '--category', 'Product',
        '--severity', 'Critical'
    ])

    run_command([
        'python3', 'churn_tracker.py', 'add-issue', 'SH-2023-087',
        '--description', 'Unable to match competitor pricing',
        '--category', 'Pricing',
        '--severity', 'High'
    ])

    print("\n" + "="*80)
    print("✅ Example data created successfully!")
    print("="*80)
    print("\nNext steps:")
    print("1. View the dashboard:    python3 churn_tracker.py dashboard")
    print("2. See all clients:       python3 churn_tracker.py list")
    print("3. View a client:         python3 churn_tracker.py view HF-2024-001")
    print("4. Generate report:       python3 churn_tracker.py weekly-report")
    print("\nYou can now explore the tool with realistic example data!")
    print("="*80 + "\n")


if __name__ == '__main__':
    try:
        setup_example_data()
    except Exception as e:
        print(f"\n❌ Error setting up example data: {e}")
        sys.exit(1)
