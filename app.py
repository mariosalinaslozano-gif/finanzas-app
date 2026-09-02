from flask import Flask, render_template, request, redirect, url_for
from models import db, Cuenta, Categoria, Transaccion
from datetime import datetime, date 
from sqlalchemy import func
import csv
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finanzas.db"
db.init_app(app)

CODIGOS_CUENTA = {
    "deb-us":  "Debito EE.UU.",
    "cred-us": "Credito EE.UU.",
    "deb-mx":  "Debito MXN",
    "cred-mx": "Credito MXN",
}

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

    #Start with query that we can add conditions to
    consulta = Transaccion.query

    tipo = request.args.get("tipo")
    cuenta_id = request.args.get("cuenta_id")
    categoria_id = request.args.get("categoria_id")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")

    if tipo:
        consulta = consulta.filter_by(tipo=tipo)
    if cuenta_id:
        consulta = consulta.filter_by(cuenta_id=int(cuenta_id))
    if categoria_id:
        consulta = consulta.filter_by(categoria_id=int(categoria_id))
    if desde:
        consulta = consulta.filter(Transaccion.fecha >= datetime.strptime(desde, "%Y-%m-%d").date())
    if hasta:
        consulta = consulta.filter(Transaccion.fecha <= datetime.strptime(hasta, "%Y-%m-%d").date())

    transacciones = consulta.order_by(Transaccion.fecha.desc()).all()

    cuentas = Cuenta.query.all()
    categorias = Categoria.query.all()

    return render_template("lista.html", 
                           transacciones=transacciones,
                           cuentas=cuentas,
                           categorias=categorias)

@app.route("/transacciones/nueva", methods=["GET", "POST"])
def nueva_transaccion():
    if request.method == "POST":
    # basic validation
        errores = []

        try:
            monto = float(request.form["monto"])
            if monto <= 0:
                errores.append("Amount must be greater than 0.")
        except ValueError:
            errores.append("Amount must be a number.")

        if not request.form.get("cuenta_id"):
            errores.append("You must choose an account.")

        if errores:
            # re-show the form with the error messages
            cuentas = Cuenta.query.all()
            categorias = Categoria.query.all()
            return render_template("formulario.html",
                                cuentas=cuentas, categorias=categorias,
                                errores=errores)

        # if we get here, input is valid → save
        t = Transaccion(
            fecha=datetime.strptime(request.form["fecha"], "%Y-%m-%d").date(),
            tipo=request.form["tipo"],
            monto=monto,
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

@app.route("/importar", methods=["GET", "POST"])
def importar():
    if request.method == "POST":
        archivo = request.files.get("archivo")
        if not archivo:
            return render_template("importar.html", resultado="No file selected.")

        contenido = archivo.read().decode("utf-8-sig")
        lector = csv.DictReader(io.StringIO(contenido))

        creadas = 0
        errores = 0

        for fila in lector:
            try:
                # find the account and category by name
                cuenta = Cuenta.query.filter_by(nombre=fila["cuenta"]).first()
                categoria = Categoria.query.filter_by(nombre=fila["categoria"]).first()

                if not cuenta:
                    errores += 1
                    continue   # skip this row, no matching account

                t = Transaccion(
                    fecha=datetime.strptime(fila["fecha"], "%Y-%m-%d").date(),
                    monto=float(fila["monto"]),
                    tipo=fila["tipo"],
                    nota=fila.get("nota", ""),
                    cuenta_id=cuenta.id,
                    categoria_id=categoria.id if categoria else None,
                )
                db.session.add(t)
                creadas += 1
            except (ValueError, KeyError):
                errores += 1
                continue

        db.session.commit()   # save all the new rows at once
        return render_template("importar.html",
                               resultado=f"{creadas} imported, {errores} skipped.")

    return render_template("importar.html")

@app.route("/captura", methods=["GET", "POST"])
def captura():
    if request.method == "POST":
        texto = request.form.get("lineas", "")
        creadas = 0
        fallidas = []   # lines we couldn't process

        for linea in texto.strip().split("\n"):
            linea = linea.strip()
            if not linea:
                continue   # skip empty lines

            partes = [p.strip() for p in linea.split(",")]

            # we need at least tipo, cuenta, monto
            if len(partes) < 3:
                fallidas.append(linea)
                continue

            tipo = partes[0].lower()
            codigo = partes[1].lower()
            monto_texto = partes[2]
            nota = partes[3] if len(partes) > 3 else ""

            nombre_cuenta = CODIGOS_CUENTA.get(codigo)
            if nombre_cuenta is None:
                fallidas.append(linea)          # unknown code
                continue

            # find the account by name
            cuenta = Cuenta.query.filter_by(nombre=nombre_cuenta).first()

            try:
                monto = float(monto_texto)
            except ValueError:
                fallidas.append(linea)
                continue

            if not cuenta or tipo not in ("entrada", "salida", "transferencia") or monto <= 0:
                fallidas.append(linea)
                continue

            # all good → create the transaction
            t = Transaccion(
                fecha=date.today(),
                tipo=tipo,
                monto=monto,
                nota=nota,
                cuenta_id=cuenta.id,
                categoria_id=None,   # quick entry skips category; add later if you want
            )
            db.session.add(t)
            creadas += 1

        db.session.commit()
        resultado = f"{creadas} saved, {len(fallidas)} failed."
        return render_template("captura.html", resultado=resultado, fallidas=fallidas)

    return render_template("captura.html")

if __name__ == "__main__":
    app.run(debug=True)