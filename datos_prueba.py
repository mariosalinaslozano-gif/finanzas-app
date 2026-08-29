from app import app, db
from models import Cuenta, Categoria, Transaccion

with app.app_context():
    # Crear una cuenta y dos categorías
    efectivo = Cuenta(nombre="Efectivo", saldo_inicial=1000)
    sueldo = Categoria(nombre="Sueldo", tipo="ingreso")
    comida = Categoria(nombre="Comida", tipo="gasto")

    db.session.add(efectivo)
    db.session.add(sueldo)
    db.session.add(comida)
    db.session.commit()   # guardar de verdad

    # Crear una transacción de gasto
    gasto = Transaccion(monto=150, tipo="salida", nota="Tacos",
                        cuenta_id=efectivo.id, categoria_id=comida.id)
    db.session.add(gasto)
    db.session.commit()

    # Leer y mostrar lo que hay
    print("Cuentas:", Cuenta.query.all())
    print("Categorías:", Categoria.query.all())
    print("Transacciones:", Transaccion.query.all())