import asyncio
from dataclasses import dataclass
from functools import lru_cache
import threading

from celery.app import app_or_default


@lru_cache(maxsize=None)  # Python 3.9+: @cache
@dataclass
class _CeleryViestikanava:

  kanava: str

  def __post_init__(self):
    super().__init__()
    sovellus = app_or_default()
    channel = sovellus.broker_connection().channel()
    self.dispatcher = sovellus.events.Dispatcher(
      channel=channel
    )
    self._lukko = threading.Lock()
    self._vastaanottajat = {}

    self._receiver = sovellus.events.Receiver(
      channel=channel,
      handlers={
        self.kanava: self.saapuva_viesti
      }
    )
    self._kaynnissa = 0
    # def __post_init__

  def __enter__(self):
    if self._kaynnissa <= 0:
      loop = asyncio.get_running_loop()
      self._receiver.should_stop = False
      self._luku = loop.run_in_executor(
        None,
        self._receiver.capture
      )
    self._kaynnissa += 1
    # def __enter__

  def __exit__(self, *args):
    self._kaynnissa -= 1
    if self._kaynnissa <= 0:
      self._receiver.should_stop = True
    # def __exit__

  def saapuva_viesti(self, viesti):
    with self._lukko:
      vastaanottajat = set(self._vastaanottajat.get(
        viesti['_alikanava'], set()
      ))
    for vastaanottaja in vastaanottajat:
      vastaanottaja(viesti)
      # for vastaanottaja in vastaanottajat
    # def saapuva_viesti

  def laheta_viesti(self, _alikanava, **viesti):
    self.dispatcher.send(
      type=self.kanava,
      _alikanava=_alikanava,
      **viesti
    )
    # def laheta_viesti

  def lisaa_vastaanottaja(self, _alikanava, vastaanottaja):
    with self._lukko:
      self._vastaanottajat.setdefault(
        _alikanava, set()
      ).add(vastaanottaja)
    # def lisaa_vastaanottaja

  def poista_vastaanottaja(self, _alikanava, vastaanottaja):
    with self._lukko:
      self._vastaanottajat.get(
        _alikanava, set()
      ).remove(vastaanottaja)
    # def poista_vastaanottaja

  # class _CeleryViestikanava


@dataclass
class Viestikanava:
  '''
  Kanava viestien lähetykseen ja vastaanottoon Celeryn välityksellä.

  >>> with Viestikanava(
  ...   kanava='viestit',
  ...   alikanava='kissat',
  ... ) as kanava:
  ...   await kanava.kirjoita(nimi='Mirri', tervehdys='Miau')
  ...   print('vastaus', await kanava.lue())
  '''

  kanava: str
  alikanava: str

  def __post_init__(self):
    self._viestikanava = _CeleryViestikanava(self.kanava)

  def _vastaanottaja(self, viesti):
    asyncio.run_coroutine_threadsafe(
      self._saapuva.put(viesti),
      self._loop
    )
    # def _vastaanottaja

  async def __aenter__(self):
    self._loop = asyncio.get_running_loop()
    self._saapuva = asyncio.Queue()
    self._viestikanava.lisaa_vastaanottaja(
      self.alikanava,
      self._vastaanottaja
    )
    self._viestikanava.__enter__()
    return self
    # async def __aenter__

  async def __aexit__(self, *args):
    self._viestikanava.__exit__(*args)
    self._viestikanava.poista_vastaanottaja(
      self.alikanava,
      self._vastaanottaja
    )
    # async def __aexit__

  async def __aiter__(self):
    while True:
      yield await self.lue()
    # async def __aiter__

  async def lue(self):
    return await self._saapuva.get()

  async def kirjoita(self, *args, **kwargs):
    self._viestikanava.laheta_viesti(
      _alikanava=self.alikanava,
      **dict(*args, **kwargs),
    )
    # async def kirjoita

  def kirjoita_taustalla(self, *args, **kwargs):
    self._viestikanava.laheta_viesti(
      _alikanava=self.alikanava,
      **dict(*args, **kwargs),
    )
    # def kirjoita_taustalla

  # class Viestikanava
