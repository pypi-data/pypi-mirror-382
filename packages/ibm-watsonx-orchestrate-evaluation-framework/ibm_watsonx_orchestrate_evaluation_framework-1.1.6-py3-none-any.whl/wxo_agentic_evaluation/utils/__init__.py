import json
from wxo_agentic_evaluation.utils.utils import TestCaseResources, add_line_seperator, list_run_files, load_run_metrics, N_A
from wxo_agentic_evaluation.utils.open_ai_tool_extractor import ToolExtractionOpenAIFormat
from wxo_agentic_evaluation.utils.parsers import ReferencelessEvalParser


def json_dump(output_path, object):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(object, f, indent=4)
