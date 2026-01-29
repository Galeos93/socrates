from dataclasses import asdict
import json
from typing import List, Dict

from opik import Opik, Prompt
import opik
from openai import OpenAI

from experiments.exp_001.dataset import DOCUMENTS_DATASET
from experiments.exp_001.templates import TEMPLATE_V1
from experiments.exp_001.prompt_factory import OpikPromptFactory
from experiments.common.metrics.knowledge_unit_gen_rule import KnowledgeUnitGenerationRule
from domain.entities.learning import KnowledgeUnit
from domain.entities.document import Document
from application.ports.prompt_template_repository import PromptTemplateRepository
from infrastructure.adapters.knowledge_unit_generation.llm.service import LLMKnowledgeUnitGenerationService

EXPERIMENT_NAME = "exp_001_knowledge_unit_generation_evaluation"
DATASET_NAME = "KU_GEN_TEXT_ANALYS IS"
OPIK_TEMPLATE_NAME = "KnowledgeUnitGenerationPrompt"
PROJECT_NAME = "playground"


# Configure Opik
opik.configure()

# Get or create a dataset
client = Opik(project_name=PROJECT_NAME)

# OpenAI client
openai_client =OpenAI()

class TemplateRepo(PromptTemplateRepository):
    @staticmethod
    def get(name: str, version: str) -> str:
        return TEMPLATE_V1

    @staticmethod
    def save(name: str, content: str, version: str) -> None:
        pass


ku_generation_service = LLMKnowledgeUnitGenerationService(
    client=openai_client,
    model="gpt-4o",
    prompt_factory=OpikPromptFactory(opik_template_name=OPIK_TEMPLATE_NAME),
    template_repo= TemplateRepo()
)

dataset = client.get_or_create_dataset(name=DATASET_NAME)
# Remove 'id' field before inserting - Opik will auto-generate UUIDs
cleaned_documents = [
    {k: v for k, v in asdict(doc).items() if k != 'id'}
    for doc in DOCUMENTS_DATASET
]
dataset.insert(cleaned_documents)

# Load template from Opik
opik_template: Prompt = client.get_prompt(name=OPIK_TEMPLATE_NAME)

# Create experiment
experiment = client.create_experiment(
    dataset_name=DATASET_NAME,
    name=EXPERIMENT_NAME,
    prompt=opik_template,
)

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
    experiment_name=experiment.name,
    experiment_id=experiment.id,
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
