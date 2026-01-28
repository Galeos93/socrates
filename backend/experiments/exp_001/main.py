from dataclasses import asdict
import json
from pydoc import doc
from typing import List, Dict
import uuid

from opik import Opik
import opik
from openai import OpenAI

from experiments.exp_001.dataset import DOCUMENTS_DATASET
from experiments.common.metrics.knowledge_unit_gen_rule import KnowledgeUnitGenerationRule
from domain.entities.learning import KnowledgeUnit
from domain.entities.document import Document
from infrastructure.adapters.knowledge_unit_generation.llm.service import LLMKnowledgeUnitGenerationService

EXPERIMENT_NAME = "exp_001_knowledge_unit_generation_evaluation"
DATASET_NAME = "KU_GEN_TEXT_ANALYSIS"

# Configure Opik
opik.configure()

# Get or create a dataset
client = Opik()

# OpenAI client
openai_client =OpenAI()

ku_generation_service = LLMKnowledgeUnitGenerationService(
    client=openai_client,
    model="gpt-4o",
)

dataset = client.get_or_create_dataset(name=DATASET_NAME)
# Remove 'id' field before inserting - Opik will auto-generate UUIDs
cleaned_documents = [
    {k: v for k, v in asdict(doc).items() if k != 'id'}
    for doc in DOCUMENTS_DATASET
]
dataset.insert(cleaned_documents)

knowledge_units_per_doc: Dict[str, List[KnowledgeUnit]] = {
    dataset_item["id"]: ku_generation_service.generate_knowledge_units([
        Document(
            id=dataset_item["id"],
            text=dataset_item["text"],
        )
    ])
    for dataset_item in dataset.get_items()
}

metric = KnowledgeUnitGenerationRule(model_name="gpt-4o-mini")

evaluation_items = []

for dataset_item in dataset.get_items():
    # Find the corresponding ku
    kus = knowledge_units_per_doc[dataset_item['id']]
    # Turn document into a json str
    input = dataset_item['text']
    output = json.dumps([asdict(ku) for ku in kus])
    scores = metric.score(input=input, output=output)

    evaluation_items.append({
        "dataset_item_id": dataset_item['id'],
        "evaluate_task_result": {
            "knowledge_units": [asdict(ku) for ku in kus],
        },
        "feedback_scores": [
            {
                "name": score.name,
                "value": score.value,
                "reason": score.reason,
            }
            for score in scores],
    })

# Log experiment results using the bulk method
client.rest_client.experiments.experiment_items_bulk(
    experiment_name=EXPERIMENT_NAME,
    dataset_name=DATASET_NAME,
    items=[
        {
            "dataset_item_id": item["dataset_item_id"],
            "evaluate_task_result": item["evaluate_task_result"],
            "feedback_scores": [
                {**score, "source": "sdk"}
                for score in item["feedback_scores"]
            ]
        }
        for item in evaluation_items
    ]
)
