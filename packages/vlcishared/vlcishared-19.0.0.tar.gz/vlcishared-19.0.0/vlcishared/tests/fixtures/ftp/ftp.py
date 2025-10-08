from datetime import datetime
import fnmatch
import os
import shutil
from unittest.mock import MagicMock

import pytz

import pytest

from vlcishared.ftp.ftp import FTPClient
from vlcishared.tests.fixtures.ftp.sftp import patch_delete_side_effect, patch_upload_side_effect


@pytest.fixture
def mock_ftp_patch(monkeypatch):
    """
    Fixture reutilizable que mockea la clase FTPClient para evitar conexiones reales con FTP.

    - Mockea los métodos para evitar efectos reales.
    - Requiere pasar la ruta donde se usa FTPClient (para monkeypatching dinámico).

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `FTPClient` (ej. "mi_paquete.mi_modulo.FTPClient").
    - list_return (list): Lista de archivos que devolverá `list()`.
    - list_side_effect (callable|None): Función a ejecutar en `list()`.
    - list_matching_files_return (list): Lista de archivos que devolverá `list_matching_files()`.
    - list_matching_files_side_effect (callable|None): Función a ejecutar en `list_matching_files()`.
    - upload_side_effect (callable|None): Función a ejecutar en `upload()`.
    - delete_side_effect (callable|None): Función a ejecutar en `delete()`.
    - execute_with_connection_side_effect (callable|None): Función a ejecutar en `execute_with_connection()`.

    Uso:
        def test_xxx(mock_ftp_patch):
            mock_ftp = mock_ftp_patch("modulo.donde.importa.FTPClient", list_return=["file1.csv"], ...)
    """

    def _patch(
        ruta_importacion: str,
        list_return=[],
        list_side_effect=None,
        list_matching_files_return=[],
        list_matching_files_side_effect=None,
        download_side_effect=patch_ftp_download_side_effect,
        upload_side_effect=patch_upload_side_effect,
        delete_side_effect=patch_delete_side_effect,
        execute_with_connection_side_effect=None,
    ):
        ftp_mock = MagicMock(spec=FTPClient)
        ftp_mock.connect.return_value = None
        ftp_mock.close.return_value = None

        ftp_mock.list.return_value = list_return
        if list_side_effect:
            ftp_mock.list.side_effect = list_side_effect

        ftp_mock.list_matching_files.return_value = list_matching_files_return
        if list_matching_files_side_effect:
            ftp_mock.list_matching_files.side_effect = list_matching_files_side_effect

        ftp_mock.download.side_effect = lambda remote_path, local_path, pattern, min_date=None: download_side_effect(
            ftp_mock, remote_path, local_path, pattern, min_date
        )
        ftp_mock.upload.side_effect = upload_side_effect
        ftp_mock.delete.side_effect = delete_side_effect

        if execute_with_connection_side_effect:
            ftp_mock.execute_with_connection.side_effect = execute_with_connection_side_effect
        else:
            ftp_mock.execute_with_connection.side_effect = lambda func, *args, **kwargs: patch_ftp_execute_with_connection_side_effect(
                ftp_mock, func, *args, **kwargs
            )

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: ftp_mock)
        return ftp_mock

    return _patch


def patch_ftp_execute_with_connection_side_effect(ftp_mock, func, *args, **kwargs):
    """
    Simula execute_with_connection ejecutando la función pasada sin manejar conexiones reales.
    """
    return func(*args, **kwargs)


def patch_ftp_list_matching_files_side_effect(directorio, patron):
    """
    Simula list_matching_files listando archivos del directorio que coincidan con el patrón.
    """
    archivos = os.listdir(directorio)
    archivos_coincidentes = fnmatch.filter(archivos, patron)
    return archivos_coincidentes


def patch_ftp_download_side_effect(self, remote_path, local_path, pattern, min_date=None):
    """
    Simula la descarga de archivos desde remote_path a local_path,
    filtrando por patrón regex y copiando los archivos locales que coincidan.
    """
    archivos = os.listdir(remote_path)
    matching_files = fnmatch.filter(archivos, pattern)
    for archivo in matching_files:
        origen = os.path.join(remote_path, archivo)
        destino = os.path.join(local_path, archivo)

        fecha_mod = datetime.fromtimestamp(os.path.getmtime(origen), pytz.UTC)

        # Filtrar por min_date si se proporciona
        if min_date and fecha_mod <= min_date:
            continue

        shutil.copyfile(origen, destino)
