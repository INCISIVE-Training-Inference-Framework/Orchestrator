from rest_framework import serializers


# Main class

class ExecutionInputSerializerForFailedUpdate(serializers.Serializer):
    message = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
