"""
Containers for the end-to-end tests: a ganache chain, the Ledger emulator and
the Trezor emulators. They are started through testcontainers and stopped at
the end of the session. The tests are marked `e2e` or `e2e_trezor` and skipped
when Docker is not reachable, so the default run stays offline.
"""

import hashlib
import importlib
import json
import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

import docker
import pytest
from eth_account import Account
from safe_eth.eth import EthereumClient
from safe_eth.safe.proxy_factory import ProxyFactoryV141
from safe_eth.safe.safe import SafeV141
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

from safe_cli.operators.hw_wallets.hw_wallet_manager import get_hw_wallet_manager

# Images pinned by digest: the screen texts the tests assert come from the
# apps inside, and `latest` would move under them
GANACHE_IMAGE = "trufflesuite/ganache@sha256:7b58eeff2a5cfeb62ee19fe16ce7c5b88b9e9bae0f627719121609e9e188b730"  # v7.9.2
SPECULOS_IMAGE = "ghcr.io/ledgerhq/speculos@sha256:6ed9eefd51cddd862b746719af4cd7a3265fe43d0588c388359753cab8d46d11"  # 2026-09
TREZOR_ENV_IMAGE = "ghcr.io/trezor/trezor-user-env@sha256:778ae4f0ae7ba91581faf3e12ae5a52e8afc853adf1cccd02c19ca7d83047442"  # 2026-09
ETH_APP_VERSION = "1.22.3"
ETH_APP_SHA256 = "d8631ab43961928851e66175bef6d0157e5c516389b8b61bdb3c239a8125944e"
ETH_APP_URL = (
    "https://github.com/LedgerHQ/app-ethereum/releases/download/"
    f"{ETH_APP_VERSION}/app-{ETH_APP_VERSION}-nanos2.elf"
)
# First account of ganache --deterministic
DEPLOYER_KEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
SPECULOS_SEED = "abandon " * 11 + "about"


@pytest.fixture(scope="session")
def docker_daemon():
    try:
        docker.from_env().ping()
    except Exception:
        pytest.skip("Docker is not reachable")


@pytest.fixture(scope="session")
def ganache(docker_daemon) -> str:
    """
    :return: RPC URL of a fresh deterministic ganache (chain id 1337)
    """
    container = (
        DockerContainer(GANACHE_IMAGE)
        .with_command(
            "--defaultBalanceEther 10000 -a 10 --chain.chainId 1337 "
            "--deterministic --host 0.0.0.0"
        )
        .with_exposed_ports(8545)
        .waiting_for(
            LogMessageWaitStrategy("RPC Listening on").with_startup_timeout(60)
        )
    )
    with container:
        yield f"http://{container.get_container_host_ip()}:{container.get_exposed_port(8545)}"


@pytest.fixture(scope="session")
def client(ganache) -> EthereumClient:
    return EthereumClient(ganache)


@pytest.fixture(scope="session")
def deployer():
    return Account.from_key(DEPLOYER_KEY)


@pytest.fixture(scope="session")
def safe_contracts(client, deployer) -> tuple[str, str]:
    """
    :return: Safe 1.4.1 master copy and proxy factory, shared by every test
    """
    master_copy = SafeV141.deploy_contract(client, deployer).contract_address
    factory = ProxyFactoryV141.deploy_contract(client, deployer).contract_address
    assert master_copy is not None and factory is not None
    return master_copy, factory


@pytest.fixture(autouse=True)
def fresh_hw_wallet_manager():
    """
    The manager is a process wide singleton, so every test gets a new one
    without wallets or sender from the previous test.
    """
    get_hw_wallet_manager.cache_clear()
    yield
    get_hw_wallet_manager.cache_clear()


def _ethereum_app() -> Path:
    """
    :return: path of the Ethereum app binary Ledger publishes, cached between runs
    """
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    target = cache / "safe-cli-tests" / f"app-ethereum-{ETH_APP_VERSION}-nanos2.elf"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(ETH_APP_URL, timeout=60) as response:
            target.write_bytes(response.read())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if digest != ETH_APP_SHA256:
        target.unlink()
        raise RuntimeError(
            f"Ledger app binary hash {digest} does not match {ETH_APP_SHA256}"
        )
    return target


