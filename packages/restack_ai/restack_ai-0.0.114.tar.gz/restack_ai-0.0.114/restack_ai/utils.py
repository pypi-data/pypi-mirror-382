def rpm_to_second(rpm: int) -> float:
    seconds_in_a_minute = 60
    return rpm / seconds_in_a_minute


def should_use_https(address: str) -> bool:
    """Determine if an address should use HTTPS based on common patterns.

    Args:
        address: The address to check (e.g., "localhost:6233", "api.restack.io")

    Returns:
        True if HTTPS should be used, False for HTTP
    """
    if not address:
        return False

    # Remove port if present for hostname checking
    hostname = address.split(":")[0]

    # Use HTTP for localhost and local addresses (excluding 0.0.0.0 for security)
    if hostname in [
        "localhost",
        "127.0.0.1",
        "host.docker.internal",
    ]:
        return False

    # Use HTTP for private IP ranges (Docker/K8s common)
    if hostname.startswith(("10.", "192.168.", "172.")):
        return False

    # Maximum dots for K8s service names
    max_k8s_service_dots = 2

    # Use HTTP for Kubernetes service names
    if hostname.endswith(".svc.cluster.local") or (
        hostname.endswith(".svc")
        and hostname.count(".") <= max_k8s_service_dots
    ):
        return False

    # Use HTTP for container names (no dots, common in Docker)
    # Return True for public domains (has dots)
    return "." in hostname
