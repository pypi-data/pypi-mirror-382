import json
import os
import re
import time
import traceback
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import rich
from jsonargparse import CLI
from rich import box
from rich.rule import Rule
from rich.console import Group, Console
from rich.panel import Panel
from rich.progress import Progress
from rich.style import Style
from rich.table import Table
from rich.text import Text

from wxo_agentic_evaluation.arg_configs import AnalyzeConfig, AnalyzeMode
from wxo_agentic_evaluation.description_quality_checker import (
    DescriptionQualityInspector,
)
from wxo_agentic_evaluation.metrics.metrics import (
    EnhancedAnalyzeMetrics,
    TextMatchType,
    ToolCallAndRoutingMetrics,
    DescriptionQualityMetric,
    DescriptionQuality,
)
from wxo_agentic_evaluation.referenceless_eval import ReferencelessEvaluation
from wxo_agentic_evaluation.type import (
    ContentType,
    ExtendedMessage,
    ToolDefinition,
)
from wxo_agentic_evaluation.utils import (
    ReferencelessEvalParser,
    TestCaseResources,
    ToolExtractionOpenAIFormat,
    add_line_seperator,
    list_run_files,
    load_run_metrics,
    N_A,
)

MODEL_ID = "meta-llama/llama-3-405b-instruct"
GATE_TOOL_ENRICHMENTS = (
    os.getenv("GATE_TOOL_ENRICHMENTS", "true").lower().strip() == "true"
)
LOCK = Lock()


class AnalyzerBase(ABC):
    @abstractmethod
    def analyze(self, config: AnalyzeConfig):
        pass

    @abstractmethod
    def render(self):
        pass

    def _is_failed_tool_call(self, message: ExtendedMessage):
        if message.reason and message.message.type == ContentType.tool_call:
            if (
                reason := message.reason.get("reason")
            ) and reason != "irrelevant tool call":
                return True

    def _single_run(
        self, test_case_name, run_map, test_cases_resource: TestCaseResources
    ):
        if not run_map:
            # Legacy single-run files
            test_messages, meta = test_cases_resource.get_analyze_messages(
                test_case_name=test_case_name
            )
            metrics: ToolCallAndRoutingMetrics = (
                test_cases_resource.get_test_metrics(
                    test_case_name=test_case_name
                )
            )
        else:
            run_id = next(iter(run_map))
            paths = run_map[run_id]
            metrics = test_cases_resource.get_test_metrics(
                path=paths["metrics"]
            )
            test_messages, meta = test_cases_resource.get_analyze_messages(
                path=paths["analyze"]
            )

        # --- compute status uniformly (legacy & run1) ---
        runs_problematic = self._is_failed_test_case(metrics)

        return test_messages, meta, metrics, runs_problematic

    def _is_failed_test_case(self, data) -> bool:
        """
        True -> test case failed
        False -> test success
        """

        # not ideal if statement
        # in the future, refactor so this if statement is not needed
        # this if statement is needed because this function is called in two cases:
        # 1. if data is an instance ToolCallAndRoutingMetrics
        # 2. if data is a row in the summary table (dictionary)

        # ideal the SummaryMetrics should be parsed into pydantic class as well

        if isinstance(data, ToolCallAndRoutingMetrics):
            is_success = data.is_success
            had_incorrect_param = data.tool_calls_with_incorrect_parameter > 0
            low_precision = float(data.tool_call_precision) < 1.0
            low_recall = float(data.tool_call_recall) < 1.0
        else:
            is_success = str(data["is_success"]).strip().lower() == "true"
            had_incorrect_param = (
                float(data.get("tool_calls_with_incorrect_parameter", 0) or 0)
                > 0
            )
            low_precision = float(data.get("tool_call_precision", 1) or 1) < 1.0
            low_recall = float(data.get("tool_call_recall", 1) or 1) < 1.0

        return (
            not is_success or had_incorrect_param or low_precision or low_recall
        )

    def _get_test_case_with_failed_tools(self, summary) -> List[str]:
        test_case_with_failed_tools = []

        for entry in summary:
            test_case_name = entry["dataset_name"]

            if test_case_name.lower().strip() == "summary (average)":
                continue

            if self._is_failed_test_case(entry):
                test_case_with_failed_tools.append(entry)

        return test_case_with_failed_tools


