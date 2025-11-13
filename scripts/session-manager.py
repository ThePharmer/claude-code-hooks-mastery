#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "python-dateutil>=2.8.0",
# ]
# ///

"""
Session Manager for Claude Code Hooks Mastery

Provides utilities to:
- Clean up old sessions
- Show session statistics
- Export session data
- Analyze session patterns
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class SessionManager:
    """Manage Claude Code session data."""

    def __init__(self, sessions_dir: str = ".claude/data/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def list_sessions(self) -> List[Dict]:
        """List all sessions with metadata."""
        sessions = []

        if not self.sessions_dir.exists():
            return sessions

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)

                sessions.append({
                    'id': session_file.stem,
                    'file': str(session_file),
                    'agent_name': data.get('agent_name', 'Unnamed'),
                    'created': data.get('created', 'Unknown'),
                    'prompt_count': len(data.get('prompts', [])),
                    'last_prompt': data.get('prompts', [])[-1] if data.get('prompts') else None,
                })
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not read {session_file}: {e}", file=sys.stderr)
                continue

        # Sort by created timestamp (newest first)
        sessions.sort(key=lambda x: x.get('created', ''), reverse=True)
        return sessions

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get a specific session by ID."""
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading session {session_id}: {e}", file=sys.stderr)
            return None

    def cleanup_old_sessions(self, days: int = 30, dry_run: bool = True) -> List[str]:
        """Remove sessions older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        removed = []

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(session_file.stat().st_mtime)

                if mtime < cutoff:
                    if dry_run:
                        removed.append(str(session_file))
                        print(f"Would remove: {session_file.name} (modified: {mtime.strftime('%Y-%m-%d')})")
                    else:
                        session_file.unlink()
                        removed.append(str(session_file))
                        print(f"Removed: {session_file.name}")
            except (IOError, OSError) as e:
                print(f"Warning: Could not process {session_file}: {e}", file=sys.stderr)
                continue

        return removed

    def get_statistics(self) -> Dict:
        """Calculate session statistics."""
        sessions = self.list_sessions()

        if not sessions:
            return {
                'total_sessions': 0,
                'total_prompts': 0,
                'avg_prompts_per_session': 0,
                'unique_agents': 0,
                'agent_names': [],
                'oldest_session': None,
                'newest_session': None,
            }

        total_prompts = sum(s['prompt_count'] for s in sessions)
        agent_names = [s['agent_name'] for s in sessions if s['agent_name'] != 'Unnamed']
        unique_agents = len(set(agent_names))

        # Get agent name frequency
        agent_freq = {}
        for name in agent_names:
            agent_freq[name] = agent_freq.get(name, 0) + 1

        # Sort by frequency
        top_agents = sorted(agent_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'total_sessions': len(sessions),
            'total_prompts': total_prompts,
            'avg_prompts_per_session': total_prompts / len(sessions) if sessions else 0,
            'unique_agents': unique_agents,
            'agent_names': agent_names,
            'top_agents': top_agents,
            'oldest_session': sessions[-1] if sessions else None,
            'newest_session': sessions[0] if sessions else None,
        }

    def export_session(self, session_id: str, output_file: Optional[str] = None) -> bool:
        """Export a session to a file."""
        session = self.get_session(session_id)

        if not session:
            print(f"Session {session_id} not found", file=sys.stderr)
            return False

        if output_file is None:
            output_file = f"session_{session_id}_export.json"

        try:
            with open(output_file, 'w') as f:
                json.dump(session, f, indent=2)
            print(f"Exported session {session_id} to {output_file}")
            return True
        except IOError as e:
            print(f"Error exporting session: {e}", file=sys.stderr)
            return False

    def export_all_statistics(self, output_file: str = "session_statistics.json") -> bool:
        """Export comprehensive statistics."""
        stats = self.get_statistics()
        sessions = self.list_sessions()

        export_data = {
            'generated': datetime.now().isoformat(),
            'statistics': stats,
            'sessions': [
                {
                    'id': s['id'],
                    'agent_name': s['agent_name'],
                    'created': s['created'],
                    'prompt_count': s['prompt_count'],
                }
                for s in sessions
            ],
        }

        try:
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"Exported statistics to {output_file}")
            return True
        except IOError as e:
            print(f"Error exporting statistics: {e}", file=sys.stderr)
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Claude Code Session Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all sessions
  %(prog)s list

  # Show statistics
  %(prog)s stats

  # Clean up sessions older than 30 days (dry run)
  %(prog)s cleanup --days 30

  # Actually remove old sessions
  %(prog)s cleanup --days 30 --execute

  # Export a specific session
  %(prog)s export <session-id>

  # Export all statistics
  %(prog)s export-stats
        """
    )

    parser.add_argument(
        'command',
        choices=['list', 'stats', 'cleanup', 'export', 'export-stats'],
        help='Command to execute'
    )
    parser.add_argument(
        'session_id',
        nargs='?',
        help='Session ID (for export command)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for cleanup (default: 30)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually perform cleanup (default is dry run)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output file for export'
    )
    parser.add_argument(
        '--sessions-dir',
        default='.claude/data/sessions',
        help='Sessions directory (default: .claude/data/sessions)'
    )

    args = parser.parse_args()
    manager = SessionManager(args.sessions_dir)

    if args.command == 'list':
        sessions = manager.list_sessions()

        if not sessions:
            print("No sessions found")
            return

        print(f"\n{'ID':<40} {'Agent Name':<30} {'Prompts':<10} {'Created':<20}")
        print("-" * 100)

        for session in sessions[:20]:  # Show last 20
            print(f"{session['id']:<40} {session['agent_name']:<30} {session['prompt_count']:<10} {session['created']:<20}")

        if len(sessions) > 20:
            print(f"\n... and {len(sessions) - 20} more sessions")

    elif args.command == 'stats':
        stats = manager.get_statistics()

        print("\n=== Session Statistics ===\n")
        print(f"Total Sessions: {stats['total_sessions']}")
        print(f"Total Prompts: {stats['total_prompts']}")
        print(f"Avg Prompts/Session: {stats['avg_prompts_per_session']:.2f}")
        print(f"Unique Agent Names: {stats['unique_agents']}")

        if stats['oldest_session']:
            print(f"\nOldest Session: {stats['oldest_session']['id']} ({stats['oldest_session']['created']})")
        if stats['newest_session']:
            print(f"Newest Session: {stats['newest_session']['id']} ({stats['newest_session']['created']})")

        if stats.get('top_agents'):
            print(f"\n=== Top Agent Names ===\n")
            for name, count in stats['top_agents']:
                print(f"  {name:<40} {count:>3} sessions")

    elif args.command == 'cleanup':
        print(f"\nCleaning up sessions older than {args.days} days...")
        if not args.execute:
            print("(DRY RUN - use --execute to actually remove files)\n")

        removed = manager.cleanup_old_sessions(args.days, dry_run=not args.execute)

        print(f"\n{'Removed' if args.execute else 'Would remove'}: {len(removed)} sessions")

    elif args.command == 'export':
        if not args.session_id:
            print("Error: session_id required for export command", file=sys.stderr)
            sys.exit(1)

        success = manager.export_session(args.session_id, args.output)
        sys.exit(0 if success else 1)

    elif args.command == 'export-stats':
        output_file = args.output or 'session_statistics.json'
        success = manager.export_all_statistics(output_file)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
