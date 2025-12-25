import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
from .api import LianderApi  # your API wrapper

class LianderConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            if self.is_already_configured(username):
                errors[CONF_USERNAME] = "Username already used"
            else:
                for entry in self._async_current_entries():
                    if entry.data.get(CONF_USERNAME) == username:
                        return self.async_abort(reason="already_configured")

                session = async_get_clientsession(self.hass)
                api = LianderApi(username, password, session)
                try:
                    await api.get_access_token()
                except Exception:
                    errors["base"] = "Invalid username or password"
                else:
                    return self.async_create_entry(
                        title=f"Liander ({username})",
                        data=user_input,
                    )

        schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

    def is_already_configured(self, username: str) -> bool:
        for entry in self._async_current_entries():
            if entry.data.get(CONF_USERNAME) == username:
                return True
        return False