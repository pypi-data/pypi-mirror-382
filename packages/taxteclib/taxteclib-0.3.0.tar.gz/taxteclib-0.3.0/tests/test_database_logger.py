from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.taxteclib.database_logger import Base, EstadoMonitoreo, SqlServerClient


@pytest.fixture
def db_session() -> sessionmaker:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_insertar_monitoreo_valores_basicos(db_session: sessionmaker) -> None:
    cliente = SqlServerClient()
    cliente.Session = lambda: db_session

    registro = cliente.insertar_monitoreo(
        username="usuario1",
        proceso="Proceso A",
        estado=EstadoMonitoreo.CORRECTO,
        iniciado=datetime(2025, 9, 26, 9, 0),
        finalizado=datetime(2025, 9, 26, 9, 30),
        cliente="ClienteA",
        items_count=10,
    )

    assert registro is not None
    assert registro.id is not None
    assert registro.username == "usuario1"
    assert registro.items_count == 10


def test_insertar_monitoreo_items_count_cero(db_session: sessionmaker) -> None:
    cliente = SqlServerClient()
    cliente.Session = lambda: db_session

    registro = cliente.insertar_monitoreo(
        username="usuario2",
        proceso="Proceso B",
        estado=EstadoMonitoreo.FINALIZADO_CON_ERRORES,
        iniciado=datetime(2025, 9, 26, 10, 0),
        finalizado=datetime(2025, 9, 26, 10, 5),
        cliente="ClienteB",
        items_count=0,
    )

    assert registro is not None
    assert registro.items_count == 0
    assert int(registro.estado) == EstadoMonitoreo.FINALIZADO_CON_ERRORES


def test_insertar_monitoreo_fechas_invertidas(db_session: sessionmaker) -> None:
    cliente = SqlServerClient()
    cliente.Session = lambda: db_session

    registro = cliente.insertar_monitoreo(
        username="usuario3",
        proceso="Proceso C",
        estado=EstadoMonitoreo.ERRONEO,
        iniciado=datetime(2025, 9, 26, 11, 0),
        finalizado=datetime(2025, 9, 26, 10, 0),  # finalizado antes que iniciado
        cliente="ClienteC",
        items_count=3,
    )

    assert registro is not None
    assert registro.finalizado < registro.iniciado  # test lógico, no falla por diseño


def test_insertar_monitoreo_estado_largo(db_session: sessionmaker) -> None:
    cliente = SqlServerClient()
    cliente.Session = lambda: db_session

    registro = cliente.insertar_monitoreo(
        username="usuario4",
        proceso="Proceso D",
        estado=EstadoMonitoreo.CORRECTO,
        iniciado=datetime(2025, 9, 26, 12, 0),
        finalizado=datetime(2025, 9, 26, 12, 30),
        cliente="ClienteD",
        items_count=7,
    )

    assert registro is not None
    assert int(registro.estado) == EstadoMonitoreo.CORRECTO


def test_insertar_monitoreo_falla_por_falta_de_campo(db_session: sessionmaker) -> None:
    cliente = SqlServerClient()
    cliente.Session = lambda: db_session

    with pytest.raises(TypeError):
        cliente.insertar_monitoreo(
            username="usuario5",
            proceso="Proceso E",
            estado=EstadoMonitoreo.ERRONEO,
            iniciado=datetime(2025, 9, 26, 13, 0),
            finalizado=datetime(2025, 9, 26, 13, 30),
            # falta el campo 'cliente'
            items_count=2,
        )
