import glob
import json
import os
import re
import csv
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Union, Mapping, Tuple, Any
from urllib.parse import urlparse

import yaml
import rich
from rich import box, print
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style
from rich.table import Table

from wxo_agentic_evaluation.metrics.llm_as_judge import Faithfulness
from wxo_agentic_evaluation.metrics.metrics import (
    KnowledgeBaseMetricSummary,
    ReferenceLessEvalMetrics,
    ToolCallAndRoutingMetrics,
    EnhancedAnalyzeMetrics,
)
from wxo_agentic_evaluation.type import (
    ConversationalConfidenceThresholdScore,
    Message,
    ExtendedMessage,
)

console = Console()

RUN_FILE_RE = re.compile(
    r"^(?P<base>.+)\.run(?P<run>\d+)\.(?P<kind>messages(?:\.analyze)?|metrics)\.json$"
)
N_A = "N/A"

class AttackResultsTable:
    def __init__(self, attack_results: dict):
        self.table = Table(
            title="Attack Results",
            box=box.ROUNDED,
            show_lines=True,
        )
        self.table.add_column("Attack Category", style="magenta")
        self.table.add_column("Count", style="cyan")
        self.table.add_column("Success Rate", style="green")

        # Extract values
        n_on_policy = attack_results.get("n_on_policy_attacks", 0)
        n_off_policy = attack_results.get("n_off_policy_attacks", 0)
        n_on_policy_successful = attack_results.get("n_on_policy_successful", 0)
        n_off_policy_successful = attack_results.get(
            "n_off_policy_successful", 0
        )

        # Calculate success rates
        on_policy_rate = (
            f"{round(100 * safe_divide(n_on_policy_successful, n_on_policy))}%"
            if n_on_policy
            else "0%"
        )
        off_policy_rate = (
            f"{round(100 * safe_divide(n_off_policy_successful, n_off_policy))}%"
            if n_off_policy
            else "0%"
        )

        self.table.add_row("On Policy", str(n_on_policy), on_policy_rate)
        self.table.add_row("Off Policy", str(n_off_policy), off_policy_rate)

    def print(self):
        console.print(self.table)


