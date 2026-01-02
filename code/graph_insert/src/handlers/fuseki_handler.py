from pyfuseki import FusekiQuery, FusekiUpdate
from time import sleep
import asyncio


class FusekiHandler(object):
    """
    Class defined to provide necessary logic to easily interact with the Apache Jena Fuseki SPARQL Server.
    """

    def __init__(self, endpoint: str, database_name: str) -> None:
        self._endpoint = endpoint
        self._dbname = database_name

        asyncio.run(self.heartbeat())  # db connection check!

    def send_query(self, raw_query: str) -> None:
        """Send a SPARQL Query to the database."""
        try:
            fuseki_query = FusekiQuery(self._endpoint, self._dbname)
            print(f"Sending query to database: {raw_query}")
            fuseki_query.run_sparql(raw_query)
            print("Query sent succesfully.")
        except Exception as e:
            print(f"Failed sending query to database: {e}.")

    def send_update(self, raw_update: str) -> None:
        """Send a SPARQL Update to the database"""
        try:
            fuseki_update = FusekiUpdate(self._endpoint, self._dbname)
            print(f"Sending update to database: {raw_update}")
            fuseki_update.run_sparql(raw_update)
            print("Update sent successfully")
        except Exception as e:
            print(f"Failed sending update to database: {e}")

    async def heartbeat(self) -> None:
        """Checks that the connection is still alive"""
        try:
            fuseki_query = FusekiQuery(self._endpoint)
            fuseki_query.run_sparql("ASK { }")
        except Exception as e:
            print(f"Connection heartbeat failed: {e}. Retrying...")
        finally:
            sleep(20)
            self.heartbeat()

    # TODO: add admin helpers
