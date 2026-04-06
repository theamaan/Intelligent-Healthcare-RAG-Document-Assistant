import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

from backend.app.config import get_settings
from backend.app.core.retriever import get_retriever
from backend.app.rag.pipeline import answer_query


def run_evaluation() -> Path:
    settings = get_settings()
    test_file = Path("data/test_sets/sample_qa.json")
    if not test_file.exists():
        raise FileNotFoundError("Create data/test_sets/sample_qa.json before evaluation.")

    test_items = json.loads(test_file.read_text(encoding="utf-8"))
    rows: list[dict] = []

    for item in test_items:
        doc_id = item["doc_id"]
        question = item["question"]
        ground_truth = item["ground_truth"]

        retriever = get_retriever(doc_id)
        docs = retriever.invoke(question)
        contexts = [d.page_content for d in docs]

        response = answer_query(doc_id, question)

        rows.append(
            {
                "question": question,
                "answer": response.answer,
                "contexts": contexts,
                "ground_truth": ground_truth,
            }
        )

    dataset = Dataset.from_pandas(pd.DataFrame(rows))
    result = evaluate(
        dataset,
        metrics=[faithfulness, context_precision, context_recall, answer_relevancy],
    )

    output = settings.eval_results_dir / f"eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    return output


if __name__ == "__main__":
    path = run_evaluation()
    print(f"Evaluation written to: {path}")
