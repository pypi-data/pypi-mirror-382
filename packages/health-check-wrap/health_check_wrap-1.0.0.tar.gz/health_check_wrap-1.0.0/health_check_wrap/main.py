import argparse
import signal
import subprocess
import sys
import time
import threading
import logging # Still need to import the module

SHUTDOWN_TIMEOUT_SECONDS = 60

SERVICE_PROCESS = None
STOP_EVENT = threading.Event()
HEALTH_SHUTDOWN = False


def setup_logging(info_mode=False, silent_mode=False):
    """
    Configures the logging system based on command-line arguments.
    Logs are directed to sys.stderr.
    """
    if silent_mode:
        # Disable all logging
        logging.disable(logging.CRITICAL)
        return

    # Set default level to WARNING
    level = logging.WARNING
    if info_mode:
        level = logging.INFO

    # Configure the root logger
    logging.basicConfig(
        level=level,
        stream=sys.stderr,  # Log to standard error as requested
        format='health-check-wrap - [%(levelname)s] %(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Initial log to confirm mode (only visible if not silent)
    logging.info("Logging initialized at %s level.", logging.getLevelName(level))




def terminate_service():
    global HEALTH_SHUTDOWN
    HEALTH_SHUTDOWN = True
    if SERVICE_PROCESS and SERVICE_PROCESS.poll() is None:
        # FIXED: Using %s for string formatting in logging
        logging.warning("Terminating process...")
        SERVICE_PROCESS.terminate()
        try:
            # Wait for the service to exit gracefully
            SERVICE_PROCESS.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
            logging.warning("Service shut down after SIGTERM.")
        except subprocess.TimeoutExpired:
            # Service ignored SIGTERM, proceed to force kill
            # Changed logger.warning to logging.warning
            logging.warning(
                "Service ignored SIGTERM for %s seconds. Sending SIGKILL.", SHUTDOWN_TIMEOUT_SECONDS
            )
            SERVICE_PROCESS.kill()

def signal_handler(signum, frame):
    """Handles SIGTERM and SIGINT from the service manager."""
    del frame
    # FIXED: Using %s for string formatting in logging
    logging.info("Signal %s received. Initiating graceful shutdown...", signum)
    # Calls terminate_service with exit_code 0 for clean exit
    terminate_service()


def health_check_loop(checks, interval):
    """Runs health checks periodically."""
    while not STOP_EVENT.is_set():
        logging.info("Running health checks...")
        for cmd in checks:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    check=False,
                )

                # Health Check Contract: 0 for success, non-zero for failure
                if result.returncode != 0:
                    # Note: Using print() here to ensure output even if logging is fully disabled
                    logging.error(f"health-check-wrapper - Health check failed (Exit Code %r)",  result.returncode)
                    # Failure forces wrapper exit, triggering service manager restart
                    terminate_service()
                else:
                    logging.info("Health check passed: %s", cmd)

            except Exception as e:
                # Execution error (e.g., command not found) is also a critical failure
                print(f"\n[Wrapper] Error executing health check '{cmd}': {e}", file=sys.stderr)
                terminate_service()

        # Wait for the interval, but check for stop event periodically
        STOP_EVENT.wait(interval)

# --- Service Runtime Logic ---

def start_service(service_cmd):
    """Starts the main service and watches for its exit, max_runtime, or external stop."""
    global SERVICE_PROCESS #pylint: disable=global-statement

    # FIXED: Using %s for string formatting in logging
    logging.info("Starting service: %s", service_cmd)
    try:
        SERVICE_PROCESS = subprocess.Popen(service_cmd, shell=True) # pylint: disable=consider-using-with
        logging.info("Service started with PID: %s", SERVICE_PROCESS.pid)

        SERVICE_PROCESS.wait()

        if HEALTH_SHUTDOWN:
            sys.exit(2)

        if STOP_EVENT.is_set():
            # Changed logger.info to logging.info
            logging.info("Service exited as requested with code %s.", SERVICE_PROCESS.returncode)
        else:
            # FIXED: Using %s for string formatting in logging
            logging.error("Service exited unexpectedly with code %s.", SERVICE_PROCESS.returncode)

            # Exit with the service's return code (or 1 if None)
            sys.exit(SERVICE_PROCESS.returncode if SERVICE_PROCESS.returncode is not None else 1)

    except Exception as e:
        # Changed logger.critical to logging.critical
        logging.critical("Error starting service '%s': %s", service_cmd, e)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="A lightweight wrapper to provide periodic health checks and supervision for a service.")
    parser.add_argument('--service', required=True, help='The command to run the main service.')
    parser.add_argument('--health-check', action='append', dest='health_checks', help='One or more commands to run as a health check.')
    parser.add_argument('--interval', type=int, default=60, help='Interval between health checks in seconds (Default: 60).')
    parser.add_argument('--max-runtime', type=int, default=0, help='Maximum time the service is allowed to run in seconds. Set to 0 for unlimited (Default: 0).')

    # NEW: Logging flags
    parser.add_argument('--info', action='store_true', help='Enable INFO level logging (Default is WARNING).')
    parser.add_argument('--silent', action='store_true', help='Disable all logging output.')

    args = parser.parse_args()

    # Input validation for mutually exclusive flags
    if args.info and args.silent:
        print("Error: The --info and --silent flags are mutually exclusive.", file=sys.stderr)
        sys.exit(1)

    # 0. Setup Logging based on flags
    setup_logging(args.info, args.silent)

    # 1. Setup Signal Handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # 2. Start Health Check Thread
    if args.health_checks:
        logging.info(f"Starting health check thread with interval: {args.interval}s")
        check_thread = threading.Thread(
            target=health_check_loop,
            args=(args.health_checks, args.interval),
            daemon=True
        )
        check_thread.start()
    else:
        logging.info("No health checks configured.")

    # 3. Run Service (Blocking call)
    start_service(args.service)

    # Clean shutdown if run_service completes successfully
    STOP_EVENT.set()
    sys.exit(0)

if __name__ == '__main__':
    main()
