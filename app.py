from flask import Flask
from models import db, Cuenta, Categoria, Transaccion

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finanzas.db"
db.init_app(app)

@app.route("/")
def inicio():
    return "<h1>¡Hola Mario! Tu app de finanzas está viva.</h1>"

if __name__ == "__main__":
    app.run(debug=True)