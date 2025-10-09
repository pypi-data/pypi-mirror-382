
from typing import Optional, Coroutine
from asyncio import run

import rubigram


class Run:
    def run(
            self: "rubigram.Client",
            coroutine: Optional[Coroutine] = None,
            phone_number: str = None,
            logger=False):
        """
        Run the client in either synchronous or asynchronous mode.

        Args:
        - coroutine (Optional[Coroutine]): An optional coroutine to run asynchronously.
        - phone_number (str): The phone number to use for starting the client.

        Returns:
        - If running synchronously, returns the initialized client.
        - If running asynchronously, returns None.
        """
        if self.is_sync:
            if logger:
                self.type_writer(
                    f"{
                        self.BOLD}{
                        self.WHITE}Initializing {
                        self.CYAN}synchronous {
                        self.MAGENTA}connection {
                        self.YELLOW}...{
                            self.RESET}",
                    line=True)
                self.start(phone_number=phone_number)
                self.type_writer(
                    f"{
                        self.BOLD}{
                        self.WHITE}synchronous {
                        self.CYAN}connection {
                        self.GREEN}successfully {
                        self.YELLOW}...{
                            self.RESET}",
                    line=True)
                self.get_updates()
            else:
                self.start(phone_number=phone_number)
                self.get_updates()
            return self

        async def main_runner():
            if logger:
                await self.type_writer(f"{self.BOLD}{self.WHITE}Initializing {self.CYAN}asynchronous {self.MAGENTA}aconnection {self.YELLOW}...{self.RESET} ", line=True)
                await self.start(phone_number=phone_number)
                await self.type_writer(f"{self.BOLD}{self.WHITE}asynchronous {self.CYAN}connection {self.GREEN}successfully {self.YELLOW}... {self.RESET}", line=True)
                await self.get_updates()
            else:
                await self.start(phone_number=phone_number)
                await self.get_updates()

        if coroutine:
            run(coroutine)

        run(main_runner())
