from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Import admin module
import admin

# Import routes after app creation
from urls import *

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
