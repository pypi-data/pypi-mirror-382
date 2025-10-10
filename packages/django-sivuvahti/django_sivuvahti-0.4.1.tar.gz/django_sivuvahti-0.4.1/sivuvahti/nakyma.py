import asyncio
import uuid

from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils import timezone

from django_sivumedia import Mediasaate
from pistoke.nakyma import WebsocketNakyma
from pistoke.protokolla import WebsocketProtokolla
from pistoke.tyokalut import CsrfKattely, JsonLiikenne
from viestikanava import Viestikanava

from .sivuvahti import Sivuvahti


class Sivuvahtinakyma(Mediasaate, WebsocketNakyma):
  '''
  Luokkapohjainen näkymä, joka välittää Celery-viestikanavan kautta samalla
  sivulla (request.GET['sivu']) auki oleville istunnoille tiedon toisistaan,
  ja näihin istuntoihin liittyvistä käyttäjistä.

  Viestikanavan kautta voi myös lähettää viestejä käyttäjältä toisille.

  Lisää osoitteisto:
  >>> from sivuvahti import Sivuvahti
  >>> urlpatterns = [
  ...    path('sivuvahti', Sivuvahti.as_view(
  ...      kayttajan_tiedot=lambda self: {
  ...        'id': self.request.user.pk,
  ...        'nimi': self.request.user.first_name,
  ...      }
  ...    ), name='sivuvahti'),
  ... ]

  Lisää tarvittava komentosarja HTML-aihioon:
  {{ view.media.js }}

  Reagoi haluttuihin tapahtumiin sivulla:
  <script>
    let sivuvahti = new Sivuvahti(location.pathname);
    document.addEventListener("sivuvahti.yhteysAvattu", ...);
    document.addEventListener("sivuvahti.yhteysKatkaistu", ...);
    document.addEventListener("sivuvahti.saapuvaKayttaja", ...);
    document.addEventListener("sivuvahti.poistuvaKayttaja", ...);
    document.addEventListener("sivuvahti.saapuvaViesti", ...);
  </script>
  '''

  class Media:
    js = [
      f'https://cdn.jsdelivr.net/gh/an7oine/kantoaalto-js'
      f'@v0.2-1-gc37fa10/kantoaalto.min.js',
      'sivuvahti/js/sivuvahti.js',
    ]

  # Käytetty Celery-viestikanava.
  kanava: str = 'sivuvahti'

  # Käytetty Sivuvahti-toteutus.
  Sivuvahti: type[Sivuvahti] = Sivuvahti

  @property
  def alikanava(self) -> str:
    return self.request.GET['sivu']

  @property
  def viestikanava(self) -> Viestikanava:
    return Viestikanava(
      kanava=self.kanava,
      alikanava=self.alikanava,
    )
    # def viestikanava

  @cached_property
  def kayttajan_tiedot(self) -> dict:  # pyright: ignore
    ''' Käyttäjästä toisille välitettävät tiedot. '''
    return {
      'id': self.request.user.pk,
      'nimi': str(self.request.user),
    }
    # def kayttajan_tiedot

  @method_decorator(WebsocketProtokolla)
  @method_decorator(JsonLiikenne)
  @method_decorator(CsrfKattely(
    csrf_avain='csrfmiddlewaretoken',
    virhe_avain='virhe'
  ))
  async def websocket(self, request, *args, **kwargs):
    await self.Sivuvahti(
      viestikanava=self.viestikanava,
      request=self.request,
      kayttajan_tiedot=self.kayttajan_tiedot,
    )()
    # async def websocket

  # class Sivuvahti
