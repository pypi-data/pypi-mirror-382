#! /usr/bin/env python

import hashlib
import logging
import subprocess
from collections.abc import Generator
from pathlib import Path

import click
from hyprpy import Hyprland
from hyprpy.components.instancesignals import InstanceSignalCollection

CONFIG_DIR = Path.home() / ".config" / "hyprmonmon"

logger = logging.getLogger("hyprmonmon")
logging.basicConfig(level=logging.INFO)


def get_monitor_fingerprint(instance: Hyprland) -> str:
    fingerprint = "\0".join(
        sorted(
            f"{monitor.name}\0{monitor.description}"
            for monitor in instance.get_monitors()
        )
    )
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]


def load_config_file(path: Path, prefix: str) -> Generator[str]:
    try:
        with path.open() as f:
            for line_raw in f:
                line = line_raw.split("#")[0].strip()
                if not line:
                    continue

                if not line.startswith(prefix):
                    logger.warning("Ignoring line %s.", line)
                    continue

                yield line.removeprefix(prefix)
    except OSError:
        logger.info("Could not load %s.", path)


def apply_config(instance: Hyprland, fingerprint: str) -> None:
    ok = True

    for arg in load_config_file(
        CONFIG_DIR / f"{fingerprint}.monitors.conf", "monitor="
    ):
        r = instance.command_socket.send_command("keyword", args=["monitor", arg])
        if r != "ok":
            logger.error(
                "Failed to apply monitor config for %s - %s.", fingerprint, arg
            )
            ok = False

    workspace_map = {ws.name: ws.monitor.name for ws in instance.get_workspaces()}
    for arg in load_config_file(
        CONFIG_DIR / f"{fingerprint}.workspaces.conf", "workspace="
    ):
        args = arg.split(",")

        if len(args) < 2:
            logger.warning("Not enough arguments in '%s'.", arg)
            continue

        if not args[1].startswith("monitor:"):
            logger.warning("Unsupported workspace option '%s'.", arg)
            continue

        workspace, monitor = args[0], args[1].removeprefix("monitor:")
        if workspace not in workspace_map or workspace_map[workspace] == monitor:
            continue

        if err := instance.dispatch(["moveworkspacetomonitor", workspace, monitor]):
            logger.error(
                "Failed to apply workspace config: %s",
                err,
            )
            ok = False

    if ok:
        logger.info("Applied monitor and workspace config for %s.", fingerprint)


@click.group()
def cli() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


@cli.command()
def apply() -> None:
    instance = Hyprland()
    apply_config(instance, get_monitor_fingerprint(instance))


@cli.command()
@click.option("--apply/--no-apply", " /-A", default=True)
def watch(*, apply: bool) -> None:
    instance = Hyprland()

    if apply:
        apply_config(instance, get_monitor_fingerprint(instance))

    def callback(sender: InstanceSignalCollection, **_kwargs: str) -> None:  # noqa: ARG001
        fingerprint = get_monitor_fingerprint(instance)
        logger.info("Detected monitor fingerprint %s", fingerprint)
        apply_config(instance, fingerprint)

    instance.signals.monitoradded.connect(callback)
    instance.signals.monitorremoved.connect(callback)
    instance.watch()


@cli.command()
@click.option("-f", "--fingerprint", type=str, required=False)
@click.option("-n", "--num_ws", type=int, default=10)
def config(fingerprint: str | None, num_ws: str) -> None:
    instance = Hyprland()

    if fingerprint is None:
        fingerprint = get_monitor_fingerprint(instance)

    monitors_path = CONFIG_DIR / f"{fingerprint}.monitors.conf"
    workspaces_path = CONFIG_DIR / f"{fingerprint}.workspaces.conf"

    subprocess.run(
        [
            "nwg-displays",
            "-m",
            monitors_path,
            "-w",
            workspaces_path,
            "--num_ws",
            str(num_ws),
        ],
        check=False,
    )


if __name__ == "__main__":
    cli()
