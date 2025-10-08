# coding: utf-8
# Copyright (c) 2025 inclusionAI.
import uuid
from typing import Union

from aworld.agents.llm_agent import Agent
from aworld.config import AgentConfig
from aworld.core.agent.swarm import Swarm

from train.adapter.verl.aworld_agent_loop import AworldAgentLoop
from train.adapter.common import get_agent_tool_env_and_servers

GAIA_SYSTEM_PROMPT = """
You are an all-capable AI assistant, aimed at solving any task presented by the user.
"""


class GaiaAgentLoop(AworldAgentLoop):
    async def build_agents(self) -> Union[Agent, Swarm]:
        gaia_env_config, gaia_env_servers = get_agent_tool_env_and_servers()

        return Agent(
            conf=AgentConfig(
                llm_model_name=await self.get_llm_server_model_name(),
                llm_base_url=await self.get_llm_server_address(),
                llm_api_key="dummy",
                llm_provider="verl",
                params={"client": self.server_manager,
                        "tokenizer": self.tokenizer,
                        "request_id": uuid.uuid4().hex,
                        "tool_parser": "hermes"}
            ),
            name="gaia_super_agent",
            system_prompt=GAIA_SYSTEM_PROMPT,

            # MCP tool configuration for the agent
            mcp_config=gaia_env_config,
            mcp_servers=gaia_env_servers,
        )
