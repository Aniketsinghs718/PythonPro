# Base class (Parent class)
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display_person_info(self):
        print(f"Name: {self.name}, Age: {self.age}")

# Derived class (Child class)
class Employee(Person):
    def __init__(self, name, age, employee_id, department):
        super().__init__(name, age)  # Call parent class constructor
        self.employee_id = employee_id
        self.department = department

    def display_employee_info(self):
        self.display_person_info()  # Call parent method
        print(f"Employee ID: {self.employee_id}, Department: {self.department}")

# Creating an Employee object
emp = Employee("John Doe", 30, "E12345", "IT")

# Display employee information
emp.display_employee_info()
