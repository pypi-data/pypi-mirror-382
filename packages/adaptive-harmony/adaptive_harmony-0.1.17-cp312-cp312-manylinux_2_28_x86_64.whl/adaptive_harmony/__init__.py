# ruff: noqa: F403, F401
from typing import TYPE_CHECKING
from .adaptive_harmony import (
    StringThread as StringThread,
    TokenizedThread as TokenizedThread,
    InferenceModel as InferenceModel,
    ModelBuilder as ModelBuilder,
    TrainingModel as TrainingModel,
    get_client as get_client,
    HarmonyClient as HarmonyClient,
    JobNotifier as JobNotifier,
    HarmonyJobNotifier as HarmonyJobNotifier,
    StageNotifier as StageNotifier,
    EvalSampleInteraction as EvalSampleInteraction,
    EvalSample as EvalSample,
    Grade as Grade,
    JobArtifact as JobArtifact,
)
from rich.progress import Progress, TaskID

if TYPE_CHECKING:
    from .adaptive_harmony import StringTurn as StringTurn
else:
    from typing import NamedTuple

    class StringTurn(NamedTuple):
        role: str
        content: str


from adaptive_harmony.core.dataset import DataSet
from adaptive_harmony.core.schedulers import CosineScheduler, CombinedSchedule, CosineSchedulerWithoutWarmup, Scheduler
from adaptive_harmony.metric_logger import WandbLogger, Logger
from adaptive_harmony.file_storage import (
    FileStorage,
    FileStorageConfig,
    LocalFileStorageConfig,
    S3FileStorageConfig,
    StoredFile,
)
from adaptive_harmony.evaluation.evaluation_artifact import EvaluationArtifact
from adaptive_harmony.artifacts.custom_artifact import CustomArtifact
from adaptive_harmony.artifacts.dataset_artifact import DatasetArtifact
import adaptive_harmony.core.rl_utils as rl_utils


# Ensure key classes are available at module level
__all__ = [
    "StringThread",
    "StringTurn",
    "TokenizedThread",
    "InferenceModel",
    "ModelBuilder",
    "TrainingModel",
    "HarmonyClient",
    "get_client",
    "DataSet",
    "CosineScheduler",
    "CombinedSchedule",
    "CosineSchedulerWithoutWarmup",
    "Scheduler",
    "WandbLogger",
    "Logger",
    "FileStorage",
    "FileStorageConfig",
    "LocalFileStorageConfig",
    "S3FileStorageConfig",
    "StoredFile",
    "EvaluationArtifact",
    "CustomArtifact",
    "DatasetArtifact",
    "rl_utils",
    "Grade",
    "EvalSample",
    "EvalSampleInteraction",
    "JobArtifact",
]


# Patch StringThread to use rich for display
from adaptive_harmony.core.display import _stringthread_repr, _tokenizedthread_repr
from adaptive_harmony.core.image_utils import string_thread_to_html_string

# Patch InferenceModel to have json output capabilities
from adaptive_harmony.core.structured_output import generate_and_validate, render_schema, render_pydantic_model

StringThread.__repr__ = _stringthread_repr  # type: ignore
TokenizedThread.__repr__ = _tokenizedthread_repr  # type: ignore
setattr(StringThread, "_repr_html_", string_thread_to_html_string)
setattr(InferenceModel, "generate_and_validate", generate_and_validate)
setattr(InferenceModel, "render_schema", staticmethod(render_schema))
setattr(InferenceModel, "render_pydantic_model", staticmethod(render_pydantic_model))


async def spawn_train(self: ModelBuilder, name: str, max_batch_size: int) -> TrainingModel:
    fut = await self.spawn_train_with_progress(name, max_batch_size)  # type:ignore

    with Progress() as pbar:
        task = pbar.add_task("Loading model", total=1000)

        while (prog := await fut._await_progress()) != 1.0:
            pbar.update(task, completed=prog, total=1.0)
        pbar.update(task, completed=1.0, total=1.0)

    return await fut.get()


async def spawn_inference(self: ModelBuilder, name: str) -> InferenceModel:
    fut = await self.spawn_inference_with_progress(name)  # type:ignore

    with Progress() as pbar:
        task = pbar.add_task("Loading model", total=1000)

        while (prog := await fut._await_progress()) != 1.0:
            pbar.update(task, completed=prog, total=1.0)
        pbar.update(task, completed=1.0, total=1.0)

    return await fut.get()


setattr(ModelBuilder, "spawn_inference", spawn_inference)
setattr(ModelBuilder, "spawn_train", spawn_train)