class DescriptionQualityAnalyzer(AnalyzerBase):
    def __init__(self):
        self.analysis_cache: Dict[str, DescriptionQualityMetric] = {}
        # tool_name -> description analysis
        self.missing_tools = set()
        self.tools_not_found = set()

    def _get_tools_not_found_in_source(
        self,
        tools_to_analyze: List[str],
        failing_tool_definitions: List[ToolDefinition],
    ) -> Set[str]:

        return set(tools_to_analyze) - {
            tool_def.tool_name for tool_def in failing_tool_definitions
        }

    def _failing_tool_from_messages(self, messages: List[ExtendedMessage]):
        failed_tool_calls = set()
        for message in messages:
            if self._is_failed_tool_call(message):
                content = json.loads(message.message.content)
                tool_call_name = content["name"]
                failed_tool_calls.add(tool_call_name)

        return failed_tool_calls

    def failing_tools(self, data_path):
        messages_dir = os.path.join(data_path, "messages")
        test_case_resources = TestCaseResources(data_path)
        processed_test_cases = set()
        failed_tool_calls = set()

        for test_case in test_case_resources.get_summary:
            dataset_name = test_case["dataset_name"]
            if dataset_name in processed_test_cases:
                continue
            processed_test_cases.add(dataset_name)

            run_map = list_run_files(messages_dir, test_case["dataset_name"])

            if not run_map:
                test_messages, _ = test_case_resources.get_analyze_messages(
                    test_case_name=dataset_name
                )
                failed_tool_calls.update(
                    self._failing_tool_from_messages(test_messages)
                )

            else:
                for paths in run_map.values():
                    test_messages, _ = test_case_resources.get_analyze_messages(
                        path=paths["analyze"]
                    )
                    failed_tool_calls.update(
                        self._failing_tool_from_messages(test_messages)
                    )

        return failed_tool_calls

    def analyze_failing_tool_description_quality(
        self,
        inspector: DescriptionQualityInspector,
        tool_definition_path: str,
        failing_tools: Set[str],
    ) -> Tuple[List[DescriptionQualityMetric], List[str]]:
        """
        :param tool_definition_path: Path to the tool definition file.
        :param failing_tools: Set of tool names that failed.
        :return: A tuple where the first item in the tuple is List[DescriptionQualityMetric] for failed tools that were analyzed,
        the second item in the list is a list of missing tools
        """

        failing_tool_definitions: List[ToolDefinition] = (
            inspector.extract_tool_desc_from_tool_source(
                Path(tool_definition_path),
                failing_tools,
            )
        )

        if not failing_tool_definitions:
            """
            No tool definitions(with '@tool' decorators) for failed tools: '{tools_to_analyze}' found in the file: '{tool_definition_path}'"
            """
            with Lock:
                self.tools_not_found.add(failing_tools)

        missing_tools = self._get_tools_not_found_in_source(
            failing_tools, failing_tool_definitions
        )
        for tool_definition in failing_tool_definitions:
            tool_analysis = inspector.detect_bad_description(tool_definition)
            with LOCK:
                self.analysis_cache[tool_definition.tool_name] = tool_analysis
                self.missing_tools.update(missing_tools)

        return 1

    def analyze(self, config):
        failing_tools = self.failing_tools(config.data_path)
        inspector = DescriptionQualityInspector()
        tool_definition_path = config.tool_definition_path

        with ThreadPoolExecutor(
            max_workers=config.num_workers, thread_name_prefix="[Worker]"
        ) as pool:
            futures = [
                pool.submit(
                    self.analyze_failing_tool_description_quality,
                    inspector,
                    tool_definition_path,
                    [failing_tool],
                )
                for failing_tool in failing_tools
            ]

            if futures:
                with Progress() as progress:
                    task = progress.add_task(
                        f"[purple]Analyzing description quality for {len(futures)} tasks...",
                        total=len(futures),
                    )
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception:
                            traceback.print_exc()
                        finally:
                            progress.update(task, advance=1)

    def render(self):
        raise NotImplementedError("Not implemented")


