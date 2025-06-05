# lib/employee.py
from __init__ import CURSOR, CONN
from department import Department

class Employee:
    _all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self._name = name
        self._job_title = job_title
        self._department_id = department_id
        self.id = id

    def __repr__(self):
        return f"<Employee id={self.id} name={self.name} job_title={self.job_title} department_id={self.department_id}>"

    @classmethod
    def create_table(cls):
        from lib.__init__ import CONN, CURSOR
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        from lib.__init__ import CONN, CURSOR
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        from lib.__init__ import CONN, CURSOR
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Employee._all[self.id] = self

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def find_by_id(cls, id):
        from lib.__init__ import CONN, CURSOR
        sql = "SELECT * FROM employees WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def instance_from_db(cls, row):
        if row is None:
            return None
        employee_id, name, job_title, department_id = row
        if employee_id in cls._all:
            return cls._all[employee_id]
        employee = cls(name, job_title, department_id, employee_id)
        cls._all[employee.id] = employee
        return employee

    @classmethod
    def get_all(cls):
        from lib.__init__ import CONN, CURSOR
        sql = "SELECT * FROM employees"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property methods
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Name cannot be empty")
        self._name = value

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise ValueError("Job title must be a string")
        if len(value.strip()) == 0:
            raise ValueError("Job title cannot be empty")
        self._job_title = value

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        department = Department.find_by_id(value)
        if not department:
            raise ValueError("Department ID must correspond to an existing Department")
        self._department_id = value

    def reviews(self):
        from lib.__init__ import CONN, CURSOR
        sql = "SELECT * FROM reviews WHERE employee_id = ?"
        CURSOR.execute(sql, (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows if row] or []