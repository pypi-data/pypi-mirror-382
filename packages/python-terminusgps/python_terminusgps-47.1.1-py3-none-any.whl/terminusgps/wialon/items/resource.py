import collections.abc
import datetime

from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject, requires_id


class WialonResource(WialonObject):
    """A Wialon `resource/account <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/accounts-and-resources>`_."""

    def create(
        self,
        creator_id: int | str,
        name: str,
        skip_creator_check: bool = False,
    ) -> dict[str, str]:
        """
        Creates the resource in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the resource's creator.
        :type creator_id: int | str
        :param name: Wialon resource name.
        :type name: str
        :param skip_creator_check: Whether to ignore creator check during the API call. Default is :py:obj:`False`.
        :type skip_creator_check: bool
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: dict[str, str]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(
                f"'creator_id' must be a digit, got '{creator_id}'."
            )
        response = self.session.wialon_api.core_create_resource(
            **{
                "creatorId": int(creator_id),
                "name": name,
                "dataFlags": flags.DataFlag.RESOURCE_BASE,
                "skipCreatorCheck": int(skip_creator_check),
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response

    @requires_id
    def get_notification_data(
        self, notification_ids: collections.abc.Collection[int] | None = None
    ) -> dict[str, str]:
        """
        Returns the resource's notification data by id(s).

        Returns *all* notification data if ``notification_ids`` is :py:obj:`None`.

        :param notification_ids: An optional collection of notification ids. Default is :py:obj:`None`.
        :type notification_ids: ~collections.abc.Collection[int] | None
        :raises AssertionError: If the Wialon resource id wasn't set.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary of notification data.
        :rtype: dict[str, str]

        """
        return self.session.wialon_api.resource_get_notification_data(
            **{"itemId": self.id, "col": notification_ids}
            if notification_ids is not None
            else {"itemId": self.id}
        )

    @requires_id
    def get_driver_bindings(
        self,
        start: datetime.datetime,
        stop: datetime.datetime,
        unit_id: int | str = 0,
        driver_id: int | str = 0,
    ) -> dict[str, str]:
        """
        Returns the resource's bound drivers from ``start`` to ``stop``.

        :param start: Interval start date/time.
        :type start: ~datetime.datetime
        :param stop: Interval end date/time.
        :type stop: ~datetime.datetime
        :param unit_id: A Wialon unit id to retrieve drivers for. If not provided, assume *all* units in the resource.
        :type unit_id: int | str
        :param driver_id: A Wialon driver id to retrieve data for. If not provided, assume *all* drivers.
        :type driver_id: int
        :raises AssertionError: If the Wialon resource id wasn't set.
        :raises ValueError: If ``unit_id`` wasn't a digit.
        :raises ValueError: If ``driver_id`` wasn't a digit.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary of Wialon drivers.
        :rtype: dict[str, str]

        """
        if isinstance(unit_id, str) and not unit_id.isdigit():
            raise ValueError(
                f"'unit_id' can only contain digits, got '{unit_id}'."
            )
        if isinstance(driver_id, str) and not driver_id.isdigit():
            raise ValueError(
                f"'driver_id' can only contain digits, got '{driver_id}'."
            )
        return self.session.wialon_api.resource_get_driver_bindings(
            **{
                "resourceId": self.id,
                "unitId": int(unit_id),
                "driverId": int(driver_id),
                "timeFrom": start.timestamp(),
                "timeTo": stop.timestamp(),
            }
        )

    @requires_id
    def get_creator_id(self) -> str | None:
        return (
            self.session.wialon_api.core_search_item(
                **{
                    "id": self.id,
                    "flags": flags.DataFlag.RESOURCE_BILLING_PROPERTIES,
                }
            )
            .get("item", {})
            .get("crt")
        )
