from sqlmodel import SQLModel, create_engine, Session, select
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db():
    # Activamos el modo WAL directamente en la conexión de SQLite antes de crear las tablas
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA journal_mode=WAL")
        connection.exec_driver_sql("PRAGMA journal_mode=NORMAL")

    # IMPORTANTE: Aquí importas tu archivo de modelos para que SQLModel los registre
    from app.modules.sales_invoices.model import SalesInvoice, SupportingDocument
    from app.modules.auth.model import User

    # Crea las tablas si no existen
    SQLModel.metadata.create_all(engine)

    # Crear usuario por defecto si no hay usuarios en la base de datos
    from app.core.auth import get_password_hash
    from app.config import DEFAULT_ADMIN_PASSWORD

    with Session(engine) as session:
        existing_user = session.exec(select(User)).first()
        if not existing_user:
            print("Creando usuario administrador por defecto...")
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
                full_name="Administrador",
            )
            session.add(admin_user)
            session.commit()
            print("Usuario administrador creado exitosamente!")


def get_session():
    with Session(engine) as session:
        yield session

