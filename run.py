# Import Flask to create the web application.
# Import render_template to display HTML templates.
from flask import Flask, render_template

# Create the Stellafy Flask application.
app = Flask(__name__)

# Connect the homepage URL to the home function.
@app.route("/")
def home():
    # Find index.html inside the templates folder.
    # Render the HTML and send it to the browser.
    return render_template("index.html")


# Run the development server when this file is executed directly.
if __name__ == "__main__":
    # Enable debugging while developing locally.
    app.run(debug=True)
