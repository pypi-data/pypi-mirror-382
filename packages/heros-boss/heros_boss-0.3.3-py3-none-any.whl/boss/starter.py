import argparse
import sys
import os
import asyncio
import platform
import uuid
import signal
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor

from .helper import log
from .factory import HEROFactory
from .boss import BOSS
from .configuration import WorkerConfigurationDocument


def create_unique_instance_name() -> str:
    """
    Creates a unique instance identifier consisting of the hostname and an UUID.

    Returns:
        A unique identifier.
    """
    short_uuid = str(uuid.uuid4()).split("-")[0]
    hostname = platform.node()
    return f"{hostname}_{short_uuid}"


def run(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="info", help="loglevel: spam < debug < info")
    parser.add_argument("--expose", action="store_true", help="whether the BOSS object should expose itself as HERO")
    parser.add_argument("--realm", default="heros", help="Realm under which the HEROs should be exposed")
    parser.add_argument("--max-workers", default=int(cpu_count()), help="Max number of worker for the ProcessPool")
    parser.add_argument("--no-autostart", action="store_true", help="turn off autostart")
    parser.add_argument(
        "--name",
        default=create_unique_instance_name(),
        help="name of the BOSS instance. This needs to be unique of the BOSS object is exposed",
    )
    parser.add_argument(
        "-u", "--url", action="append", default=[], help="Path to configuration file or url of database"
    )
    parser.add_argument(
        "-e",
        "--env",
        action="append",
        default=["BOSS"],
        help="name of the environment variable storing the configuration",
    )

    args = parser.parse_args(args)
    log.setLevel(args.log)

    if not (args.url or args.env):
        parser.error("Either --url or --env have to be specified")

    # generate asyncio loop and process pool executor
    # both can be passed to the child HEROs
    loop = asyncio.new_event_loop()
    pool = ProcessPoolExecutor(max_workers=int(args.max_workers))

    # create BOSS object
    if args.expose:
        boss = HEROFactory.build(
                "boss.BOSS", {"name": args.name, "configs": [], "loop": loop, "pool": pool, "realm": args.realm}, args.name, realm=args.realm
        )
    else:
        boss = BOSS(name=args.name, configs=[], loop=loop, pool=pool, realm=args.realm)

    if len(args.url) > 0:
        log.info("Reading device(s) from %s ", args.url)
        for url in args.url:
            boss.add_hero_source(WorkerConfigurationDocument.parse_url, url)

    if len(args.env) > 0:
        for var in args.env:
            if var in os.environ:
                boss.add_hero_source(WorkerConfigurationDocument.parse_string, os.environ[var])

    boss.refresh_hero_sources(auto_start=not args.no_autostart)

    # to set the loggers of the started objects we have to set them globally
    log.setLevel(args.log, globally=True)

    log.info("Starting BOSS")

    def exit_gracefully(*args):
        log.info("Stopping BOSS...")
        loop.stop()
        boss.stop_all()
        if hasattr(boss, "_destroy_hero"):
            boss._destroy_hero()
            boss._session_manager.force_close()

        log.info("Exited BOSS")
        sys.exit()

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)
    # only register SIGHUP if it exists on this platform
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, exit_gracefully)

    # start asyncio mainloop
    loop.run_forever()


if __name__ == "__main__":
    run()
