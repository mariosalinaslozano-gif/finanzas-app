from app import app, db
from models import Cuenta, Categoria, Transaccion

with app.app_context():
    # one account per currency
    efectivo_mx = Cuenta(nombre="Efectivo MX", saldo_inicial=1000, moneda="MXN")
    banco_usa   = Cuenta(nombre="Banco EE.UU.", saldo_inicial=500, moneda="USD")
    comida      = Categoria(nombre="Comida", tipo="gasto")

    db.session.add_all([efectivo_mx, banco_usa, comida])
    db.session.commit()

    # a peso expense and a dollar expense
    gasto_mx  = Transaccion(monto=150, tipo="salida", nota="Tacos",
                            cuenta_id=efectivo_mx.id, categoria_id=comida.id)
    gasto_usd = Transaccion(monto=25, tipo="salida", nota="Lunch",
                            cuenta_id=banco_usa.id, categoria_id=comida.id)

    db.session.add_all([gasto_mx, gasto_usd])
    db.session.commit()
    print("Test accounts created in MXN and USD")