from __future__ import annotations


class LinuxRouteManager:
    """Simulation adapter for future Linux route execution."""

    def apply_route(self, route_name: str) -> None:
        # Placeholder for later integration with Linux routing tables.
        if not route_name:
            raise ValueError("route_name is required")
