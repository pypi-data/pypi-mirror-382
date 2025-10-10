import os
import time

import dotenv
import pytest
from pydantic import SecretStr

from cluefin_openapi.kiwoom._auth import Auth
from cluefin_openapi.kiwoom._client import Client
from cluefin_openapi.kiwoom._domestic_theme_types import (
    DomesticThemeGroup,
    DomesticThemeGroupStocks,
)


@pytest.fixture
def auth() -> Auth:
    dotenv.load_dotenv(dotenv_path=".env.test")
    return Auth(
        app_key=os.getenv("KIWOOM_APP_KEY", ""),
        secret_key=SecretStr(os.getenv("KIWOOM_SECRET_KEY", "")),
        env="dev",
    )


@pytest.fixture
def client(auth: Auth) -> Client:
    token = auth.generate_token()
    return Client(token=token.get_token(), env="dev")


@pytest.mark.integration
def test_get_theme_group(client: Client):
    time.sleep(1)

    response = client.theme.get_theme_group(
        qry_tp=1,
        date_tp="1",
        thema_nm="test",
        flu_pl_amt_tp=1,
        stex_tp=1,
    )
    assert response.headers is not None
    assert response.body is not None
    assert isinstance(response.body, DomesticThemeGroup)


@pytest.mark.integration
def test_get_theme_group_stocks(client: Client):
    time.sleep(1)

    response = client.theme.get_theme_group_stocks(date_tp="2", thema_grp_cd="100", stex_tp="1")
    assert response.headers is not None
    assert response.body is not None
    assert isinstance(response.body, DomesticThemeGroupStocks)
