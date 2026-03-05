# Function & Class List

## `__init__.py`
* **`async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool`**: Sets up the VMC integration using data from config entry. Initializes the data update coordinator.
* **`async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool`**: Removes the integration and unloads platforms.
* **`class ThesanDataUpdateCoordinator(DataUpdateCoordinator)`**: Coordinates polling local HTTP data from the VMC.
    * `__init__(self, hass, session, host)`: Initialize the coordinator with update intervals.
    * `_async_update_data(self) -> dict`: Polls the device for speed, mode, temperatures, humidity, and filter days via multiple HTTP GET endpoints.
    * `async_set_speed(self, speed: int) -> bool`: Sends an HTTP POST command to change the fan speed.
    * `async_set_mode(self, mode: int) -> bool`: Sends an HTTP POST command to change the operating mode (Auto, Manual, Bypass).

## `config_flow.py`
* **`class ThesanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN)`**: Handles the UI configuration flow.
    * `async_step_user(self, user_input=None)`: Steps the user through entering the Host IP address and verifies connectivity by hitting `/device`.

## `fan.py`
* **`async_setup_entry(hass, entry, async_add_entities)`**: Registers the fan entity with Home Assistant.
* **`class ThesanVMCFan(CoordinatorEntity, FanEntity)`**: Represents the VMC unit as a Home Assistant Fan.
    * `__init__(self, coordinator, entry)`: Sets up fan properties.
    * `is_on(self) -> bool`: Checks if fan speed > 0.
    * `percentage(self) -> int | None`: Parses the current speed level (1-5) into a UI percentage (0-100%).
    * `preset_mode(self) -> str | None`: Returns the current string representation of the mode (Auto, Manual, Bypass).
    * `async_set_preset_mode(self, preset_mode: str) -> None`: Sets the target preset mode.
    * `speed_count(self) -> int`: Returns 5 (number of speeds).
    * `async_set_percentage(self, percentage: int) -> None`: Converts a requested percentage back to a 1-5 speed and sends it to the VMC.
    * `async_turn_on(self, percentage=None, preset_mode=None, **kwargs) -> None`: Turns on the fan to speed 2 or the configured percentage.
    * `async_turn_off(self, **kwargs) -> None`: Sets fan speed to 0.
    * `extra_state_attributes(self) -> dict`: Provides extra raw diagnostic data (`mode_value`, `raw_speed`).

## `sensor.py`
* **`async_setup_entry(hass, entry, async_add_entities)`**: Registers all sensor entities.
* **`class ThesanSensorBase(CoordinatorEntity, SensorEntity)`**: Base class for all Thesan sensors.
    * `__init__(self, coordinator, entry, sensor_key, sensor_name)`: Default setup using coordinator data keys.
* **`class ThesanTemperatureSensor(ThesanSensorBase)`**: Reads temperatures (`temp_int`, `temp_ext`).
    * `native_value(self) -> float | None`: Returns the parsed temperature value.
* **`class ThesanHumiditySensor(ThesanSensorBase)`**: Reads internal humidity (`humidity`).
    * `native_value(self) -> float | None`: Returns the parsed humidity percentage.
* **`class ThesanFilterSensor(ThesanSensorBase)`**: Reads filter days remaining (`filter_days`).
    * `native_value(self) -> int | None`: Returns the remaining filter lifespan in days.