class Analyzer(AnalyzerBase):
    def __init__(
        self,
        enhanced_metrics: Optional[List[EnhancedAnalyzeMetrics]] = None,
        description_quality_analyzer: DescriptionQualityAnalyzer = None,
    ):
        self.enhanced_metrics = enhanced_metrics
        self.enhanced_metrics_idx_map = {}

        if self.enhanced_metrics:
            # do some post-processing on the enhanced metrics
            # create a mapping between test case name and index
            if self.enhanced_metrics:
                for idx, metric in enumerate(self.enhanced_metrics):
                    self.enhanced_metrics_idx_map[metric.test_case_name] = idx

        self.description_quality_analyzer = description_quality_analyzer

    @staticmethod
    def _generate_style_config():
        return Style(
            color="magenta",
            blink=True,
            bold=True,
        )

    def _parse_enhanced_metrics(self, test_case_name) -> Optional[Table]:
        table = Table(
            box=box.ROUNDED,
            show_lines=True,
        )

        columns = [
            "Tool Name",
            "Root Cause Analysis",
            "Docstring Recommendations",
        ]

        rows = []

        if (
            self.enhanced_metrics
            and (index := self.enhanced_metrics_idx_map.get(test_case_name))
            is not None
        ):
            enhanced_metric: EnhancedAnalyzeMetrics = self.enhanced_metrics[
                index
            ]

            for idx, tool_call in enumerate(enhanced_metric.tool_names):
                static_root_causes = []
                parsed_tool_annotations = []
                param_annotations = defaultdict(list)

                row = [tool_call]

                # if this is true, then there are no semantic metrics
                static_root_causes = [
                    Text(item.explanation)
                    for item in enhanced_metric.static_metrics[idx]
                ]

                static_root_causes = Text().join(static_root_causes)

                # Parameter Root Cause
                parameter_annotations = enhanced_metric.parameter_annotations[
                    idx
                ]
                formatted_param_root_cause = [
                    Text(metric.explanation) for metric in parameter_annotations
                ]
                formatted_param_root_cause = Text().join(
                    formatted_param_root_cause
                )

                # Tool Root Cause
                tool_annotations = enhanced_metric.tool_annotations[idx]
                formatted_tool_root_cause = [
                    Text(metric.explanation) for metric in tool_annotations
                ]
                formatted_tool_root_cause = Text().join(
                    formatted_tool_root_cause
                )

                if formatted_param_root_cause or formatted_tool_root_cause:
                    root_cause = (
                        formatted_tool_root_cause
                        if len(formatted_tool_root_cause)
                        > len(formatted_param_root_cause)
                        else formatted_param_root_cause
                    )
                elif static_root_causes:
                    root_cause = static_root_causes
                else:
                    root_cause = N_A

                row.append(root_cause)

                # Parameter Level Docstring
                for metric in parameter_annotations:
                    if annotations := metric.annotations:
                        for annotation in annotations:
                            param_annotations[annotation.parameter_name].append(
                                f"[b][i][cyan]{annotation.quote}[/b][/i][/cyan]"
                            )

                newline = "\n"
                param_annotations = [
                    f"- [b]{param_name}:[/b] {newline.join(doc_string)}"
                    for param_name, doc_string in param_annotations.items()
                ]
                param_annotations = "\n".join(param_annotations)

                # Tool Level Docstring
                for metric in tool_annotations:
                    if annotations := metric.annotations:
                        for annotation in annotations:
                            parsed_tool_annotations.append(
                                f"[b][i][cyan]{annotation.quote}[/b][/i][/cyan]"
                            )
                parsed_tool_annotations = "\n".join(parsed_tool_annotations)
                docstring_cell = Table(
                    show_lines=False, show_header=False, box=None
                )
                add_divider = False

                # - Gate the Doc String Enrichments.
                # - Ensure the environment variable is enabled.
                if GATE_TOOL_ENRICHMENTS and self.description_quality_analyzer:
                    # check if tool in cache
                    tool_description_analysis = (
                        self.description_quality_analyzer.analysis_cache.get(
                            tool_call
                        )
                    )
                    is_missing_tool = (
                        tool_call
                        in self.description_quality_analyzer.missing_tools
                    )  # tool call not in tool_definition_path
                    # failed tool call that failed to get extracted from the tool_definition_path because of missing `@tool` decorator
                    # TODO: figure out if this edge is needed? taken from original Analyze implementation
                    tool_not_found = (
                        tool_call
                        in self.description_quality_analyzer.tools_not_found
                    )

                    # If the tool_call is in `missing_tools`, don't show the annotations
                    if is_missing_tool or tool_not_found:
                        parsed_tool_annotations = []
                        param_annotations = []

                    if tool_description_analysis is not None:
                        if (
                            tool_description_analysis.description_quality
                            == DescriptionQuality.GOOD
                        ):
                            parsed_tool_annotations = []
                            param_annotations = []
                    else:
                        print("cache miss: ", tool_call)

                if not parsed_tool_annotations and not param_annotations:
                    docstring_cell.add_row(N_A)
                if parsed_tool_annotations:
                    docstring_cell.add_row(
                        "[b]Tool Docstrings", parsed_tool_annotations
                    )
                    add_divider = True
                if param_annotations:
                    if add_divider:
                        docstring_cell.add_row(Rule(characters="--"))
                    docstring_cell.add_row(
                        "[b]Parameter Docstrings", param_annotations
                    )

                row.append(docstring_cell)
                rows.append(row)

        is_empty = not any(rows)
        if is_empty:
            return None

        for idx, column in enumerate(columns):
            table.add_column(column)

        for row in rows:
            table.add_row(*row)

        return table

    def render(
        self,
        data: List[ExtendedMessage],
        tool_definition_path: Optional[str],
        meta: Optional[dict] = None,
        test_case_name=None,
    ) -> Group:
        """
        Render the conversation history and analysis results.
        :param data: List of ExtendedMessage objects containing the conversation history.
        :param tool_definition_path: Path to the tool definition file.
        :return: A rich Group object containing the conversation and analysis results.
        """
        conversation_lines = []
        reason_lines = []
        failing_tools = []
        added_missed_header = False

        for entry in data:
            msg = entry.message
            role = msg.role
            content = msg.content
            reason = entry.reason
            tool_name = None
            if (
                msg.type == ContentType.tool_call
                or msg.type == ContentType.tool_response
            ):
                tool_name = json.loads(msg.content)["name"]

            if role == "user":
                label = "👤 User"
            elif role == "assistant" and msg.type == ContentType.tool_call:
                if reason:
                    label = "❌ Tool Call"

                    if reason.get("reason") == "incorrect parameter":
                        failing_tools.append(
                            tool_name
                        )  # create a list of failing tools for description quality analysis.
                else:
                    label = "✅ Tool Call"
            elif role == "assistant":
                label = "🤖 Assistant"
            else:
                label = "📦 Unknown"

            text_line = Text(f"{label}: {content}\n")
            if reason:
                text_line.stylize("bold red")
                reason_text = f"❌ {tool_name}: {json.dumps(reason)}\n\n"
                reason_lines.append(Text(reason_text, style="red"))
            conversation_lines.append(text_line)

        if meta:
            missed = meta.get("missed_tool_calls") or []
            if missed:
                if not added_missed_header:
                    reason_lines.append(
                        Text("\nMissed Calls:\n", style="bold red")
                    )
                    added_missed_header = True
                for tool in missed:
                    reason_lines.append(Text(f"❌ {tool}\n", style="red"))

        conversation_panel = Panel(
            Text().join(conversation_lines),
            title="Conversation History",
            border_style="bold deep_sky_blue2",
        )
        reason_panel = Panel(
            Text().join(reason_lines),
            box=box.ROUNDED,
            title=f"[bold red]Tool Call Errors[/bold red]",
            border_style="bold red",
        )
        table = self._parse_enhanced_metrics(test_case_name=test_case_name)
        if table:
            group = Group(conversation_panel, reason_panel, table)
        else:
            group = Group(conversation_panel, reason_panel)

        return group

    def analyze(self, config: AnalyzeConfig):
        """
        Analyze the results of the tool calls and routing metrics.
        :param config: AnalyzeConfig object containing user provided paths for analysis.
        """

        test_case_resources = TestCaseResources(config.data_path)
        summary = test_case_resources.get_summary

        test_case_with_failed_tools = self._get_test_case_with_failed_tools(
            summary=summary
        )

        output_panels = []

        if len(test_case_with_failed_tools) == 0:
            header_table = Table(show_header=False, box=None)

            header_table.add_row("No Tool Call Error found!")

            panel = Panel(
                header_table,
                title="[bold green]📋 Analysis Summary[/bold green]",
            )

            output_panels.append(panel)

        messages_dir = os.path.join(config.data_path, "messages")

        RUN_NAME_ONLY_RE = re.compile(r"^(?P<parent>.+)\.run(?P<id>\d+)$")
        processed_parents: Set[str] = set()

        overall_runs_performed = 0
        overall_runs_problematic = 0
        overall_text_match_hits = 0
        overall_text_match_den = 0
        overall_journey_vals = []

        for test_case_entry in summary:
            dataset_base = test_case_entry["dataset_name"]

            # If CSV row looks like "<parent>.runN" and we have runs on disk for <parent>, skip the per-run row.
            m = RUN_NAME_ONLY_RE.match(dataset_base)
            if m:
                parent = m.group("parent")
                if list_run_files(messages_dir, parent):
                    continue

            # Avoid processing a parent twice if it appears multiple times in CSV.
            if dataset_base in processed_parents:
                continue

            run_map = list_run_files(messages_dir, dataset_base, config.run)

            # ---- SINGLE RUN (legacy or run1 only) ----
            if not run_map or len(run_map) == 1:
                runs_performed = 1
                test_messages, meta, metrics, runs_problematic = (
                    self._single_run(
                        test_case_name=dataset_base,
                        run_map=run_map,
                        test_cases_resource=test_case_resources,
                    )
                )

                processed_parents.add(dataset_base)

                # ✅ Dataset-level panel (print BEFORE details)
                ds_table = Table(show_header=False, box=None)
                ds_table.add_row("Type: Single-run")
                status = (
                    "❌ Problematic" if runs_problematic else "✅ No problems"
                )
                ds_table.add_row(f"Status: {status}")
                # Update overall counters/averages
                overall_runs_performed += runs_performed
                overall_runs_problematic += runs_problematic
                tm = getattr(metrics, "text_match", None)
                tm_val = getattr(tm, "value", None) if tm else None

                if tm_val is not None and tm_val != TextMatchType.na:
                    overall_text_match_den += 1
                    overall_text_match_hits += (
                        tm_val == TextMatchType.text_match
                    )
                if getattr(metrics, "is_success", None) is not None:
                    overall_journey_vals.append(
                        1 if bool(metrics.is_success) else 0
                    )

                header_group = Group(
                    *[
                        ds_table,
                        self._create_header_analysis_panel(
                            dataset_base, metrics
                        ),
                    ],
                )
                border_style = "bold red" if runs_problematic else "bold green"
                header_panel = Panel(
                    header_group,
                    title=f"[b]📋 Analysis Summary — {dataset_base}[/b]",
                    border_style=border_style,
                )
                output_panels.append(header_panel)

                if runs_problematic:
                    output_panels.append(
                        self.render(
                            test_messages,
                            config.tool_definition_path,
                            meta,
                            test_case_name=dataset_base,
                        )
                    )
                    output_panels.append(
                        add_line_seperator(
                            self._generate_style_config(), print=False
                        )
                    )

                else:
                    output_panels.append(
                        add_line_seperator(
                            self._generate_style_config(), print=False
                        )
                    )

                continue

            # ---- MULTI RUN (two-pass: compute first, then print summary, then details) ----
            processed_parents.add(dataset_base)
            runs_performed = len(run_map)
            runs_problematic = 0
            text_match_hits = 0
            text_match_den = 0
            journey_vals = []

            # First pass: compute aggregates and collect problematic runs to replay later
            deferred_runs = []
            for run_id in sorted(run_map):
                paths = run_map[run_id]
                if not paths["metrics"]:
                    runs_problematic += 1
                    # no analyze file to replay; still counted as problematic
                    continue

                metrics = load_run_metrics(paths["metrics"])

                # Aggregate for per-dataset
                tm = getattr(metrics, "text_match", None)
                tm_val = getattr(tm, "value", None) if tm is not None else None
                if tm_val is not None and tm_val != TextMatchType.na.value:
                    text_match_den += 1
                    text_match_hits += tm_val == TextMatchType.text_match.value

                if getattr(metrics, "is_success", None) is not None:
                    journey_vals.append(1 if bool(metrics.is_success) else 0)

                # Decide if problematic
                had_incorrect_param = (
                    hasattr(metrics, "tool_calls_with_incorrect_parameter")
                    and float(metrics.tool_calls_with_incorrect_parameter or 0)
                    > 0
                )
                low_precision = (
                    hasattr(metrics, "tool_call_precision")
                    and float(
                        metrics.tool_call_precision
                        if metrics.tool_call_precision is not None
                        else 1.0
                    )
                    < 1.0
                )
                low_recall = (
                    hasattr(metrics, "tool_call_recall")
                    and float(
                        metrics.tool_call_recall
                        if metrics.tool_call_recall is not None
                        else 1.0
                    )
                    < 1.0
                )

                is_problem = (
                    (hasattr(metrics, "is_success") and not metrics.is_success)
                    or had_incorrect_param
                    or low_precision
                    or low_recall
                )
                if is_problem:
                    runs_problematic += 1
                    deferred_runs.append(
                        {
                            "title": f"{dataset_base}.run{run_id}",
                            "metrics": metrics,
                            "analyze_path": paths.get("analyze"),
                        }
                    )

            # Second pass: now replay only the problematic runs (so summary stays at the top)
            for item in deferred_runs:
                ds_table = Table(show_header=False, box=None)
                ds_table.add_row(f"Type: Multi-run ({runs_performed} runs)")
                ds_table.add_row(
                    f"Runs with problems: {runs_problematic} / {runs_performed}"
                )
                status = (
                    "❌ Problematic"
                    if runs_problematic > 0
                    else "✅ No problems"
                )
                ds_table.add_row(f"Status: {status}")
                header_table = self._create_header_analysis_panel(
                    item["title"], item["metrics"]
                )

                group = Group(*[ds_table, header_table])
                output_panels.append(
                    Panel(
                        group,
                        title=f"📋 Analysis Summary — {dataset_base}",
                        border_style="green",
                    )
                )

                if item["analyze_path"]:
                    with open(item["analyze_path"], "r", encoding="utf-8") as f:
                        raw = json.load(f)
                    meta = {}
                    if raw and isinstance(raw[-1], dict) and "meta" in raw[-1]:
                        meta = raw[-1]["meta"]
                        raw = raw[:-1]
                    test_messages = [ExtendedMessage(**entry) for entry in raw]

                    output_panels.append(
                        self.render(
                            test_messages, config.tool_definition_path, meta
                        )
                    )
                output_panels.append(
                    add_line_seperator(
                        self._generate_style_config(), print=False
                    )
                )

            # Update overall aggregates
            overall_runs_performed += runs_performed
            overall_runs_problematic += runs_problematic
            overall_text_match_hits += text_match_hits
            overall_text_match_den += text_match_den
            overall_journey_vals.extend(journey_vals)

        # --- Overall summary ---
        overall_lines = [
            f"Test cases analyzed: {len(processed_parents)}",
            f"Total runs executed: {overall_runs_performed}",
            f"Problematic runs: {overall_runs_problematic} ({round((overall_runs_problematic/overall_runs_performed)*100,1) if overall_runs_performed else 0}%)",
        ]

        if overall_text_match_den:
            tm_pct = round(
                (overall_text_match_hits / overall_text_match_den) * 100, 2
            )
            overall_lines.append(f"Avg text-match success: {tm_pct}%")
        else:
            overall_lines.append("Avg text-match success: N/A")

        if overall_journey_vals:
            js_pct = round(
                (sum(overall_journey_vals) / len(overall_journey_vals)) * 100, 2
            )
            overall_lines.append(f"Avg journey success: {js_pct}%")
        else:
            overall_lines.append(f"Avg journey success: N/A")

        output_panels.append(
            Panel(
                Text("\n".join(overall_lines)),
                title="📋 Overall Summary",
                border_style="cyan",
            )
        )

        console = Console()
        with console.pager(styles=True):
            for panel in output_panels:
                console.print(panel, overflow="crop")

    def _create_header_analysis_panel(
        self, test_case_name: str, metrics: ToolCallAndRoutingMetrics
    ) -> Panel:
        header_table = Table(show_header=False, box=None)

        header_table.add_row(f"Test Case Name: {test_case_name}")
        header_table.add_row(
            f"Expected Tool Calls: {metrics.expected_tool_calls}"
        )
        header_table.add_row(
            f"Correct Tool Calls: {metrics.correct_tool_calls}"
        )
        header_table.add_row(f"Text Match: {metrics.text_match.value}")
        header_table.add_row(f"Journey Success: {metrics.is_success}")

        return header_table


