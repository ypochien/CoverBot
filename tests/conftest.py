from loguru import logger
import pytest
import shioaji as sj
import pickle
from coverbot.cover import CoverBot
import pathlib
from typing import Dict, List

contract_filename = f"{pathlib.Path(__file__).parent.absolute()}/data/contracts.pkl"


@pytest.fixture
def deal_data() -> List[Dict]:
    deal_filename = f"{pathlib.Path(__file__).parent.absolute()}/data/_deals.pkl"
    with open(deal_filename, "rb") as f:
        test_data = pickle.load(f)
    return test_data


@pytest.fixture
def mock_api() -> sj.Shioaji:
    api: sj.Shioaji = sj.Shioaji()
    with open(contract_filename, "rb") as f:
        api.Contracts = pickle.load(f)
    return api


@pytest.fixture
def sut(mock_api: sj.Shioaji) -> CoverBot:
    sut = CoverBot(mock_api)
    return sut
