import pytest
from core.config import MainSettings
from domains.controllers.oauth import OauthController
from domains.controllers.user import UserController
from services.dependencies.oauth import get_oauth_controller
from services.dependencies.users import get_user_controller


@pytest.fixture(scope="function")
def provide_user_controller(get_test_settings: MainSettings) -> UserController:
    return get_user_controller(settings=get_test_settings)


@pytest.fixture(scope="function")
def provide_auth_controller(get_test_settings: MainSettings) -> OauthController:
    return get_oauth_controller(settings=get_test_settings)
