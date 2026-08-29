from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Cuenta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)      # ej. "Efectivo", "Banco"
    saldo_inicial = db.Column(db.Float, default=0.0)
    moneda = db.Column(db.String(10), default="MXN")

    def __repr__(self):
        return f"<Cuenta {self.nombre}>"


class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)      # ej. "Comida", "Sueldo"
    tipo = db.Column(db.String(20), nullable=False)        # "ingreso" o "gasto"

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=date.today)
    monto = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)        # "entrada", "salida", "transferencia"
    nota = db.Column(db.String(200))

    # Relaciones: a qué cuenta y categoría pertenece
    cuenta_id = db.Column(db.Integer, db.ForeignKey("cuenta.id"))
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"))

    def __repr__(self):
        return f"<Transaccion {self.id} {self.tipo} {self.monto}>"