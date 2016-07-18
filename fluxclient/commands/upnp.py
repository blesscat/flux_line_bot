
from getpass import getpass, getuser
from uuid import UUID
import argparse
import sys

from .misc import (get_or_create_default_key, setup_logger,
                   network_config_helper)


def quit_program(upnp, logger):
    """Quit"""
    sys.exit(0)


def change_device_name(upnp, logger):
    """Change device name"""
    name = input("New device name: ").strip()
    if name:
        upnp.rename(name)
        logger.error("Done.")
    else:
        logger.error("No name given.")


def change_device_password(upnp, logger):
    """Change device password"""
    old_pass = getpass("Old password: ")
    new_pass = getpass("New password: ")
    if getpass("Confirm new password: ") != new_pass:
        logger.error("New password not match")
        return
    if len(new_pass) < 3:
        logger.error("Password too short")
        return
    upnp.modify_password(old_pass, new_pass)


def change_network_settings(upnp, logger):
    """Change network settings"""
    settings = network_config_helper.run()
    upnp.modify_network(**settings)


def get_wifi_list(upnp, logger):
    """Get wifi list"""
    logger.info("%17s %5s %23s %s", "bssid", "rssi", "security", "ssid")
    for r in upnp.get_wifi_list():
        logger.info("%17s %5s %23s %s", r["bssid"], r["rssi"], r["security"],
                    r["ssid"])

    logger.info("--\n")


def add_trust(upnp, logger):
    """Add an ID to trusted list"""

    filename = input("Keyfile (keep emptry to use current session key): ")
    if filename:
        with open(filename, "r") as f:
            aid = upnp.add_trust(getuser(), f.read())
    else:
        aid = upnp.add_trust(getuser(),
                             upnp.client_key.public_key_pem.decode())

    logger.info("Key added with Access ID: %s\n", aid)


def list_trust(upnp, logger):
    """List trusted ID"""

    logger.info("=" * 79)
    logger.info("%40s  %s", "access_id", "label")
    logger.info("-" * 79)
    for meta in upnp.list_trust():
        logger.info("%40s  %s", meta["access_id"], meta.get("label"))
    logger.info("=" * 79 + "\n")


def remove_trust(upnp, logger):
    """Remove trusted ID"""
    access_id = input("Access id to remove: ")
    upnp.remove_trust(access_id)
    logger.info("Access ID %s REMOVED.\n", access_id)


def run_commands(upnp, logger):
    from fluxclient.upnp import UpnpError

    tasks = [
        quit_program,
        change_device_name,
        change_device_password,
        change_network_settings,
        get_wifi_list,
        add_trust,
        list_trust,
        remove_trust,
    ]

    while True:
        logger.info("Upnp tool: Choose task id")
        for i, t in enumerate(tasks):
            logger.info("  %i: %s", i, t.__doc__)
        logger.info("")

        try:
            r = input("> ").strip()
            if not r:
                continue

            i = int(r, 10)
            t = tasks[i]
            t(upnp, logger)
        except UpnpError as e:
            logger.error("Error '%s'", e)
        except KeyboardInterrupt as e:
            logger.info("\n")
            return

        logger.info("")


def main():
    parser = argparse.ArgumentParser(description='Flux upnp tool')
    parser.add_argument(dest='target', type=str,
                        help='Device UUID or IP Address')
    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False, help='Print debug message')
    parser.add_argument('--key', dest='client_key', type=str, default=None,
                        help='Client identify key (RSA key with pem format)')

    options = parser.parse_args()

    logger = setup_logger(__name__, debug=options.debug)

    from fluxclient.robot.misc import is_uuid
    from fluxclient.upnp import UpnpTask

    client_key = get_or_create_default_key(options.client_key)

    if is_uuid(options.target):
        upnp = UpnpTask(UUID(hex=options.target), client_key)
    else:
        upnp = UpnpTask(UUID(int=0), client_key, ipaddr=options.target)

    if not upnp.authorized:
        password = getpass("Device Password: ")
        upnp.authorize_with_password(password)

    logger.info("\n"
                "Serial: %s (uuid={%s})\n"
                "Model: %s\n"
                "Version: %s\n"
                "IP Address: %s\n", upnp.serial, upnp.uuid, upnp.model_id,
                upnp.version, upnp.ipaddr)

    run_commands(upnp, logger)


if __name__ == "__main__":
    sys.exit(main())
