from flask import Flask, render_template, request, redirect, url_for, flash
import os
from utils.api_handler import fetch_results
from utils.game_checker import check_games

app = Flask(__name__)
app.secret_key = "super_secret_key"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Crie a pasta de upload se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename.endswith(".txt"):
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(file_path)
                flash("Arquivo carregado com sucesso!", "success")
                return redirect(url_for("results", file=file.filename))
            else:
                flash("Apenas arquivos .txt são suportados!", "error")
        elif "manual_entry" in request.form:
            manual_entry = request.form["manual_entry"]
            return redirect(url_for("results", manual_entry=manual_entry))
    return render_template("index.html")

@app.route("/results", methods=["GET"])
def results():
    manual_entry = request.args.get("manual_entry", None)
    file_name = request.args.get("file", None)
    user_games = []

    # Obtém os jogos do arquivo ou da entrada manual
    if file_name:
        with open(os.path.join(app.config["UPLOAD_FOLDER"], file_name), "r") as f:
            user_games = [line.strip() for line in f.readlines()]
    elif manual_entry:
        user_games = manual_entry.split(";")

    # Obtém o resultado da API
    results = fetch_results()
    if not results:
        flash("Erro ao obter os resultados da API.", "error")
        return redirect(url_for("index"))

    # Verifica os jogos
    checked_results = check_games(user_games, results["dezenas"])

    return render_template("result.html", checked_results=checked_results, results=results)

if __name__ == "__main__":
    app.run(debug=True)
