import asyncio


from SPARQLWrapper import SPARQLWrapper, POST, DIGEST, BASIC, JSON


class FusekiHandler:
    """Minimal Fuseki client using SPARQLWrapper with Basic/Digest auth."""

    def __init__(
        self,
        endpoint: str,
        dataset: str,
        user: str | None = None,
        password: str | None = None,
        port: int = 3030,
    ):
        if not endpoint.startswith("http"):
            endpoint = "http://" + endpoint

        self.endpoint = endpoint.rstrip("/")
        self.port = port
        self.dataset = dataset.strip("/")
        self.user = user
        self.password = password

        self.query_url = f"{self.endpoint}:{self.port}/{self.dataset}/query"
        self.update_url = f"{self.endpoint}:{self.port}/{self.dataset}/update"

        # Start background heartbeat
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def _make_wrapper(self, url: str, is_update: bool = False) -> SPARQLWrapper:
        wrapper = SPARQLWrapper(url)
        wrapper.setMethod(POST)
        # Prefer BASIC if credentials provided; fallback to DIGEST for compatibility
        if self.user and self.password:
            try:
                wrapper.setHTTPAuth(BASIC)
                wrapper.setCredentials(self.user, self.password)
            except Exception:
                wrapper.setHTTPAuth(DIGEST)
                wrapper.setCredentials(self.user, self.password)
        return wrapper

    async def _heartbeat_loop(self):
        while True:
            try:
                wrapper = self._make_wrapper(self.query_url)
                wrapper.setQuery("ASK {}")
                wrapper.setReturnFormat(JSON)
                wrapper.query()
                print("✔ Fuseki heartbeat OK")
            except Exception as e:
                print(f"❌ Fuseki heartbeat FAILED: {e}")
            await asyncio.sleep(20)

    def send_query(self, query: str):
        try:
            wrapper = self._make_wrapper(self.query_url)
            wrapper.setQuery(query)
            wrapper.setReturnFormat(JSON)
            return wrapper.query()
        except Exception as e:
            print(f"Query failed: {e}")

    def send_update(self, update: str):
        try:
            wrapper = self._make_wrapper(self.update_url, is_update=True)
            wrapper.setQuery(update)
            return wrapper.query()
        except Exception as e:
            print(f"Update failed: {e}")
