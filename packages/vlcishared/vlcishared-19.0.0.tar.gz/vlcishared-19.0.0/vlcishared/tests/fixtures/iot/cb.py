import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_cb_manager_patch(monkeypatch):
    """
    Fixture que devuelve una instancia de cbManager con varias partes mockeadas:
    - session: para no hacer llamadas HTTP reales.
    - métodos internos como get_entities, send_batch, __send_batch, etc.
    """

    def _patch(
        ruta_importacion: str,
        get_entities_return_value=None,
        get_entities_side_effect=None,
        get_entities_page_return_value=None,
        get_entities_page_side_effect=None,
        send_batch_return_value=True,
        send_batch_side_effect=None,
        delete_entities_return_value=None,
        delete_entities_side_effect=None,
    ):
        mock_cb = MagicMock()
        mock_cb.session = MagicMock()

        mock_cb.get_entities.return_value = get_entities_return_value
        if get_entities_side_effect:
            mock_cb.get_entities.side_effect = get_entities_side_effect

        mock_cb.get_entities_page.return_value = get_entities_page_return_value
        if get_entities_page_side_effect:
            mock_cb.get_entities_page.side_effect = get_entities_page_side_effect

        mock_cb.send_batch.return_value = send_batch_return_value
        if send_batch_side_effect:
            mock_cb.send_batch.side_effect = send_batch_side_effect

        mock_cb.delete_entities.return_value = delete_entities_return_value
        if delete_entities_side_effect:
            mock_cb.delete_entities.side_effect = delete_entities_side_effect

        # Inyectar mock en la ruta indicada
        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: mock_cb)
        return mock_cb

    return _patch
