# ==========================================
# STELLAFY - MAIN FLASK APPLICATION
# ==========================================

# Import Flask tools for displaying pages and handling requests.
from flask import Flask, render_template, redirect, url_for, session, request

# Import tools for file paths and environment settings.
import os

# Import Decimal for accurate financial calculations.
from decimal import Decimal, ROUND_HALF_UP

# Import our database manager and transaction model.
from models import db, Transaction


# ==========================================
# 1. CREATE AND CONFIGURE THE APPLICATION
# ==========================================

# Create the Stellafy Flask application.
app = Flask(__name__)

# Set a secret key to protect Flask session cookies.
# The fallback is ONLY for local development.
# Set a strong SECRET_KEY environment variable before deployment.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "stellafy-local-development-only"
)

# Get the location of the Stellafy project.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Create the folder where our SQLite database will be stored.
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# Configure the SQLite database location.
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(INSTANCE_DIR, "stellafy.db")
)

# Connect Flask to SQLAlchemy.
db.init_app(app)

# Create database tables if they do not exist.
with app.app_context():
    db.create_all()


# ==========================================
# 2. SAMPLE PRODUCTS
# ==========================================

# Each product has a unique ID, name, and price.
# All products and transactions are simulated.
PRODUCTS = [
    {"id": 1, "name": "Reusable Water Bottle", "price": 25.00, "type": "original", "seller": "Stellafy", "image": "bottle.svg"},
    {"id": 2, "name": "Reusable Shopping Bag", "price": 15.00, "type": "marketplace", "seller": "Good Earth Goods", "image": "bag.svg"},
    {"id": 3, "name": "Eco-Friendly Notebook", "price": 12.00, "type": "marketplace", "seller": "Paper & Pine", "image": "notebook.svg"},
    {"id": 4, "name": "Ceramic Coffee Mug", "price": 20.00, "type": "marketplace", "seller": "Riverbend Studio", "image": "mug.svg"},
    {"id": 5, "name": "Cotton Tote Bag", "price": 18.00, "type": "original", "seller": "Stellafy", "image": "tote.svg"},
    {"id": 6, "name": "Bamboo Desk Organizer", "price": 30.00, "type": "original", "seller": "Stellafy", "image": "organizer.svg"}
]

# Define the social causes customers can support.
CAUSES = [
    "Education for All",
    "Protect Our Planet",
    "Stronger Communities"
]


# ==========================================
# 3. HELPER FUNCTION FOR MONEY
# ==========================================

def to_cents(amount):
    # Convert an amount into integer cents.
    # Decimal avoids common floating-point rounding problems.
    return int(
        (Decimal(str(amount)) * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


# ==========================================
# 4. HOMEPAGE
# ==========================================

@app.route("/")
def home():
    # Display our HTML storefront and product catalogue.
    return render_template("index.html", products=PRODUCTS)


# ==========================================
# 5. ADD PRODUCTS TO CART
# ==========================================

@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    # Find the selected product using its ID.
    product = next(
        (p for p in PRODUCTS if p["id"] == product_id),
        None
    )

    # Reject a product ID that does not exist.
    if product is None:
        return "Product not found", 404

    # Retrieve the current cart or create an empty one.
    cart = session.get("cart", {})

    # Session dictionary keys are stored as strings.
    product_key = str(product_id)

    # Increase the product quantity by one.
    cart[product_key] = cart.get(product_key, 0) + 1

    # Save the updated cart in the Flask session.
    session["cart"] = cart

    # Return the customer to the product catalogue.
    return redirect(url_for("home") + "#products")


# ==========================================
# 6. VIEW SHOPPING CART
# ==========================================

@app.route("/cart")
def view_cart():

    # Retrieve the customer's shopping cart.
    cart = session.get("cart", {})

    # Prepare a list of products to display.
    cart_items = []

    # Store the combined cart total in cents.
    total_cents = 0

    # Check the quantity of each product.
    for product in PRODUCTS:
        quantity = cart.get(str(product["id"]), 0)

        if quantity > 0:

            # Convert the unit price to integer cents.
            price_cents = to_cents(product["price"])

            # Calculate this product's subtotal.
            subtotal_cents = price_cents * quantity

            # Add the product information to our display list.
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "price": price_cents / 100,
                "quantity": quantity,
                "subtotal": subtotal_cents / 100
            })

            # Add the subtotal to the shopping cart total.
            total_cents += subtotal_cents

    # Convert cents into dollars for the HTML template.
    total = total_cents / 100

    # Display the shopping cart.
    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


# ==========================================
# 7. REMOVE PRODUCTS FROM CART
# ==========================================

