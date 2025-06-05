import sqlite3
from lib.employee import Employee
from department import Department
#from employee import Employee


class Review:
    # Class-level dictionary to cache Review instances/of objects saved to the db.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    # def __repr__(self):
    #     return (
    #         f"<Review {self.id}: {self.year}, {self.summary}, "
    #         + f"Employee: {self.employee_id}>"
    #     )
    def __repr__(self):
        return f"<Review id={self.id} year={self.year} summary={self.summary} employee_id={self.employee_id}>"

    @classmethod
    def create_table(cls):
        from lib.__init__ import CONN, CURSOR
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        from lib.__init__ import CONN, CURSOR
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()
# ORM methods
    def save(self):
        from lib.__init__ import CONN, CURSOR
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""

        # if self.id is None:
        #     CURSOR.execute("""
        #         INSERT INTO reviews (year, summary, employee_id)
        #         VALUES (?, ?, ?)
        #     """, (self._year, self._summary, self._employee_id))
        #     self.id = CURSOR.lastrowid
        #     Review._registry[self.id] = self
        #     CONN.commit()
        # else:
        #     self.update()

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
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key

        review_id = row[0]
        # Check if instance exists in dictionary
        if review_id in cls._all:
            return cls._all[review_id]
        # Create new instance and add to dictionary
        review = cls(row[1], row[2], row[3], row[0])
        cls._all[review.id] = review
        return review
    
        # if review_id in cls._registry:
        #     return cls._registry[review_id]
        
        # review = cls(row[1], row[2], row[3], id=review_id)
        # cls._registry[review_id] = review
        # return review
   

    @classmethod
    def find_by_id(cls, id):
        from lib.__init__ import CONN, CURSOR
        """Return a Review instance having the attribute values from the table row."""
        # CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        # row = CURSOR.fetchone()
        # return cls.instance_from_db(row) if row else None

        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        from lib.__init__ import CONN, CURSOR
        """Update the table row corresponding to the current Review instance."""
        # CURSOR.execute("""
        #     UPDATE reviews
        #     SET year = ?, summary = ?, employee_id = ?
        #     WHERE id = ?
        # """, (self._year, self._summary, self._employee_id, self.id))
        # CONN.commit()

        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        from lib.__init__ import CONN, CURSOR
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        # if self.id:
        #     CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        #     CONN.commit()
        #     Review._registry.pop(self.id, None)
        #     self.id = None

        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        # Remove from dictionary and reset id
        del Review._all[self.id]
        self.id = None


    @classmethod
    def get_all(cls):
        from lib.__init__ import CONN, CURSOR
        """Return a list containing one Review instance per table row"""
        # CURSOR.execute("SELECT * FROM reviews")
        # rows = CURSOR.fetchall()
        # return [cls.instance_from_db(row) for row in rows]

        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    # Property methods
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

