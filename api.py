import aiohttp

BASE_URL = "https://mijn-liander-gateway.web.liander.nl/api/v1"

class LianderApi:
    def __init__(self, username: str, password: str, session):
        self._username = username
        self._password = password
        self._session = session
        self._token = None

    async def _request(self, method, url, headers=None, json=None):
        async with self._session.request(method, url, headers=headers, json=json) as response:
            response.raise_for_status()

            return await response.json()

    async def get_access_token(self):
        if self._token:
            return self._token

        result = await self._request(
            "POST",
            f"{BASE_URL}/auth/login",
            headers={"Content-Type": "application/json"},
            json={
                "username": self._username,
                "password": self._password,
            },
        )
        self._token = result["jwt"]

        return self._token

    async def get_connections(self):
        return await self._request(
            "GET",
            f"{BASE_URL}/aansluitingen",
            headers={"Authorization": f"Bearer {await self.get_access_token()}"},
        )

    async def get_connection_energy_supplier(self, ean: str):
        return await self._request(
            "GET",
            f"{BASE_URL}/aansluitingen/{ean}/energieleverancier",
            headers={"Authorization": f"Bearer {await self.get_access_token()}"},
        )

    async def get_meter_issues(self, ean: str):
        return await self._request(
            "GET",
            f"{BASE_URL}/aansluitingen/{ean}/meterstoring",
            headers={"Authorization": f"Bearer {await self.get_access_token()}"},
        )

    async def get_meter_reading_request_id(self, ean: str):
        result = await self._request(
            "POST",
            f"{BASE_URL}/aansluitingen/{ean}/meterstand-aanvraag",
            headers={"Authorization": f"Bearer {await self.get_access_token()}"},
        )

        return result.get("meterstandAanvraagId")

    async def get_meter_reading(self, ean: str, request_id: str):
        result = await self._request(
            "GET",
            f"{BASE_URL}/aansluitingen/{ean}/meterstand-aanvraag/{request_id}",
            headers={"Authorization": f"Bearer {await self.get_access_token()}"},
        )

        return result