class TestCaseResources:
    def __init__(self, output_dir: str):
        """Todo flesh out for all resources that are saved"""
        self.output_dir = Path(output_dir)

    @property
    def get_summary(self):
        summary = []

        with open(self.output_dir / "summary_metrics.csv", "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                summary.append(dict(zip(header, row)))

        return summary

    def get_analyze_messages(
        self, test_case_name=None, path=None
    ) -> Tuple[List[ExtendedMessage], Mapping[str, Any]]:
        test_messages = []

        if test_case_name:
            path = os.path.join(
                self.output_dir,
                "messages",
                f"{test_case_name}.messages.analyze.json",
            )

        if not Path(str(path)).is_file():
            rich.print(f"[r]No analyze file found at {path}")
            raise Exception(f"No analyze file found at {path}")

        with open(path, "r", encoding="utf-8") as f:
            temp = json.load(f)
            meta = None
            if temp and isinstance(temp[-1], dict) and "meta" in temp[-1]:
                meta = temp[-1]["meta"]
                temp = temp[:-1]

            for entry in temp:
                msg = ExtendedMessage(**entry)
                test_messages.append(msg)

        return test_messages, meta

    def get_messages(self, test_case_name=None, path=None) -> List[Message]:
        test_messages = []

        if test_case_name:
            path = os.path.join(
                self.output_dir,
                "messages",
                f"{test_case_name}.messages.json",
            )

        if not Path(str(path)).is_file():
            rich.print(f"[r]No messages file found at {path}")
            raise Exception(f"No messages file found at {path}")

        with open(path, "r", encoding="utf-8") as f:
            temp = json.load(f)
            for entry in temp:
                msg = Message(**entry)
                test_messages.append(msg)

        return test_messages

    def get_test_metrics(
        self, test_case_name=None, path=None
    ) -> ToolCallAndRoutingMetrics:
        if test_case_name:
            path = os.path.join(
                self.output_dir,
                "messages",
                f"{test_case_name}.metrics.json",
            )

        if not Path(str(path)).is_file():
            rich.print(f"[r]No metrics file found at {path}")
            raise Exception(f"No metrics file found at {path}")

        with open(path, "r", encoding="utf-8") as f:
            metrics = ToolCallAndRoutingMetrics(**json.load(f))

        return metrics


class AgentMetricsTable:
    def __init__(self, data):
        self.table = Table(
            title="Agent Metrics",
            box=box.ROUNDED,
            show_lines=True,
        )

        if not data:
            return

        # Add columns with styling
        headers = list(data[0].keys())
        for header in headers:
            self.table.add_column(header, style="cyan")

        # Add rows
        for row in data:
            self.table.add_row(*[str(row.get(col, "")) for col in headers])

    def print(self):
        console.print(self.table)


def create_table(data: List[dict]) -> AgentMetricsTable:
    """
    Generate a Rich table from a list of dictionaries.
    Returns the AgentMetricsTable instance.
    """
    if isinstance(data, dict):
        data = [data]

    if not data:
        print("create_table() received an empty dataset. No table generated.")
        return None

    return AgentMetricsTable(data)


def safe_divide(nom, denom):
    if denom == 0:
        return 0
    else:
        return nom / denom


def is_saas_url(service_url: str) -> bool:
    hostname = urlparse(service_url).hostname
    return hostname not in ("localhost", "127.0.0.1", "0.0.0.0", "::1")


def is_ibm_cloud_url(service_url: str) -> bool:
    hostname = urlparse(service_url).hostname
    return ".cloud.ibm.com" in hostname


def add_line_seperator(
    style_config: Optional[Union[str, Style]] = None,
    print=True,
):
    """
    Adds a lined seperator provided the style config.
    `print` is a boolean to indicate if the lined seperator should go to stdout immeadiatly or returned as an object.
    Set `print` to False, the lined seperator is printed later as part of the pager view for example.
    """

    if not style_config:
        style = "grey42"
    else:
        style = style_config

    if print:
        console.print(
            Rule(
                style=style,
            )
        )
    else:
        return Rule(style=style, characters="==")


class FaithfulnessTable:
    def __init__(
        self, faithfulness_metrics: List[Faithfulness], tool_call_ids: List[str]
    ):
        self.table = Table(
            title="Faithfulness", box=box.ROUNDED, show_lines=True
        )

        self.table.add_column("Tool Call Id", style="blue")
        self.table.add_column("Faithfulness Score", style="blue3")
        self.table.add_column("Evidence", style="cyan")
        self.table.add_column("Reasoning", style="yellow3")

        for tool_call_id, faithfulness in zip(
            tool_call_ids, faithfulness_metrics
        ):
            faithfulness = faithfulness.table()
            self.table.add_row(
                tool_call_id,
                faithfulness["faithfulness_score"],
                faithfulness["evidence"],
                faithfulness["reason"],
            )

    def print(self):
        console.print(self.table)


class ConversationalSearchTable:
    def __init__(
        self,
        confidence_scores_list: List[ConversationalConfidenceThresholdScore],
        tool_call_ids: List[str],
    ):
        self.table = Table(
            title="Conversational Search", box=box.ROUNDED, show_lines=True
        )

        self.table.add_column("Tool Call Id", style="blue")
        self.table.add_column("Response Confidence", style="blue3")
        self.table.add_column("Response Confidence Threshold", style="cyan")
        self.table.add_column("Retrieval Confidence", style="blue3")
        self.table.add_column("Retrieval Confidence Threshold", style="cyan")

        for tool_call_id, confidence_scores in zip(
            tool_call_ids, confidence_scores_list
        ):
            confidence_scores = confidence_scores.table()
            self.table.add_row(
                tool_call_id,
                confidence_scores["response_confidence"],
                confidence_scores["response_confidence_threshold"],
                confidence_scores["retrieval_confidence"],
                confidence_scores["retrieval_confidence_threshold"],
            )


class KnowledgePanel:
    def __init__(
        self,
        dataset_name: str,
        tool_call_id: List[str],
        faithfulness: List[Faithfulness] = None,
        confidence_scores: List[ConversationalConfidenceThresholdScore] = None,
    ):
        self.faithfulness = FaithfulnessTable(faithfulness, tool_call_id)
        self.confidence_scores = ConversationalSearchTable(
            confidence_scores, tool_call_id
        )
        self.group = Group(
            self.faithfulness.table, self.confidence_scores.table
        )

        # Panel acts as a section
        self.section = Panel(
            self.group,
            title=f"Agent with Knowledge Metrics for {dataset_name}",
            border_style="grey37",
            title_align="left",
        )

    def print(self):
        console.print(self.section)


class SummaryPanel:
    def __init__(self, summary_metrics: KnowledgeBaseMetricSummary):

        self.table = Table(
            title="Agent with Knowledge Summary Metrics",
            box=box.ROUNDED,
            show_lines=True,
        )
        self.table.add_column("Dataset", style="blue3")
        self.table.add_column("Average Response Confidence", style="cyan")
        self.table.add_column("Average Retrieval Confidence", style="blue3")
        self.table.add_column("Average Faithfulness", style="cyan")
        self.table.add_column("Average Answer Relevancy", style="blue3")
        self.table.add_column("Number Calls to Knowledge Bases", style="cyan")
        self.table.add_column("Knowledge Bases Called", style="blue3")

        average_metrics = summary_metrics.average
        for dataset, metrics in average_metrics.items():
            self.table.add_row(
                dataset,
                str(round(metrics["average_response_confidence"], 4)),
                str(round(metrics["average_retrieval_confidence"], 4)),
                str(metrics["average_faithfulness"]),
                str(metrics["average_answer_relevancy"]),
                str(metrics["number_of_calls"]),
                metrics["knowledge_bases_called"],
            )

    def print(self):
        console.print(self.table)


class Tokenizer:
    PATTERN = r"""
            \w+(?=n't)|              # Words before n't contractions (e.g., "do" in "don't")
            n't|                     # n't contractions themselves
            \w+(?=')|                # Words before apostrophes (e.g., "I" in "I'm")
            '|                       # Apostrophes as separate tokens
            \w+|                     # Regular words (letters, numbers, underscores)
            [^\w\s]                  # Punctuation marks (anything that's not word chars or whitespace)
        """

    def __init__(self):
        self.compiled_pattern = re.compile(
            self.PATTERN, re.VERBOSE | re.IGNORECASE
        )

    def __call__(self, text: str) -> List[str]:
        """
        Tokenizes text by splitting on punctuation and handling contractions.

        Args:
            text: Input text to tokenize.

        Returns:
            List of tokenized words (lowercase, no punctuation).

        Examples:
            - "I'm fine"      -> ['i', 'm', 'fine']
            - "don't go"      -> ['do', "n't", 'go']
            - "Hello, world!" -> ['hello', 'world']
        """

        tokens = self.compiled_pattern.findall(text)

        return self._clean_tokens(tokens)

    def _clean_tokens(self, raw_tokens: List[str]) -> List[str]:
        """
        Applies some basic post-processing to tokenized messages.

        Args:
            raw_tokens: list of tokens extracted from a message.
        """

        filtered_tokens = [
            token.lower()
            for token in raw_tokens
            if token.strip() and not (len(token) == 1 and not token.isalnum())
        ]

        return filtered_tokens


class ReferencelessEvalPanel:
    def __init__(self, referenceless_metrics: List[ReferenceLessEvalMetrics]):
        self.table = Table(
            title="Quick Evaluation Summary Metrics",
            box=box.ROUNDED,
            show_lines=True,
        )

        self.table.add_column("Dataset", style="yellow", justify="center")
        self.table.add_column(
            "Tool Calls", style="deep_sky_blue1", justify="center"
        )
        self.table.add_column(
            "Successful Tool Calls", style="magenta", justify="center"
        )
        self.table.add_column(
            "Tool Calls Failed due to Schema Mismatch",
            style="deep_sky_blue1",
            justify="center",
        )
        self.table.add_column(
            "Tool Calls Failed due to Hallucination",
            style="magenta",
            justify="center",
        )

        for metric in referenceless_metrics:
            self.table.add_row(
                str(metric.dataset_name),
                str(metric.number_of_tool_calls),
                str(metric.number_of_successful_tool_calls),
                str(metric.number_of_static_failed_tool_calls),
                str(metric.number_of_semantic_failed_tool_calls),
            )

    def print(self):
        console.print(self.table)


# Function to load messages from JSON file
def load_messages(file_path):
    """TODO: replace in favor of TestCaseResources.get_messages(...)"""
    with open(file_path, "r") as f:
        try:
            message_data = json.load(f)
            messages = []
            for msg in message_data:
                messages.append(Message.model_validate(msg))

            return messages

        except Exception as e:
            print(file_path)
            print(e)
            return None


def load_agents_from_disk(agents_path: str):
    agents_json = glob.glob(os.path.join(agents_path, "*.json"))
    agents_yaml = glob.glob(os.path.join(agents_path, "*.yaml"))

    agents = []

    for agent_path in agents_json:
        with open(agent_path, "r") as f:
            agents.append(json.load(f))

    for agent_path in agents_yaml:
        with open(agent_path, "r") as f:
            agents.append(yaml.safe_load(f))

    return agents


def list_run_files(messages_dir: str, dataset_base: str, filter_run: int = -1):
    """
    Returns: dict[run_id] -> {"analyze": path|None, "metrics": path|None}
    (We only need analyze+metrics for this feature.)

    `filter_run` only get gets the runs files for that run. If it is -1, then all run files are retrieved
    For example, if there is `data3.run1.messages.json`, `data3.run2.messages.json`, and filter_run is 2, then,
    the files related to only the second run are retrieved.

    """
    runs = defaultdict(
        lambda: {"analyze": None, "metrics": None, "messages": None}
    )
    for fn in os.listdir(messages_dir):
        m = RUN_FILE_RE.match(fn)
        if not m or m.group("base") != dataset_base:
            continue
        run_id = int(m.group("run"))
        if filter_run != -1 and run_id != filter_run:
            continue

        kind = m.group("kind")
        full = os.path.join(messages_dir, fn)
        if kind == "messages.analyze":
            runs[run_id]["analyze"] = full
        elif kind == "metrics":
            runs[run_id]["metrics"] = full
        elif kind == "messages":
            runs[run_id]["messages"] = full
    return runs


def load_run_metrics(metrics_path: str) -> ToolCallAndRoutingMetrics:
    """Todo remove in a later PR"""
    with open(metrics_path, "r", encoding="utf-8") as f:
        return ToolCallAndRoutingMetrics(**json.load(f))
