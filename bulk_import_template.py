#!/usr/bin/env python3
"""
Bulk Import Script for Churn Risk Tracker

Use this script to import multiple clients from a CSV file.

CSV Format:
name,account_id,contract_value,renewal_date,risk_level,status,account_owner,notes
Acme Corp,ACME-001,250000,2026-06-15,High,At Risk,Sarah Johnson,Budget concerns
TechCo,TECH-002,150000,2026-07-20,Medium,In Progress,Mike Chen,Support issues resolved

Date format: YYYY-MM-DD
Risk levels: High, Medium, Low
Status: At Risk, In Progress, Resolved, Churned, Renewed
"""

import csv
import subprocess
import sys
import os


def import_from_csv(csv_file):
    """Import clients from CSV file"""

    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found")
        return

    print(f"\n{'='*80}")
    print(f"Importing clients from: {csv_file}")
    print(f"{'='*80}\n")

    imported = 0
    errors = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            try:
                # Required fields
                name = row.get('name', '').strip()
                account_id = row.get('account_id', '').strip()
                value = row.get('contract_value', '0').strip()
                renewal_date = row.get('renewal_date', '').strip()
                risk = row.get('risk_level', 'Medium').strip()

                # Optional fields
                status = row.get('status', 'At Risk').strip()
                owner = row.get('account_owner', '').strip()
                notes = row.get('notes', '').strip()

                # Validate required fields
                if not all([name, account_id, renewal_date]):
                    print(f"❌ Row {i}: Missing required fields (name, account_id, or renewal_date)")
                    errors += 1
                    continue

                # Build command
                cmd = [
                    'python3', 'churn_tracker.py', 'add-client',
                    '--name', name,
                    '--account-id', account_id,
                    '--value', value,
                    '--renewal-date', renewal_date,
                    '--risk', risk,
                    '--status', status,
                    '--owner', owner,
                    '--notes', notes
                ]

                # Execute command
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"✓ Imported: {name} ({account_id})")
                    imported += 1
                else:
                    print(f"❌ Row {i}: {result.stderr.strip()}")
                    errors += 1

            except Exception as e:
                print(f"❌ Row {i}: {str(e)}")
                errors += 1

    print(f"\n{'='*80}")
    print(f"Import complete!")
    print(f"Successfully imported: {imported}")
    print(f"Errors: {errors}")
    print(f"{'='*80}\n")


def create_template_csv():
    """Create a template CSV file for reference"""
    template_file = 'import_template.csv'

    with open(template_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'name',
            'account_id',
            'contract_value',
            'renewal_date',
            'risk_level',
            'status',
            'account_owner',
            'notes'
        ])
        writer.writerow([
            'Acme Healthcare',
            'ACME-001',
            '250000',
            '2026-06-15',
            'High',
            'At Risk',
            'Sarah Johnson',
            'Budget concerns due to merger'
        ])
        writer.writerow([
            'TechCorp Solutions',
            'TECH-002',
            '150000',
            '2026-07-20',
            'Medium',
            'In Progress',
            'Mike Chen',
            'Support issues being addressed'
        ])
        writer.writerow([
            'Wellness Partners',
            'WP-003',
            '95000',
            '2026-08-10',
            'Low',
            'At Risk',
            'Lisa Park',
            'Minor feature requests'
        ])

    print(f"✓ Created template file: {template_file}")
    print(f"\nEdit this file with your client data, then run:")
    print(f"  python3 bulk_import_template.py {template_file}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\nBulk Import Script for Churn Risk Tracker")
        print("="*50)
        print("\nUsage:")
        print("  Create template:  python3 bulk_import_template.py --create-template")
        print("  Import CSV:       python3 bulk_import_template.py your_file.csv")
        print("\n")
        sys.exit(1)

    if sys.argv[1] == '--create-template':
        create_template_csv()
    else:
        import_from_csv(sys.argv[1])
