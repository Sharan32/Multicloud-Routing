# Route Execution Engine

## Why execution is separated from routing

Routing decides which route is best based on telemetry. Execution is a separate concern because applying a route is an operational action that can fail, require cooldowns, or need platform-specific integrations. Keeping the orchestration logic independent makes the system easier to test and safer to evolve.

## Linux route integration

The executor is designed around an adapter interface that can later invoke Linux routing commands such as `ip route` or `ip rule` without changing the orchestration flow. The current implementation uses a simulation adapter, but the architecture is ready for a real Linux-backed manager.

## WireGuard integration

The same interface can later be used to update WireGuard peer routing or interface state. A dedicated adapter can translate an execution decision into WireGuard-specific operations while the core executor remains unchanged.

## Multiple cloud provider support

The executor only consumes a route decision and applies it through an adapter. That means each cloud provider or networking backend can implement its own adapter while the orchestration and state machine stay consistent.
