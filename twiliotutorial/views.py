import logging

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from twilio.rest import Client
from twilio.twiml import voice_response

from twiliotutorial.beer import Beer, BeerFact

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

        return HttpResponse(response.to_xml(), content_type='text/xml')

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


class BeerFactView(View):

    def build_response(self, beer_fact: BeerFact) -> voice_response.VoiceResponse:
        response = voice_response.VoiceResponse()
        response.say("Hello! I am going to drop a dank beer on you.", voice=settings.VOICE)
        gather = voice_response.Gather(
            action="/beertext?beerid=" + beer_fact.id,
            action_on_empty_result=False,
            timeout=200,
            numDigits=1,
            finishOnKey='')
        gather.say(f"Our beer today is {beer_fact.name}", voice=settings.VOICE)

        if beer_fact.abv:
            gather.say(f"Coming in at {beer_fact.abv} percent.", voice=settings.VOICE)

        if beer_fact.style:
            if 'description' in beer_fact.style:
                description = beer_fact.style['description']
                gather.say(f"{description}", voice=settings.VOICE)
        response.append(gather)
        response.say("Wow! You made it to the end. Be excellent to each other.", voice=settings.VOICE)
        response.hangup()
        return response

    def get_beer_fact(self) -> BeerFact:
        beer = Beer()
        fact = beer.get_random_beer_fact()
        logging.debug("Beer info: %s", beer)
        return fact

    def post(self, request):
        beer_fact = self.get_beer_fact()
        response = self.build_response(beer_fact)
        return HttpResponse(response.to_xml(), content_type='text/xml')


class BeerTextView(View):
    def create_text_body(self, beer_fact):
        body = f"Hi there! You were listening to: {getattr(beer_fact, 'name')}, " \
               f"{getattr(beer_fact, 'abv', 'Unknown')}%, IBU: {getattr(beer_fact, 'ibu', 'Unknown')}"
        return body

    def text_beer_info_to_number(self, beer_fact: BeerFact, from_: str,
                                 to_: str) -> None:

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)

        text_body = self.create_text_body(beer_fact)

        message = client.messages.create(
            body=text_body,
            from_=to_,
            to=from_
        )
        logging.info("Sent sms: %s", message.sid)

    def get_beer_fact_for_beer_id(self, beer_id: str) -> BeerFact:
        beer = Beer()
        fact = beer.get_beer_by_id(beer_id=beer_id)
        logging.debug("Beer info: %s", beer)
        return fact

    def post(self, request):
        logging.info("OOhhh...Engagement.")
        request_beerid = request.GET.get('beerid')  # Even though this is a post, django puts query params in the GET.
        request_from_number = request.POST.get("From", None)
        request_to_number = request.POST.get("To", None)

        if request_beerid is None:
            logging.info("Weird, we didn't get a beerid")
        elif request_from_number is None:
            logging.info("Weird, we didn't get a number")
        else:
            beer_fact = self.get_beer_fact_for_beer_id(beer_id=request_beerid)
            self.text_beer_info_to_number(beer_fact=beer_fact, from_=request_from_number,
                                          to_=request_to_number)

        response = voice_response.VoiceResponse()
        response = HttpResponse(response.to_xml(), content_type='text/xml')
        return response
