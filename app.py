from flask import Flask, render_template, request, redirect, url_for, session
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_dev_key")


with open("data/wordle_words.txt") as f:
    WORD_LIST = [word.strip().upper() for word in f if len(word.strip()) == 5]

MAX_ATTEMPTS = 7

def new_game():
    session["solution"] = random.choice(WORD_LIST).upper()
    session["attempts"] = []
    session["game_over"] = False
    session["is_solved"] = False

def render_guess(guess, solution):
    tiles = []
    for i, letter in enumerate(guess):
        if letter == solution[i]:
            tiles.append(f'<span class="tile correct">{letter}</span>')
        elif letter in solution:
            tiles.append(f'<span class="tile present">{letter}</span>')
        else:
            tiles.append(f'<span class="tile absent">{letter}</span>')
    return "".join(tiles)

@app.route("/", methods=["GET", "POST"])
def index():
    timestamp = int(time.time())
    if "solution" not in session:
        new_game()

    message = ""
    rows = [render_guess(guess, session["solution"]) for guess in session["attempts"]]
    attempts_left = MAX_ATTEMPTS - len(session["attempts"])
    game_over = session.get("game_over", False)
    is_solved = session.get("is_solved", False)
    solution = session.get("solution", "")

    if request.method == "POST" and not game_over:
        guess = request.form["guess"].upper()

        if len(guess) != 5 or guess.lower() not in [word.lower() for word in WORD_LIST]:
            message = "Invalid word. Try again."
        else:
            session["attempts"].append(guess)
            session.modified = True
            if guess == session["solution"]:
                session["game_over"] = True
                session["is_solved"] = True
            elif len(session["attempts"]) >= MAX_ATTEMPTS:
                session["game_over"] = True

            return redirect(url_for("index"))

    return render_template(
        "index.html",
        timestamp=timestamp,
        rows=rows,
        attempts_left=attempts_left,
        game_over=game_over,
        is_solved=is_solved,
        solution=solution,
        message=message,
    )

@app.route("/reset")
def reset():
    new_game()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
