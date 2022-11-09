import ast
import random

from django.conf import settings
from django.db import models
from typedmodels.models import TypedModel


# We use typed models to only have one db table for all types
# In this way, the API calls like retrieve or list only suppose one database call


def random_string():
    return str(random.randint(10000, 99999))


class JobStatus(models.TextChoices):
    PENDING = 'Pending'
    RUNNING = 'Running'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'


class JobUseCase(models.TextChoices):
    TRAINING_FROM_SCRATCH = settings.TRAINING_FROM_SCRATCH
    TRAINING_FROM_PRETRAINED_MODEL = settings.TRAINING_FROM_PRETRAINED_MODEL
    EVALUATING_FROM_PRETRAINED_MODEL = settings.EVALUATING_FROM_PRETRAINED_MODEL
    INFERENCING_FROM_PRETRAINED_MODEL = settings.INFERENCING_FROM_PRETRAINED_MODEL


class Job(TypedModel):
    random_id = models.CharField(default=random_string, max_length=100)
    data_partners_patients = models.TextField(null=True)  # nullable for inference
    data_path = models.CharField(max_length=100, null=True)
    number_iterations = models.IntegerField(null=True)
    status = models.CharField(
        max_length=10,
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
    )
    result = models.CharField(max_length=100, null=True)
    use_case = models.CharField(
        max_length=33,
        choices=JobUseCase.choices
    )
    ai_engine_config = models.FileField(upload_to='ai_engine_configs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def complete_id(self) -> str:
        return f'{self.id}-{self.random_id}'

    @property
    def parsed_data_partners_patients(self) -> dict:
        if isinstance(self.data_partners_patients, dict):
            return self.data_partners_patients
        return ast.literal_eval(self.data_partners_patients)

    @property
    def is_parallel(self) -> bool:
        return self.data_partners_patients and len(self.parsed_data_partners_patients) > 1


class JobTraining(Job):
    model_name = models.CharField(max_length=200, null=True)
    model_type = models.CharField(max_length=50, null=True)
    model_description = models.CharField(max_length=500, null=True)


class JobWithPretrainedModel(Job):
    model_id = models.IntegerField(null=True)


class JobTrainingFromScratch(JobTraining):
    ai_engine_id = models.IntegerField(null=True)


class JobTrainingFromPretrainedModel(JobTraining, JobWithPretrainedModel):
    pass


class JobEvaluatingFromPretrainedModel(JobWithPretrainedModel):
    pass


class JobInferencingFromPretrainedModel(JobWithPretrainedModel):
    input_data_files = models.FileField(
        upload_to='inference_input_data_files',
        null=True
    )
