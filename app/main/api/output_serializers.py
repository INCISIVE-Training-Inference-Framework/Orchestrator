import ast

from rest_framework import serializers

from main.models import \
    Job


def ignore_null_values(instance):
    fields = list(instance.keys())
    for field in fields:
        try:
            if instance[field] is None:
                instance.pop(field)
        except KeyError:
            pass


class JobOutputSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='jobs-detail')
    id = serializers.IntegerField()
    ai_engine_config = serializers.HyperlinkedIdentityField(
        view_name='jobs-download_ai_engine_config'
    )

    class Meta:
        model = Job
        exclude = ['type', 'random_id']

    def to_representation(self, instance: Job):
        use_case = instance.use_case
        instance = super().to_representation(instance)
        ignore_null_values(instance)

        instance['use_case'] = use_case

        if 'data_partners_patients' in instance:
            instance['data_partners_patients'] = ast.literal_eval(instance['data_partners_patients'])
        if 'input_data_files' in instance:
            instance.pop('input_data_files')

        return instance
