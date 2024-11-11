from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ShortURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    shortened_url = db.Column(db.String(100), unique=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def welcome_page():
    return render_template("UrlShortener.html")

@app.route("/generate_url", methods=["POST"])
def generate_url():
    original_url = request.form.get("url")
    custom_short_url = request.form.get("custom_short_url")

    if not original_url:
        return redirect(url_for("welcome_page"))

    if custom_short_url:
        existing_url = ShortURL.query.filter_by(shortened_url=f"http://localhost:5000/{custom_short_url}").first()
        if existing_url:
            return render_template("UrlShortener.html", error_message="Custom URL already exists. Please choose a different one.")

        # Check if the custom name is "secret", and link it to secret.html
        if custom_short_url.lower() == "secret":
            shortened_url = f"http://localhost:5000/{custom_short_url}"
            new_url = ShortURL(original_url="secret.html", shortened_url=shortened_url)
        else:
            shortened_url = f"http://localhost:5000/{custom_short_url}"
            new_url = ShortURL(original_url=original_url, shortened_url=shortened_url)
    else:
        random_length = int(request.form.get("slider_value"))
        random_path = ''.join(random.choices(string.ascii_letters + string.digits, k=random_length))
        shortened_url = f"http://localhost:5000/{random_path}"
        new_url = ShortURL(original_url=original_url, shortened_url=shortened_url)

    db.session.add(new_url)
    db.session.commit()

    return render_template("UrlShortener.html", shortened_url=shortened_url)

@app.route("/<shortened_url>")
def redirect_to_original(shortened_url):
    short_url_record = ShortURL.query.filter_by(shortened_url=f"http://localhost:5000/{shortened_url}").first()
    if short_url_record:
        if short_url_record.original_url == "secret":
            return render_template("secret.html")
        else:
            return redirect(short_url_record.original_url)
    else:
        return "URL not found", 404

@app.route('/lookup/<shortened_url>', methods=['GET'])
def lookup_url(shortened_url):
    short_url_record = ShortURL.query.filter_by(shortened_url=f"http://localhost:5000/{shortened_url}").first()
    if short_url_record:
        return jsonify({'original_url': short_url_record.original_url})
    else:
        return jsonify({'original_url': None})

if __name__ == '__main__':
    app.run(debug=True)
