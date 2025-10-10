import json
from typing import Any, List, Mapping

import rich

from wxo_agentic_evaluation.referenceless_eval.function_calling.consts import (
    METRIC_FUNCTION_SELECTION_APPROPRIATENESS,
    METRIC_GENERAL_HALLUCINATION_CHECK,
)
from wxo_agentic_evaluation.referenceless_eval.function_calling.pipeline.pipeline import (
    ReflectionPipeline,
)
from wxo_agentic_evaluation.referenceless_eval.function_calling.pipeline.types import (
    ToolCall,
    ToolSpec,
)
from wxo_agentic_evaluation.service_provider import get_provider
from wxo_agentic_evaluation.type import Message

DEFAULT_GENERATION_PARAMS= {
    "min_new_tokens": 0,
    "decoding_method": "greedy",
    "max_new_tokens": 4096,
}

class ReferencelessEvaluation:
    """
    Note: static.final_decison, if `True` -> then all static metrics were valid. If false, atleast one of the static metrics failed. Look at explanation for reasoning
    Note: if static.final_decision == True, check semantic metrics. Semantic metrics **not** run if static.final_decision is False.
    ---
    Note: For semantic metrics, check agentic constraints. If agent-constraints == False, no point in checking others. If true, check others.
    Note: METRIC_FUNCTION_SELECTION_APPROPRIATENESS == False, implies that the LLM should have called some other function/tool before *OR* it is a redundant call.
    Note: When parsing the semantic metrics, check for `is_correct` field.  if `false` there is some mistake that the LLMaJ found in that tool call.
    """

    def __init__(
        self,
        api_spec: List[Mapping[str, Any]],
        model_id: str,
        task_n: str,
        dataset_name: str,
        runtime_pipeline: bool = True,
        generation_params = DEFAULT_GENERATION_PARAMS
    ):

        self.metrics_client = get_provider(
            model_id=model_id,
            params=generation_params,
            referenceless_eval=True,
        )

        self.pipeline = ReflectionPipeline(
            metrics_client=self.metrics_client,
            general_metrics=[METRIC_GENERAL_HALLUCINATION_CHECK],
            function_metrics=[METRIC_FUNCTION_SELECTION_APPROPRIATENESS],
            parameter_metrics=None,
            runtime_pipeline=runtime_pipeline,
        )

        self.task_n = task_n
        self.dataset_name = dataset_name

        self.apis_specs = [ToolSpec.model_validate(spec) for spec in api_spec]

    @staticmethod
    def fmt_tool_call(tool_id, tool_call_name, arguments, context):
        call = {
                "call": {
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": tool_call_name,
                        "arguments": arguments,
                    },
                },
                "context": context,
            }
        
        return call

    @staticmethod
    def fmt_msgs_referenceless(
        messages: List[Message],
    ) -> List[Mapping[str, Any]]:
        """Assume that the last item in the `messages` array is the tool call, and preceding items
        in the messages array is the context.
        """
        examples = []
        processed_data = [
            {
                k: msg.model_dump().get(k)
                for k in ["role", "content", "type"]
                if k in msg.model_dump()
            }
            for msg in messages
        ]

        for idx, message in enumerate(processed_data):
            role = message["role"]
            content = message["content"]
            context = processed_data[:idx]

            if role == "assistant" and message["type"] == "tool_call":
                tool_call_msg = json.loads(content)
                if tool_call_msg["name"].startswith("transfer_to"):
                    continue
                
                call = ReferencelessEvaluation.fmt_tool_call(
                    tool_id=tool_call_msg.get("id", "1"),
                    tool_call_name=tool_call_msg["name"],
                    arguments=json.dumps(tool_call_msg["args"]),
                    context=context
                )
                examples.append(call)

        return examples

    def _run_pipeline(self, examples: List[Mapping[str, Any]]):
        results = []
        for example in examples:
            result = self.pipeline.run_sync(
                conversation=example["context"],
                inventory=self.apis_specs,
                call=example["call"],
                continue_on_static=False,
                retries=2,
            )
            result_dict = result.model_dump()
            results.append(result_dict)

        return results

    def run(self, examples: List[Mapping[str, str]], verbose=False):
        """`examples` should be an array where each element is formatted:

        call = {
            "call": {
                "id": tool_call_msg.get("id", "1"),
                "type": "function",
                "function": {
                    "name": tool_call_msg["name"],
                    "arguments": json.dumps(tool_call_msg["args"]),
                },
            },
            "context": context,
        }
        """

        examples = [
            {
                "call": ToolCall.model_validate(ex["call"]),
                "context": ex["context"],
            }
            for ex in examples
        ]

        if verbose:
            rich.print(
                f"[yellow][b][Task-{self.task_n}] There are {len(examples)} examples to analyze"
            )
        results = self._run_pipeline(examples)

        return results
