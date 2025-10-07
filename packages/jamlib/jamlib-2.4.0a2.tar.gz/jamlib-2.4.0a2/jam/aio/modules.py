# -*- coding: utf-8 -*-

import datetime
from collections.abc import Callable
from typing import Any, Literal, Optional, Union
from uuid import uuid4

from jam.aio.jwt.tools import __gen_jwt_async__, __validate_jwt_async__
from jam.exceptions import TokenInBlackList, TokenNotInWhiteList
from jam.modules import BaseModule
from jam.utils.config_maker import __module_loader__


class JWTModule(BaseModule):
    """Module for JWT auth."""

    def __init__(
        self,
        alg: Literal[
            "HS256",
            "HS384",
            "HS512",
            "RS256",
            "RS384",
            "RS512",
            # "PS256",
            # "PS384",
            # "PS512",
        ] = "HS256",
        secret_key: Optional[str] = None,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        expire: int = 3600,
        list: Optional[dict[str, Any]] = None,
    ) -> None:
        """Class constructor.

        Args:
            alg (Literal["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "PS512", "PS384", "PS512"]): Algorithm for token encryption
            secret_key (str | None): Secret key for HMAC enecryption
            private_key (str | None): Private key for RSA enecryption
            public_key (str | None): Public key for RSA
            expire (int): Token lifetime in seconds
            list (dict[str, Any]): List config
        """
        super().__init__(module_type="jwt")
        self._secret_key = secret_key
        self.alg = alg
        self._private_key = private_key
        self.public_key = public_key
        self.exp = expire

        self.list = None
        if list is not None:
            self.list = self._init_list(list)

    @staticmethod
    def _init_list(config: dict[str, Any]):
        backend = config["backend"]
        if backend == "redis":
            from jam.aio.jwt.lists.redis import RedisList

            return RedisList(
                type=config["type"],
                redis_uri=config["redis_uri"],
                in_list_life_time=config["in_list_life_time"],
            )
        elif backend == "json":
            from jam.aio.jwt.lists.json import JSONList

            return JSONList(type=config["type"], json_path=config["json_path"])
        elif backend == "custom":
            module = __module_loader__(config["custom_module"])
            cfg = dict(config)
            cfg.pop("type")
            cfg.pop("custom_module")
            cfg.pop("backend")
            return module(**cfg)
        else:
            raise ValueError(
                f"Unknown list_type: {config.get('list_type', backend)}"
            )

    async def make_payload(
        self, exp: Optional[int] = None, **data: Any
    ) -> dict[str, Any]:
        """Payload maker tool.

        Args:
            exp (int | None): If none exp = JWTModule.exp
            **data: Custom data
        """
        if not exp:
            _exp = self.exp
        else:
            _exp = exp
        payload = {
            "jti": str(uuid4()),
            "exp": _exp + datetime.datetime.now().timestamp(),
            "iat": datetime.datetime.now().timestamp(),
        }
        payload.update(**data)
        return payload

    async def gen_token(self, **payload) -> str:
        """Creating a new token.

        Args:
            **payload: Payload with information

        Raises:
            EmptySecretKey: If the HMAC algorithm is selected, but the secret key is None
            EmtpyPrivateKey: If RSA algorithm is selected, but private key None
        """
        header = {"alg": self.alg, "typ": "jwt"}
        token = await __gen_jwt_async__(
            header=header,
            payload=payload,
            secret=self._secret_key,
            private_key=self._private_key,
        )

        if self.list:
            if self.list.__list_type__ == "white":
                await self.list.add(token)
        return token

    async def validate_payload(
        self, token: str, check_exp: bool = False, check_list: bool = True
    ) -> dict[str, Any]:
        """A method for verifying a token.

        Args:
            token (str): The token to check
            check_exp (bool): Check for expiration?
            check_list (bool): Check if there is a black/white list

        Raises:
            ValueError: If the token is invalid.
            EmptySecretKey: If the HMAC algorithm is selected, but the secret key is None.
            EmtpyPublicKey: If RSA algorithm is selected, but public key None.
            NotFoundSomeInPayload: If 'exp' not found in payload.
            TokenLifeTimeExpired: If token has expired.
            TokenNotInWhiteList: If the list type is white, but the token is  not there
            TokenInBlackList: If the list type is black and the token is there

        Returns:
            (dict[str, Any]): Payload from token
        """
        if check_list:
            if self.list.__list_type__ == "white":  # type: ignore
                if not await self.list.check(token):  # type: ignore
                    raise TokenNotInWhiteList
            if self.list.__list_type__ == "black":  # type: ignore
                if await self.list.check(token):  # type: ignore
                    raise TokenInBlackList

        payload = await __validate_jwt_async__(
            token=token,
            check_exp=check_exp,
            secret=self._secret_key,
            public_key=self.public_key,
        )

        return payload


