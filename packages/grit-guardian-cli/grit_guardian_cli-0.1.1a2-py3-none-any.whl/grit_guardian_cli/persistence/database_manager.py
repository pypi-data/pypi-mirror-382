import sqlite3
import shutil  # For high-level operations on files
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


# Date and time datatypes in SQLite are stored as TEXT ("YYYY-MM-DD HH:MM:SS.SSS")
# See: https://www.sqlite.org/datatype3.html
def adapt_datetime(dt):
    """Converts datetime to ISO format string for SQLite."""
    return dt.isoformat()


def convert_datetime(s):
    """Converts ISO format string from SQLite to datetime."""
    return datetime.fromisoformat(s.decode())


# For proper date and time handling we register adapter and converter callables.
# See: https://docs.python.org/3/library/sqlite3.html#how-to-convert-sqlite-values-to-custom-python-types
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("TIMESTAMP", convert_datetime)


class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        """Initializes the database manager.

        Args:
            db_path: Optional custom database path. If None, uses default XDG config location.
        """
        self.db_path = db_path or self._get_default_db_path()
        self._ensure_config_dir()
        self._init_database()

    def _get_default_db_path(self) -> Path:
        """Gets the default database path following XDG Base Directory specification."""
        config_dir = Path.home() / ".config" / "grit-guardian-cli"  # path concatenation
        return config_dir / "habits.db"

    def _ensure_config_dir(self):
        """Ensures the configuration directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _init_database(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")

            # Create habits table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS habits(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    task TEXT NOT NULL,
                    periodicity TEXT CHECK(periodicity IN ('daily', 'weekly')) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
                    );
            """)

            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_completions_habit_id
                ON completions(habit_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_completions_completed_at
                ON completions(completed_at)
            """)

    @contextmanager
    def _get_connection(self):
        """Context manager for database connection."""
        conn = None
        try:
            # PRAGMA is specific to SQLite
            # is used for db engine configuration
            # and querying of internal state and metadata
            # https://www.sqlite.org/pragma.html
            conn = sqlite3.connect(
                self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
            )  # Use PARSE_DECLTYPES in detect_types param to enable auto type conversion
            conn.row_factory = sqlite3.Row
            # Enable foreign key constraints for this connection
            conn.execute(
                "PRAGMA foreign_keys = ON"
            )  # By default, foreign keys are not enforced
            yield conn
            conn.commit()
        # DatabaseError is the base exception class for all errors related to database interactions
        # https://docs.python.org/3/library/sqlite3.html#sqlite3.DatabaseError
        except sqlite3.DatabaseError as e:
            if conn:
                conn.rollback()
            # Attempt to restore from backup if database is corrupted
            if "database disk image is malformed" in str(
                e
            ) or "file is not a database" in str(e):
                self._restore_from_backup()
                raise Exception(
                    "Database was corrupted. Restored from backup. Please retry operation."
                )
            raise
        finally:
            if conn:
                conn.close()

    def create_habit(self, name: str, task: str, periodicity: str) -> int | None:
        """Creates a new habit.

        Args:
            name: Unique name for the habit
            task: Description of the task
            periodicity: Either 'daily' or 'weekly'

        Returns:
            The ID of the created habit

        Raises:
            sqlite3.IntegrityError: if habit with same name already exists
            ValueError: If periodicity is invalid
        """
        if periodicity not in ("daily", "weekly"):
            raise ValueError(
                f"Invalid periodicity: {periodicity}. Must be 'daily' or 'weekly'"
            )

        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO habits (name, task, periodicity) VALUES (?, ?, ?);",
                (name, task, periodicity),
            )
            return cursor.lastrowid

    def get_habits(self) -> List[Dict[str, Any]]:
        """Gets all habits with their completion counts.

        Returns:
            List of habit dictionaries with completion information
        """
        with self._get_connection() as conn:
            habits = conn.execute("""
                SELECT
                    h.id,
                    h.name,
                    h.task,
                    h.periodicity,
                    h.created_at,
                    COUNT(c.id) as total_completions,
                    MAX(c.completed_at) as last_completed
                FROM habits h
                LEFT JOIN completions c ON h.id = c.habit_id
                GROUP BY h.id
                ORDER BY h.created_at DESC
            """).fetchall()

            return [dict(habit) for habit in habits]

    def get_habit_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Gets a specific habit by name.

        Args:
            name: The habit name

        Returns:
            Habit dictionary or None if not found
        """
        with self._get_connection() as conn:
            habit = conn.execute(
                "SELECT * FROM habits WHERE name = ?;", (name,)
            ).fetchone()

            return dict(habit) if habit else None

    def delete_habit(self, name: str) -> bool:
        """Deletes a habit and all its completions.

        Args:
            name: The habit name to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM habits WHERE name = ?;", (name,))
            return (
                cursor.rowcount > 0
            )  # check whether the DELETE operation actually deleted any rows from the db

    def add_completion(
        self, habit_name: str, completed_at: Optional[datetime] = None
    ) -> int | None:
        """Adds a completion record for a habit.

        Args:
            habit_name: Name of the habit to complete
            completed_at: Optional completion timestamp (defaults to now)

        Raises:
            ValueError: If habit not found or completion date is in the future
        """
        # Defaults to current timestamp if no date is provided
        if completed_at is None:
            completed_at = datetime.now()

        # Validate that completion date is not in the future
        if completed_at > datetime.now():
            raise ValueError("Completion date cannot be in the future")

        with self._get_connection() as conn:
            # Get habit ID
            habit = conn.execute(
                "SELECT id FROM habits WHERE name = ?;", (habit_name,)
            ).fetchone()

            if not habit:
                raise ValueError(f"Quest '{habit_name}' not found")

            cursor = conn.execute(
                "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
                (habit["id"], completed_at),
            )
            return cursor.lastrowid

    def get_completions(
        self, habit_name: str, limit: Optional[int] = None
    ) -> List[datetime]:
        """Gets completion timestamps for a habit.

        Args:
            habit_name: Name of the habit
            limit: Optional limit on number of completions to return

        Returns:
            List of completion timestamps, most recent first
        """
        with self._get_connection() as conn:
            query = """
                SELECT c.completed_at
                FROM completions c
                JOIN habits h ON c.habit_id = h.id
                WHERE h.name = ? 
                ORDER BY c.completed_at DESC
            """

            if limit:
                query += f" LIMIT {limit}"

            completions = conn.execute(query, (habit_name,)).fetchall()
            # completed_at is already a datetime object due to PARSE_DECLTYPES
            return [c["completed_at"] for c in completions]

    def backup_database(self) -> Path:
        """Creates a backup of the database.

        Returns:
            Path to the backup file
        """
        backup_path = self.db_path.with_suffix(".db.backup")
        shutil.copy2(self.db_path, backup_path)
        return backup_path

    def _restore_from_backup(self):
        """Restores database from backup if it exists."""
        backup_path = self.db_path.with_suffix(".db.backup")
        if backup_path.exists():
            shutil.copy2(backup_path, self.db_path)
        else:
            # If no backup exists, move corrupted database aside and create new one
            corrupted_path = self.db_path.with_suffix(".db.corrupted")
            shutil.move(str(self.db_path), str(corrupted_path))
            self._init_database()

    def get_stats(self) -> Dict[str, Any]:
        """Gets overall statistics about habits and completions.

        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            stats = {
                "total_habits": conn.execute("SELECT COUNT(*) FROM habits;").fetchone()[
                    0
                ],
                "total_completions": conn.execute(
                    "SELECT COUNT(*) FROM completions;"
                ).fetchone()[0],
                "habits_by_periodicity": {},
            }

            # Get count by periodicity
            periodicity_counts = conn.execute("""
                SELECT periodicity, COUNT(*) as count
                FROM habits
                GROUP BY periodicity
            """).fetchall()

            for row in periodicity_counts:
                stats["habits_by_periodicity"][row["periodicity"]] = row["count"]

            return stats
