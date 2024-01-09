import os
import ast

from django.db import models

from .utils import get_class_name_low_case


# Auxiliary choice structures


class SchemaType(models.TextChoices):
    INDIVIDUAL = 'individual'
    JOINT = 'joint'


class SchemaImplementation(models.TextChoices):
    ARGO_WORKFLOWS = 'argo_workflows'
    DUMMY = 'dummy'


# Main class

def schema_auxiliary_file_path(instance, filename):
    _, file_extension = os.path.splitext(filename)
    return f'schema/' \
           f'auxiliary_file/' \
           f'{instance.name}{file_extension}'


class Schema(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    type = models.CharField(
        max_length=10,
        choices=SchemaType.choices
    )
    implementation = models.CharField(
        max_length=15,
        choices=SchemaImplementation.choices
    )
    description = models.TextField()
    auxiliary_file = models.FileField(upload_to=schema_auxiliary_file_path, max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    # input elements

    def requires_input_elements_platform_data(self):
        return hasattr(self, get_class_name_low_case(SchemaInputPlatformData))

    def requires_input_elements_external_data(self):
        return hasattr(self, get_class_name_low_case(SchemaInputExternalData))

    def requires_input_elements_report_metadata(self):
        return hasattr(self, get_class_name_low_case(SchemaInputReportMetadata))

    def requires_input_elements_federated_learning_configuration(self):
        return hasattr(self, get_class_name_low_case(SchemaInputFederatedLearningConfiguration))

    # ai elements

    def get_ai_items_ai_engines(self):
        return SchemaInputAIEngine.objects.filter(schema=self)

    def get_ai_elements_specific_ai_engine(self, descriptor):
        return SchemaInputAIEngine.objects.filter(schema=self, descriptor=descriptor)

    # output elements

    def produces_output_elements_ai_model(self):
        return hasattr(self, get_class_name_low_case(SchemaOutputAIModel))

    def produces_output_elements_evaluation_metrics(self):
        return hasattr(self, get_class_name_low_case(SchemaOutputEvaluationMetric))

    def produces_output_elements_generic_file(self):
        return hasattr(self, get_class_name_low_case(SchemaOutputGenericFile))


# Input classes

class SchemaInputPlatformData(models.Model):
    schema = models.OneToOneField(
        Schema,
        on_delete=models.CASCADE,
        primary_key=True
    )


class SchemaInputExternalData(models.Model):
    schema = models.OneToOneField(
        Schema,
        on_delete=models.CASCADE,
        primary_key=True
    )


class SchemaInputReportMetadata(models.Model):
    schema = models.OneToOneField(
        Schema,
        on_delete=models.CASCADE,
        primary_key=True
    )


class SchemaInputFederatedLearningConfiguration(models.Model):
    schema = models.OneToOneField(
        Schema,
        on_delete=models.CASCADE,
        primary_key=True
    )


# AI logic classes

class SchemaInputAIEngine(models.Model):
    descriptor = models.CharField(max_length=100)
    role_type = models.CharField(max_length=50)
    functionalities = models.TextField()
    schema = models.ForeignKey(
        Schema,
        on_delete=models.CASCADE
    )

    def requires_ai_model(self):
        return hasattr(self, get_class_name_low_case(SchemaInputAIModel))

    @property
    def parsed_functionalities(self) -> list:
        if isinstance(self.functionalities, list):
            return self.functionalities
        return ast.literal_eval(self.functionalities)


class SchemaInputAIModel(models.Model):
    input_ai_engine = models.OneToOneField(
        SchemaInputAIEngine,
        on_delete=models.CASCADE,
        primary_key=True
    )


# Output classes

class SchemaOutputAIModel(models.Model):
    schema = models.OneToOneField(
        Schema,
        on_delete=models.CASCADE,
        primary_key=True
    )


class SchemaOutputEvaluationMetric(models.Model):
    schema = models.OneToOneField(
        Schema,
        on_delete=models.CASCADE,
        primary_key=True
    )


class SchemaOutputGenericFile(models.Model):
    schema = models.OneToOneField(
        Schema,
        on_delete=models.CASCADE,
        primary_key=True
    )
