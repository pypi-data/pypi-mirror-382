import json

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.plugins.base_plugin import BasePlugin
from opentelemetry import trace

from freeplay_python_adk.constants import FreeplayOTelAttributes


class TraceInputStatePlugin(BasePlugin):
    def __init__(self):
        super().__init__(name="trace_input_state_plugin")

    async def before_agent_callback(
        self,
        *,
        agent: BaseAgent,  # noqa: ARG002
        callback_context: CallbackContext,
    ) -> None:
        span = trace.get_current_span()
        span.set_attribute(
            FreeplayOTelAttributes.FREEPLAY_INPUT_VARIABLES.value,
            json.dumps(callback_context.state.to_dict()),
        )
