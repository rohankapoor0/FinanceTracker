import re
from abc import ABC, abstractmethod
from database import db, TransactionModel
from datetime import datetime

# Custom Exception for validation errors
class InvalidTransactionError(Exception):
    """Exception raised for invalid transactions."""
    def __init__(self, message):
        super().__init__(message)

# Abstract Base Class with Abstraction
class Transaction(ABC):
    """Abstract base class for transactions, enforcing get_details method in subclasses."""
    total_transactions = 0

    def __init__(self, name, amount, source, date):
        """Initialize a transaction with name, amount, source, and date."""
        self._name = name
        self._amount = amount
        self._source = source
        self._date = date
        Transaction.total_transactions += 1

    @property
    def amount(self):
        """Getter for amount."""
        return self._amount

    @amount.setter
    def amount(self, value):
        """Setter for amount with validation."""
        if not self.validate_amount(value):
            raise InvalidTransactionError("Invalid amount. Must be a positive number with up to 2 decimal places.")
        self._amount = value

    @abstractmethod
    def get_details(self):
        """Abstract method to get transaction details, must be implemented by subclasses."""
        pass

    @staticmethod
    def validate_amount(amount_str):
        """Validate amount format."""
        pattern = r'^\d+(\.\d{1,2})?$'
        return re.match(pattern, str(amount_str))

    @staticmethod
    def validate_date(date_str):
        """Validate date format."""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return re.match(pattern, date_str)

    @staticmethod
    def validate_source(source):
        """Validate source format."""
        pattern = r'^[A-Za-z\s]+$'
        return re.match(pattern, source)

class Expense(Transaction):
    """Represents an expense transaction."""
    def __init__(self, name, amount, source, date):
        super().__init__(name, amount, source, date)

    def get_details(self):
        """Returns details of the expense transaction."""
        return f"Expense: {self._name}, Amount: {self._amount}, Source: {self._source}, Date: {self._date}"

class Income(Transaction):
    """Represents an income transaction."""
    def __init__(self, name, amount, source, date):
        super().__init__(name, amount, source, date)

    def get_details(self):
        """Returns details of the income transaction."""
        return f"Income: {self._name}, Amount: {self._amount}, Source: {self._source}, Date: {self._date}"

class SavingsTracker:
    """Handles transaction management for users."""

    def add_expense(self, user_id, name, amount, source, date):
        """Adds an expense for a user with error handling."""
        try:
            expense = Expense(name, amount, source, date)
            expense_date = datetime.strptime(date, "%Y-%m-%d")
            print(expense.get_details())
            transaction = TransactionModel(user_id=user_id, amount=expense.amount, description=expense._name, source=expense._source, date=expense_date)
            db.session.add(transaction)
            db.session.commit()
        except InvalidTransactionError as e:
            print(f"Error: {e}")

    def add_income(self, user_id, name, amount, source, date):
        """Adds an income for a user with error handling."""
        try:
            income = Income(name, amount, source, date)
            income_date = datetime.strptime(date, "%Y-%m-%d")
            print(income.get_details())
            transaction = TransactionModel(user_id=user_id, amount=income.amount, description=income._name, source=income._source, date=income_date)
            db.session.add(transaction)
            db.session.commit()
        except InvalidTransactionError as e:
            print(f"Error: {e}")