from rest_framework import serializers


# Output classes

class ExecutionInputSerializerForSucceededUpdateOutputElementsAIModel(serializers.Serializer):
    ai_model = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ExecutionInputSerializerForSucceededUpdateOutputElementsEvaluationMetric(serializers.Serializer):
    evaluation_metric = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ExecutionInputSerializerForSucceededUpdateOutputElementsGenericFile(serializers.Serializer):
    generic_file = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


# Main class

class ExecutionInputSerializerForSucceededUpdate(serializers.Serializer):
    ai_model = ExecutionInputSerializerForSucceededUpdateOutputElementsAIModel(required=False)
    evaluation_metrics = serializers.ListField(allow_empty=False, required=False, child=ExecutionInputSerializerForSucceededUpdateOutputElementsEvaluationMetric())
    generic_file = ExecutionInputSerializerForSucceededUpdateOutputElementsGenericFile(required=False)

    def validate(self, validated_data):
        schema = self.context.get('schema')

        is_ai_model_produced = schema.produces_output_elements_ai_model()
        if is_ai_model_produced and 'ai_model' not in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" should produce an AI Model')
        if not is_ai_model_produced and 'ai_model' in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" does not produce an AI Model')

        are_evaluation_metrics_produced = schema.produces_output_elements_evaluation_metrics()
        if are_evaluation_metrics_produced and 'evaluation_metrics' not in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" should produce a list of Evaluation Metrics')
        if not are_evaluation_metrics_produced and 'evaluation_metrics' in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" does not produce a list of Evaluation Metrics')

        is_generic_file_produced = schema.produces_output_elements_generic_file()
        if is_generic_file_produced and 'generic_file' not in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" should produce a Generic File')
        if not is_generic_file_produced and 'generic_file' in validated_data:
            raise serializers.ValidationError(f'schema \"{schema.name}\" does not produce a Generic File')

        return validated_data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
