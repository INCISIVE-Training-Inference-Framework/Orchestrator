from rest_framework import serializers

from main.models import \
    Schema


class SchemaOutputSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='schemas-detail')
    auxiliary_file = serializers.HyperlinkedIdentityField(view_name='schemas-auxiliary_file')

    class Meta:
        model = Schema
        fields = [
            'url',
            'name',
            'type',
            'implementation',
            'description',
            'auxiliary_file',
            'created_at'
        ]

    def to_representation(self, instance: Schema):
        representation = super().to_representation(instance)

        # input elements
        representation['input_elements'] = {
            'platform_data': instance.requires_input_elements_platform_data(),
            'external_data': instance.requires_input_elements_external_data(),
            'federated_learning_configuration': instance.requires_input_elements_federated_learning_configuration()
        }

        # ai elements
        representation['ai_elements'] = {
            'ai_engines': [
                {
                    'descriptor': ai_engine.descriptor,
                    'role_type': ai_engine.role_type,
                    'functionalities': ai_engine.parsed_functionalities,
                    'ai_model': ai_engine.requires_ai_model()
                } for ai_engine in instance.get_ai_items_ai_engines()
            ]
        }

        # output elements
        representation['output_elements'] = {
            'ai_model': instance.produces_output_elements_ai_model(),
            'evaluation_metrics': instance.produces_output_elements_evaluation_metrics(),
            'generic_file': instance.produces_output_elements_generic_file()
        }

        return representation
