from flask import Flask, render_template, request, redirect, url_for
from models import db, Cuenta, Categoria, Transaccion
from datetime import datetime
from sqlalchemy import func


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finanzas.db"
db.init_app(app)

def calcular_saldo(cuenta):
    entradas = db.session.query(func.sum(Transaccion.monto)) \
            .filter_by(cuenta_id = cuenta.id, tipo="entrada").scalar() or 0
    salidas = db.session.query(func.sum(Transaccion.monto)) \
            .filter_by(cuenta_id = cuenta.id, tipo="salida").scalar() or 0
    return cuenta.saldo_inicial + entradas - salidas

@app.route("/")
def inicio():
    cuentas = Cuenta.query.all()
    # build a list of (account, its balance) pairs
    saldos = [(c, calcular_saldo(c)) for c in cuentas]

    # totals grouped by currency
    totales_por_moneda = {}
    for cuenta, saldo in saldos:
        totales_por_moneda[cuenta.moneda] = totales_por_moneda.get(cuenta.moneda, 0) + saldo

    return render_template("dashboard.html",
                           saldos=saldos,
                           totales=totales_por_moneda)


@app.route("/resumen")
def resumen():
    # sum of expenses grouped by category name
    filas = db.session.query(
                Categoria.nombre,
                func.sum(Transaccion.monto)
            ).join(Transaccion, Transaccion.categoria_id == Categoria.id) \
             .filter(Transaccion.tipo == "salida") \
             .group_by(Categoria.nombre).all()

    etiquetas = [nombre for nombre, total in filas]   # ["Comida", "Renta"]
    valores = [float(total) for nombre, total in filas]  # [450.0, 8000.0]

    return render_template("resumen.html", 
                           filas=filas,
                           etiquetas=etiquetas,
                           valores=valores)

@app.route("/transacciones")
def lista_transacciones():
    transacciones = Transaccion.query.order_by(Transaccion.fecha.desc()).all()
    return render_template("lista.html", transacciones=transacciones)

@app.route("/transacciones/nueva", methods=["GET", "POST"])
def nueva_transaccion():
    if request.method == "POST":
        # El usuario llenó el formulario y le dio Guardar
        t = Transaccion(
            fecha=datetime.strptime(request.form["fecha"], "%Y-%m-%d").date(),
            tipo=request.form["tipo"],
            monto=float(request.form["monto"]),
            cuenta_id=int(request.form["cuenta_id"]),
            categoria_id=int(request.form["categoria_id"]) if request.form["categoria_id"] else None,
            nota=request.form["nota"],
        )
        db.session.add(t)
        db.session.commit()
        return redirect(url_for("lista_transacciones"))

    # Si es GET, solo mostramos el formulario vacío
    cuentas = Cuenta.query.all()
    categorias = Categoria.query.all()
    return render_template("formulario.html", cuentas=cuentas, categorias=categorias)

@app.route("/transacciones/<int:id>/editar", methods=["GET", "POST"])
def editar_transaccion(id):
    t = Transaccion.query.get_or_404(id)

    if request.method == "POST":
        t.fecha = datetime.strptime(request.form["fecha"], "%Y-%m-%d").date()
        t.tipo = request.form["tipo"]
        t.monto = float(request.form["monto"])
        t.cuenta_id = int(request.form["cuenta_id"])
        t.categoria_id = int(request.form["categoria_id"]) if request.form["categoria_id"] else None
        t.nota = request.form["nota"]
        db.session.commit()   # sin add: ya existe, solo guardamos los cambios
        return redirect(url_for("lista_transacciones"))

    cuentas = Cuenta.query.all()
    categorias = Categoria.query.all()
    return render_template("editar.html", t=t, cuentas=cuentas, categorias=categorias)

@app.route("/transacciones/<int:id>/borrar", methods=["POST"])
def borrar_transaccion(id):
    t = Transaccion.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for("lista_transacciones"))

if __name__ == "__main__":
    app.run(debug=True)