from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from ..models import WhatsAppCloudApiBusiness, WhatsAppEmbeddedSignUp
from .serializers import WhatsAppCloudApiBusinessSerializer

logger = logging.getLogger(__name__)


class EmbeddedSignupCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EmbeddedSignupEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        payload = serializer.validated_data
        data = payload.get('data', {})
        event = payload.get('event')
        
        # Log dos dados recebidos
        logger.info(
            "EmbeddedSignup callback received",
            extra={
                'user_id': user.id,
                'user_email': getattr(user, 'email', None),
                'event': event,
                'payload': payload
            }
        )
        
        # Salvar dados no modelo WhatsAppCloudApiBusiness apenas se for evento de sucesso
        if event in ['FINISH', 'FINISH_ONLY_WABA', 'FINISH_WHATSAPP_BUSINESS_APP_ONBOARDING']:
            phone_number_id = data.get('phone_number_id', '')
            
            if phone_number_id:
                try:
                    # Buscar WhatsAppCloudApiBusiness pelo phone_number_id
                    business, created = WhatsAppCloudApiBusiness.objects.update_or_create(
                        phone_number_id=phone_number_id,
                        defaults={
                            'waba_id': data.get('waba_id', ''),
                            'business_id': data.get('business_id', ''),
                            'phone_number': data.get('phone_number', ''),
                            'token': data.get('business_token', ''),  # Usando business_token como token
                            'api_version': 'v23.0',  # Versão padrão da API
                        }
                    )
                    
                    action = 'created' if created else 'updated'
                    
                    logger.info(
                        f"WhatsAppCloudApiBusiness {action} and WhatsAppEmbeddedSignUp {signup_action} successfully",
                        extra={
                            'user_id': user.id,
                            'phone_number_id': phone_number_id,
                            'action': action
                        }
                    )
                except Exception as e:
                    logger.error(
                        "Failed to save WhatsAppCloudApiBusiness or WhatsAppEmbeddedSignUp data",
                        extra={
                            'user_id': user.id,
                            'phone_number_id': phone_number_id,
                            'error': str(e),
                            'payload': payload
                        },
                        exc_info=True
                    )
            else:
                logger.warning(
                    "phone_number_id not provided in callback data",
                    extra={
                        'user_id': user.id,
                        'event': event,
                        'data': data
                    }
                )
        else:
            logger.info(
                "Non-success event received, data not saved",
                extra={
                    'user_id': user.id,
                    'event': event,
                    'phone_number_id': data.get('phone_number_id', '')
                }
            )

        return Response({
            "status": "ok",
            "user_id": user.id,
            "event": event,
            "saved": event in ['FINISH', 'FINISH_ONLY_WABA', 'FINISH_WHATSAPP_BUSINESS_APP_ONBOARDING'],
            "received": payload,
        }, status=status.HTTP_200_OK)
