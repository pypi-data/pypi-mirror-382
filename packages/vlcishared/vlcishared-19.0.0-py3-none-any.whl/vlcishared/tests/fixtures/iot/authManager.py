import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_auth_manager_patch(monkeypatch):
    """
    Fixture que devuelve una instancia de authManager mockeada,
    con posibilidad de configurar valores de retorno y side effects.

    Métodos mockeados:
    - set_token
    - get_info
    - check_mandatory_fields
    - _post_auth_request
    - get_auth_token_subservice
    - get_auth_token_service
    """

    def _patch(
        ruta_importacion: str,
        set_token_return_value=None,
        set_token_side_effect=None,
        get_info_return_value=None,
        get_info_side_effect=None,
        check_mandatory_fields_return_value=None,
        check_mandatory_fields_side_effect=None,
        post_auth_request_return_value=None,
        post_auth_request_side_effect=None,
        get_auth_token_subservice_return_value=None,
        get_auth_token_subservice_side_effect=None,
        get_auth_token_service_return_value=None,
        get_auth_token_service_side_effect=None,
    ):
        mock_auth = MagicMock()

        mock_auth.set_token.return_value = set_token_return_value
        if set_token_side_effect:
            mock_auth.set_token.side_effect = set_token_side_effect

        mock_auth.get_info.return_value = get_info_return_value
        if get_info_side_effect:
            mock_auth.get_info.side_effect = get_info_side_effect

        mock_auth.check_mandatory_fields.return_value = check_mandatory_fields_return_value
        if check_mandatory_fields_side_effect:
            mock_auth.check_mandatory_fields.side_effect = check_mandatory_fields_side_effect

        mock_auth._post_auth_request.return_value = post_auth_request_return_value
        if post_auth_request_side_effect:
            mock_auth._post_auth_request.side_effect = post_auth_request_side_effect

        mock_auth.get_auth_token_subservice.return_value = get_auth_token_subservice_return_value
        if get_auth_token_subservice_side_effect:
            mock_auth.get_auth_token_subservice.side_effect = get_auth_token_subservice_side_effect

        mock_auth.get_auth_token_service.return_value = get_auth_token_service_return_value
        if get_auth_token_service_side_effect:
            mock_auth.get_auth_token_service.side_effect = get_auth_token_service_side_effect

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: mock_auth)
        return mock_auth

    return _patch
