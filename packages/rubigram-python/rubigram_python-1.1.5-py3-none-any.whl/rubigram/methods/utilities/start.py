
from ... import exceptions
from ...crypto import Crypto
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import rubigram


class Start:
    async def start(self: "rubigram.Client", phone_number: str = None):
        """
        Start the RubPy client, handling user registration if necessary.

        Args:
        - phone_number (str): The phone number to use for starting the client.

        Returns:
        - The initialized client.
        """
        if not hasattr(self, 'connection'):
            await self.connect()

        try:
            self.decode_auth = Crypto.decode_auth(
                self.auth) if self.auth is not None else None
            self.import_key = pkcs1_15.new(RSA.import_key(
                self.private_key.encode())) if self.private_key is not None else None
            result = await self.get_me()
            self.guid = result.user.user_guid
            self.logger.info('user', extra={'guid': result})

        except exceptions.NotRegistered:
            self.logger.debug('user not registered!')
            if phone_number is None:
                await self.type_writer(f"{self.BOLD}{self.WHITE}Enter {self.CYAN}Phone Number{self.WHITE}: {self.ORANGE}")
                phone_number = input()
                print(f"{self.RESET}", end="")

            if phone_number.startswith('0'):
                phone_number = '98{}'.format(phone_number[1:])
            elif phone_number.startswith('+98'):
                phone_number = phone_number[1:]
            elif phone_number.startswith('0098'):
                phone_number = phone_number[2:]

            result = await self.send_code(phone_number=phone_number)

            if result.status == 'SendPassKey':
                while True:
                    await self.type_writer(f"{self.BOLD}{self.WHITE}Enter {self.CYAN}Password {self.WHITE}[{self.MAGENTA}{result.hint_pass_key}{self.WHITE}] > {self.ORANGE}")
                    pass_key = input()
                    print(f"{self.RESET}", end="")
                    result = await self.send_code(phone_number=phone_number, pass_key=pass_key)

                    if result.status == 'OK':
                        break

            public_key, self.private_key = Crypto.create_keys()
            while True:
                await self.type_writer(f"{self.BOLD}{self.WHITE}Enter {self.CYAN}Code {self.WHITE}> {self.ORANGE}")
                phone_code = input()
                print(f"{self.RESET}", end="")

                result = await self.sign_in(
                    phone_code=phone_code,
                    phone_number=phone_number,
                    phone_code_hash=result.phone_code_hash,
                    public_key=public_key)

                if result.status == 'OK':
                    result.auth = Crypto.decrypt_RSA_OAEP(
                        self.private_key, result.auth)
                    self.key = Crypto.passphrase(result.auth)
                    self.auth = result.auth
                    self.decode_auth = Crypto.decode_auth(self.auth)
                    self.import_key = pkcs1_15.new(RSA.import_key(
                        self.private_key.encode())) if self.private_key is not None else None
                    self.session.insert(
                        auth=self.auth,
                        guid=result.user.user_guid,
                        user_agent=self.user_agent,
                        phone_number=result.user.phone,
                        private_key=self.private_key)

                    await self.register_device(device_model=self.name)
                    break

        return self