class Speculos:
    """
    The emulator REST API: read the screen and press buttons.
    """

    def __init__(self, api_url: str) -> None:
        self.api_url = api_url

    def screen(self) -> list[str]:
        with urllib.request.urlopen(
            f"{self.api_url}/events?currentscreenonly=true", timeout=5
        ) as response:
            return [event["text"] for event in json.load(response)["events"]]

    def press(self, button: str, pause: float = 0.5) -> None:
        request = urllib.request.Request(
            f"{self.api_url}/button/{button}",
            data=b'{"action":"press-and-release"}',
            method="POST",
        )
        urllib.request.urlopen(request, timeout=5).read()
        time.sleep(pause)

    def wait_idle(self, timeout: float = 10) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if "app is ready" in " ".join(self.screen()).lower():
                return
            time.sleep(0.2)
        raise TimeoutError(
            f"Speculos did not return to the main screen: {self.screen()}"
        )

    def enable_blind_signing(self) -> None:
        """
        Settings → Blind signing → toggle → Back. The app refuses EIP-712
        hashes and contract calls without it.
        """
        self.wait_idle()
        self.press("right")  # App settings
        self.press("both")
        assert "Blind signing" in self.screen(), self.screen()
        if "Enabled" not in self.screen():
            self.press("both")
        assert "Enabled" in self.screen(), self.screen()
        while "Back" not in self.screen():
            self.press("right")
        self.press("both")

    def approve_everything(self) -> "SpeculosApprover":
        return SpeculosApprover(self)


class SpeculosApprover(threading.Thread):
    """
    Walks through review screens and confirms on the accept screen, until
    stopped. Every distinct screen is recorded, so a test can assert what the
    device showed. Pauses are slow on purpose: with faster presses Speculos
    misses the accept screen.
    """

    ACCEPT_WORDS = ("accept", "sign message", "sign transaction")
    IDLE_SCREENS = {
        "app settings",
        "app info",
        "quit app",
        "message signed",
        "transaction signed",
    }

    def __init__(self, speculos: Speculos) -> None:
        super().__init__(daemon=True)
        self.speculos = speculos
        self.stop_event = threading.Event()
        self.seen: list[list[str]] = []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_exc):
        self.stop_event.set()
        self.join(timeout=5)

    def run(self) -> None:
        while not self.stop_event.is_set():
            try:
                texts = self.speculos.screen()
            except Exception:
                time.sleep(0.2)
                continue
            joined = " ".join(texts).lower().strip()
            if not texts or "app is ready" in joined or joined in self.IDLE_SCREENS:
                time.sleep(0.2)
                continue
            if texts not in self.seen:
                self.seen.append(texts)
            if (
                any(word in joined for word in self.ACCEPT_WORDS)
                and "reject" not in joined
            ):
                self.speculos.press("both", pause=0.8)
            else:
                self.speculos.press("right", pause=0.3)

    def saw(self, text: str) -> bool:
        return any(text in " ".join(screen) for screen in self.seen)

    def shown(self) -> str:
        return " ".join("".join(screen) for screen in self.seen)


@pytest.fixture(scope="session")
def speculos(docker_daemon):
    """
    The Ledger emulator running the Ethereum app, with blind signing enabled
    and ledgerblue pointed at it through the proxy variables.
    """
    app = _ethereum_app()
    container = (
        DockerContainer(SPECULOS_IMAGE)
        .with_volume_mapping(str(app), "/app.elf", "ro")
        .with_command(
            "--model nanosp --display headless --apdu-port 9999 --api-port 5000 "
            f'--seed "{SPECULOS_SEED}" /app.elf'
        )
        .with_exposed_ports(9999, 5000)
        .waiting_for(LogMessageWaitStrategy("Env app version").with_startup_timeout(60))
    )
    with container:
        host = container.get_container_host_ip()
        emulator = Speculos(f"http://{host}:{container.get_exposed_port(5000)}")
        os.environ["LEDGER_PROXY_ADDRESS"] = host
        os.environ["LEDGER_PROXY_PORT"] = str(container.get_exposed_port(9999))
        # ledgerblue reads the proxy variables when its comm module is imported
        if "ledgerblue.comm" in sys.modules:
            importlib.reload(sys.modules["ledgerblue.comm"])
        emulator.enable_blind_signing()
        yield emulator


@pytest.fixture(scope="session")
def trezor_user_env(docker_daemon):
    """
    trezor-user-env on the host network: controller on 9001, emulator on UDP
    21324/21325. Host networking because the emulator binds loopback inside
    the container, so published ports cannot reach it.
    """
    container = (
        DockerContainer(TREZOR_ENV_IMAGE)
        .with_kwargs(network_mode="host")
        .waiting_for(
            LogMessageWaitStrategy("Uvicorn running").with_startup_timeout(120)
        )
    )
    with container:
        time.sleep(2)  # the websocket controller comes up right after the log line
        yield container
