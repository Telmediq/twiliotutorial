from django.http import HttpResponse
from django.views import View
from django.conf import settings


from twilio.twiml import voice_response

from twiliotutorial.beer import Beer

import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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


class BeerFact(View):

    def post(self, request):
        response = voice_response.VoiceResponse()
        response.say("Hello! I am going to drop a dank beer on you.", voice=settings.VOICE)

        beer = Beer()
        mug = beer.get_beer_fact()
        name = mug['name']
        logging.debug(f"Beer info: {name}")
        response.say(f"Our beer today is {name}", voice=settings.VOICE)

        if 'abv' in mug.keys():
            abv = mug['abv']
            response.say(f"Coming in at {abv} percent.", voice=settings.VOICE)

        if 'description' in mug['style'].keys():
            description = mug['style']['description']
            response.say(f"{description}", voice=settings.VOICE)

        response.hangup()

        return HttpResponse(response.to_xml())