class AnalyzerEnhanced(AnalyzerBase):
    PARAMETER_DOCUMENTATION = "PARAMETER_DOCUMENTATION"
    TOOL_USAGE_EXAMPLES = "TOOL_USAGE_EXAMPLES"
    TOOL_DOCUMENTATION = "TOOL_DOCUMENTATION"

    DEFAULT_GENERATION_PARAMS = {
        "min_new_tokens": 0,
        "decoding_method": "greedy",
        "max_new_tokens": 10_000,
        "random_seed": 42,
    }

    def __init__(self):
        super().__init__()

    def _deduplicate_tool_call_failures(self, messages: List[ExtendedMessage]):
        """If there are multiple failures from the same tool, then choose the failure that occurs later in the trajectory

        ex.
        1. Tool A fails
        2. Tool A Error response
        3. Tool A call again which fails
        4. Tool A error response

        For the analysis, we analyze the second time the tool call fails, with the previous messages serving as context.

        """
        tool_indices = []
        seen_tools = set()

        for idx, message in enumerate(reversed(messages)):
            if self._is_failed_tool_call(message):
                content = json.loads(message.message.content)
                tool_call_name = content["name"]
                if tool_call_name not in seen_tools:
                    seen_tools.add(tool_call_name)
                    tool_indices.append(len(messages) - 1 - idx)

        return sorted(tool_indices)

    def process_messages(self, task_name, test_case, tools, messages):
        eval = ReferencelessEvaluation(
            api_spec=tools,
            model_id=MODEL_ID,
            task_n=task_name,
            dataset_name=test_case,
            runtime_pipeline=False,
            generation_params=AnalyzerEnhanced.DEFAULT_GENERATION_PARAMS,
        )

        processed_data = [
            {
                k: msg.model_dump().get(k)
                for k in ["role", "content", "type"]
                if k in msg.model_dump()
            }
            for msg in messages
        ]

        context = processed_data[:-1]
        tool_call = processed_data[
            -1
        ]  # assume that the message is the last tool call
        tool_call_msg = json.loads(tool_call["content"])
        call = ReferencelessEvaluation.fmt_tool_call(
            tool_id=tool_call_msg.get("id", "1"),
            tool_call_name=tool_call_msg["name"],
            arguments=json.dumps(tool_call_msg["args"]),
            context=context,
        )
        return test_case, eval.run([call])

    def _extract_semantic_metrics(
        self, metrics_dictionary, annotation_filters: Optional[List[str]]
    ):
        semantic_analysis = []
        for metric_data in metrics_dictionary.values():
            raw_response = metric_data.get("raw_response")
            if raw_response is None:
                continue

            is_correct = metric_data.get("is_correct", False)
            if is_correct:
                continue

            failed_semantic_test_case = ReferencelessEvalParser.semantic_parser(
                metric_name=metric_data.get("metric_name"),
                data=raw_response,
                annotation_filters=annotation_filters,
            )

            semantic_analysis.append(failed_semantic_test_case)

        return semantic_analysis

    def tool_enrichment_view(self, results):
        enhanced_metrics = []
        tool_enrichment_metrics = defaultdict(list)
        for result in results:
            for test_case, eval_results in result.items():
                for result in eval_results:
                    # for metric in result:
                    failed_static_metrics = []
                    parameter_annotations = []
                    tool_annotations = []

                    static_metrics_passed = result.get("static", {}).get(
                        "final_decision", False
                    )
                    tool_call_obj = result.get("inputs", {}).get(
                        "tool_call", {}
                    )

                    if static_metrics_passed:
                        semantic_metrics = result.get("semantic")
                        function_selection_metrics = semantic_metrics.get(
                            "function_selection", {}
                        ).get("metrics", {})
                        tool_annotations = self._extract_semantic_metrics(
                            function_selection_metrics,
                            [
                                AnalyzerEnhanced.TOOL_DOCUMENTATION,
                                AnalyzerEnhanced.TOOL_USAGE_EXAMPLES,
                            ],
                        )

                        general_metrics = semantic_metrics.get(
                            "general", {}
                        ).get("metrics", {})
                        parameter_annotations = self._extract_semantic_metrics(
                            general_metrics,
                            [AnalyzerEnhanced.PARAMETER_DOCUMENTATION],
                        )
                    else:
                        static_metrics = result.get("static").get("metrics")
                        failed_static_metrics = (
                            ReferencelessEvalParser.static_parser(
                                static_metrics=static_metrics
                            )
                        )

                    parsed_metrics = {
                        "tool_name": tool_call_obj.get("function", {}).get(
                            "name"
                        ),
                        "parameter_annotations": parameter_annotations,
                        "tool_annotations": tool_annotations,
                        "static_metrics": failed_static_metrics,
                    }
                    tool_enrichment_metrics[test_case].append(parsed_metrics)

        for test_case, metrics in tool_enrichment_metrics.items():
            failed_tools = [metric["tool_name"] for metric in metrics]
            parameter_annotations = [
                metric["parameter_annotations"] for metric in metrics
            ]
            tool_annotation = [metric["tool_annotations"] for metric in metrics]
            static_metrics = [metric["static_metrics"] for metric in metrics]

            # don't add to final metrics array if there were no annotations
            if (
                not any(parameter_annotations)
                and not any(tool_annotation)
                and not any(static_metrics)
            ):
                continue

            enhanced_metrics.append(
                EnhancedAnalyzeMetrics(
                    test_case_name=test_case,
                    parameter_annotations=parameter_annotations,
                    tool_annotations=tool_annotation,
                    tool_names=failed_tools,
                    static_metrics=static_metrics,
                )
            )

        return enhanced_metrics

    def analyze(
        self, config: AnalyzeConfig
    ) -> Optional[List[EnhancedAnalyzeMetrics]]:
        start = time.time()
        all_tools = ToolExtractionOpenAIFormat.from_path(
            config.tool_definition_path
        )
        messages_dir = os.path.join(config.data_path, "messages")
        test_case_resources = TestCaseResources(config.data_path)

        failed_test_cases = {}
        for test_case in test_case_resources.get_summary:
            if test_case["dataset_name"] in failed_test_cases:
                continue
            run_map = list_run_files(
                messages_dir, test_case["dataset_name"], config.run
            )
            if run_map and config.run == -1:
                rich.print(
                    "[red]Enhanced Mode only operates on a single run for a dataset. Since there are multiple runs, set the `--run` flag to the specific run for enhanced analysis."
                )
                # run the first run in the config map
                rich.print(
                    f"[b]Defaulting to run {next(iter(run_map))} to analyze for {test_case['dataset_name']}"
                )
                config.run = next(iter(run_map))
                run_map = {config.run: run_map.get(config.run)}

            _, _, _, run_problematic = self._single_run(
                test_case["dataset_name"], run_map, test_case_resources
            )
            if run_problematic:
                if run_files := run_map.get(config.run):
                    failed_test_cases[test_case["dataset_name"]] = run_files

                else:
                    # legacy runs without n runs
                    # tranform the legacy runs into the same data structure from `list_files`

                    messages_path = os.path.join(
                        test_case_resources.output_dir,
                        "messages",
                        f"{test_case['dataset_name']}.messages.json",
                    )

                    analyze_path = os.path.join(
                        test_case_resources.output_dir,
                        "messages",
                        f"{test_case['dataset_name']}.messages.analyze.json",
                    )

                    metrics_path = os.path.join(
                        test_case_resources.output_dir,
                        "messages",
                        f"{test_case['dataset_name']}.metrics.json",
                    )

                    failed_test_cases[test_case["dataset_name"]] = {
                        "analyze": analyze_path,
                        "messages": messages_path,
                        "metrics": metrics_path,
                    }

        max_workers = config.num_workers
        rich.print(
            f"[bold green]INFO:[/bold green] Number of workers set to: {max_workers}"
        )

        jobs = []

        with ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="[Worker]"
        ) as pool:
            aggregate_results = []
            for test_case, file_mapping in failed_test_cases.items():
                analyze_messages, _ = test_case_resources.get_analyze_messages(
                    path=file_mapping["analyze"]
                )
                idx_failed_tool_calls = self._deduplicate_tool_call_failures(
                    analyze_messages
                )
                messages = test_case_resources.get_messages(
                    path=file_mapping["messages"]
                )

                for idx in idx_failed_tool_calls:
                    jobs.append(
                        {
                            "task_name": f"{test_case}-0-{idx + 1}",
                            "test_case": test_case,
                            "tools": all_tools,
                            "messages": messages[0 : idx + 1],
                        }
                    )
            jobs = sorted(jobs, key=lambda x: len(x["messages"]))
            futures = [
                pool.submit(
                    self.process_messages,
                    job["task_name"],
                    job["test_case"],
                    job["tools"],
                    job["messages"],
                )
                for job in jobs
            ]

            if futures:
                with Progress() as progress:
                    task = progress.add_task(
                        f"[purple]Evaluating {len(futures)} tasks...",
                        total=len(futures),
                    )
                    for future in as_completed(futures):
                        try:
                            test_case, results = future.result()
                            aggregate_results.append({test_case: results})
                        except Exception as e:
                            rich.print(
                                f"test case, {test_case} ,fails with {e}"
                            )
                            traceback.print_exc()
                        finally:
                            progress.update(task, advance=1)

            enhanced_metrics = self.tool_enrichment_view(aggregate_results)
            end = time.time()
            rich.print(f"Enhanced Analysis took {end - start} s")

            return enhanced_metrics

    def render(self):
        raise NotImplementedError("Not implemented")


def run(args):
    d = DescriptionQualityAnalyzer()
    if args.mode == AnalyzeMode.enhanced:
        if GATE_TOOL_ENRICHMENTS:
            d.analyze(args)

        enhanced = AnalyzerEnhanced()
        enhanced_metrics = enhanced.analyze(config=args)
        dummy_analyzer = Analyzer(enhanced_metrics, d)
        dummy_analyzer.analyze(args)

    else:
        dummy_analyzer = Analyzer()
        dummy_analyzer.analyze(args)


if __name__ == "__main__":
    args = CLI(AnalyzeConfig, as_positional=False)
    run(args)
