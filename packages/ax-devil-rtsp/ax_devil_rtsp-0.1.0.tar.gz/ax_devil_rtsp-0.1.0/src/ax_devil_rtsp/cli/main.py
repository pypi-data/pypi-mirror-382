from __future__ import annotations

import queue
import sys
import time
from types import SimpleNamespace

import click
import cv2
import numpy as np

from ..logging import init_app_logging, get_logger

from ..rtsp_data_retrievers import (
    RtspApplicationDataRetriever,
    RtspDataRetriever,
    RtspVideoDataRetriever,
)
from ..utils import build_axis_rtsp_url


def simple_video_processing_example(
    payload: dict, shared_config: dict
) -> np.ndarray:
    """
    Example video processing function that demonstrates the video_processing_fn feature.
    Adds a timestamp overlay and optionally applies brightness adjustment.
    """
    frame = payload["data"]
    processed = frame.copy()

    # Add timestamp overlay
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(
        processed, "Local: " +
        timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
    )

    # Apply brightness adjustment if configured
    brightness = shared_config.get("brightness_adjustment", 0)
    if brightness != 0:
        processed = cv2.convertScaleAbs(processed, alpha=1.0, beta=brightness)

    # Add frame counter
    shared_config["frame_count"] = shared_config.get("frame_count", 0) + 1
    frame_text = f"Frame: {shared_config['frame_count']}"
    cv2.putText(
        processed, frame_text, (10,
                                60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1
    )

    ntp_time = payload.get("latest_rtp_data", {}).get("human_time")
    if ntp_time:
        cv2.putText(
            processed,
            f"NTP: {ntp_time}",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1,
        )

    return processed


def _display_loop(video_frames, args, retriever, logger):
    """Display loop for showing video frames."""
    if args.only_application_data:
        logger.info("Application data only mode - no video display")
        try:
            while retriever.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            return
        return

    logger.info("Starting video display...")

    while retriever.is_running:
        try:
            frame = video_frames.get(timeout=0.1)
            if frame is not None:
                cv2.imshow("RTSP Stream", frame)

            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("User pressed 'q' to quit")
                break

        except queue.Empty:
            continue
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            break
        except Exception as e:
            logger.error(f"Error in display loop: {e}")
            break

    cv2.destroyAllWindows()


def main(**kwargs):
    args = SimpleNamespace(**kwargs)
    init_app_logging(debug=args.log_level.upper() == "DEBUG")
    logger = get_logger("cli")
    logger.info(f"Starting with args: {args}")

    if getattr(args, "rtsp_url", None):
        rtsp_url = args.rtsp_url
    else:
        try:
            rtsp_url = build_axis_rtsp_url(
                ip=args.ip,
                username=args.username,
                password=args.password,
                video_source=getattr(args, "source", 1),
                get_video_data=not args.only_application_data,
                get_application_data=not args.only_video,
                rtp_ext=getattr(args, "rtp_ext", True),
                resolution=getattr(args, "resolution", None),
            )
        except ValueError as e:
            logger.error(e)
            sys.exit(1)
    logger.info(f"Starting stream on {rtsp_url=}")

    # Callback functions for handling different data types
    # Queue for transferring frames to the main thread
    video_frames: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=1)

    def on_video_data(payload):
        if args.only_application_data:
            return
        frame = payload["data"]
        try:
            video_frames.put_nowait(frame)
        except queue.Full:
            # Drop frame if the display thread is lagging
            pass

    def on_application_data(payload):
        if args.only_video:
            return
        xml = payload["data"]
        diag = payload["diagnostics"]
        logger.info(f"[APPLICATION DATA] {len(xml)} bytes, diag={diag}")
        logger.info(xml)

    def on_session_start(payload):
        logger.info(f"[SESSION METADATA] {payload}")

    def on_error(payload):
        error_type = payload.get("error_type", "Unknown")
        message = payload.get("message", "Unknown error")
        error_count = payload.get("error_count", 0)
        logger.error(
            f"[ERROR] {error_type}: {message} (total errors: {error_count})")

    # Set up video processing if requested
    video_processing_fn = None
    shared_config = None
    if args.enable_video_processing and not args.only_application_data:
        video_processing_fn = simple_video_processing_example
        shared_config = {
            "brightness_adjustment": args.brightness_adjustment,
            "frame_count": 0,
        }
        logger.info(
            "[DEMO] Video processing enabled with brightness adjustment: "
            f"{args.brightness_adjustment}"
        )

    retriever_classes = {
        (True, False): (RtspVideoDataRetriever, "video-only retriever"),
        (False, True): (RtspApplicationDataRetriever, "application data-only retriever"),
        (False, False): (RtspDataRetriever, "combined video+application data retriever")
    }

    retriever_class, desc = retriever_classes[(
        args.only_video, args.only_application_data)]
    logger.info(f"[DEMO] Using {retriever_class.__name__} ({desc})")

    # Build kwargs based on retriever class signature
    kwargs = {
        "rtsp_url": rtsp_url,
        "on_session_start": on_session_start,
        "on_error": on_error,
        "latency": args.latency,
        "video_processing_fn": video_processing_fn,
        "shared_config": shared_config,
        "connection_timeout": args.connection_timeout,
    }

    # Add class-specific callback arguments
    if retriever_class is RtspVideoDataRetriever:
        kwargs["on_video_data"] = on_video_data
    elif retriever_class is RtspApplicationDataRetriever:
        kwargs["on_application_data"] = on_application_data
    else:  # RtspDataRetriever
        kwargs["on_video_data"] = on_video_data
        kwargs["on_application_data"] = on_application_data

    retriever = retriever_class(**kwargs)

    try:
        logger.info(
            f"[DEMO] Using {'manual lifecycle' if args.manual_lifecycle else 'context manager'}")

        if args.manual_lifecycle:
            retriever.start()
            logger.info("RTSP Data Retriever started manually")
            try:
                logger.info(
                    "Press Ctrl+C to stop, or 'q' in video window to quit")
                _display_loop(video_frames, args, retriever, logger)
            finally:
                retriever.stop()
        else:
            with retriever:
                logger.info("RTSP Data Retriever started")
                logger.info(
                    "Press Ctrl+C to stop, or 'q' in video window to quit")
                _display_loop(video_frames, args, retriever, logger)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error running retriever: {e}")
    finally:
        logger.info("Cleaning up...")
        if not args.only_application_data:
            cv2.destroyAllWindows()


