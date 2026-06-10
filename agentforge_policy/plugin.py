"""AgentForge plugin entry point for agentforge-policy-plugin.

`register(app)` is called by `PluginRegistry.register_plugin()`:
1. Mounts the policy-test router onto the host FastAPI app.
2. Loads both policy-test agents into the host's AgentLoader (if present).
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI

logger = logging.getLogger(__name__)

_AGENTS_DIR = Path(__file__).parent / "agents"
_NAMESPACE = "project.policy-test"


def register(app: FastAPI) -> None:
    from agentforge_policy.routes import demo_router, router

    app.include_router(router)
    app.include_router(demo_router)

    agent_loader = getattr(app.state, "agent_loader", None)
    if agent_loader is None:
        logger.debug(
            "policy plugin: no agent_loader on app.state — skipping agent load"
        )
        return

    try:
        newly_loaded = agent_loader.load_external(_AGENTS_DIR, _NAMESPACE)
        logger.info(
            "policy plugin: loaded %d agent(s) from %s", len(newly_loaded), _AGENTS_DIR
        )
    except Exception:
        logger.exception("policy plugin: agent load failed")
