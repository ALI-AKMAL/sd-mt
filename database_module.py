import sqlite3
import hashlib

class DatabaseManager:
    """Manages user authentication and settings."""

    def __init__(self, db_name='system_monitor.db'):
        self.db_name = db_name
        
        self.create_tables()
        self._migrate()
    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # users — no email; includes security question/answer
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id           INTEGER PRIMARY KEY AUTOINCREMENT,
                username          TEXT UNIQUE NOT NULL,
                password_hash     TEXT NOT NULL,
                full_name         TEXT NOT NULL,
                security_question TEXT NOT NULL DEFAULT '',
                security_answer   TEXT NOT NULL DEFAULT '',
                created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login        TIMESTAMP,
                is_active         INTEGER DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                login_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP,
                ip_address  TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                log_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                action    TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details   TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id                INTEGER PRIMARY KEY,
                theme                  TEXT NOT NULL DEFAULT 'dark',
                update_interval        INTEGER NOT NULL DEFAULT 500,
                auto_start_monitoring  INTEGER NOT NULL DEFAULT 1,
                show_notifications     INTEGER NOT NULL DEFAULT 1,
                updated_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
        print('[OK] Database tables ready')

    def _migrate(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Fetch current column names
        cursor.execute("PRAGMA table_info(users)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        new_cols = {
            'security_question': "ALTER TABLE users ADD COLUMN security_question TEXT NOT NULL DEFAULT ''",
            'security_answer':   "ALTER TABLE users ADD COLUMN security_answer   TEXT NOT NULL DEFAULT ''",
        }

        for col, sql in new_cols.items():
            if col not in existing_cols:
                cursor.execute(sql)
                print(f'[MIGRATE] Added column: {col}')

        conn.commit()
        conn.close()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, full_name,
                      security_question='', security_answer=''):
        """
        Register a new user.
        security_answer should be passed in already lowercased by the caller
        so comparisons are case-insensitive.
        """
        try:
            if not username or not password or not full_name:
                return False, 'All fields are required', None
            if len(username) < 3:
                return False, 'Username must be at least 3 characters', None
            if len(password) < 6:
                return False, 'Password must be at least 6 characters', None
            if not security_question or not security_answer:
                return False, 'Security question and answer are required', None

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return False, 'Username already exists', None

            password_hash = self.hash_password(password)

            cursor.execute(
                """
                INSERT INTO users
                    (username, password_hash, full_name, security_question, security_answer)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, password_hash, full_name,
                 security_question, security_answer.lower()),
            )
            user_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO user_settings
                    (user_id, theme, update_interval, auto_start_monitoring, show_notifications)
                VALUES (?, 'dark', 500, 1, 1)
                """,
                (user_id,),
            )

            cursor.execute(
                """
                INSERT INTO activity_log (user_id, action, details)
                VALUES (?, ?, ?)
                """,
                (user_id, 'REGISTER', f'New user registered: {username}'),
            )

            conn.commit()
            conn.close()
            return True, 'Registration successful!', user_id

        except sqlite3.IntegrityError as e:
            return False, f'Database error: {e}', None
        except Exception as e:
            return False, f'Error: {e}', None

    def login_user(self, username, password):
        try:
            if not username or not password:
                return False, 'Username and password required', None

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            password_hash = self.hash_password(password)

            cursor.execute(
                """
                SELECT user_id, username, full_name, is_active
                FROM users
                WHERE username = ? AND password_hash = ?
                """,
                (username, password_hash),
            )
            user = cursor.fetchone()

            if not user:
                conn.close()
                return False, 'Invalid username or password', None

            user_id, username, full_name, is_active = user
            if not is_active:
                conn.close()
                return False, 'Account is deactivated', None

            cursor.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?',
                (user_id,),
            )
            cursor.execute(
                'INSERT INTO sessions (user_id, ip_address) VALUES (?, ?)',
                (user_id, 'localhost'),
            )
            session_id = cursor.lastrowid

            cursor.execute(
                'INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)',
                (user_id, 'LOGIN', f'User logged in: {username}'),
            )

            conn.commit()
            conn.close()

            return True, 'Login successful!', {
                'user_id':    user_id,
                'username':   username,
                'full_name':  full_name,
                'session_id': session_id,
            }

        except Exception as e:
            return False, f'Error: {e}', None

    def logout_user(self, session_id, user_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE sessions SET logout_time = CURRENT_TIMESTAMP WHERE session_id = ?',
                (session_id,),
            )
            cursor.execute(
                'INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)',
                (user_id, 'LOGOUT', 'User logged out'),
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f'Logout error: {e}')
            return False

    # ------------------------------------------------------------------
    # FORGOT PASSWORD — security question/answer flow
    # ------------------------------------------------------------------

    def get_security_question(self, username):
        """
        Returns the security question string for the given username,
        or None if the username does not exist.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT security_question FROM users WHERE username = ?',
                (username,),
            )
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            print(f'Error fetching security question: {e}')
            return None

    def reset_password_with_answer(self, username, answer, new_password):
        """
        Verifies the security answer (case-insensitive) then resets the password.
        Returns (success: bool, message: str).
        """
        try:
            if len(new_password) < 6:
                return False, 'Password must be at least 6 characters'

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                'SELECT user_id, security_answer FROM users WHERE username = ?',
                (username,),
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False, 'Username not found'

            user_id, stored_answer = row

            if stored_answer.lower() != answer.lower():
                conn.close()
                return False, 'Incorrect answer to security question'

            new_hash = self.hash_password(new_password)
            cursor.execute(
                'UPDATE users SET password_hash = ? WHERE user_id = ?',
                (new_hash, user_id),
            )
            cursor.execute(
                'INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)',
                (user_id, 'PASSWORD_RESET', f'Password reset via security question for: {username}'),
            )
            conn.commit()
            conn.close()
            return True, 'Password reset successfully!'

        except Exception as e:
            return False, f'Error: {e}'

    # ------------------------------------------------------------------
    # USER INFO & SETTINGS
    # ------------------------------------------------------------------

    def get_user_info(self, user_id):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT username, full_name, created_at, last_login
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            )
            user = cursor.fetchone()
            conn.close()
            if user:
                return {
                    'username':   user[0],
                    'full_name':  user[1],
                    'created_at': user[2],
                    'last_login': user[3],
                }
            return None
        except Exception as e:
            print(f'Error getting user info: {e}')
            return None

    def get_user_activity(self, user_id, limit=10):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT action, timestamp, details
                FROM activity_log
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            activities = cursor.fetchall()
            conn.close()
            return [
                {'action': act[0], 'timestamp': act[1], 'details': act[2]}
                for act in activities
            ]
        except Exception as e:
            print(f'Error getting activity: {e}')
            return []

    def change_password(self, user_id, old_password, new_password):
        try:
            if len(new_password) < 6:
                return False, 'New password must be at least 6 characters'

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            old_hash = self.hash_password(old_password)
            cursor.execute(
                'SELECT user_id FROM users WHERE user_id = ? AND password_hash = ?',
                (user_id, old_hash),
            )
            if not cursor.fetchone():
                conn.close()
                return False, 'Current password is incorrect'

            new_hash = self.hash_password(new_password)
            cursor.execute(
                'UPDATE users SET password_hash = ? WHERE user_id = ?',
                (new_hash, user_id),
            )
            cursor.execute(
                'INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)',
                (user_id, 'PASSWORD_CHANGE', 'Password changed successfully'),
            )
            conn.commit()
            conn.close()
            return True, 'Password changed successfully'
        except Exception as e:
            return False, f'Error: {e}'

    def get_user_settings(self, user_id):
        defaults = {
            'theme': 'dark',
            'update_interval': 500,
            'auto_start_monitoring': True,
            'show_notifications': True,
        }
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT theme, update_interval, auto_start_monitoring, show_notifications
                FROM user_settings
                WHERE user_id = ?
                """,
                (user_id,),
            )
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    """
                    INSERT INTO user_settings
                        (user_id, theme, update_interval, auto_start_monitoring, show_notifications)
                    VALUES (?, 'dark', 500, 1, 1)
                    """,
                    (user_id,),
                )
                conn.commit()
                conn.close()
                return defaults
            conn.close()
            return {
                'theme':                 row[0] if row[0] in ('dark', 'light') else 'dark',
                'update_interval':       int(row[1]) if row[1] else 500,
                'auto_start_monitoring': bool(row[2]),
                'show_notifications':    bool(row[3]),
            }
        except Exception as e:
            print(f'Error loading settings: {e}')
            return defaults

    def save_user_settings(self, user_id, theme, update_interval,
                           auto_start_monitoring, show_notifications):
        try:
            if theme not in ('dark', 'light'):
                return False, 'Invalid theme'
            if int(update_interval) not in (250, 500, 1000, 2000, 5000):
                return False, 'Invalid update interval'

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_settings
                    (user_id, theme, update_interval, auto_start_monitoring,
                     show_notifications, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    theme                 = excluded.theme,
                    update_interval       = excluded.update_interval,
                    auto_start_monitoring = excluded.auto_start_monitoring,
                    show_notifications    = excluded.show_notifications,
                    updated_at            = CURRENT_TIMESTAMP
                """,
                (user_id, theme, int(update_interval),
                 int(bool(auto_start_monitoring)), int(bool(show_notifications))),
            )
            cursor.execute(
                'INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)',
                (
                    user_id,
                    'SETTINGS_UPDATE',
                    (f'theme={theme}, interval={int(update_interval)}, '
                     f'auto_start={int(bool(auto_start_monitoring))}, '
                     f'notifications={int(bool(show_notifications))}'),
                ),
            )
            conn.commit()
            conn.close()
            return True, 'Settings saved successfully'
        except Exception as e:
            return False, f'Error: {e}'