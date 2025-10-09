from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject


class WialonRetranslator(WialonObject):
    """A Wialon `retranslator <https://wialon.com/en/gps-hardware/soft>`_."""

    def create(
        self, creator_id: int | str, name: str, config: str
    ) -> dict[str, str]:
        """
        Creates the retranslator in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the retranslator's creator.
        :type creator_id: int | str
        :param name: Wialon retranslator name.
        :type name: str
        :param config: Wialon retranslator configuration.
        :type config: str
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: dict[str, str]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(
                f"'creator_id' must be a digit, got '{creator_id}'."
            )
        response = self.session.wialon_api.core_create_retranslator(
            **{
                "creatorId": int(creator_id),
                "name": name,
                "config": config,
                "dataFlags": flags.DataFlag.UNIT_BASE,
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response
