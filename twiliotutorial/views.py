from django.http import HttpResponse
from django.views import View

from twilio.twiml import voice_response


class InteractiveVoiceResponseView(View):

    def post(self, request, *args, **kwargs):

        if 'Digits' in request.POST:
            response = self.handle_digits(digits=request.POST['Digits'])
        else:
            response = self.handle_prompt()

        return HttpResponse(response.to_xml())

    def handle_prompt(self):
        response = voice_response.VoiceResponse()
        gather = response.gather(action='/callback', num_digits=2, timeout=30)
        gather.say("Pick a number between 0 and 99")
        return response

    def handle_digits(self, digits):
        response = voice_response.VoiceResponse()
        response.say(f"You picked {digits}")
        response.redirect('/play-again')

        return response


class PlayAgain(View):

    def post(self, request):
        if 'Digits' in request.POST:
            response = self.handle_digits(digits=request.POST['Digits'])
        else:
            response = self.handle_prompt()

        return HttpResponse(response.to_xml())

    def handle_prompt(self):
        response = voice_response.VoiceResponse()
        gather = response.gather(num_digits=1, timeout=30, action='/play-again')
        gather.say('Press 1 to run again, press 2 to hang up')
        return response

    def handle_digits(self, digits):
        response = voice_response.VoiceResponse()

        if digits == '1':
            response.redirect('/callback')
        else:
            response.say('Goodbye')
            response.hangup()

        return response
