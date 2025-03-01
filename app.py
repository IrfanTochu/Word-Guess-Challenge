from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "word_guess_secret_key"

SCORE_FILE = "scores.txt"

# Load words from words.txt file
def load_words():
    categories = {}
    try:
        with open("words.txt", "r", encoding="utf-8") as file:
            category = None
            for line in file:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    category = line[1:-1]
                    categories[category] = []
                elif category:
                    categories[category].append(line)
    except FileNotFoundError:
        print("❌ words.txt file not found")
        categories = {"Default": ["defaultword"]}
    return categories

# Select a random category and word
def select_word(categories, choice):
    category_list = list(categories.keys())
    if choice < 0 or choice >= len(category_list):
        return None, None
    
    category_name = category_list[choice]
    words = categories[category_name]
    
    if not words:
        return category_name, "defaultword"
    
    word = random.choice(words)
    return category_name, word

@app.route("/", methods=["GET", "POST"])
def index():
    categories = load_words()
    if request.method == "POST":
        try:
            choice = int(request.form.get("category_choice", -1))
            category, word = select_word(categories, choice)
            if not word:
                return redirect(url_for("index"))
            
            session["category"] = category
            session["word"] = word
            session["hidden_word"] = ["_"] * len(word)
            session["attempts"] = 6
            session["guessed_letters"] = []
            
            return redirect(url_for("play_game"))
        except ValueError:
            return redirect(url_for("index"))
    return render_template("index.html", categories=categories)

@app.route("/play", methods=["GET", "POST"])
def play_game():
    category = session.get("category", "Unknown")
    word = session.get("word")
    hidden_word = session.get("hidden_word", [])
    attempts = session.get("attempts", 6)
    guessed_letters = session.get("guessed_letters", [])
    
    if word is None:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        guess = request.form.get("guess", "").lower()
        if guess and guess not in guessed_letters:
            guessed_letters.append(guess)
            if guess in word:
                for i, letter in enumerate(word):
                    if letter == guess:
                        hidden_word[i] = guess
            else:
                attempts -= 1
            
            session["hidden_word"] = hidden_word
            session["attempts"] = attempts
            session["guessed_letters"] = guessed_letters
            
            if "_" not in hidden_word:
                score = 10
                return render_template("win.html", word=word, score=score)
            if attempts == 0:
                return render_template("lose.html", word=word)
    
    return render_template("game.html", category=category, hidden_word=" ".join(hidden_word), attempts=attempts, guessed_letters=guessed_letters)

@app.route("/save_score", methods=["POST"])
def save_score():
    name = request.form.get("player_name", "Unknown")
    word = session.get("word", "Unknown")
    score = request.form.get("score", 0)
    
    if name and word:
        try:
            with open(SCORE_FILE, "a", encoding="utf-8") as file:
                file.write(f"{name} - {word} - {score} points\n")
        except Exception as e:
            print(f"❌ Error saving score: {e}")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
