from flask import Flask, render_template, request
import scoring, purchaser

app = Flask(__name__)

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/prompter", methods=['POST'])
def handle_prompt():
    if request.method == 'POST':
        data = request.get_json()
        prmpt = data['prompt']
        score = scoring.get_score(prmpt)
        purchases = purchaser.get_purchases(prmpt)
        return {'score':score, 'purchases':purchases}