
import asyncio

import rubigram


class Typewriter:

    async def type_writer(
            self,
            text: str,
            delay: float = 0.01,
            line: bool = False):
        """
        Simulate typing a line of text with a delay.

        Args:
            client (rubigram.Client): The client instance, if needed for communication.
            text (str): The text to be typed.
            delay (float): The delay between each character in seconds.
            line (bool): Whether or not to add a newline after typing the text.
        """
        for char in text:
            print(char, end='', flush=True)
            await asyncio.sleep(delay)
        if line:
            print()
