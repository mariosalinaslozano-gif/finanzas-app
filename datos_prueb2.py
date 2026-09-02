from app import app, db
from models import Cuenta, Categoria, Transaccion

with app.app_context():
    # make sure the tables exist (safe to run even if they already do)
    db.create_all()

    # avoid creating duplicates if you run this script more than once
    if Cuenta.query.first():
        print("Accounts already exist. Skipping.")
    else:
        debito_mx   = Cuenta(nombre="Debito MXN",    saldo_inicial=0, moneda="MXN")
        credito_mx  = Cuenta(nombre="Credito MXN",   saldo_inicial=0, moneda="MXN")
        debito_usa  = Cuenta(nombre="Debito EE.UU.", saldo_inicial=0, moneda="USD")
        credito_usa = Cuenta(nombre="Credito EE.UU.", saldo_inicial=0, moneda="USD")

        # a couple of categories too, so your dropdowns aren't empty
        comida = Categoria(nombre="Comida", tipo="gasto")
        sueldo = Categoria(nombre="Sueldo", tipo="ingreso")
        renta  = Categoria(nombre="Renta",  tipo="gasto")

        db.session.add_all([debito_mx, credito_mx, debito_usa, credito_usa,
                            comida, sueldo, renta])
        db.session.commit()
        print("Accounts and categories created!")