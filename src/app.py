#!/usr/bin/env python3

from flask import Flask, request, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def main():
    response_text = None
    if request.method == "POST":
        input_text = request.form.get("user_input", "").strip()
        response_text = (
            "You entered: " + input_text
            if input_text
            else "Please enter a query to get intelligence feedback."
        )
    return render_template("index.html", response_text=response_text)
