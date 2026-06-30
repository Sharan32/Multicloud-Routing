# Routing Engine

## Purpose

The routing engine evaluates candidate nodes using configurable scoring and failover behavior. It is intentionally independent of FastAPI so it can be reused by tests, CLI tools, background workers, or scheduled jobs.

## How it works

1. Metrics are converted into RouteCandidate objects.
2. A policy scores each candidate using normalized latency, packet loss, throughput, health, and uptime values.
3. The highest-scoring healthy node is selected.
4. If the selected node fails health thresholds, failover selects another candidate.
5. Every decision is recorded in the routing history store.
