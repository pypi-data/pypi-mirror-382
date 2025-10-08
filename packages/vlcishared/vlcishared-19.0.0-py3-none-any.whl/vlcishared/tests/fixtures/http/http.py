import os
import shutil
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_http_patch(monkeypatch):
    """
    Fixture reutilizable que mockea la clase ClienteHTTP para evitar conexiones reales con HTTP.

    - Mockea los métodos: get, post, descargar_archivo y cerrar para evitar efectos secundarios.
    - Requiere pasar la ruta del módulo donde se importa ClienteHTTP (para el monkeypatch dinámico).
    - Retorna una función auxiliar que permite personalizar los efectos de los métodos mockeados.

    Parámetros de la función auxiliar `_patch`:
    - ruta_importacion (str): Ruta donde se importa ClienteHTTP (ej. "mi_paquete.mi_modulo.ClienteHTTP").
    - get_side_effect (callable|None): Función a ejecutar cuando se llama a `get()`.
    - post_side_effect (callable|None): Función a ejecutar cuando se llama a `post()`.
    - descargar_archivo_side_effect (callable|None): Función a ejecutar cuando se llama a `descargar_archivo()`.

    Uso:
        def test_xxx(mock_http_patch):
            mock_http = mock_http_patch("modulo.donde.se.importa.ClienteHTTP", descargar_archivo_side_effect=mi_funcion)
    """

    def _patch(
        ruta_importacion: str,
        get_side_effect=None,
        post_side_effect=None,
        post_con_reintentos_side_effect=None,
        descargar_archivo_get_side_effect=None,
        descargar_archivo_post_side_effect=None,
    ):
        http = MagicMock()
        http.cerrar.return_value = None

        http.get.side_effect = get_side_effect
        http.post.side_effect = post_side_effect
        http.post_con_reintentos.side_effect = post_con_reintentos_side_effect
        http.descargar_archivo_get.side_effect = (
            descargar_archivo_get_side_effect or patch_descargar_archivo_get_side_effect
        )
        http.descargar_archivo_post.side_effect = (
            descargar_archivo_post_side_effect or patch_descargar_archivo_post_side_effect()
        )

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: http)
        return http

    return _patch


def patch_descargar_archivo_get_side_effect(url, destino):
    """
    Simula la descarga de un archivo desde HTTP copiándolo desde 'url' a 'destino'.
    """
    shutil.copyfile(url, destino)
    return True

def patch_descargar_archivo_post_side_effect(contenido_salida: str = "<Respuesta><Ok>True</Ok></Respuesta>"):
    """
    Devuelve una función side effect que escribe 'contenido_salida' en el archivo destino.
    Esto permite parametrizar el contenido fácilmente en los tests.
    """

    def _inner(url_origen, destino, url_headers, url_body):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            f.write(contenido_salida)
        return True

    return _inner
