#!/usr/bin/env python3
"""
Churn Risk Tracker - A CLI tool for managing client renewal risks
"""

import sqlite3
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple
import json


class ChurnTracker:
    """Main class for managing churn risk tracking"""

    def __init__(self, db_path: str = "churn_tracker.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                account_id TEXT UNIQUE,
                contract_value REAL,
                renewal_date TEXT,
                risk_level TEXT CHECK(risk_level IN ('High', 'Medium', 'Low')),
                status TEXT CHECK(status IN ('At Risk', 'In Progress', 'Resolved', 'Churned', 'Renewed')),
                account_owner TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)

        # Actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                action_date TEXT DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT CHECK(action_type IN ('Call', 'Email', 'Meeting', 'Escalation', 'Follow-up', 'Other')),
                description TEXT NOT NULL,
                owner TEXT,
                status TEXT CHECK(status IN ('Pending', 'In Progress', 'Completed', 'Blocked')),
                due_date TEXT,
                completed_date TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)

        # Issues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                issue_date TEXT DEFAULT CURRENT_TIMESTAMP,
                issue_category TEXT,
                description TEXT NOT NULL,
                severity TEXT CHECK(severity IN ('Critical', 'High', 'Medium', 'Low')),
                status TEXT CHECK(status IN ('Open', 'In Progress', 'Resolved', 'Closed')),
                resolution TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)

        # Weekly reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                week_start TEXT,
                summary TEXT,
                progress_status TEXT,
                next_steps TEXT,
                reviewed_by TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)

        self.conn.commit()

    def add_client(self, name: str, account_id: str, contract_value: float,
                   renewal_date: str, risk_level: str, status: str = "At Risk",
                   account_owner: str = "", notes: str = "") -> int:
        """Add a new at-risk client"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO clients (name, account_id, contract_value, renewal_date,
                                   risk_level, status, account_owner, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, account_id, contract_value, renewal_date, risk_level,
                  status, account_owner, notes))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Error: Client with account_id '{account_id}' already exists")
            return -1

    def update_client(self, account_id: str, **kwargs):
        """Update client details"""
        allowed_fields = ['name', 'contract_value', 'renewal_date', 'risk_level',
                         'status', 'account_owner', 'notes']
        updates = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = ?")
                values.append(value)

        if not updates:
            print("No valid fields to update")
            return

        updates.append("last_updated = CURRENT_TIMESTAMP")
        values.append(account_id)

        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE clients
            SET {', '.join(updates)}
            WHERE account_id = ?
        """, values)
        self.conn.commit()

        if cursor.rowcount > 0:
            print(f"✓ Updated client: {account_id}")
        else:
            print(f"✗ Client not found: {account_id}")

    def add_action(self, account_id: str, action_type: str, description: str,
                   owner: str = "", status: str = "Pending", due_date: str = ""):
        """Add an action item for a client"""
        client_id = self._get_client_id(account_id)
        if client_id is None:
            print(f"Error: Client '{account_id}' not found")
            return

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO actions (client_id, action_type, description, owner, status, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (client_id, action_type, description, owner, status, due_date))
        self.conn.commit()
        print(f"✓ Added action for {account_id}")

    def update_action(self, action_id: int, status: str, completed_date: str = ""):
        """Update action status"""
        cursor = self.conn.cursor()
        if not completed_date and status == "Completed":
            completed_date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("""
            UPDATE actions
            SET status = ?, completed_date = ?
            WHERE id = ?
        """, (status, completed_date, action_id))
        self.conn.commit()
        print(f"✓ Updated action #{action_id}")

    def add_issue(self, account_id: str, description: str, category: str = "",
                  severity: str = "Medium", status: str = "Open"):
        """Add an issue for a client"""
        client_id = self._get_client_id(account_id)
        if client_id is None:
            print(f"Error: Client '{account_id}' not found")
            return

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO issues (client_id, description, issue_category, severity, status)
            VALUES (?, ?, ?, ?, ?)
        """, (client_id, description, category, severity, status))
        self.conn.commit()
        print(f"✓ Added issue for {account_id}")

    def add_weekly_review(self, account_id: str, summary: str, progress_status: str,
                         next_steps: str = "", reviewed_by: str = ""):
        """Add a weekly review for a client"""
        client_id = self._get_client_id(account_id)
        if client_id is None:
            print(f"Error: Client '{account_id}' not found")
            return

        week_start = self._get_week_start()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO weekly_reviews (client_id, week_start, summary, progress_status, next_steps, reviewed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (client_id, week_start, summary, progress_status, next_steps, reviewed_by))
        self.conn.commit()
        print(f"✓ Added weekly review for {account_id}")

    def list_clients(self, risk_level: str = None, status: str = None,
                     days_to_renewal: int = None):
        """List clients with optional filters"""
        query = "SELECT * FROM clients WHERE 1=1"
        params = []

        if risk_level:
            query += " AND risk_level = ?"
            params.append(risk_level)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY renewal_date ASC"

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        clients = cursor.fetchall()

        if not clients:
            print("No clients found matching criteria")
            return

        # Print header
        print("\n" + "="*120)
        print(f"{'ID':<5} {'Account ID':<15} {'Client Name':<25} {'Risk':<8} {'Status':<12} {'Renewal Date':<12} {'Value':<12}")
        print("="*120)

        total_value = 0
        for client in clients:
            if days_to_renewal:
                days_diff = self._days_until(client['renewal_date'])
                if days_diff > days_to_renewal:
                    continue

            value_str = f"${client['contract_value']:,.0f}" if client['contract_value'] else "N/A"
            total_value += client['contract_value'] or 0

            print(f"{client['id']:<5} {client['account_id']:<15} {client['name']:<25} "
                  f"{client['risk_level']:<8} {client['status']:<12} {client['renewal_date']:<12} {value_str:<12}")

        print("="*120)
        print(f"Total clients: {len(clients)} | Total contract value: ${total_value:,.0f}\n")

    def view_client(self, account_id: str):
        """View detailed information about a client"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE account_id = ?", (account_id,))
        client = cursor.fetchone()

        if not client:
            print(f"Client '{account_id}' not found")
            return

        print("\n" + "="*80)
        print(f"CLIENT DETAILS: {client['name']}")
        print("="*80)
        print(f"Account ID:       {client['account_id']}")
        print(f"Contract Value:   ${client['contract_value']:,.0f}" if client['contract_value'] else "N/A")
        print(f"Renewal Date:     {client['renewal_date']}")
        print(f"Days to Renewal:  {self._days_until(client['renewal_date'])}")
        print(f"Risk Level:       {client['risk_level']}")
        print(f"Status:           {client['status']}")
        print(f"Account Owner:    {client['account_owner']}")
        print(f"Last Updated:     {client['last_updated']}")
        if client['notes']:
            print(f"Notes:            {client['notes']}")

        # Get issues
        cursor.execute("""
            SELECT * FROM issues
            WHERE client_id = ?
            ORDER BY issue_date DESC
        """, (client['id'],))
        issues = cursor.fetchall()

        if issues:
            print(f"\n{'-'*80}")
            print("ISSUES:")
            print(f"{'-'*80}")
            for issue in issues:
                print(f"  [{issue['severity']}] {issue['description']}")
                print(f"    Status: {issue['status']} | Category: {issue['issue_category'] or 'N/A'}")
                if issue['resolution']:
                    print(f"    Resolution: {issue['resolution']}")
                print()

        # Get actions
        cursor.execute("""
            SELECT * FROM actions
            WHERE client_id = ?
            ORDER BY action_date DESC
        """, (client['id'],))
        actions = cursor.fetchall()

        if actions:
            print(f"{'-'*80}")
            print("ACTIONS:")
            print(f"{'-'*80}")
            for action in actions:
                status_icon = "✓" if action['status'] == "Completed" else "○"
                print(f"  {status_icon} [{action['action_type']}] {action['description']}")
                print(f"    Status: {action['status']} | Owner: {action['owner'] or 'Unassigned'}")
                if action['due_date']:
                    print(f"    Due: {action['due_date']}")
                print()

        # Get weekly reviews
        cursor.execute("""
            SELECT * FROM weekly_reviews
            WHERE client_id = ?
            ORDER BY week_start DESC
            LIMIT 3
        """, (client['id'],))
        reviews = cursor.fetchall()

        if reviews:
            print(f"{'-'*80}")
            print("RECENT WEEKLY REVIEWS:")
            print(f"{'-'*80}")
            for review in reviews:
                print(f"  Week of {review['week_start']}:")
                print(f"    Summary: {review['summary']}")
                print(f"    Progress: {review['progress_status']}")
                if review['next_steps']:
                    print(f"    Next Steps: {review['next_steps']}")
                print()

        print("="*80 + "\n")

    def dashboard(self):
        """Show overview dashboard with key metrics"""
        cursor = self.conn.cursor()

        print("\n" + "="*80)
        print("CHURN RISK DASHBOARD")
        print("="*80)

        # Overall stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'At Risk' THEN 1 ELSE 0 END) as at_risk,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
                SUM(CASE WHEN status = 'Churned' THEN 1 ELSE 0 END) as churned,
                SUM(CASE WHEN status = 'Renewed' THEN 1 ELSE 0 END) as renewed,
                SUM(contract_value) as total_value
            FROM clients
        """)
        stats = cursor.fetchone()

        print(f"\nOVERALL STATUS:")
        print(f"  Total Clients:     {stats['total']}")
        print(f"  At Risk:           {stats['at_risk']}")
        print(f"  In Progress:       {stats['in_progress']}")
        print(f"  Resolved:          {stats['resolved']}")
        print(f"  Churned:           {stats['churned']}")
        print(f"  Renewed:           {stats['renewed']}")
        print(f"  Total Value:       ${stats['total_value']:,.0f}" if stats['total_value'] else "  Total Value:       $0")

        # Risk breakdown
        cursor.execute("""
            SELECT
                risk_level,
                COUNT(*) as count,
                SUM(contract_value) as value
            FROM clients
            WHERE status IN ('At Risk', 'In Progress')
            GROUP BY risk_level
        """)
        risk_stats = cursor.fetchall()

        if risk_stats:
            print(f"\nRISK BREAKDOWN (Active Only):")
            for risk in risk_stats:
                value_str = f"${risk['value']:,.0f}" if risk['value'] else "$0"
                print(f"  {risk['risk_level']:<10} {risk['count']:>3} clients | {value_str}")

        # Upcoming renewals
        cursor.execute("""
            SELECT COUNT(*) as count, SUM(contract_value) as value
            FROM clients
            WHERE renewal_date <= date('now', '+30 days')
            AND status NOT IN ('Churned', 'Renewed')
        """)
        upcoming = cursor.fetchone()

        print(f"\nUPCOMING RENEWALS (Next 30 days):")
        print(f"  Clients:           {upcoming['count']}")
        print(f"  Value at Risk:     ${upcoming['value']:,.0f}" if upcoming['value'] else "  Value at Risk:     $0")

        # Action items
        cursor.execute("""
            SELECT
                status,
                COUNT(*) as count
            FROM actions
            GROUP BY status
        """)
        action_stats = cursor.fetchall()

        if action_stats:
            print(f"\nACTION ITEMS:")
            for action in action_stats:
                print(f"  {action['status']:<15} {action['count']}")

        # Open issues
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM issues
            WHERE status IN ('Open', 'In Progress')
        """)
        open_issues = cursor.fetchone()

        print(f"\nOPEN ISSUES:         {open_issues['count']}")

        print("="*80 + "\n")

    def weekly_report(self, week_offset: int = 0):
        """Generate weekly report for review"""
        week_start = self._get_week_start(week_offset)
        week_end = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")

        cursor = self.conn.cursor()

        print("\n" + "="*100)
        print(f"WEEKLY CHURN RISK REPORT: {week_start} to {week_end}")
        print("="*100)

        # High priority clients
        cursor.execute("""
            SELECT * FROM clients
            WHERE risk_level = 'High'
            AND status IN ('At Risk', 'In Progress')
            ORDER BY renewal_date ASC
        """)
        high_risk = cursor.fetchall()

        if high_risk:
            print(f"\n🔴 HIGH RISK CLIENTS ({len(high_risk)}):")
            print(f"{'-'*100}")
            for client in high_risk:
                print(f"  • {client['name']} ({client['account_id']})")
                print(f"    Renewal: {client['renewal_date']} ({self._days_until(client['renewal_date'])} days) | "
                      f"Value: ${client['contract_value']:,.0f}" if client['contract_value'] else "Value: N/A")

                # Get recent actions
                cursor.execute("""
                    SELECT * FROM actions
                    WHERE client_id = ?
                    ORDER BY action_date DESC
                    LIMIT 2
                """, (client['id'],))
                recent_actions = cursor.fetchall()

                if recent_actions:
                    print(f"    Recent Actions:")
                    for action in recent_actions:
                        print(f"      - [{action['status']}] {action['description']}")
                print()

        # Clients needing review
        cursor.execute("""
            SELECT c.* FROM clients c
            LEFT JOIN weekly_reviews wr ON c.id = wr.client_id AND wr.week_start = ?
            WHERE c.status IN ('At Risk', 'In Progress')
            AND wr.id IS NULL
            ORDER BY c.risk_level, c.renewal_date
        """, (week_start,))
        needs_review = cursor.fetchall()

        if needs_review:
            print(f"\n⚠️  CLIENTS NEEDING WEEKLY REVIEW ({len(needs_review)}):")
            print(f"{'-'*100}")
            for client in needs_review:
                print(f"  • {client['name']} ({client['account_id']}) - {client['risk_level']} Risk")

        # Completed actions this week
        cursor.execute("""
            SELECT a.*, c.name, c.account_id
            FROM actions a
            JOIN clients c ON a.client_id = c.id
            WHERE a.completed_date >= ?
            AND a.completed_date <= ?
            ORDER BY a.completed_date DESC
        """, (week_start, week_end))
        completed = cursor.fetchall()

        if completed:
            print(f"\n✅ COMPLETED ACTIONS THIS WEEK ({len(completed)}):")
            print(f"{'-'*100}")
            for action in completed:
                print(f"  • {action['name']} ({action['account_id']}): {action['description']}")

        # Pending actions
        cursor.execute("""
            SELECT a.*, c.name, c.account_id
            FROM actions a
            JOIN clients c ON a.client_id = c.id
            WHERE a.status IN ('Pending', 'In Progress')
            AND (a.due_date <= ? OR a.due_date IS NULL)
            ORDER BY a.due_date ASC
        """, (week_end,))
        pending = cursor.fetchall()

        if pending:
            print(f"\n📋 PENDING/OVERDUE ACTIONS ({len(pending)}):")
            print(f"{'-'*100}")
            for action in pending:
                due = action['due_date'] or "No due date"
                print(f"  • {action['name']} ({action['account_id']}): {action['description']}")
                print(f"    Due: {due} | Owner: {action['owner'] or 'Unassigned'}")

        print("\n" + "="*100 + "\n")

    def export_data(self, output_file: str = "churn_export.json"):
        """Export all data to JSON for external analysis"""
        cursor = self.conn.cursor()

        data = {
            'clients': [],
            'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()

        for client in clients:
            client_data = dict(client)

            # Get related data
            cursor.execute("SELECT * FROM issues WHERE client_id = ?", (client['id'],))
            client_data['issues'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM actions WHERE client_id = ?", (client['id'],))
            client_data['actions'] = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT * FROM weekly_reviews WHERE client_id = ?", (client['id'],))
            client_data['weekly_reviews'] = [dict(row) for row in cursor.fetchall()]

            data['clients'].append(client_data)

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Exported data to {output_file}")

    def _get_client_id(self, account_id: str) -> Optional[int]:
        """Get client ID from account_id"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM clients WHERE account_id = ?", (account_id,))
        result = cursor.fetchone()
        return result['id'] if result else None

    def _get_week_start(self, offset: int = 0) -> str:
        """Get the start date (Monday) of the current week or offset weeks"""
        today = datetime.now()
        monday = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
        return monday.strftime("%Y-%m-%d")

    def _days_until(self, date_str: str) -> int:
        """Calculate days until a given date"""
        try:
            target = datetime.strptime(date_str, "%Y-%m-%d")
            delta = target - datetime.now()
            return delta.days
        except:
            return 999

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Churn Risk Tracker - Manage client renewal risks",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add client
    add_parser = subparsers.add_parser('add-client', help='Add a new at-risk client')
    add_parser.add_argument('--name', required=True, help='Client name')
    add_parser.add_argument('--account-id', required=True, help='Unique account ID')
    add_parser.add_argument('--value', type=float, required=True, help='Contract value')
    add_parser.add_argument('--renewal-date', required=True, help='Renewal date (YYYY-MM-DD)')
    add_parser.add_argument('--risk', required=True, choices=['High', 'Medium', 'Low'], help='Risk level')
    add_parser.add_argument('--status', default='At Risk', choices=['At Risk', 'In Progress', 'Resolved', 'Churned', 'Renewed'])
    add_parser.add_argument('--owner', default='', help='Account owner')
    add_parser.add_argument('--notes', default='', help='Additional notes')

    # Update client
    update_parser = subparsers.add_parser('update-client', help='Update client details')
    update_parser.add_argument('account_id', help='Account ID')
    update_parser.add_argument('--name', help='Client name')
    update_parser.add_argument('--value', type=float, help='Contract value')
    update_parser.add_argument('--renewal-date', help='Renewal date (YYYY-MM-DD)')
    update_parser.add_argument('--risk', choices=['High', 'Medium', 'Low'], help='Risk level')
    update_parser.add_argument('--status', choices=['At Risk', 'In Progress', 'Resolved', 'Churned', 'Renewed'])
    update_parser.add_argument('--owner', help='Account owner')
    update_parser.add_argument('--notes', help='Additional notes')

    # List clients
    list_parser = subparsers.add_parser('list', help='List clients with filters')
    list_parser.add_argument('--risk', choices=['High', 'Medium', 'Low'], help='Filter by risk level')
    list_parser.add_argument('--status', choices=['At Risk', 'In Progress', 'Resolved', 'Churned', 'Renewed'], help='Filter by status')
    list_parser.add_argument('--days', type=int, help='Show clients with renewal within X days')

    # View client
    view_parser = subparsers.add_parser('view', help='View detailed client information')
    view_parser.add_argument('account_id', help='Account ID')

    # Add action
    action_parser = subparsers.add_parser('add-action', help='Add action item for client')
    action_parser.add_argument('account_id', help='Account ID')
    action_parser.add_argument('--type', required=True, choices=['Call', 'Email', 'Meeting', 'Escalation', 'Follow-up', 'Other'])
    action_parser.add_argument('--description', required=True, help='Action description')
    action_parser.add_argument('--owner', default='', help='Action owner')
    action_parser.add_argument('--status', default='Pending', choices=['Pending', 'In Progress', 'Completed', 'Blocked'])
    action_parser.add_argument('--due', default='', help='Due date (YYYY-MM-DD)')

    # Update action
    update_action_parser = subparsers.add_parser('update-action', help='Update action status')
    update_action_parser.add_argument('action_id', type=int, help='Action ID')
    update_action_parser.add_argument('--status', required=True, choices=['Pending', 'In Progress', 'Completed', 'Blocked'])

    # Add issue
    issue_parser = subparsers.add_parser('add-issue', help='Add issue for client')
    issue_parser.add_argument('account_id', help='Account ID')
    issue_parser.add_argument('--description', required=True, help='Issue description')
    issue_parser.add_argument('--category', default='', help='Issue category')
    issue_parser.add_argument('--severity', default='Medium', choices=['Critical', 'High', 'Medium', 'Low'])

    # Add weekly review
    review_parser = subparsers.add_parser('add-review', help='Add weekly review for client')
    review_parser.add_argument('account_id', help='Account ID')
    review_parser.add_argument('--summary', required=True, help='Review summary')
    review_parser.add_argument('--progress', required=True, help='Progress status')
    review_parser.add_argument('--next-steps', default='', help='Next steps')
    review_parser.add_argument('--reviewed-by', default='', help='Reviewer name')

    # Dashboard
    subparsers.add_parser('dashboard', help='Show overview dashboard')

    # Weekly report
    report_parser = subparsers.add_parser('weekly-report', help='Generate weekly report')
    report_parser.add_argument('--week-offset', type=int, default=0, help='Week offset (0=current, -1=last week, etc.)')

    # Export
    export_parser = subparsers.add_parser('export', help='Export data to JSON')
    export_parser.add_argument('--output', default='churn_export.json', help='Output file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    tracker = ChurnTracker()

    try:
        if args.command == 'add-client':
            tracker.add_client(
                args.name, args.account_id, args.value, args.renewal_date,
                args.risk, args.status, args.owner, args.notes
            )

        elif args.command == 'update-client':
            updates = {}
            if args.name: updates['name'] = args.name
            if args.value: updates['contract_value'] = args.value
            if args.renewal_date: updates['renewal_date'] = args.renewal_date
            if args.risk: updates['risk_level'] = args.risk
            if args.status: updates['status'] = args.status
            if args.owner: updates['account_owner'] = args.owner
            if args.notes: updates['notes'] = args.notes
            tracker.update_client(args.account_id, **updates)

        elif args.command == 'list':
            tracker.list_clients(args.risk, args.status, args.days)

        elif args.command == 'view':
            tracker.view_client(args.account_id)

        elif args.command == 'add-action':
            tracker.add_action(args.account_id, args.type, args.description,
                             args.owner, args.status, args.due)

        elif args.command == 'update-action':
            tracker.update_action(args.action_id, args.status)

        elif args.command == 'add-issue':
            tracker.add_issue(args.account_id, args.description,
                            args.category, args.severity)

        elif args.command == 'add-review':
            tracker.add_weekly_review(args.account_id, args.summary,
                                    args.progress, args.next_steps, args.reviewed_by)

        elif args.command == 'dashboard':
            tracker.dashboard()

        elif args.command == 'weekly-report':
            tracker.weekly_report(args.week_offset)

        elif args.command == 'export':
            tracker.export_data(args.output)

    finally:
        tracker.close()


if __name__ == '__main__':
    main()