@app.route("/remove-from-cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):

    # Retrieve the shopping cart.
    cart = session.get("cart", {})

    # Identify the product to remove.
    product_key = str(product_id)

    # Remove the product if it is in the cart.
    cart.pop(product_key, None)

    # Save the updated cart.
    session["cart"] = cart

    # Return to the shopping cart.
    return redirect(url_for("view_cart"))


# ==========================================
# 8. SIMULATED CHECKOUT
# ==========================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    # Retrieve the shopping cart.
    cart = session.get("cart", {})

    # Calculate the purchase total in cents.
    total_cents = 0

    for product in PRODUCTS:
        quantity = cart.get(str(product["id"]), 0)

        if quantity > 0:
            price_cents = to_cents(product["price"])
            total_cents += price_cents * quantity

    # Prevent checkout if the cart is empty.
    if total_cents <= 0:
        return redirect(url_for("view_cart"))

    # Calculate the merchant commission: 10%.
    commission_cents = int(
        (Decimal(total_cents) * Decimal("0.10")).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )

    # Calculate the cause contribution: 60% of commission.
    contribution_cents = int(
        (Decimal(commission_cents) * Decimal("0.60")).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )

    # Stellafy keeps the remaining commission before expenses.
    revenue_cents = commission_cents - contribution_cents

    # Convert cents to dollars for displaying the results.
    total = total_cents / 100
    commission = commission_cents / 100
    contribution = contribution_cents / 100
    revenue = revenue_cents / 100

    # Handle the checkout form when the customer submits it.
    if request.method == "POST":

        # Get the customer's selected social cause.
        selected_cause = request.form.get("cause")

        # Check that the cause is one of our allowed options.
        if selected_cause not in CAUSES:
            return "Please select a valid cause.", 400

        # Create a new simulated transaction database record.
        transaction = Transaction(
            total_cents=total_cents,
            commission_cents=commission_cents,
            contribution_cents=contribution_cents,
            revenue_cents=revenue_cents,
            cause=selected_cause
        )

        # Prepare the new transaction for database storage.
        db.session.add(transaction)

        # Save the transaction permanently in SQLite.
        db.session.commit()

        # Keep the latest transaction details for the receipt page.
        session["last_checkout"] = {
            "total": total,
            "commission": commission,
            "contribution": contribution,
            "revenue": revenue,
            "cause": selected_cause
        }

        # Clear the shopping cart after checkout.
        session["cart"] = {}

        # Send the customer to the confirmation page.
        return redirect(url_for("checkout_success"))

    # For a GET request, display the checkout form.
    return render_template(
        "checkout.html",
        total=total,
        commission=commission,
        contribution=contribution,
        revenue=revenue,
        causes=CAUSES
    )


# ==========================================
# 9. PURCHASE CONFIRMATION
# ==========================================

@app.route("/checkout/success")
def checkout_success():

    # Get the last completed simulated purchase.
    transaction = session.get("last_checkout")

    # Redirect if no completed purchase is available.
    if not transaction:
        return redirect(url_for("home"))

    # Display the confirmation and social impact.
    return render_template(
        "success.html",
        transaction=transaction
    )

# ==========================================
# 10. SALES AND SOCIAL IMPACT DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    # Retrieve all completed simulated transactions.
    transactions = Transaction.query.order_by(
        Transaction.id.desc()
    ).all()

    # Calculate financial totals using integer cents.
    total_sales = sum(t.total_cents for t in transactions) / 100
    total_commission = sum(t.commission_cents for t in transactions) / 100
    total_contributions = sum(t.contribution_cents for t in transactions) / 100
    total_revenue = sum(t.revenue_cents for t in transactions) / 100

    # Calculate total contributions for each social cause.
    cause_totals = {cause: 0 for cause in CAUSES}

    for transaction in transactions:
        cause_totals[transaction.cause] += transaction.contribution_cents

    # Convert contribution totals from cents to dollars.
    cause_totals = {
        cause: cents / 100
        for cause, cents in cause_totals.items()
    }

    # Render the dashboard with our calculated data.
    return render_template(
        "dashboard.html",
        transactions=transactions,
        transaction_count=len(transactions),
        total_sales=total_sales,
        total_commission=total_commission,
        total_contributions=total_contributions,
        total_revenue=total_revenue,
        cause_totals=cause_totals
    )


# ==========================================
# 10. START THE FLASK SERVER
# ==========================================

if __name__ == "__main__":

    # Run the development server on port 5001.
    # Debug mode must not be enabled in production.
    app.run(debug=True, port=5001)
