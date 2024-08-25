"""Platform for sensor integration."""

from __future__ import annotations

import logging

from urllib.parse import urlparse
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.components.sensor.const import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_ICON,
    DOMAIN,
    UNIT_OF_MEASUREMENT,
    CONFIG_ENDPOINT,
    CONFIG_PASSWORD,
    CONFIG_FILE,
    CONFIG_CERT,
    CONFIG_ENCRYPT_PASSWORD,
)
from .actualbudget import ActualBudget

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Time between updating data from API
SCAN_INTERVAL = timedelta(minutes=60)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Setup sensor platform."""
    config = config_entry.data
    endpoint = config[CONFIG_ENDPOINT]
    password = config[CONFIG_PASSWORD]
    file = config[CONFIG_FILE]
    cert = config.get(CONFIG_CERT)
    if cert == "SKIP":
        cert = False
    encrypt_password = config.get(CONFIG_ENCRYPT_PASSWORD)
    api = ActualBudget(hass, endpoint, password, file, cert, encrypt_password)

    domain = urlparse(endpoint).hostname
    port = urlparse(endpoint).port
    unique_source_id = f"{domain}_{port}_{file}"

    accounts = await api.get_accounts()
    accounts = [
        actualbudgetAccountSensor(
            api,
            endpoint,
            password,
            file,
            cert,
            encrypt_password,
            account["name"],
            account["balance"],
            unique_source_id,
        )
        for account in accounts
    ]
    async_add_entities(accounts, update_before_add=True)

    budgets = await api.get_budgets()
    budgets = [
        actualbudgetBudgetSensor(
            api,
            endpoint,
            password,
            file,
            cert,
            encrypt_password,
            budget["name"],
            budget["amount"],
            unique_source_id,
        )
        for budget in budgets
    ]
    async_add_entities(budgets, update_before_add=True)


class actualbudgetAccountSensor(SensorEntity):
    """Representation of a actualbudget Sensor."""

    def __init__(
        self,
        api: ActualBudget,
        endpoint: str,
        password: str,
        file: str,
        cert: str,
        encrypt_password: str | None,
        name: str,
        balance: float,
        unique_source_id: str,
    ):
        super().__init__()
        self._api = api
        self._name = name
        self._balance = balance
        self._unique_source_id = unique_source_id
        self._endpoint = endpoint
        self._password = password
        self._file = file
        self._cert = cert
        self._encrypt_password = encrypt_password

        self._icon = DEFAULT_ICON
        self._unit_of_measurement = UNIT_OF_MEASUREMENT
        self._device_class = SensorDeviceClass.MONETARY
        self._state_class = SensorStateClass.MEASUREMENT
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{DOMAIN}-{self._unique_source_id}-{self._name}".lower()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> float:
        return self._state

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        return self._icon

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            api = self._api
            account = await api.get_account(self._name)
            if account:
                self._state = account.get("balance")
        except Exception as err:
            self._available = False
            _LOGGER.exception(
                "Unknown error updating data from ActualBudget API to account %s. %s",
                self._name,
                err,
            )


class actualbudgetBudgetSensor(SensorEntity):
    """Representation of a actualbudget Sensor."""

    def __init__(
        self,
        api: ActualBudget,
        endpoint: str,
        password: str,
        file: str,
        cert: str,
        encrypt_password: str | None,
        name: str,
        balance: float,
        unique_source_id: str,
    ):
        super().__init__()
        self._api = api
        self._name = name
        self._balance = balance
        self._unique_source_id = unique_source_id
        self._endpoint = endpoint
        self._password = password
        self._file = file
        self._cert = cert
        self._encrypt_password = encrypt_password

        self._icon = DEFAULT_ICON
        self._unit_of_measurement = UNIT_OF_MEASUREMENT
        self._device_class = SensorDeviceClass.MONETARY
        self._state_class = SensorStateClass.MEASUREMENT
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{DOMAIN}-{self._unique_source_id}-{self._name}".lower()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> float:
        return self._state

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        return self._icon

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            api = self._api
            account = await api.get_budget(self._name)
            if account:
                self._state = account.get("amount")
        except Exception as err:
            self._available = False
            _LOGGER.exception(
                "Unknown error updating data from ActualBudget API to budget %s. %s",
                self._name,
                err,
            )
