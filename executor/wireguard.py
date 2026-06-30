from __future__ import annotations


class WireGuardManager:
    """Simulation adapter for future WireGuard updates."""

    def apply_route(self, route_name: str) -> None:
        # Placeholder for later integration with WireGuard interfaces.
        if not route_name:
            raise ValueError("route_name is required")