def _shared_options(func):
    """Decorator for options common to all commands."""

    func = click.option(
        "--latency",
        default=100,
        show_default=True,
        type=int,
        help="RTSP latency in ms (to gather out of order packets)",
    )(func)

    func = click.option(
        "--only-video",
        is_flag=True,
        default=False,
        show_default=True,
        help=(
            "Enable only video frames (disable application data) - "
            "demonstrates RtspVideoDataRetriever"
        ),
    )(func)

    func = click.option(
        "--only-application-data",
        is_flag=True,
        default=False,
        show_default=True,
        help=(
            "Enable only application data XML (disable video) - "
            "demonstrates RtspApplicationDataRetriever"
        ),
    )(func)

    func = click.option(
        "--log-level",
        default="INFO",
        show_default=True,
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        help="Logging verbosity",
    )(func)

    func = click.option(
        "--connection-timeout",
        default=30,
        show_default=True,
        type=int,
        help="Connection timeout in seconds",
    )(func)

    func = click.option(
        "--enable-video-processing",
        is_flag=True,
        default=False,
        show_default=True,
        help=(
            "Demonstrate video_processing_fn with timestamp overlay "
            "and brightness adjustment"
        ),
    )(func)

    func = click.option(
        "--brightness-adjustment",
        default=0,
        show_default=True,
        type=int,
        help="Brightness adjustment value for video processing example (-100 to 100)",
    )(func)

    func = click.option(
        "--manual-lifecycle",
        is_flag=True,
        default=False,
        show_default=True,
        help="Demonstrate manual start()/stop() instead of context manager",
    )(func)

    return func


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """Retrieve RTSP video and application data from Axis devices."""
    pass


@cli.command("device")
@click.option(
    "--ip",
    envvar="AX_DEVIL_TARGET_ADDR",
    required=True,
    help="Camera IP address (env: AX_DEVIL_TARGET_ADDR)",
)
@click.option(
    "--username",
    envvar="AX_DEVIL_TARGET_USER",
    default="",
    show_default=True,
    help="Device username (env: AX_DEVIL_TARGET_USER)",
)
@click.option(
    "--password",
    envvar="AX_DEVIL_TARGET_PASS",
    default="",
    show_default=True,
    help="Device password (env: AX_DEVIL_TARGET_PASS)",
)
@click.option(
    "--source",
    default="1",
    show_default=True,
    help='What device "source"/"camera head" to use',
)
@click.option(
    "--rtp-ext/--no-rtp-ext",
    default=True,
    show_default=True,
    help="Enable or disable RTP extension",
)
@click.option(
    "--resolution",
    default=None,
    show_default=True,
    help=(
        "Video resolution (e.g. 1280x720 or 500x500) "
        "(default: None, lets device decide)"
    ),
)
@_shared_options
def device(**kwargs) -> None:
    """Build the RTSP URL from device info and connect."""
    main(**kwargs)


@cli.command("url")
@click.argument("rtsp_url")
@_shared_options
def url(rtsp_url: str, **kwargs) -> None:
    """Connect using an existing RTSP URL.

    Options that build the URL (e.g. ``--resolution``) are not available."""
    main(rtsp_url=rtsp_url, **kwargs)


if __name__ == "__main__":
    cli()
