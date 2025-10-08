from rest_framework import serializers


class WhatsAppCloudApiBusinessSerializer(serializers.Serializer):
    phone_number_id = serializers.CharField(required=False, allow_blank=True)
    waba_id = serializers.CharField(required=False, allow_blank=True)
    business_id = serializers.CharField(required=False, allow_blank=True)
    current_step = serializers.CharField(required=False, allow_blank=True)
    error_message = serializers.CharField(required=False, allow_blank=True)
    error_id = serializers.CharField(required=False, allow_blank=True)
    session_id = serializers.CharField(required=False, allow_blank=True)
    timestamp = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

class WhatsAppEmbeddedSignUpSerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_blank=True)
    business_token = serializers.CharField(required=False, allow_blank=True)
    desired_pin = serializers.CharField(required=False, allow_blank=True, max_length=6)

class EmbeddedSignupEventSerializer(serializers.Serializer):
    data = WhatsAppCloudApiBusinessSerializer()
    type = serializers.ChoiceField(choices=["WA_EMBEDDED_SIGNUP"])  # fixed per docs
    event = serializers.CharField()  # FINISH, CANCEL, etc


class BusinessCallbackDataSerializer(serializers.Serializer):
    phone_number_id = serializers.CharField(required=True)
    waba_id = serializers.CharField(required=True)
    business_id = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    meta_app_id = serializers.CharField(required=True)


class BusinessCallbackSerializer(serializers.Serializer):
    data = BusinessCallbackDataSerializer()
