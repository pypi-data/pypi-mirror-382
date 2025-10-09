
import shadigram


class SetBirthday:
    """
    Provides a method to update the birth date of a user.

    Methods:
    - set_birthday: Update the user's birth date.

    Attributes:
    - self (shadigram.Client): The shadigram client instance.
    """

    async def set_birthday(
            self: "shadigram.Client",
            date: str,
    ) -> "shadigram.types.Update":
        """
        Update the birth date of the user.

        Args:
        - date (str): The birth date in str format. example(`2024-04-04`)

        Returns:
        - shadigram.types.Update: The result of the update operation.
        """
        return await self.builder('updateProfile',
                                  input={
                                      'birth_date': date,
                                      "updated_parameters": ["birth_date"]
                                  })
