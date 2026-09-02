from app import app, db
from models import Cuenta, Categoria, Transaccion

with app.app_context():
    db.create_all()   # make sure the tables exist (safe to run anytime)

    if Cuenta.query.first():
        print("Accounts already exist. Skipping.")
    else:
        # ============================================================
        # EDIT HERE 1 — YOUR ACCOUNTS
        # Pattern: variable = Cuenta(nombre="Name", saldo_inicial=0, moneda="USD" or "MXN")
        # If you rename an account, also update CODIGOS_CUENTA in app.py
        # ============================================================
        cuentas = [
            Cuenta(nombre="Debito EE.UU.",  saldo_inicial=0, moneda="USD"),
            Cuenta(nombre="Credito EE.UU.", saldo_inicial=0, moneda="USD"),
            Cuenta(nombre="Debito MXN",     saldo_inicial=0, moneda="MXN"),
            Cuenta(nombre="Credito MXN",    saldo_inicial=0, moneda="MXN"),
        ]

        # ============================================================
        # EDIT HERE 2 — YOUR CATEGORIES
        # Pattern: Categoria(nombre="Name", tipo="gasto" or "ingreso")
        # "gasto" = expense, "ingreso" = income
        # ============================================================
        categorias = [
            Categoria(nombre="Comida",        tipo="gasto"),
            Categoria(nombre="Renta",         tipo="gasto"),
            Categoria(nombre="Suscripciones", tipo="gasto"),
            Categoria(nombre="otro",          tipo="gasto"),
            Categoria(nombre="Sueldo",        tipo="ingreso"),
            Categoria(nombre="Transferencia",       tipo="ingreso"),
        ]

        # This saves everything — no need to touch it
        db.session.add_all(cuentas + categorias)
        db.session.commit()
        print(f"{len(cuentas)} accounts and {len(categorias)} categories created!")