class SessionModule(BaseModule):
    """Module for session management."""

    def __init__(
        self,
        sessions_type: Literal["redis", "json", "custom"],
        id_factory: Callable[[], str] = lambda: str(uuid4()),
        is_session_crypt: bool = False,
        session_aes_secret: Optional[bytes] = None,
        **module_kwargs: Any,
    ) -> None:
        """Class constructor.

        Args:
            sessions_type (Literal["redis", "json"]): Type of session storage.
            id_factory (Callable[[], str], optional): A callable that generates unique IDs. Defaults to a UUID factory.
            is_session_crypt (bool, optional): If True, session keys will be encoded. Defaults to False.
            session_aes_secret (Optional[bytes], optional): AES secret for encoding session keys.
            **module_kwargs (Any): Additional keyword arguments for the session module. See <DOCS>
        """
        super().__init__(module_type="session")
        from jam.sessions.__abc_session_repo__ import BaseSessionModule

        self.module: BaseSessionModule

        if sessions_type == "redis":
            from jam.aio.sessions.redis import RedisSessions

            self.module = RedisSessions(
                redis_uri=module_kwargs.get(
                    "redis_uri", "redis://localhost:6379/0"
                ),
                redis_sessions_key=module_kwargs.get(
                    "sessions_path", "sessions"
                ),
                default_ttl=module_kwargs.get("session_ttl"),
                is_session_crypt=is_session_crypt,
                session_aes_secret=session_aes_secret,
                id_factory=id_factory,
            )
        elif sessions_type == "json":
            from jam.aio.sessions.json import JSONSessions

            self.module = JSONSessions(
                json_path=module_kwargs.get("json_path", "sessions.json"),
                is_session_crypt=is_session_crypt,
                session_aes_secret=session_aes_secret,
                id_factory=id_factory,
            )
        elif sessions_type == "custom":
            _module: Optional[Union[Callable, str]] = module_kwargs.get(
                "custom_module"
            )
            if not _module:
                raise ValueError("Custom module not provided")
            module_kwargs.__delitem__("custom_module")
            if isinstance(_module, str):
                _m = __module_loader__(_module)
                self.module = _m(
                    is_session_crypt=is_session_crypt,
                    session_aes_secret=session_aes_secret,
                    id_factory=id_factory,
                    **module_kwargs,
                )
                del _m
            elif callable(_module):
                self.module = _module(
                    is_session_crypt=is_session_crypt,
                    session_aes_secret=session_aes_secret,
                    id_factory=id_factory,
                    **module_kwargs,
                )
            del _module
            if not self.module:
                raise ValueError("Custom module not provided")
            if not isinstance(self.module, BaseSessionModule):
                raise TypeError(
                    "Custom module must be an instance of BaseSessionModule. See <DOCS>"
                )
        else:
            raise ValueError(
                f"Unsupported session type: {sessions_type} \n"
                f"See docs: https://jam.makridenko.ru/sessions/"
            )

    async def create(self, session_key: str, data: dict) -> str:
        """Create a new session with the given session key and data.

        Args:
            session_key (str): The key for the session.
            data (dict): The data to be stored in the session.

        Returns:
            str: The ID of the created session.
        """
        return await self.module.create(session_key, data)

    async def get(self, session_id: str) -> Optional[dict]:
        """Retrieve a session by its key or ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            dict | None: The data stored in the session.

        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        return await self.module.get(session_id)

    async def rework(self, session_id: str) -> str:
        """Reworks a session and returns its new ID.

        Args:
            session_id (str): The ID of the session to rework.

        Returns:
            str: The new ID of the reworked session.

        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        return await self.module.rework(session_id)

    async def delete(self, session_id: str) -> None:
        """Delete a session by its key or ID.

        Args:
            session_id (str): The ID of the session to delete.

        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        await self.module.delete(session_id)

    async def update(self, session_id: str, data: dict) -> None:
        """Update an existing session with new data.

        Args:
            session_id (str): The ID of the session to update.
            data (dict): The new data to be stored in the session.

        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        await self.module.update(session_id, data)

    async def clear(self, session_key: str) -> None:
        """Clear all sessions by key.

        Args:
            session_key (str): The session key to clear.

        Raises:
            SessionNotFoundError: If the session does not exist.
        """
        await self.module.clear(session_key)
