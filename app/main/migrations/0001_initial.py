# Generated by Django 4.2.4 on 2023-08-02 15:53

from django.db import migrations, models
import django.db.models.deletion
import main.models.execution
import main.models.schema


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionInputAIEngine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descriptor', models.CharField(max_length=100)),
                ('version', models.IntegerField()),
                ('version_user_vars', models.FileField(max_length=300, upload_to=main.models.execution.execution_ai_engine_version_user_vars_path)),
                ('container_name', models.CharField(max_length=200)),
                ('container_version', models.CharField(max_length=50)),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='Schema',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('individual', 'Individual'), ('joint', 'Joint')], max_length=10)),
                ('implementation', models.CharField(choices=[('argo_workflows', 'Argo Workflows'), ('dummy', 'Dummy')], max_length=15)),
                ('description', models.TextField()),
                ('auxiliary_file', models.FileField(max_length=300, upload_to=main.models.schema.schema_auxiliary_file_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SchemaInputAIEngine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descriptor', models.CharField(max_length=100)),
                ('role_type', models.CharField(max_length=50)),
                ('functionalities', models.TextField()),
                ('schema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.schema')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionInputAIModel',
            fields=[
                ('ai_model', models.IntegerField()),
                ('input_ai_engine', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.executioninputaiengine')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionInputExternalData',
            fields=[
                ('contents', models.FileField(max_length=300, upload_to=main.models.execution.execution_external_data_contents_path)),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionInputFederatedLearningConfiguration',
            fields=[
                ('number_iterations', models.IntegerField()),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionInputPlatformData',
            fields=[
                ('data_partners_patients', models.TextField()),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionOutputAIModel',
            fields=[
                ('ai_model', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('merge_type', models.CharField(max_length=50, null=True)),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionOutputGenericFile',
            fields=[
                ('generic_file', models.IntegerField()),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionResources',
            fields=[
                ('requested_cpu', models.FloatField()),
                ('requested_memory', models.IntegerField()),
                ('requested_gpu', models.BooleanField()),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionState',
            fields=[
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('succeeded', 'Succeeded'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('message', models.TextField(null=True)),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionWorkflow',
            fields=[
                ('workflow_name', models.CharField(max_length=200)),
                ('execution', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.execution')),
            ],
        ),
        migrations.CreateModel(
            name='SchemaInputAIModel',
            fields=[
                ('input_ai_engine', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.schemainputaiengine')),
            ],
        ),
        migrations.CreateModel(
            name='SchemaInputExternalData',
            fields=[
                ('schema', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.schema')),
            ],
        ),
        migrations.CreateModel(
            name='SchemaInputFederatedLearningConfiguration',
            fields=[
                ('schema', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.schema')),
            ],
        ),
        migrations.CreateModel(
            name='SchemaInputPlatformData',
            fields=[
                ('schema', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.schema')),
            ],
        ),
        migrations.CreateModel(
            name='SchemaOutputAIModel',
            fields=[
                ('schema', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.schema')),
            ],
        ),
        migrations.CreateModel(
            name='SchemaOutputEvaluationMetric',
            fields=[
                ('schema', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.schema')),
            ],
        ),
        migrations.CreateModel(
            name='SchemaOutputGenericFile',
            fields=[
                ('schema', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='main.schema')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionOutputEvaluationMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluation_metric', models.IntegerField()),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.execution')),
            ],
        ),
        migrations.AddField(
            model_name='execution',
            name='schema',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.schema'),
        ),
    ]
