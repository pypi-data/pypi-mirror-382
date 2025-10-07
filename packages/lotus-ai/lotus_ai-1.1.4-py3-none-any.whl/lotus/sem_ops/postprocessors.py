import json
from typing import Callable

import lotus
from lotus.types import (
    SemanticExtractPostprocessOutput,
    SemanticFilterPostprocessOutput,
    SemanticMapPostprocessOutput,
)


def cot_postprocessor(llm_answers: list[str]):
    outputs: list[str | None] = []
    explanations: list[str | None] = []
    for llm_answer in llm_answers:
        reasoning_idx = llm_answer.find("Reasoning:\n")
        if reasoning_idx == -1:
            reasoning_idx = 0
        else:
            reasoning_idx += len("Reasoning:\n")

        answer_idx = llm_answer.find("Answer:")
        reasoning = llm_answer[reasoning_idx:answer_idx].rstrip("\n").lstrip("\n")
        answer = llm_answer[answer_idx + len("Answer:") :]

        explanations.append(reasoning)
        outputs.append(answer)

    return outputs, explanations


def deepseek_cot_postprocessor(llm_answers: list[str], for_extract: bool = False):
    """
    Postprocess outputs from DeepSeek models with CoT reasoning.

    Args:
        llm_answers (list[str]): The list of llm answers from DeepSeek.

    Returns:
        Tuple: (outputs, explanations)
    """
    outputs: list[str | None] = []
    explanations: list[str | None] = []

    for llm_answer in llm_answers:
        think_start = llm_answer.find("<think>")
        think_end = llm_answer.find("</think>")

        answer_start = llm_answer.find("Answer:")

        if think_start != -1 and think_end != -1:
            # Extract the reasoning between the <think> tags
            reasoning = llm_answer[think_start + len("<think>") : think_end].strip()
            answer = llm_answer[answer_start + len("Answer:") :].strip()

            answer = answer.strip()

            # If ther is nothing after </think> tag, check if the answer is at the beginning
            if not answer and think_start > 0:
                answer = llm_answer[:think_start].strip()

        else:
            reasoning = ""
            answer = llm_answer.strip()

        explanations.append(reasoning)

        if for_extract:
            try:
                json_obj = json.loads(llm_answer)
            except json.JSONDecodeError:
                lotus.logger.info(f"\t Failed to parse: {llm_answer}")
                json_obj = {}
            json_obj = {key: str(value) for key, value in json_obj.items()}
            outputs.append(json_obj)
        else:
            outputs.append(answer)

    return outputs, explanations


COT_POSTPROCESSORS = {
    "deepseek-r1": deepseek_cot_postprocessor,
    # Add more model-specific postprocessors here
}


def get_cot_postprocessor(model: lotus.models.LM, for_extract: bool = False) -> Callable:
    """
    Returns the appropriate CoT postprocessor for the given model.
    Falls back to standard postprocessor if no specific one is defined.

    Args:
        model (lotus.models.LM): The language model.
        for_extract (bool): Whether to process for extraction (convert to JSON).

    Returns:
        Callable: The appropriate postprocessor function.
    """
    model_name = model.get_model_name()
    for processor_key in COT_POSTPROCESSORS:
        if model_name.startswith(processor_key):
            base_processor = COT_POSTPROCESSORS[processor_key]
            return lambda llm_answers: base_processor(llm_answers, for_extract=for_extract)

    return cot_postprocessor


def map_postprocess(
    llm_answers: list[str],
    model: lotus.models.LM,
    cot_reasoning: bool = False,
) -> SemanticMapPostprocessOutput:
    """
    Postprocess the output of the map operator.

    Args:
        llm_answers (list[str]): The list of llm answers.
        cot_reasoning (bool): Whether there is CoT reasoning.

    Returns:
        SemanticMapPostprocessOutput
    """

    if cot_reasoning:
        postprocessor = get_cot_postprocessor(model)
        outputs, explanations = postprocessor(llm_answers)
    else:
        outputs = llm_answers
        explanations = [None] * len(llm_answers)

    return SemanticMapPostprocessOutput(raw_outputs=llm_answers, outputs=outputs, explanations=explanations)


def extract_postprocess(
    llm_answers: list[str], model: lotus.models.LM, cot_reasoning: bool = False
) -> SemanticExtractPostprocessOutput:
    """
    Postprocess the output of the extract operator to extract the schema.

    Args:
        llm_answers (list[str]): The list of llm answers containging the extract.

    Returns:
        SemanticExtractPostprocessOutput
    """

    if cot_reasoning:
        postprocessor = get_cot_postprocessor(model, for_extract=True)
        extract_data, explanations = postprocessor(llm_answers)
    else:
        extract_data = []
        explanations = [None] * len(llm_answers)

    for llm_answer in llm_answers:
        try:
            output = json.loads(llm_answer)
        except json.JSONDecodeError:
            lotus.logger.info(f"\t Failed to parse: {llm_answer}")
            output = {}

        output = {key: str(value) for key, value in output.items()}
        extract_data.append(output)

    return SemanticExtractPostprocessOutput(raw_outputs=llm_answers, outputs=extract_data, explanations=explanations)


def filter_postprocess(
    llm_answers: list[str],
    model: lotus.models.LM,
    default: bool = True,
) -> SemanticFilterPostprocessOutput:
    """
    Postprocess the output of the filter operator.

    Args:
        llm_answers (list[str]): The list of llm answers.
        default (bool): The default value to use if we fail to parse the answer.
        cot_reasoning (bool): Whether there is CoT reasoning.

    Returns:
        SemanticFilterPostprocessOutput

    """

    def process_outputs(answer):
        if answer is None:
            lotus.logger.info(f"\t Failed to parse {answer}: defaulting to {default}")
            return default

        if "True" in answer:
            return True
        elif "False" in answer:
            return False
        else:
            lotus.logger.info(f"\t Failed to parse {answer}: defaulting to {default}")
            return default

    postprocessor = get_cot_postprocessor(model)
    outputs, explanations = postprocessor(llm_answers)

    boolean_outputs = [process_outputs(answer) for answer in outputs]

    return SemanticFilterPostprocessOutput(raw_outputs=llm_answers, outputs=boolean_outputs, explanations=explanations)
