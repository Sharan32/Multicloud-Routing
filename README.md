# Multicloud Routing & Monitoring Platform

This repository contains the infrastructure and application layers for a multicloud routing and monitoring platform. The current focus is on the network monitoring agent, which collects latency, packet loss, and throughput data for remote nodes.

## Project structure

- infra/: Terraform infrastructure definitions and state.
- agent/: Monitoring agent modules for collecting and persisting network metrics.
- api/: FastAPI control plane (planned for the next phase).
- router/: Routing engine (planned for a later phase).
- monitoring/: Observability and dashboard configuration (planned for a later phase).

## Current phase

Phase 1 implements a modular network monitoring agent with:

- configuration via environment variables
- structured logging
- JSON-based metric persistence
- ping-based latency and reachability checks
- iperf3-based throughput benchmarking

## Setup

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

Run the agent:

```bash
python -m agent.main
```

Run tests:

```bash
pytest tests/agent/test_agent.py
```
