from datetime import datetime

from kaomy.core.exceptions import ProviderError
from kaomy.models import ResourceMetadata, ResourceState
from kaomy.providers.base_provider import BaseProvider


class CDEProvider(BaseProvider):
    """
    Provider for CDE water consumption data.
    """

    def __init__(
        self,
        username: str,
        password: str,
        collector: str,
        location: str,
        point_installation_id: str,
        simulation: bool = False,
    ):
        super().__init__(name="cde", simulation=simulation)

        self.username = username
        self.password = password
        self.collector = collector
        self.location = location
        self.point_installation_id = point_installation_id

        self.session = None
        self.csrf_token = None

        self.login_url = "https://cde.toutsurmoneau.nc/Portail/fr-FR/Connexion/Login"
        self.data_url = "https://cde.toutsurmoneau.nc/Portail/fr-FR/Usager/Abonnement/Consommations/234935"
        self.ajax_url = "https://cde.toutsurmoneau.nc/Portail/fr-FR/Usager/Abonnement/GetGraphRelevesData"

    def authenticate(self) -> None:
        if self.simulation:
            return

        self._init_session()

        try:
            login_page = self.session.get(self.login_url, timeout=30)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(login_page.text, "html.parser")
            token_input = soup.find("input", {"name": "__RequestVerificationToken"})

            if token_input is None:
                raise ProviderError("CDE CSRF token not found")

            self.csrf_token = token_input["value"]

            response = self.session.post(
                self.login_url,
                data={
                    "__RequestVerificationToken": self.csrf_token,
                    "Login": self.username,
                    "MotDePasse": self.password,
                },
                timeout=30,
            )

            if "MES CONTRATS" not in response.text:
                raise ProviderError("CDE login failed")

        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(f"CDE authentication error: {exc}") from exc

    def collect(self) -> ResourceState:
        if self.simulation:
            return self._simulation_state()

        self.authenticate()
        raw_data = self._get_consumption_data()
        history = self._build_history(raw_data)

        if not history:
            raise ProviderError("CDE returned no consumption values")

        return self._build_state(history)

    def _init_session(self) -> None:
        if self.session is not None:
            return

        try:
            import requests

            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0",
            })

        except Exception as exc:
            raise ProviderError(f"Unable to initialize CDE HTTP session: {exc}") from exc

    def _get_consumption_data(self) -> dict:
        today = datetime.today()

        date_start = today.replace(day=1).strftime("%d/%m/%Y")
        date_end = today.strftime("%d/%m/%Y")

        try:
            response = self.session.post(
                self.ajax_url,
                data={
                    "__RequestVerificationToken": self.csrf_token,
                    "pointDInstallationId": self.point_installation_id,
                    "dateDebut": date_start,
                    "dateFin": date_end,
                    "granularite": "Jour",
                },
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": self.data_url,
                    "User-Agent": "Mozilla/5.0",
                },
                timeout=30,
            )

            return response.json()

        except Exception as exc:
            raise ProviderError(f"CDE consumption API error: {exc}") from exc

    def _build_history(self, raw_data: dict) -> list:
        dates = raw_data["labels"]
        values = raw_data["datasets"][0]["data"]

        history = []

        for date_text, raw_value in zip(dates, values):
            date_iso = self._parse_cde_date(date_text)
            value = self._parse_cde_value(raw_value)

            if value is None:
                history.append({"date": date_iso})
            else:
                history.append({
                    "date": date_iso,
                    "value": value,
                })

        return history

    def _build_state(self, history: list) -> ResourceState:
        values = [
            item["value"]
            for item in history
            if item.get("value") is not None
        ]

        conso_mois = round(sum(values), 3)

        non_zero = [
            item for item in history
            if item.get("value", 0) > 0
        ]

        if non_zero:
            last = non_zero[-1]
            conso_jour = last["value"]
            releve_date = last["date"]
        else:
            conso_jour = 0
            releve_date = history[-1]["date"]

        metadata = ResourceMetadata(
            provider="cde",
            collector=self.collector,
            resource="water",
            location=self.location,
            unit="m³",
            currency="XPF",
            device_class="water",
            icon="mdi:water",
            last_sync=ResourceState.now_iso(),
            last_reading=releve_date,
        )

        return ResourceState(
            metadata=metadata,
            measurements={
                "conso_jour": conso_jour,
                "conso_mois": conso_mois,
                "total": conso_jour,
            },
            history=history,
        )

    @staticmethod
    def _parse_cde_date(date_text: str) -> str:
        clean_date = str(date_text).strip().split(" ")[0]

        if len(clean_date.split("/")[-1]) == 2:
            return datetime.strptime(clean_date, "%d/%m/%y").date().isoformat()

        return datetime.strptime(clean_date, "%d/%m/%Y").date().isoformat()

    @staticmethod
    def _parse_cde_value(raw_value):
        if raw_value in [None, "", "null", "None"]:
            return None

        try:
            return round(float(str(raw_value).replace(",", ".")), 3)
        except Exception:
            return None

    def _simulation_state(self) -> ResourceState:
        history = [
            {"date": "2026-05-20"},
            {"date": "2026-05-21"},
            {"date": "2026-05-22", "value": 1},
            {"date": "2026-05-23"},
        ]

        return self._build_state(history)
