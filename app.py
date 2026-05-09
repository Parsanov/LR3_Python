from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "kn224s-lr3-secret"

trips = [
    {"країна": "Туреччина",  "туроператор": "Join UP!",         "ціна": 850,  "кількість_днів": 7},
    {"країна": "Туреччина",  "туроператор": "Coral Travel",     "ціна": 1200, "кількість_днів": 10},
    {"країна": "Туреччина",  "туроператор": "TEZ TOUR",         "ціна": 2500, "кількість_днів": 14},
    {"країна": "Туреччина",  "туроператор": "Anex Tour",        "ціна": 1100, "кількість_днів": 7},
    {"країна": "Єгипет",     "туроператор": "Coral Travel",     "ціна": 920,  "кількість_днів": 10},
    {"країна": "Іспанія",    "туроператор": "TEZ TOUR",         "ціна": 1350, "кількість_днів": 8},
    {"країна": "Італія",     "туроператор": "Pegas Touristik",  "ціна": 1600, "кількість_днів": 10},
    {"країна": "ОАЕ",        "туроператор": "Join UP!",         "ціна": 2100, "кількість_днів": 7},
    {"країна": "Таїланд",    "туроператор": "Coral Travel",     "ціна": 1800, "кількість_днів": 14},
    {"країна": "Португалія", "туроператор": "Anex Tour",        "ціна": 1450, "кількість_днів": 9},
]

OPERATORS = sorted(set(t["туроператор"] for t in trips))


# ── Головна ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", trips=trips)


# ── Пошук за туроператором ───────────────────────────────────────────────────
@app.route("/tour_operator", methods=["GET"])
def tour_operator():
    value = request.args.get("findTour", "").strip()
    result = None

    if value:
        result = [t for t in trips if t["туроператор"].lower() == value.lower()]
        if result:
            flash(f"Знайдено {len(result)} турів", "success")
        else:
            flash("За даним критерієм турів не знайдено", "warning")

    return render_template("operator.html", result=result, value=value,
                           operators=OPERATORS)


# ── Пошук за мінімальною кількістю днів ─────────────────────────────────────
@app.route("/days", methods=["GET"])
def find_days():
    n_raw = request.args.get("n", "").strip()
    result = None
    searched = "n" in request.args and n_raw != ""

    if searched:
        try:
            n = int(n_raw)
            if n <= 0:
                raise ValueError
            result = [t for t in trips if t["кількість_днів"] >= n]
            if result:
                flash(f"Знайдено {len(result)} турів", "success")
            else:
                flash("За даним критерієм турів не знайдено", "warning")
        except ValueError:
            flash("Кількість днів має бути цілим позитивним числом", "danger")

    return render_template("days.html", result=result, n_raw=n_raw,
                           searched=searched)


# ── Найдорожчий тур до Туреччини ─────────────────────────────────────────────
@app.route("/the_most_expensive")
def most_expensive():
    turkey = [t for t in trips if t["країна"] == "Туреччина"]
    most_exp = max(turkey, key=lambda t: t["ціна"]) if turkey else None
    if not most_exp:
        flash("Турів до Туреччини не знайдено", "warning")
    return render_template("mostExp.html", mostExp=most_exp)


# ── Сторінка вибору запиту ───────────────────────────────────────────────────
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query_type = request.form.get("query_type")

        if query_type == "operator":
            op = request.form.get("operator_val", "").strip()
            if not op:
                flash("Оберіть або введіть туроператора", "danger")
                return redirect(url_for("search"))
            return redirect(url_for("tour_operator", findTour=op))

        elif query_type == "days":
            n = request.form.get("days_val", "").strip()
            if not n:
                flash("Введіть кількість днів", "danger")
                return redirect(url_for("search"))
            return redirect(url_for("find_days", n=n))

        elif query_type == "expensive":
            return redirect(url_for("most_expensive"))

        flash("Оберіть тип запиту", "warning")
        return redirect(url_for("search"))

    return render_template("search.html", operators=OPERATORS)


# ── Додавання нового туру ────────────────────────────────────────────────────
@app.route("/add", methods=["GET", "POST"])
def add_trip():
    errors = {}
    form_data = {}

    if request.method == "POST":
        form_data = request.form.to_dict()

        # Валідація країни
        country = form_data.get("country", "").strip()
        if not country:
            errors["country"] = "Поле не може бути порожнім"
        elif not all(c.isalpha() or c.isspace() or c == "'" for c in country):
            errors["country"] = "Назва країни має містити лише літери"

        # Валідація туроператора
        operator = form_data.get("operator", "").strip()
        if not operator:
            errors["operator"] = "Поле не може бути порожнім"

        # Валідація ціни
        price_raw = form_data.get("price", "").strip()
        price = None
        try:
            price = float(price_raw)
            if price <= 0:
                raise ValueError
        except (ValueError, TypeError):
            errors["price"] = "Ціна має бути числом більше 0"

        # Валідація кількості днів
        days_raw = form_data.get("days", "").strip()
        days = None
        try:
            days = int(days_raw)
            if days < 1 or days > 365:
                raise ValueError
        except (ValueError, TypeError):
            errors["days"] = "Кількість днів — ціле число від 1 до 365"

        if errors:
            flash("Будь ласка, виправте помилки у формі", "danger")
            return render_template("add.html", errors=errors,
                                   form_data=form_data, operators=OPERATORS)

        # Додавання запису
        trips.append({
            "країна": country,
            "туроператор": operator,
            "ціна": int(price) if price == int(price) else price,
            "кількість_днів": days,
        })
        flash("Тур успішно додано до списку!", "success")
        return redirect(url_for("index"))

    return render_template("add.html", errors={}, form_data={},
                           operators=OPERATORS)


# ── 404 ──────────────────────────────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
