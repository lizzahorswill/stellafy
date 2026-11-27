# Import the SQLAlchemy integration for Flask.
from flask_sqlalchemy import SQLAlchemy

# Create the database manager.
# We will connect it to our Flask application in run.py.
db = SQLAlchemy()


# TRANSACTION MODEL:
# Describes how a simulated purchase is stored.
class Transaction(db.Model):

    # Explicitly name the database table.
    __tablename__ = "transactions"

    # Unique identifier for each transaction.
    id = db.Column(db.Integer, primary_key=True)

    # Store financial amounts as integer cents.
    # This avoids common floating-point rounding problems.
    total_cents = db.Column(db.Integer, nullable=False)
    commission_cents = db.Column(db.Integer, nullable=False)
    contribution_cents = db.Column(db.Integer, nullable=False)
    revenue_cents = db.Column(db.Integer, nullable=False)

    # Name of the social cause selected by the customer.
    cause = db.Column(db.String(100), nullable=False)

    # Record when the transaction was created.
    created_at = db.Column(
        db.DateTime,
        default=db.func.now(),
        nullable=False
    )
