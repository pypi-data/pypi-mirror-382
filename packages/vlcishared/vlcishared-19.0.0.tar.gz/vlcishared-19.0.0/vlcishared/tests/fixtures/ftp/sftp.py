from datetime import datetime
import os
import re
import shutil
from unittest.mock import MagicMock

import pytz

import pytest

from vlcishared.sftp.sftp import SFTPClient


@pytest.fixture
def mock_sftp_patch(monkeypatch):
    """
    Fixture reutilizable que mockea la clase SFTPClient para evitar conexiones reales con SFTP.

    - Reutilizable en distintos módulos donde se importe SFTPClient.
    - Mockea los métodos: list, list_sorted_date_modification, download (con shutil.copyfile), move, upload, delete, sftp.rename y execute_with_connection para evitar efectos reales.
    - Devuelve una función que permite especificar el path del import y el retorno de list().
    - Requiere pasar la ruta donde se usa SFTPClient (para monkeypatching dinámico).

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `SFTPClient` (ej. "mi_paquete.mi_modulo.SFTPClient").
    - listdir_return (list): Lista de archivos que devolverá `os.listdir()`.
    - listdir_side_effect (callable|None): Función a ejecutar en `os.listdir()`.
    - list_matching_files_return (list): Lista de archivos que devolverá `list_matching_files()`.
    - list_matching_files_side_effect (callable|None): Función a ejecutar en `list_matching_files()`.
    - list_all_files_return (list): Lista de archivos que devolverá `list_all_files()`.
    - list_all_files_side_effect (callable|None): Función a ejecutar en `list_all_files()`.
    - list_sorted_date_modification_return (list): Resultado que devolverá `list_sorted_date_modification()`.
    - list_sorted_date_modification_side_effect (callable|None): Función a ejecutar en `list_sorted_date_modification()`.
    - get_side_effect (callable|None): Función a ejecutar en `get()`, por defecto usa `patch_get_side_effect`.
    - move_side_effect (callable|None): Función a ejecutar en `move()`.
    - upload_side_effect (callable|None): Función a ejecutar en `upload()`.
    - delete_side_effect (callable|None): Función a ejecutar en `delete()`.
    - sftp_rename_side_effect (callable|None): Función a ejecutar en `sftp.rename()`.
    - execute_with_connection_side_effect (callable|None): Función a ejecutar en `execute_with_connection()`.

    Uso:
        def test_xxx(mock_sftp_patch):
            mock_sftp = mock_sftp_patch("modulo.donde.importa.SFTPClient", list_return=["file1.csv"], ...)
    """

    def _patch(
        ruta_importacion: str,
        listdir_return=[],
        listdir_side_effect=None,
        list_matching_files_return=[],
        list_matching_files_side_effect=None,
        list_all_files_return=[],
        list_all_files_side_effect=None,
        list_sorted_date_modification_return=[],
        list_sorted_date_modification_side_effect=None,
        download_side_effect=patch_download_side_effect,
        move_side_effect=patch_move_side_effect,
        upload_side_effect=patch_upload_side_effect,
        delete_side_effect=patch_delete_side_effect,
        sftp_rename_side_effect=patch_sftp_rename_side_effect,
        execute_with_connection_side_effect=None,
    ):
        sftp_mock = MagicMock(spec=SFTPClient)
        sftp_mock.connect.return_value = None
        sftp_mock.close.return_value = None

        sftp_mock.sftp = MagicMock()
        sftp_mock.sftp.listdir.return_value = listdir_return
        if listdir_side_effect:
            sftp_mock.sftp.listdir.side_effect = listdir_side_effect

        sftp_mock.list_matching_files.return_value = list_matching_files_return
        if list_matching_files_side_effect:
            sftp_mock.list_matching_files.side_effect = list_matching_files_side_effect

        sftp_mock.list_all_files.return_value = list_all_files_return
        if list_all_files_side_effect:
            sftp_mock.list_all_files.side_effect = list_all_files_side_effect

        sftp_mock.list_sorted_date_modification.return_value = list_sorted_date_modification_return
        if list_sorted_date_modification_side_effect:
            sftp_mock.list_sorted_date_modification.side_effect = list_sorted_date_modification_side_effect

        sftp_mock.download.side_effect = lambda remote_path, local_path, pattern, min_date=None: download_side_effect(
            sftp_mock, remote_path, local_path, pattern, min_date
        )
        sftp_mock.move.side_effect = move_side_effect
        sftp_mock.upload.side_effect = upload_side_effect
        sftp_mock.delete.side_effect = delete_side_effect
        sftp_mock.sftp.rename.side_effect = sftp_rename_side_effect

        if execute_with_connection_side_effect:
            sftp_mock.execute_with_connection.side_effect = execute_with_connection_side_effect
        else:
            sftp_mock.execute_with_connection.side_effect = lambda func, *args, **kwargs: patch_execute_with_connection_side_effect(sftp_mock, func, *args, **kwargs)

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: sftp_mock)
        return sftp_mock

    return _patch


def patch_execute_with_connection_side_effect(sftp_mock, func, *args, **kwargs):
    """
    Simula execute_with_connection ejecutando la función pasada sin manejar conexiones reales.
    """
    return func(*args, **kwargs)


def patch_list_matching_files_side_effect(directorio, patron):
    """
    Simula list_matching_files listando archivos del directorio que coincidan con el patrón.
    """
    archivos = os.listdir(directorio)
    archivos_coincidentes = [f for f in archivos if re.fullmatch(patron, f)]
    return archivos_coincidentes


def patch_list_all_files_side_effect(directorio):
    return os.listdir(directorio)


def patch_download_side_effect(self, remote_path, local_path, pattern, min_date=None):
    """
    Simula la descarga de archivos desde remote_path a local_path,
    filtrando por patrón regex y copiando los archivos locales que coincidan.
    """
    archivos_remotos = self.sftp.listdir()
    matching_files = [f for f in archivos_remotos if re.fullmatch(pattern, f)]
    for archivo in matching_files:
        origen = os.path.join(remote_path, archivo)
        destino = os.path.join(local_path, archivo)

        fecha_mod = datetime.fromtimestamp(os.path.getmtime(origen), pytz.UTC)

        # Filtrar por min_date si se proporciona
        if min_date and fecha_mod <= min_date:
            continue

        shutil.copyfile(origen, destino)


def patch_move_side_effect(origen, destino, archivo):
    """
    Simula el mover de un archivo SFTP moviéndolo desde 'origen' a 'destino'.
    """
    shutil.move(os.path.join(origen, archivo), os.path.join(destino, archivo))


def patch_upload_side_effect(origen, destino):
    """
    Simula la subida de un archivo SFTP copiándolo desde 'origen' a 'destino'.
    """
    shutil.copyfile(origen, destino)


def patch_delete_side_effect(archivo):
    """
    Simula la eliminación de un archivo SFTP eliminándolo en la ruta recibida.
    """
    os.remove(archivo)


def patch_sftp_rename_side_effect(nombre_antiguo, nombre_nuevo):
    """
    Simula el renombramiento de un fichero de SFTP.
    """
    os.rename(nombre_antiguo, nombre_nuevo)