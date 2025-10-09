
import rubigram


class SetBirthday:
    """
    Provides a method to update the birth date of a user.

    Methods:
    - set_birthday: Update the user's birth date.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def set_birthday(
            self: "rubigram.Client",
            date: str,
    ) -> "rubigram.types.Update":
        """
        Update the birth date of the user.

        Args:
        - date (str): The birth date in str format. example(`2024-04-04`)

        Returns:
        - rubigram.types.Update: The result of the update operation.
        """
        return await self.builder('updateProfile',
                                  input={
                                      'birth_date': date,
                                      "updated_parameters": ["birth_date"]
                                  })
