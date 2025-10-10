from blissdata.redis_engine.scan import ScanState


def wait_for_scan_state(scan, desired_state: ScanState):
    """
    Wait until a scan reaches the desired state (or a higher one).

    Args:
        scan: The scan object to monitor.
        desired_state (ScanState): The state we want to wait for.

    Returns:
        The scan object in its final state.
    """

    while scan.state < desired_state.value:
        scan.update()
