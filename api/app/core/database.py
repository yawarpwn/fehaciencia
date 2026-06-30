from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db():
    # Activamos el modo WAL directamente en la conexión de SQLite antes de crear las tablas
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA journal_mode=WAL")
        connection.exec_driver_sql("PRAGMA journal_mode=NORMAL")

    # IMPORTANTE: Aquí importas tu archivo de modelos para que SQLModel los registre
    from app.modules.sales_invoices.model import SalesInvoice, SupportingDocument

    # Crea las tablas si no existen
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
