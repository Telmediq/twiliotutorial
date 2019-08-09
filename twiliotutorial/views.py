from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View

from twilio.twiml import voice_response


class InteractiveVoiceResponseView(View):

    def post(self, request, *args, **kwargs):

        response = voice_response.VoiceResponse()
        response.say("Jeff has a poopy butthole")
        response.hangup()

        return HttpResponse(response.to_xml())
