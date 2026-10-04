import os
import time
import threading
from datetime import datetime
from pathlib import Path
import pytest
import httpx
import uvicorn
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from pages.client_list_page import ClientListPage
from pages.client_form_page import ClientFormPage
from pages.client_detail_page import ClientDetailPage

E2E_DB_FILE = "./crm_e2e_test.db"
E2E_DB_URL = f"sqlite:///{E2E_DB_FILE}"
E2E_HOST = "127.0.0.1"
E2E_PORT = 8008
BASE_URL = f"http://{E2E_HOST}:{E2E_PORT}"

# Motor SQLite dedicado para pruebas E2E con claves foráneas activas
e2e_engine = create_engine(
    E2E_DB_URL,
    connect_args={"check_same_thread": False}
)

@event.listens_for(e2e_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

E2ESessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=e2e_engine)


def override_get_db():
    db = E2ESessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def live_server():
    """Inicia un servidor Uvicorn en un hilo separado con base de datos de pruebas aislada."""
    # Configurar base de datos de pruebas en FastAPI
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=e2e_engine)

    config = uvicorn.Config(
        app=app,
        host=E2E_HOST,
        port=E2E_PORT,
        log_level="critical",
        access_log=False
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Esperar hasta que el servidor responda
    for _ in range(50):
        try:
            res = httpx.get(f"{BASE_URL}/clients", timeout=1.0)
            if res.status_code == 200:
                break
        except Exception:
            time.sleep(0.1)
    else:
        raise RuntimeError(f"No fue posible iniciar el servidor de pruebas E2E en {BASE_URL}")

    yield BASE_URL

    # Detener servidor
    server.should_exit = True
    thread.join(timeout=3)
    app.dependency_overrides.clear()

    # Eliminar archivo de base de datos de pruebas
    if os.path.exists(E2E_DB_FILE):
        try:
            os.remove(E2E_DB_FILE)
        except Exception:
            pass


@pytest.fixture(scope="function", autouse=True)
def clean_db(live_server):
    """Limpia las tablas de la base de datos antes de cada prueba E2E."""
    Base.metadata.drop_all(bind=e2e_engine)
    Base.metadata.create_all(bind=e2e_engine)
    yield


# Hook para captura automática de pantalla en caso de fallo
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            screenshots_dir = Path("tests/e2e/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_name = item.name.replace("[", "_").replace("]", "_").replace("/", "_")
            screenshot_file = screenshots_dir / f"FAILED_{clean_name}_{timestamp}.png"
            try:
                page.screenshot(path=str(screenshot_file), full_page=True)
                print(f"\n[CAPTURA DE PANTALLA GUARDADA]: {screenshot_file.resolve()}")
            except Exception as e:
                print(f"\n[Error capturando pantalla al fallar]: {e}")


# Page Object Fixtures
@pytest.fixture
def list_page(page, live_server) -> ClientListPage:
    return ClientListPage(page, base_url=live_server)


@pytest.fixture
def form_page(page, live_server) -> ClientFormPage:
    return ClientFormPage(page, base_url=live_server)


@pytest.fixture
def detail_page(page, live_server) -> ClientDetailPage:
    return ClientDetailPage(page, base_url=live_server)
