import json
from datetime import datetime, timezone
from pathlib import Path

from ragas import EvaluationDataset, evaluate
from ragas.dataset_schema import SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness

from backend.app.config import get_settings
from backend.app.core.embeddings import get_embeddings
from backend.app.core.llm_provider import get_llm
from backend.app.core.retriever import get_retriever
from backend.app.rag.pipeline import answer_query

_PLACEHOLDER_DOC_ID = "replace_with_real_doc_id"


def run_evaluation() -> Path:
    settings = get_settings()
    test_file = Path("data/test_sets/sample_qa.json")
    if not test_file.exists():
        raise FileNotFoundError(
            "data/test_sets/sample_qa.json not found. "
            "Add your Q&A pairs before running evaluation."
        )

    test_items = json.loads(test_file.read_text(encoding="utf-8"))
    if not test_items:
        raise ValueError("sample_qa.json is empty. Add Q&A pairs before evaluation.")

    placeholders = [i for i in test_items if i.get("doc_id") == _PLACEHOLDER_DOC_ID]
    if placeholders:
        raise ValueError(
            f"{len(placeholders)} item(s) in sample_qa.json still use the placeholder "
            f"doc_id '{_PLACEHOLDER_DOC_ID}'. Upload your documents first and replace "
            "the placeholder with the actual doc_id returned by POST /upload."
        )

    samples: list[SingleTurnSample] = []
    for item in test_items:
        doc_id = item["doc_id"]
        question = item["question"]
        ground_truth = item["ground_truth"]

        retriever = get_retriever(doc_id)
        docs = retriever.invoke(question)
        contexts = [d.page_content for d in docs]

        response = answer_query(doc_id, question)

        samples.append(
            SingleTurnSample(
                user_input=question,
                response=response.answer,
                retrieved_contexts=contexts,
                reference=ground_truth,
            )
        )

    dataset = EvaluationDataset(samples=samples)
    llm_wrapper = LangchainLLMWrapper(get_llm())
    embeddings_wrapper = LangchainEmbeddingsWrapper(get_embeddings())

    result = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(), ContextPrecision(), ContextRecall(), AnswerRelevancy()],
        llm=llm_wrapper,
        embeddings=embeddings_wrapper,
    )

    result_df = result.to_pandas()
    output_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "per_sample": result_df.to_dict(orient="records"),
    }
    output = (
        settings.eval_results_dir
        / f"eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    )
    output.write_text(json.dumps(output_data, indent=2, default=str), encoding="utf-8")
    return output


if __name__ == "__main__":
    path = run_evaluation()
    print(f"Evaluation written to: {path}")
