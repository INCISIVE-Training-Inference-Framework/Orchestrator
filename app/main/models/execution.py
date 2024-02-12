import os
import ast
from typing import List

from django.db import models

from .schema import Schema
from .utils import get_class_name_low_case


# Auxiliary choice structures

class ExecutionStatus(models.TextChoices):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


# Main class

class Execution(models.Model):
    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # auxiliary elements

    def get_auxiliary_elements_state(self):
        return eval(f'self.{get_class_name_low_case(ExecutionState)}')

    # input elements

    def get_input_elements_platform_data(self):
        return eval(f'self.{get_class_name_low_case(ExecutionInputPlatformData)}')

    def get_input_elements_external_data(self):
        return eval(f'self.{get_class_name_low_case(ExecutionInputExternalData)}')

    def get_input_elements_report_metadata(self):
        return eval(f'self.{get_class_name_low_case(ExecutionInputReportMetadata)}')

    def get_input_elements_federated_learning_configuration(self):
        return eval(f'self.{get_class_name_low_case(ExecutionInputFederatedLearningConfiguration)}')

    # ai elements

    def get_ai_elements_ai_engines(self):
        return ExecutionInputAIEngine.objects.filter(execution=self)

    def get_ai_elements_specific_ai_engine(self, descriptor):
        return ExecutionInputAIEngine.objects.filter(execution=self, descriptor=descriptor)

    # output elements

    def get_output_elements_ai_model(self):
        return eval(f'self.{get_class_name_low_case(ExecutionOutputAIModel)}')

    def get_output_elements_evaluation_metrics(self):
        return ExecutionOutputEvaluationMetric.objects.filter(execution=self)

    def get_output_elements_generic_file(self):
        return eval(f'self.{get_class_name_low_case(ExecutionOutputGenericFile)}')

    # update methods

    def update_status(self, status: ExecutionStatus, error_message=None):
        values = {'status': status}
        if error_message: values['message'] = error_message
        ExecutionState.objects.filter(execution=self).update(**values)
        self.save(update_fields=['updated_at'])  # TODO do with atomic operation along previous update
        return Execution.objects.filter(pk=self.pk)[0]

    def update_output_elements_ai_model(self, ai_model: int):
        ExecutionOutputAIModel.objects.filter(execution=self).update(**{'ai_model': ai_model})

    def update_output_elements_evaluation_metrics(self, evaluation_metrics: List[int]):
        for evaluation_metric in evaluation_metrics:
            ExecutionOutputEvaluationMetric.objects.create(**{'evaluation_metric': evaluation_metric, 'execution': self})

    def update_output_elements_generic_file(self, generic_file: int):
        ExecutionOutputGenericFile.objects.filter(execution=self).create(**{'generic_file': generic_file, 'execution': self})


# Auxiliary classes

class ExecutionState(models.Model):
    status = models.CharField(
        max_length=10,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING
    )
    message = models.TextField(null=True)
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )


# TODO use this class
class ExecutionResources(models.Model):
    requested_cpu = models.FloatField()
    requested_memory = models.IntegerField()
    requested_gpu = models.BooleanField()
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )


# Input classes

class ExecutionInputPlatformData(models.Model):
    data_partners_patients = models.TextField()
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    @property
    def parsed_data_partners_patients(self) -> dict:
        if isinstance(self.data_partners_patients, dict):
            raw = self.data_partners_patients
        else:
            raw = ast.literal_eval(self.data_partners_patients)
        return {data_partner: [patient['id'] for patient in data_partner_info['patients']] for data_partner, data_partner_info in raw.items()}

    @property
    def parsed_data_partners_patients_full(self) -> dict:
        if isinstance(self.data_partners_patients, dict):
            return self.data_partners_patients
        return ast.literal_eval(self.data_partners_patients)


def execution_external_data_contents_path(instance, filename):
    _, file_extension = os.path.splitext(filename)
    return f'execution/' \
           f'external_data/' \
           f'contents/' \
           f'{instance.execution.id}{file_extension}'


class ExecutionInputExternalData(models.Model):
    contents = models.FileField(upload_to=execution_external_data_contents_path, max_length=300)
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )


def execution_external_data_report_metadata_path(instance, filename):
    _, file_extension = os.path.splitext(filename)
    return  f'execution/' \
            f'external_data/' \
            f'report_metadata/' \
            f'{instance.execution.id}{file_extension}'


class ExecutionInputReportMetadata(models.Model):
    report_metadata = models.FileField(upload_to=execution_external_data_report_metadata_path, max_length=300)
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True
    )


class ExecutionInputFederatedLearningConfiguration(models.Model):
    number_iterations = models.IntegerField()
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )


# AI logic classes

def execution_ai_engine_version_user_vars_path(instance, filename):
    _, file_extension = os.path.splitext(filename)
    return f'execution/' \
           f'ai_engine_version/' \
           f'user_vars/' \
           f'{instance.execution.id}_{instance.descriptor}{file_extension}'


class ExecutionInputAIEngine(models.Model):
    descriptor = models.CharField(max_length=100)
    version = models.IntegerField()
    version_user_vars = models.FileField(upload_to=execution_ai_engine_version_user_vars_path, max_length=300)
    container_name = models.CharField(max_length=200)
    container_version = models.CharField(max_length=50)
    max_iteration_time = models.IntegerField()
    memory_request = models.CharField(max_length=50)
    memory_limit = models.CharField(max_length=50)
    cpu_request = models.CharField(max_length=50)
    cpu_limit = models.CharField(max_length=50)

    execution = models.ForeignKey(
        Execution,
        on_delete=models.CASCADE
    )

    def requires_ai_model(self):  # TODO do checking on the schema
        return hasattr(self, get_class_name_low_case(ExecutionInputAIModel))

    def get_ai_model(self):
        return eval(f'self.{get_class_name_low_case(ExecutionInputAIModel)}')


class ExecutionInputAIModel(models.Model):
    ai_model = models.IntegerField()
    download_resume_retries = models.IntegerField()

    input_ai_engine = models.OneToOneField(
        ExecutionInputAIEngine,
        on_delete=models.CASCADE,
        primary_key=True,
    )


# Output classes

class ExecutionOutputAIModel(models.Model):
    ai_model = models.IntegerField(null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    merge_type = models.CharField(max_length=50, null=True)
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class ExecutionOutputEvaluationMetric(models.Model):
    evaluation_metric = models.IntegerField()
    execution = models.ForeignKey(
        Execution,
        on_delete=models.CASCADE
    )


class ExecutionOutputGenericFile(models.Model):
    generic_file = models.IntegerField()
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )
