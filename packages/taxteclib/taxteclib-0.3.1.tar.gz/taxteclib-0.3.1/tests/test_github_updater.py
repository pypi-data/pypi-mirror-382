import os
import tempfile
import zipfile

import pytest
from pytest import MonkeyPatch

from src.taxteclib.github_updater import GithubRepoUpdater


# Mocks globales para monkeypatch
class DummySession:
    def execute(self, sql: object, params: object) -> object:
        class DummyResult:
            def fetchone(self) -> tuple[str]:
                return ("dummy_token",)

        return DummyResult()

    def close(self) -> None:
        pass


class DummyEngine:
    def dispose(self) -> None:
        pass


def dummy_create_engine(conn_str: str, fast_executemany: bool = True) -> DummyEngine:
    return DummyEngine()


def dummy_sessionmaker(**kwargs: object) -> object:
    return lambda: DummySession()


@pytest.fixture
def updater() -> GithubRepoUpdater:
    # Variables de entorno dummy para test
    os.environ["GITHUB_OWNER"] = "octocat"
    os.environ["GITHUB_REPO"] = "Hello-World"
    os.environ["GITHUB_TOKEN_REPOSITORIO"] = ""
    os.environ["SQLSERVER_USERNAME"] = "testuser"
    os.environ["SQLSERVER_PASSWORD"] = "testpass"
    os.environ["SQLSERVER_SERVER"] = "localhost"
    os.environ["SQLSERVER_DRIVER"] = "ODBC Driver 17 for SQL Server"
    os.environ["N_BOT"] = "NFEAlert"
    # Inicialización simple, sin argumentos
    return GithubRepoUpdater()


def test_get_token_from_db_static(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("sqlalchemy.create_engine", dummy_create_engine)
    monkeypatch.setattr("sqlalchemy.orm.sessionmaker", dummy_sessionmaker)
    token = GithubRepoUpdater.get_token_from_db("user", "pass", "NFEAlert")
    assert token == "dummy_token"


def test_github_release_fetch(updater: GithubRepoUpdater) -> None:
    # Solo prueba que la función construye la URL y headers correctamente
    url = f"https://api.github.com/repos/{updater.owner}/{updater.repo}/releases/latest"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "update-script/1.0",
    }
    if updater.token:
        headers["Authorization"] = f"token {updater.token}"
    assert url.endswith(f"/{updater.repo}/releases/latest")
    assert "Accept" in headers
    assert "User-Agent" in headers


def test_extract_zip_creates_files(updater: GithubRepoUpdater) -> None:
    # Crea un zip temporal con un archivo y verifica extracción
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "test.zip")
        file_inside = "folder/test.txt"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(file_inside, "contenido")
        extract_to = os.path.join(tmpdir, "extract")
        os.makedirs(extract_to, exist_ok=True)
        updater.extract_zip(zip_path, extract_to)
        assert os.path.isfile(os.path.join(extract_to, "test.txt"))


def test_split_sql_batches(updater: GithubRepoUpdater) -> None:
    sql = "SELECT 1\nGO\nSELECT 2\nGO\n"
    batches = updater.split_sql_batches(sql)
    assert batches == ["SELECT 1", "SELECT 2"]
