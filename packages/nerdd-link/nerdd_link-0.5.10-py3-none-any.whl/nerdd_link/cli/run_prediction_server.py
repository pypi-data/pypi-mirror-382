import asyncio
import logging
import signal
from importlib import import_module
from typing import Any, List

import rich_click as click

from ..actions import Action, PredictCheckpointsAction, RegisterModuleAction
from ..channels import Channel
from ..utils import async_to_sync

__all__ = ["run_prediction_server"]

logger = logging.getLogger(__name__)


@click.command(context_settings={"show_default": True})
@click.argument("model-name")
@click.option(
    "--channel",
    type=click.Choice(["kafka"], case_sensitive=False),
    default="kafka",
    help="Channel to use for communication with the model.",
)
@click.option("--broker-url", default="localhost:9092", help="Kafka broker to connect to.")
@click.option(
    "--data-dir",
    default="sources",
    help="Directory containing structure files associated with the incoming jobs.",
)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(["debug", "info", "warning", "error", "critical"], case_sensitive=False),
    help="The logging level.",
)
@async_to_sync
async def run_prediction_server(
    # communication options
    channel: str,
    broker_url: str,
    # options
    model_name: str,
    data_dir: str,
    # log level
    log_level: str,
) -> None:
    logging.basicConfig(level=log_level.upper())

    channel_instance = Channel.create_channel(channel, broker_url=broker_url)

    await channel_instance.start()

    # enable graceful shutdown on SIGTERM
    loop = asyncio.get_running_loop()

    def handle_termination_signal(*args: Any) -> None:
        logger.info("Received termination signal, shutting down...")
        asyncio.run_coroutine_threadsafe(channel_instance.stop(), loop)

    loop.add_signal_handler(signal.SIGTERM, handle_termination_signal)

    # import the model class
    package_name, class_name = model_name.rsplit(".", 1)
    package = import_module(package_name)
    Model = getattr(package, class_name)
    model = Model()

    register_module = RegisterModuleAction(channel=channel_instance, model=model, data_dir=data_dir)

    predict_checkpoints = PredictCheckpointsAction(
        channel=channel_instance,
        model=model,
        data_dir=data_dir,
    )

    actions: List[Action] = [register_module, predict_checkpoints]

    tasks = [asyncio.create_task(action.run()) for action in actions]
    try:
        for task in tasks:
            logging.info(f"Running action {task}")
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        await channel_instance.stop()

    logger.info("Server shut down successfully")
