from sqlalchemy import text
from app import app, db

with app.app_context():
    db.session.execute(text("ALTER TABLE cuenta ADD COLUMN tipo VARCHAR(20) NOT NULL DEFAULT 'debito'"))
    db.session.execute(text("ALTER TABLE cuenta ADD COLUMN dia_corte INTEGER"))
    db.session.execute(text("ALTER TABLE cuenta ADD COLUMN dia_pago INTEGER"))
    db.session.execute(text("ALTER TABLE cuenta ADD COLUMN limite_credito FLOAT"))

    db.session.commit()

    print(db.engine.url)