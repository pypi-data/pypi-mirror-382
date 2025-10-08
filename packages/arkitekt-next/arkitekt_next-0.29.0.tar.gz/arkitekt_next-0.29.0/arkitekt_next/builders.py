from typing import List, Optional
import logging
import os

from arkitekt_next.app.fakts import (
    build_device_code_fakts,
    build_redeem_fakts,
    build_token_fakts,
)
from .utils import create_arkitekt_next_folder
from fakts_next.models import Manifest
from fakts_next.grants.remote.demanders.device_code import DeviceCodeHook
from .app import App
from .service_registry import ServiceBuilderRegistry, get_default_service_registry
from .init_registry import InitHookRegistry, get_default_init_hook_registry
from arkitekt_next.constants import DEFAULT_ARKITEKT_URL


def easy(
    identifier: str | None = None,
    version: str = "0.0.1",
    logo: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    url: str = DEFAULT_ARKITEKT_URL,
    headless: bool = False,
    log_level: str = "ERROR",
    token: Optional[str] = None,
    no_cache: bool = False,
    redeem_token: Optional[str] = None,
    service_registry: Optional[ServiceBuilderRegistry] = None,
    init_hook_registry: Optional[InitHookRegistry] = None,
    instance_id: str = "main",
    device_code_hook: DeviceCodeHook | None = None,
) -> App:
    """Creates a next app

    A simple way to create an ArkitektNext Next app, ArkitektNext next apps are
    development apps by default, as they will try to register themselves
    with services that are not yet available in production (such as the
    rekuest_next and mikro_next services). They represent the next generation
    of ArkitektNext apps, and will be the default way to create ArkitektNext apps
    in the future. From here be dragons.

    A few things to note:
        -   The Next builder closely mimics the easy builder, but will use the
            next generation of services (such as rekuest_next and mikro_next)
            and will therefore not be compatible with the current generation.

        -  Next apps will try to establish themselves a "development" apps, by default
            which means that they will be authenticated with the ArkitektNext server on
            a per user basis. If you want to create a "desktop" app, which multiple users
            can use, you should set the `app_kind` to "desktop" TODO: Currently not implemented (use next app for this)
        -  The Next builder can also be used in plugin apps, and when provided with a fakts_next token
           will be able to connect to the ArkitektNext server without any user interaction.


    Parameters
    ----------
    identifier : str
        The apps identifier (should be globally unique, see Manifest for more info)
    version : str, optional
        The version of the app, by default "0.0.1"
    logo : str, optional
        The logo of the app as a public http url, by default None
    scopes : List[str], optional
        The scopes, that this apps requires, will default to standard scopes, by default None
    url : str, optional
        The fakts_next server that will be used to configure this app, in a default ArkitektNext deployment this
        is the address of the "Lok Service" (which provides the Fakts API), by default DEFAULT_ARKITEKT_URL
        Will be overwritten by the FAKTS_URL environment variable
    headless : bool, optional
        Should we run in headless, mode, e.g printing necessary interaction into the console (will forexample
        stop opening browser windows), by default False
    log_level : str, optional
        The log-level to use, by default "ERROR"
    token : str, optional
        A fakts_next token to use, by default None
        Will be overwritten by the FAKTS_TOKEN environment variable
    no_cache : bool, optional
        Should we skip caching token, acess-token, by default False
        Attention: If this is set to True, the app will always have to be configured
        and authenticated.
    instance_id : str, optional
        The instance_id to use, by default "main"
        Can be set to a different value, if you want to run multiple intstances
        of the same app by the same user.
        Will be overwritten by the REKUEST_INSTANCE_ID environment variable
    register_reaktion : bool, optional
        Should we register the reaktion extension, by default True
        If set to False, the app will not be able to use the reaktion extension
        (which is necessary for scheduling in app` workflows from fluss)
    app_kind : str, optional
        The kind of app to create, by default "development"
        Can be set to "desktop" to create a desktop app, that can be used by multiple users.

    Returns
    -------
    NextApp
        A built app, that can be used to interact with the ArkitektNext server
    """
    service_registry = service_registry or get_default_service_registry()
    init_hook_registry = init_hook_registry or get_default_init_hook_registry()

    if identifier is None:
        identifier = __file__.split("/")[-1].replace(".py", "")

    url = os.getenv("FAKTS_URL", url)
    token = os.getenv("FAKTS_TOKEN", token)

    manifest = Manifest(
        version=version,
        identifier=identifier,
        scopes=scopes if scopes else ["openid"],
        logo=logo,
        requirements=service_registry.get_requirements(),
    )

    if token:
        fakts_next = build_token_fakts(
            manifest=manifest,
            token=token,
            url=url,
        )

    elif redeem_token:
        fakts_next = build_redeem_fakts(
            manifest=manifest,
            redeem_token=redeem_token,
            url=url,
        )
    else:
        fakts_next = build_device_code_fakts(
            manifest=manifest,
            url=url,
            no_cache=no_cache,
            headless=headless,
            device_code_hook=device_code_hook,
        )

    params = {
        "instance_id": instance_id,
    }

    create_arkitekt_next_folder(with_cache=True)

    try:
        from rich.logging import RichHandler

        logging.basicConfig(level=log_level, handlers=[RichHandler()])
    except ImportError:
        logging.basicConfig(level=log_level)

    app = App(
        fakts=fakts_next,
        services=service_registry.build_service_map(fakts=fakts_next, params=params),
    )

    init_hook_registry.run_all(app)

    return app


def interactive(
    identifier: str,
    version: str = "0.0.1",
    logo: Optional[str] = None,
    scopes: Optional[List[str]] = None,
    url: str = DEFAULT_ARKITEKT_URL,
    headless: bool = False,
    log_level: str = "ERROR",
    token: Optional[str] = None,
    no_cache: bool = False,
    redeem_token: Optional[str] = None,
    registry: Optional[ServiceBuilderRegistry] = None,
    sync_mode: bool = True,
) -> App:
    """Creates an interactive jupyter app"""

    app = easy(
        identifier=identifier,
        version=version,
        logo=logo,
        scopes=scopes,
        url=url,
        headless=headless,
        log_level=log_level,
        token=token,
        no_cache=no_cache,
        redeem_token=redeem_token,
        service_registry=registry,
    )

    if sync_mode:
        # When running in an interactive async enironvment, just like
        # in a jupyter notebook, we can opt to run the app in sync mode
        # to avoid having to use await for every call. This is the default
        # behaviour for the app, but can be overwritten by setting
        # app.koil.sync_in_async = False
        if app.__koil:
            app.__koil.sync_in_async = True
        app.enter()

    return app
