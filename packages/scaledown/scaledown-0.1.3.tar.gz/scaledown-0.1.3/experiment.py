import argparse
import os
import sys
from dotenv import dotenv_values


from src.tools.llms import LLMProviderFactory

from src.utils import get_absolute_path
from src.data.data_processor import (
    read_json,
    get_questions_from_list,
    get_questions_from_dict,
    load_simpleqa_dataset,
    get_simpleqa_questions,
)


CONFIG = dotenv_values(".env")
google_access_token = CONFIG.get("GOOGLE_API_KEY")
scaledown_api_key = CONFIG.get("SCALEDOWN_API_KEY")


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument(
        "-m",
        "--model",
        type=str,
        help="LLM to use for predictions.",
        default="scaledown-gpt-4o",
        choices=["llama2", "llama2_70b", "llama-65b", "gpt3", "gemini2.5_flash_lite", "scaledown-gpt-4o"],
    )
    argParser.add_argument(
        "-op",
        "--optimizers",
        type=str,
        help="Comma-separated list of prompt optimizers to apply (e.g., 'expert_persona,cot,uncertainty') or 'none' for baseline.",
        default="cove",
    )
    argParser.add_argument(
        "-temp", "--temperature", type=float, help="Temperature.", default=0.0
    )
    argParser.add_argument("-p", "--top-p", type=float, help="Top-p.", default=0.9)

    args = argParser.parse_args()

    # --------------------------------------------------
    # 1. Load dataset (example with simpleqa_small)
    # --------------------------------------------------
    data = load_simpleqa_dataset(get_absolute_path("dataset/simpleqa_small.json"))
    questions = get_simpleqa_questions(data)

    # --------------------------------------------------
    # 2. Setup LLM model
    # --------------------------------------------------

    llm = LLMProviderFactory.create_provider(
        model_id=args.model,
        temperature=args.temperature,
        configuration=CONFIG
    )
    print(f"🤖 Created {llm.get_model_info()['provider']} for model {args.model}")


    # --------------------------------------------------
    # 3. Run prompt optimization (simplified example)
    # --------------------------------------------------
    from src.scaledown.tools.prompt_optimizer import optimize_prompt, parse_optimizers

    optimizers_list = parse_optimizers(args.optimizers)

    # Example: optimize first question
    if questions:
        first_question = questions[0]
        optimized_prompt = optimize_prompt(first_question, optimizers_list)
        print(f"\nOriginal question: {first_question}")
        print(f"\nOptimized prompt: {optimized_prompt}")

        # Get response from LLM
        response = llm.call_llm(optimized_prompt, 100)
        print(f"\nLLM Response: {response}")
