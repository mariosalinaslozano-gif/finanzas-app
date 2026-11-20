from app import app, db
from app import Cuenta  # si Cuenta está en models.py, impórtala de ahí

with app.app_context():
    print(db.engine.url)  # debe decir sqlite, NO postgresql

    prueba_credito = Cuenta(nombre="Prueba Credito", saldo_inicial=0, moneda="MXN",
                            tipo="credito", dia_corte=20, dia_pago=10, limite_credito=5000)
    prueba_debito = Cuenta(nombre="Prueba Debito", saldo_inicial=100, moneda="USD",
                           tipo="debito")

    db.session.add(prueba_credito)
    db.session.add(prueba_debito)
    db.session.commit()
    print("Cuentas de prueba creadas")