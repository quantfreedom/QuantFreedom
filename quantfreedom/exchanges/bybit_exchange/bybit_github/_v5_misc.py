from ._http_manager import _V5HTTPManager
from .misc import Misc


class MiscHTTP(_V5HTTPManager):
    def get_announcement(self, **kwargs) -> dict:
        """
        Required args:
            locale (string): Language symbol

        Returns:
            Request results as dictionary.

        Additional information:
            https://bybit-exchange.github.io/docs/v5/announcement
        """
        return self._submit_request(
            method="GET",
            path=f"{self.endpoint}{Misc.GET_ANNOUNCEMENT}",
            query=kwargs,
        )
