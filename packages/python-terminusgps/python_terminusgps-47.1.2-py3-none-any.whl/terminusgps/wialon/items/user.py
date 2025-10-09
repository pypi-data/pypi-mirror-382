from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonObject, requires_id


class WialonUser(WialonObject):
    """A Wialon `user <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/users>`_."""

    def create(
        self, creator_id: int | str, name: str, password: str
    ) -> dict[str, str]:
        """
        Creates the user in Wialon and sets its id.

        :param creator_id: A Wialon user id to set as the new user's creator.
        :type creator_id: int | str
        :param name: Wialon user name.
        :type name: str
        :param password: Wialon user password.
        :type password: str
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A Wialon object dictionary.
        :rtype: dict[str, str]

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(
                f"'creator_id' must be a digit, got '{creator_id}'."
            )
        response = self.session.wialon_api.core_create_user(
            **{
                "creatorId": int(creator_id),
                "name": name,
                "password": password,
                "dataFlags": flags.DataFlag.USER_BASE,
            }
        )
        self.id = int(response.get("item", {}).get("id"))
        return response

    @requires_id
    def get_access(
        self, object_type: str, direct: bool = True, flags: int = 0x1
    ) -> dict[str, str]:
        """
        Returns a dictionary of Wialon objects the user has access to.

        :param object_type: A Wialon object type.
        :type object_type: str
        :param direct: Whether or not to exclude objects the user doesn't have direct access to. Default is :py:obj:`True`.
        :type direct: bool
        :param flags: Response flags. Default is ``0x1``.
        :type flags: int
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary of Wialon objects.
        :rtype: dict[str, str]

        """
        return self.session.wialon_api.user_get_items_access(
            **{
                "userId": self.id,
                "directAccess": int(direct),
                "itemSuperclass": object_type,
                "flags": flags,
            }
        )

    @requires_id
    def set_access(
        self, obj: WialonObject, access_mask: int
    ) -> dict[str, str]:
        """
        Sets the user's access to ``obj`` according to ``access_mask`` in Wialon.

        :param obj: A Wialon object.
        :type obj: ~terminusgps.wialon.items.base.WialonObject
        :param access_mask: A Wialon access mask integer.
        :type access_mask: int
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises ValueError: If the other Wialon object's id wasn't set.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: dict[str, str]

        """
        if obj.id is None:
            raise ValueError("Other Wialon object's id wasn't set.")
        return self.session.wialon_api.user_update_item_access(
            **{"userId": self.id, "itemId": obj.id, "accessMask": access_mask}
        )

    @requires_id
    def set_flags(self, flags: int, flags_mask: int) -> dict[str, str]:
        """
        Sets the user settings flags in Wialon.

        :param flags: A Wialon user settings flag integer.
        :type flags: int
        :param flags_mask: An integer mask which determines which bits will be changed.
        :type flags_mask: int
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: A dictionary containing the user's new settings flags.
        :rtype: dict[str, str]

        """
        return self.session.wialon_api.user_update_user_flags(
            **{"userId": self.id, "flags": flags, "flagsMask": flags_mask}
        )

    @requires_id
    def set_password(
        self, old_password: str, new_password: str
    ) -> dict[str, str]:
        """
        Sets the user's password to ``new_password`` in Wialon.

        :param old_password: The user's old Wialon password.
        :type old_password: str
        :param new_password: The user's new Wialon password.
        :type new_password: str
        :raises AssertionError: If the Wialon user id wasn't set.
        :raises ~terminusgps.wialon.session.WialonAPIError: If something went wrong calling the Wialon API.
        :returns: An empty dictionary.
        :rtype: dict[str, str]

        """
        return self.session.wialon_api.user_update_password(
            **{
                "userId": self.id,
                "oldPassword": old_password,
                "newPassword": new_password,
            }
        )
