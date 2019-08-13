from django.http import HttpResponse
from django.views import View
from django.conf import settings
from urllib.parse import parse_qs

from twilio.twiml import voice_response
from twilio.rest import Client



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


        beer = Beer()
        mug = beer.get_beer_fact()
        name = mug['name']
        logging.debug("Beer info: %s", mug)
        response.say("Hello! I am going to drop a dank beer on you.", voice=settings.VOICE)
        gather = voice_response.Gather(
            action="/beertext?beerid=" + mug['id'],
            action_on_empty_result=False,
            timeout=200,
            numDigits=1,
            finishOnKey='')
        gather.say(f"Our beer today is {name}", voice=settings.VOICE)

        gather.say(beer.say_beer(mug), voice=settings.VOICE)

        response.append(gather)
        response.say("Wow! You made it to the end. Be excellent to each other.", voice=settings.VOICE)
        response.hangup()

        response = HttpResponse(response.to_xml())
        return response

class BeerText(View):

    def post(self, request):

        logging.info("OOhhh...Engagement.")
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)

        request_beerid = parse_qs(request.META['QUERY_STRING'])['beerid'][0]
        request_from_number = request.POST.get("From", None)
        request_to_number = request.POST.get("To", None)

        if request_beerid is None:
            logging.info("Weird, we didn't get a beerid")
        elif request_from_number is None:
            logging.info("Weird, we didn't get a number")
        else:
            beer = Beer()
            mug = beer.get_beer_by_id(beerid=request_beerid)[0]
            beer_name = mug['name']
            mug = beer.text_beer(mug)

            message = client.messages.create(
                body=f"Hi there! You were listening to: {beer_name}, {mug['abv']}%, IBU: {mug['ibu']}",
                from_=request_to_number,
                to=request_from_number
            )

            logging.info("Sent sms: %s", message.sid)

        response = voice_response.VoiceResponse()
        response = HttpResponse(response.to_xml())
        return response
