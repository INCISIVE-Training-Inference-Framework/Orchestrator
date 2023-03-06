from django.conf import settings
from rest_framework import serializers

from main.api.serializers.schema.output import SchemaOutputSerializer
from main.models import \
    Schema, \
    SchemaInputPlatformData, \
    SchemaInputExternalData, \
    SchemaInputFederatedLearningConfiguration, \
    SchemaInputAIEngine, \
    SchemaInputAIModel, \
    SchemaOutputAIModel, \
    SchemaOutputEvaluationMetric, \
    SchemaOutputGenericFile


# TODO add validate methods


# Input classes

class SchemaInputSerializerInputElements(serializers.Serializer):
    platform_data = serializers.BooleanField()
    external_data = serializers.BooleanField()
    federated_learning_configuration = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, schema_instance, validated_data):
        # TODO roll back if error
        if validated_data['platform_data']:
            SchemaInputPlatformData.objects.create(**{
                'schema': schema_instance
            })
        if validated_data['external_data']:
            SchemaInputExternalData.objects.create(**{
                'schema': schema_instance
            })
        if validated_data['federated_learning_configuration']:
            SchemaInputFederatedLearningConfiguration.objects.create(**{
                'schema': schema_instance
            })


# AI logic classes

class SchemaInputSerializerInputAIEngine(serializers.Serializer):
    descriptor = serializers.CharField(max_length=100)  # TODO check that does not contain spaces or special symbols
    role_type = serializers.CharField(max_length=50)
    functionalities = serializers.ListField(required=True, allow_empty=False, child=serializers.ChoiceField(choices=settings.VALID_AI_ENGINE_FUNCTIONALITIES))
    ai_model = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, schema_instance, validated_data):
        # TODO roll back if error
        ai_engine_schema = SchemaInputAIEngine.objects.create(**{
            'descriptor': validated_data['descriptor'],
            'role_type': validated_data['role_type'],
            'functionalities': validated_data['functionalities'],
            'schema': schema_instance
        })
        if validated_data['ai_model']:
            SchemaInputAIModel.objects.create(**{'input_ai_engine': ai_engine_schema})


class SchemaInputSerializerAIElements(serializers.Serializer):
    ai_engines = SchemaInputSerializerInputAIEngine(many=True)

    # TODO check not repeated items

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, schema_instance, validated_data):
        serializer = SchemaInputSerializerInputAIEngine()
        for ai_engine in validated_data['ai_engines']:
            serializer.assign(schema_instance, ai_engine)

# Output classes


class SchemaInputSerializerOutputElements(serializers.Serializer):
    ai_model = serializers.BooleanField()
    evaluation_metrics = serializers.BooleanField()
    generic_file = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    def assign(self, schema_instance, validated_data):
        # TODO roll back if error
        if validated_data['ai_model']:
            SchemaOutputAIModel.objects.create(**{
                'schema': schema_instance
            })
        if validated_data['evaluation_metrics']:
            SchemaOutputEvaluationMetric.objects.create(**{
                'schema': schema_instance
            })
        if validated_data['generic_file']:
            SchemaOutputGenericFile.objects.create(**{
                'schema': schema_instance
            })


# Main class

class SchemaInputSerializer(serializers.ModelSerializer):
    input_elements = SchemaInputSerializerInputElements()
    ai_elements = SchemaInputSerializerAIElements()
    output_elements = SchemaInputSerializerOutputElements()

    class Meta:
        model = Schema
        fields = '__all__'

    def create(self, validated_data):
        # TODO if error roll back schema creation
        input_elements = validated_data.pop('input_elements')
        ai_elements = validated_data.pop('ai_elements')
        output_elements = validated_data.pop('output_elements')
        schema_instance = Schema.objects.create(**validated_data)
        SchemaInputSerializerInputElements().assign(schema_instance, input_elements)
        SchemaInputSerializerAIElements().assign(schema_instance, ai_elements)
        SchemaInputSerializerOutputElements().assign(schema_instance, output_elements)
        return schema_instance

    def to_representation(self, instance):
        instance = SchemaOutputSerializer(context=self.context).to_representation(instance)
        return instance