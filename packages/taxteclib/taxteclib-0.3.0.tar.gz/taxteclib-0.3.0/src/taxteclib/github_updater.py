import logging
import os
import re
import shutil
import zipfile

import requests
from dotenv import load_dotenv


class GithubRepoUpdater:
    """
    Clase para actualizar desde un repositorio de GitHub y aplicar SQLs de un ZIP.
    Por defecto, lee toda la configuración desde variables de entorno (.env).
    Parámetros opcionales en el constructor permiten sobreescribir valores puntuales.

    Ejemplo de uso:
        from src.taxteclib.github_updater import GithubRepoUpdater
        updater = GithubRepoUpdater()
        updater.update(extract_zip=True)

        Si necesitas sobreescribir algún parámetro:
        updater = GithubRepoUpdater(owner="otro_owner", repo="otro_repo")
        updater.update()
    """

    def __init__(
        self,
        owner: str | None = None,
        repo: str | None = None,
        token: str | None = None,
        sql_user: str | None = None,
        sql_pass: str | None = None,
        sql_server: str | None = None,
        sql_driver: str | None = None,
        n_bot: str | None = None,
    ):
        load_dotenv()
        self.owner = owner or os.getenv("GITHUB_OWNER")
        self.repo = repo or os.getenv("GITHUB_REPO")
        self.sql_user = sql_user or os.getenv("SQLSERVER_USERNAME")
        self.sql_pass = sql_pass or os.getenv("SQLSERVER_PASSWORD")
        self.sql_server = sql_server or os.getenv("SQLSERVER_SERVER")
        self.sql_driver = sql_driver or os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")
        self.n_bot = n_bot or os.getenv("GITHUB_TOKEN_REPOSITORIO", "NFEAlert")
        # Token: primero parámetro, luego entorno, luego base de datos
        env_token = os.getenv("GITHUB_TOKEN_REPOSITORIO", "")
        self.token = token or env_token
        if not self.token and self.sql_user and self.sql_pass:
            try:
                self.token = GithubRepoUpdater.get_token_from_db(self.sql_user, self.sql_pass, self.n_bot)
                if self.token:
                    logging.info("Token obtenido desde la base de datos.")
                else:
                    logging.warning("No se encontró token en la base de datos.")
            except Exception as e:
                logging.error(f"Error obteniendo token desde la base de datos: {e}")
        self.last_release_file = "last_release.txt"
        self.setup_logging()

    def setup_logging(self) -> None:
        logging.basicConfig(
            filename="update_log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def get_github_release(self) -> dict:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "update-script/1.0",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()

    def download_file(self, url: str, output_path: str) -> None:
        headers = {"Authorization": f"token {self.token}"} if self.token else {}
        with requests.get(url, headers=headers, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(output_path, "wb") as file:
                shutil.copyfileobj(response.raw, file)

    def download_asset_with_api(self, asset_id: int, output_path: str) -> None:
        headers = {"Accept": "application/octet-stream"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/assets/{asset_id}"
        with requests.get(url, headers=headers, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                shutil.copyfileobj(response.raw, f)

    def extract_zip(self, zip_path: str, extract_to: str) -> None:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            all_names = [member.filename for member in zip_ref.infolist() if member.filename and not member.is_dir()]
            if not all_names:
                return
            common_prefix = os.path.commonprefix(all_names)
            if common_prefix and not common_prefix.endswith("/"):
                common_prefix = os.path.dirname(common_prefix) + "/"
            for member in zip_ref.infolist():
                rel_path = (
                    member.filename[len(common_prefix) :]
                    if common_prefix and member.filename.startswith(common_prefix)
                    else member.filename
                )
                if not rel_path or rel_path.endswith("/"):
                    dir_path = os.path.join(extract_to, rel_path)
                    os.makedirs(dir_path, exist_ok=True)
                    continue
                extracted_path = os.path.join(extract_to, rel_path)
                os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
                with zip_ref.open(member) as source, open(extracted_path, "wb") as target:
                    shutil.copyfileobj(source, target)

    def split_sql_batches(self, sql_text: str) -> list[str]:
        parts = re.split(r"^\s*GO\s*$", sql_text, flags=re.IGNORECASE | re.MULTILINE)
        return [p.strip() for p in parts if p.strip()]

    def execute_sql_file_on_sqlserver(self, file_path: str) -> None:
        from urllib.parse import quote_plus

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        logging.info("Executing SQL file: %s", file_path)
        quoted_driver = quote_plus(self.sql_driver)
        conn_str = f"mssql+pyodbc://{self.sql_user}:{quote_plus(self.sql_pass)}@{self.sql_server}/tecnologia?driver={quoted_driver}"
        engine = create_engine(conn_str, fast_executemany=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = None
        cursor = None
        raw_conn = None
        try:
            session = SessionLocal()
            raw_conn = session.connection().connection
            cursor = raw_conn.cursor()
            with open(file_path, encoding="utf-8") as f:
                sql_text = f.read()
            batches = self.split_sql_batches(sql_text)
            logging.info("Found %d SQL batches in %s", len(batches), file_path)
            for batch in batches:
                if not batch:
                    continue
                logging.info("Executing SQL batch (len=%d)", len(batch))
                cursor.execute(batch)
            raw_conn.commit()
            logging.info("Successfully executed SQL file: %s", file_path)
        except Exception as e:
            try:
                if raw_conn is not None:
                    raw_conn.rollback()
            except Exception:
                pass
            logging.exception("Error executing SQL file %s: %s", file_path, e)
            raise
        finally:
            try:
                if cursor is not None:
                    cursor.close()
            except Exception:
                pass
            if session:
                import contextlib

                with contextlib.suppress(Exception):
                    session.close()
            import contextlib

            with contextlib.suppress(Exception):
                engine.dispose()

    def apply_sql_files_in_repo(self, root_dir: str) -> None:
        sql_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                if fname.lower().endswith(".sql"):
                    sql_files.append(os.path.join(dirpath, fname))
        if not sql_files:
            logging.info("No .sql files found under %s", root_dir)
            return
        sql_files.sort()
        logging.info("Applying %d SQL files found under %s", len(sql_files), root_dir)
        for sql_file in sql_files:
            try:
                self.execute_sql_file_on_sqlserver(sql_file)
                try:
                    os.remove(sql_file)
                    logging.info("Deleted SQL file after successful execution: %s", sql_file)
                except Exception as e:
                    logging.warning("Failed to delete SQL file %s: %s", sql_file, e)
            except Exception:
                logging.error("Failed to apply SQL file %s. Leaving file in place for inspection.", sql_file)

    def get_last_processed_release(self) -> str:
        if os.path.exists(self.last_release_file):
            with open(self.last_release_file) as file:
                return file.read().strip()
        return ""

    def save_last_processed_release(self, release_name: str) -> None:
        with open(self.last_release_file, "w") as file:
            file.write(release_name)

    def update(self, extract_zip: bool = False) -> None:
        try:
            release = self.get_github_release()
            release_name = release.get("tag_name", "")
            last_processed_release = self.get_last_processed_release()
            if release_name == last_processed_release:
                logging.info(f"Release {release_name} has already been processed. Skipping download.")
                return
            assets = release.get("assets", [])
            asset_names = [asset.get("name", "") for asset in assets]
            logging.info(f"Assets found in latest release: {asset_names}")
            if not assets:
                logging.error("No assets found in the latest release.")
                return
            zip_asset = next((asset for asset in assets if asset.get("name", "").endswith(".zip")), None)
            if not zip_asset:
                logging.error("No ZIP file found in the latest release assets.")
                return
            zip_url = zip_asset.get("browser_download_url")
            zip_name = zip_asset.get("name")
            if not zip_url or not zip_name:
                logging.error("ZIP asset is missing download URL or name.")
                return
            zip_path = os.path.join(os.getcwd(), zip_name)
            logging.info(f"Downloading {zip_name} (try API asset endpoint first)...")
            asset_id = zip_asset.get("id")
            download_succeeded = False
            if asset_id:
                logging.info(f"Attempting download via API for asset id {asset_id}...")
                try:
                    self.download_asset_with_api(asset_id, zip_path)
                    download_succeeded = True
                    logging.info("Downloaded asset via API endpoint.")
                except Exception as e:
                    logging.warning(f"API asset download failed: {e}")
            if not download_succeeded:
                logging.info(f"Attempting browser download from {zip_url} ...")
                try:
                    self.download_file(zip_url, zip_path)
                    download_succeeded = True
                    logging.info("Downloaded asset via browser_download_url.")
                except Exception as e:
                    logging.warning(f"Browser download failed: {e}")
            if not download_succeeded:
                logging.error("All download methods failed. Aborting update.")
                return
            if extract_zip:
                logging.info(f"Extracting {zip_name}...")
                try:
                    self.extract_zip(zip_path, os.getcwd())
                    sql_dir = os.path.join(os.getcwd(), "querys", "updates")
                    if os.path.isdir(sql_dir):
                        self.apply_sql_files_in_repo(sql_dir)
                    else:
                        logging.info("SQL updates directory not found, skipping: %s", sql_dir)
                except zipfile.BadZipFile:
                    logging.error("Failed to extract ZIP file. The file may be corrupted.")
                    return
                except Exception as e:
                    logging.error(f"Unexpected error extracting ZIP: {e}")
                    return
            try:
                os.remove(zip_path)
                logging.info(f"Deleted ZIP file: {zip_name}")
            except Exception as e:
                logging.error(f"Failed to delete ZIP file: {e}")
            self.save_last_processed_release(release_name)
            logging.info("Update completed successfully.")
        except requests.RequestException as e:
            logging.error(f"HTTP error occurred: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    @staticmethod
    def get_token_from_db(user: str, password: str, n_bot: str | None = None) -> str:
        """
        Intenta obtener el token GITHUB_TOKEN_REPOSITORIO desde la tabla token_updates_gh de la base 'tecnologia'.
        Busca la fila donde n_bot = n_bot (por defecto, variable de entorno N_BOT o 'NFEAlert').
        """
        import os
        from urllib.parse import quote_plus

        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker

        server = os.getenv("SQLSERVER_SERVER")
        driver = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")
        if not server:
            raise RuntimeError("SQLSERVER_SERVER no está definido en las variables de entorno")

        quoted_driver = quote_plus(driver)
        conn_str = f"mssql+pyodbc://{user}:{quote_plus(password)}@{server}/tecnologia?driver={quoted_driver}"
        engine = create_engine(conn_str, fast_executemany=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = None
        n_bot_value = n_bot or os.getenv("N_BOT")
        try:
            session = SessionLocal()
            sql = text("SELECT TOP 1 token FROM dbo.token_updates_gh WHERE n_bot = :n_bot")
            result = session.execute(sql, {"n_bot": n_bot_value}).fetchone()
            if result:
                return str(result[0])
            return ""
        finally:
            if session:
                import contextlib

                with contextlib.suppress(Exception):
                    session.close()
            import contextlib

            with contextlib.suppress(Exception):
                engine.dispose()


if __name__ == "__main__":
    updater = GithubRepoUpdater()
    updater.update(extract_zip=False)
