from django.db import models

from main.models.execution import Execution


class ExecutionWorkflow(models.Model):
    workflow_name = models.CharField(max_length=200)
    execution = models.OneToOneField(
        Execution,
        on_delete=models.CASCADE,
        primary_key=True,
    )
