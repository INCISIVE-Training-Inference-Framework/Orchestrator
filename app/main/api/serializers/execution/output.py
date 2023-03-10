from .maas_methods import get_maas_url
from rest_framework import serializers

from main.models import \
    Execution, \
    ExecutionStatus


class ExecutionOutputSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='executions-detail')
    schema = serializers.HyperlinkedRelatedField(view_name='schemas-detail', read_only=True)

    class Meta:
        model = Execution
        fields = [
            'url',
            'id',
            'schema',
            'created_at',
            'updated_at'
        ]

    def to_representation(self, instance: Execution):
        representation = super().to_representation(instance)
        schema = instance.schema

        # auxiliary elements
        state = instance.get_auxiliary_elements_state()
        representation['state'] = {
            'status': state.status
        }
        if state.message is not None:
            representation['state']['message'] = state.message

        # input elements
        representation['input_elements'] = {}

        if schema.requires_input_elements_platform_data():
            platform_data = instance.get_input_elements_platform_data()
            representation['input_elements']['platform_data'] = {
                'data_partners_patients': platform_data.parsed_data_partners_patients
            }

        if schema.requires_input_elements_external_data():
            contents_serializer = serializers.HyperlinkedIdentityField(
                view_name='executions-external_data'
            )
            contents_serializer_url = contents_serializer.get_url(
                instance,
                'executions-external_data',
                self.context.get('request'),
                None
            )
            representation['input_elements']['external_data'] = {
                'contents': contents_serializer_url
            }

        if schema.requires_input_elements_federated_learning_configuration():
            federated_learning_configuration = instance.get_input_elements_federated_learning_configuration()
            representation['input_elements']['federated_learning_configuration'] = {
                'number_iterations': federated_learning_configuration.number_iterations
            }

        # ai elements
        representation['ai_elements'] = {}

        user_vars_serializer = serializers.HyperlinkedIdentityField(
            view_name='executions-version_user_vars'
        )
        user_vars_serializer_url = user_vars_serializer.get_url(
            instance,
            'executions-version_user_vars',
            self.context.get('request'),
            None
        )

        representation['ai_elements']['ai_engines'] = []
        for ai_engine in instance.get_ai_elements_ai_engines():

            ai_engine_representation = {
                    'descriptor': ai_engine.descriptor,
                    'version': get_maas_url('ai_engine_version', ai_engine.version),
                    'version_user_vars': f'{user_vars_serializer_url}?descriptor={ai_engine.descriptor}'
                }

            if ai_engine.requires_ai_model():  # TODO do checking on the schema
                ai_engine_representation['ai_model'] = get_maas_url('ai_model', ai_engine.get_ai_model().ai_model)
            representation['ai_elements']['ai_engines'].append(ai_engine_representation)

        # output elements
        representation['output_elements'] = {}

        if schema.produces_output_elements_ai_model():
            ai_model = instance.get_output_elements_ai_model()
            if state.status != ExecutionStatus.SUCCEEDED:
                representation['output_elements']['ai_model'] = {
                    'name': ai_model.name,
                    'description': ai_model.description,
                    'merge_type': ai_model.merge_type
                }
            else:
                representation['output_elements']['ai_model'] = {
                    'ai_model': get_maas_url('ai_model', ai_model.ai_model)
                }

        if schema.produces_output_elements_evaluation_metrics() and state.status == ExecutionStatus.SUCCEEDED:
            representation['output_elements']['evaluation_metrics'] = [
                {
                    'evaluation_metric': get_maas_url('evaluation_metric', evaluation_metric.evaluation_metric)
                } for evaluation_metric in instance.get_output_elements_evaluation_metrics()
            ]

        if schema.produces_output_elements_generic_file() and state.status == ExecutionStatus.SUCCEEDED:
            generic_file = instance.get_output_elements_generic_file()
            representation['output_elements']['generic_file'] = {
                'generic_file': get_maas_url('generic_file', generic_file.generic_file)
            }


        return representation
