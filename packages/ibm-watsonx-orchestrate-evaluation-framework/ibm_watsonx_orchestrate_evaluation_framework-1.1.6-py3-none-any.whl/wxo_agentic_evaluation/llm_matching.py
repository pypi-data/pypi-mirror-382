from typing import List

from wxo_agentic_evaluation.prompt.template_render import (
    KeywordMatchingTemplateRenderer,
    SemanticMatchingTemplateRenderer,
)
from wxo_agentic_evaluation.service_provider.watsonx_provider import Provider


class LLMMatcher:
    def __init__(
        self,
        llm_client: Provider,
        keyword_template: KeywordMatchingTemplateRenderer,
        semantic_template: SemanticMatchingTemplateRenderer,
    ):
        self.llm_client = llm_client
        self.keyword_template = keyword_template
        self.semantic_template = semantic_template

    def keywords_match(self, response_text: str, keywords: List[str]) -> bool:
        if len(keywords) == 0:
            return True
        # return True if no keywords are provided
        # This allows for skipping keyword check by providing an empty list
        keywords_text = "\n".join(keywords)
        prompt = self.keyword_template.render(
            keywords_text=keywords_text, response_text=response_text
        )
        output: str = self.llm_client.query(prompt)
        result = output.strip().lower()
        return result.startswith("true")

    def semantic_match(
        self, context: str, prediction: str, ground_truth: str
    ) -> bool:
        """Performs semantic matching for the agent's final response and the expected response using the starting sentence of the conversation as the context

        Args:
            context: The starting sentence of the conversation. TODO can also consider using the LLM user's story
            prediction: the predicted string
            ground_truth: the expected string

        Returns:
            a boolean indicating if the sentences match.
        """
        prompt = self.semantic_template.render(
            context=context, expected_text=ground_truth, actual_text=prediction
        )
        output: str = self.llm_client.query(prompt)
        result = output.strip().lower()
        return result.startswith("true")
