import asyncio
from dataclasses import dataclass, field
from typing import Any, Self
import uuid

from django.utils import timezone

from pistoke.pyynto import WebsocketPyynto
from viestikanava import Viestikanava


@dataclass(kw_only=True)
class Sivuvahti:
  '''
  Toteutus, joka välittää Celery-viestikanavan kautta samalla
  tunnisteella auki oleville istunnoille tiedon toisistaan.

  Viestikanavan kautta voi myös lähettää viestejä käyttäjältä toisille.
  '''

  # Käytetty Celery-viestikanava.
  viestikanava: Viestikanava

  # Websocket-istunto.
  request: WebsocketPyynto

  # Kirjautuneesta käyttäjästä muille välitettävät tiedot.
  kayttajan_tiedot: dict[str, Any]

  # Kirjautuneen käyttäjän UUID-tunniste.
  oma_uuid: str = field(
    default_factory=lambda: str(uuid.uuid4()),
    init=False
  )

  muut: dict[str, Self] = field(default_factory=dict, init=False)

  @property
  def itse(self):
    return {
      'uuid': str(self.oma_uuid),
      'kayttaja': self.kayttajan_tiedot,
    }
    # def itse

  async def saapuva_viesti(
    self,
    viesti: dict,
  ):
    '''
    Reagointi Celery-kanavasta saapuvaan viestiin.
    - käyttäjä itse: ohitetaan
    - poistuva, tunnettu käyttäjä:
      - poistetaan `self.muut`-sanakirjasta
      - välitetään selaimelle
    - saapuva, ei-tunnettu käyttäjä:
      - lisätään `self.muut`-sanakirjaan
      - välitetään selaimelle
      - ilmoittaudutaan saapujalle
    - saapuva viesti muulta kuin käyttäjältä itseltään:
      - välitetään selaimelle
    '''
    if kayttaja := viesti.get('kayttaja'):
      kayttaja_uuid = kayttaja['uuid']
      if kayttaja_uuid == self.itse['uuid']:
        pass
      elif kayttaja.get('tila') == 'poistuu':
        if poistuva_kayttaja := self.muut.pop(kayttaja_uuid, None):
          await self.request.send(
            {'poistuva_kayttaja': poistuva_kayttaja}
          )
      elif kayttaja.get('tila') == 'saapuu' \
      and kayttaja_uuid not in self.muut:
        kayttaja = self.muut[kayttaja_uuid] = kayttaja['kayttaja']
        await self.request.send(
          {'saapuva_kayttaja': kayttaja}
        )
        # Ilmoittaudutaan uudelle saapujalle.
        await self.viestikanava.kirjoita(
          kayttaja={**self.itse, 'tila': 'saapuu'}
        )
      # elif kayttaja_uuid not in muut

    elif saapuva_viesti := viesti.get('viesti'):
      if saapuva_viesti['lahettaja']['uuid'] != self.itse['uuid']:
        await self.request.send({'saapuva_viesti': saapuva_viesti})
    # async def saapuva_viesti

  async def lahteva_viesti(self, viesti: dict):
    await self.viestikanava.kirjoita(viesti={
      **viesti,
      'lahettaja': self.itse,
      'aika': timezone.now().isoformat(),
      'data-id': str(uuid.uuid4()),
    })
    # async def lahteva_viesti

  async def aloita(self):
    ''' Avaa istunto. '''
    await self.viestikanava.kirjoita(
      kayttaja={**self.itse, 'tila': 'saapuu'}
    )
    # async def aloita

  async def lopeta(self):
    ''' Päätä istunto: poistu itse, ilmoita kaikki muut poistuneiksi. '''
    await self.viestikanava.kirjoita(
      kayttaja={**self.itse, 'tila': 'poistuu'}
    )
    for muu_kayttaja in self.muut.values():
      await self.request.send(
        {'poistuva_kayttaja': muu_kayttaja}
      )
    # async def lopeta

  async def vastaanota(self):
    ''' Kuuntele viestejä Celery-viestikanavasta ja reagoi niihin. '''
    async for viesti in self.viestikanava:
      await self.saapuva_viesti(viesti)
    # async def vastaanota

  async def laheta(self):
    ''' Kuuntele viestejä selaimelta ja välitä ne Celery-viestikanavaan. '''
    async for viesti in self.request:
      await self.lahteva_viesti(viesti)
    # async def laheta

  async def __call__(self):
    '''
    Ilmoittaudutaan muille käyttäjille ja kuunnellaan Celery-viestikanavaa.
    Ilmoitetaan lopuksi istunnon päättymisestä.
    '''
    async with self.viestikanava:
      await self.aloita()
      try:
        await asyncio.gather(
          self.vastaanota(),
          self.laheta(),
        )
      finally:
        await self.lopeta()
    # async def __call__

  # class Sivuvahti
