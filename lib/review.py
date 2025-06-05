import sqlite3
from lib.employee import Employee

class Review:
    # Class-level dictionary to cache Review instances
    _all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self._year = year
        self._summary = summary
        self._employee_id = employee_id
        self.id = id

    def __repr__(self):
        return f"<Review id={self.id} year={self.year} summary={self.summary} employee_id={self.employee_id}>"

    @classmethod
    def create_table(cls):
        from lib.__init__ import CONN, CURSOR
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        from lib.__init__ import CONN, CURSOR
        sql = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(sql)
        CONN.commit()

    # ORM Methods
    def save(self):
        from lib.__init__ import CONN, CURSOR
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Review._all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review_id = row[0]
        # Check if instance exists in dictionary
        if review_id in cls._all:
            return cls._all[review_id]
        # Create new instance and add to dictionary
        review = cls(row[1], row[2], row[3], row[0])
        cls._all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        from lib.__init__ import CONN, CURSOR
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        from lib.__init__ import CONN, CURSOR
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        from lib.__init__ import CONN, CURSOR
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        # Remove from dictionary and reset id
        if self.id in Review._all:
            del Review._all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        from lib.__init__ import CONN, CURSOR
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property Methods
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be greater than or equal to 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):
            raise ValueError("Summary must be a string")
        if not value.strip():
            raise ValueError("Summary cannot be empty")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Check if employee_id corresponds to a persisted Employee
        employee = Employee.find_by_id(value)
        if not employee:
            raise ValueError("Employee ID must correspond to an existing Employee in the database")
        self._employee_id = value