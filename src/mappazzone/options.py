from dataclasses import dataclass
from typing import Any, List, Set
import os

from constants import ENV_LANGUAGE
from locations import Continent, Direction
from board import Board


@dataclass
class Option:
    name: str
    description: str
    choices: List
    value: Any
    _var: Any = None
    
    def set(self, value: Any):
        """Set option to `value`. If `value` is a string that is not
        one of the available `choices`, try to convert the string
        based on the type of `choices`'s first element."""
        if value in self.choices:
            self.value = value
        elif type(value) is str and self.choices and value in [str(o) for o in self.choices]:
            self.value = type(self.choices[0])(value)
        else:
            raise ValueError(f"{value} is not a valid choice for option {self.name}")

    def get(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class _OptDesc:
    name: str = ''
    description: str = ''


@dataclass
class Options_:

    def __getitem__(self, option_name: str) -> Any:
        return self.get_option(option_name).value

    def get_option(self, option_name: str) -> Option:
        return self._OPTIONS[option_name]

    def set_option(self, option_name: str, value: Any):
        self._OPTIONS[option_name].set(value)

    def items(self):
        return self._OPTIONS.items()

    def continents(self) -> Set[Continent]:
        """Use only locations in these continents."""
        result = [c for c in list(Continent) if (
            (c == Continent.EU and self[Continent.EU.name]) or
            (c == Continent.AS and self[Continent.AS.name]) or
            (c == Continent.AF and self[Continent.AF.name]) or
            (c == Continent.NA and self[Continent.NA.name]) or
            (c == Continent.SA and self[Continent.SA.name]) or
            (c == Continent.OC and self[Continent.OC.name]) or
            (c == Continent.AN and self[Continent.AN.name])
        )]
        return set(result)

    def capitals_only(self) -> bool:
        """Use only capital cities?"""
        return self['capitals only']

    def turn_delay(self) -> int:
        """Wait these seconds between turns."""
        return self['turn delay']
    
    def board(self) -> Board.BoardOptions:
        """Options for board setup."""
        return Board.BoardOptions(size=self['grid size'],
                                  tolerance=self['tolerance'],
                                  wrap=self['wrap'])

    def initial(self) -> int:
        """Number of cities in each player's hand at the beginning of the game."""
        return self['initial cities']

    def may_swap(self) -> bool:
        """May players swap a location instead of playing?"""
        return self['may swap']

    def to_draw(self, place_result: List[Direction], hand: int) -> int:
        """Number of cities to draw after a placement with given
        `place_result` for a player with `hand` cities."""
        mistakes = len(place_result)
        if mistakes == 0:
            draw = 0
        elif self['draw per mistake']:
            draw = self['draw when fail'] * mistakes
        else:
            draw = self['draw when fail']
        if hand + draw > self['stop drawing']:
            return self['stop drawing'] - hand
        else:
            return draw

    def gameover(self, rounds: int, scores: List[int], placed: int, deck: int) -> str:
        """Given the number of completed `rounds`, the list of player
        `scores`, how many cities are `placed` on the board, and how
        many are still available in the `deck`, determine whether the
        game is over. Return string with gameover reason, or empty
        string if the game is not over."""
        if 0 < self['end rounds'] < rounds:
            return f"The game is over after {self['end rounds']} rounds."
        for score in scores:
            if score == 0:
                return "The game is over after a player has placed all their locations."
            elif score >= self['end hand']:
                return f"The game is over after a player has {self['end hand']} or more locations in their hand."
        if 0 < self['end placed'] <= placed:
            return f"The game is over after {self['end placed']} locations have been placed on the board."
        # len(scores) gives the number of players
        if deck - self['empty deck'] <= len(scores):
            return "The game is over because the deck is empty."
        return ""

    def __str__(self) -> str:
        options = [f"'{name}': {option.value}" for name, option in self.items()]
        return ", ".join(options)

    def __init__(self):
        try:
            for option, optdesc in self._DESCRIPTIONS.items():
                if optdesc.name:
                    self._OPTIONS[option].name = optdesc.name
                if optdesc.description:
                    self._OPTIONS[option].description = optdesc.description
        except AttributeError:
            pass

    _OPTIONS = {
        'grid size': Option(
            name='', description='',
            choices=[6, 8, 10],
            value=10
        ),
        'initial cities': Option(
            name='', description='',
            choices=[1, 2, 3, 4, 5],
            value=3
        ),
        'capitals only': Option(
            name='', description='',
            choices=[True, False],
            value=True
        ),
        Continent.EU.name: Option(
            name=Continent.EU.value, description='',
            choices=[True, False],
            value=True
        ),
        Continent.AS.name: Option(
            name=Continent.AS.value, description='',
            choices=[True, False],
            value=True
        ),
        Continent.AF.name: Option(
            name=Continent.AF.value, description='',
            choices=[True, False],
            value=True
        ),
        Continent.NA.name: Option(
            name=Continent.NA.value, description='',
            choices=[True, False],
            value=True
        ),
        Continent.SA.name: Option(
            name=Continent.SA.value, description='',
            choices=[True, False],
            value=True
        ),
        Continent.OC.name: Option(
            name=Continent.OC.value, description='',
            choices=[True, False],
            value=True
        ),
        Continent.AN.name: Option(
            name=Continent.AN.value, description='',
            choices=[True, False],
            value=True
        ),
        'tolerance': Option(
            name='', description='',
            choices=[0.0, 0.1, 1.0, 5.0, 10.0],
            value=5.0
        ),
        'draw when fail': Option(
            name='', description='',
            choices=[1, 2, 3],
            value=2
        ),
        'draw per mistake': Option(
            name='', description='',
            choices=[True, False],
            value=False
        ),
        'stop drawing': Option(
            name='', description='',
            choices=[4, 6, 8, 10],
            value=10
        ),
        'end hand': Option(
            name='', description='',
            choices=[3, 5, 7, 10],
            value=10
        ),
        'end rounds': Option(
            name='', description='',
            choices=[-1, 5, 10, 30, 50, 100],
            value=-1
        ),
        'end placed': Option(
            name='', description='',
            choices=[-1, 5, 7, 10],
            value=-1
        ),
        'empty deck': Option(
            name='', description='',
            choices=[0, 100, 1000],
            value=0
        ),
        'may swap': Option(
            name='', description='',
            choices=[True, False],
            value=True
        ),
        'only sat': Option(
            name='', description='',
            choices=[True, False],
            value=True
        ),
        'wrap': Option(
            name='', description='',
            choices=[True, False],
            value=False
        ),
        'turn delay': Option(
            name='', description='',
            choices=[0, 5, 7, 10],
            value=7
        ),
    }


class OptionsEN(Options_):

    _DESCRIPTIONS = {
        'grid size': _OptDesc(
            name="Board size",
            description="Number of cells on each side of the board (excluding the center)."
        ),
        'initial cities': _OptDesc(
            name="Initial cities",
            description="Number of cities per player at the beginning of the game."
        ),
        'capitals only': _OptDesc(
            name="Capitals only",
            description="Use only cities that are capitals."
        ),
        Continent.EU.name: _OptDesc(
            description="Include cities in Europe."
        ),
        Continent.AS.name: _OptDesc(
            description="Include cities in Asia."
        ),
        Continent.AF.name: _OptDesc(
            description="Include cities from in Africa."
        ),
        Continent.NA.name: _OptDesc(
            description="Include cities in North America."
        ),
        Continent.SA.name: _OptDesc(
            description="Include cities in South America."
        ),
        Continent.OC.name: _OptDesc(
            description="Include cities in Oceania."
        ),
        Continent.AN.name: _OptDesc(
            description="Include cities in Antarctica."
        ),
        'tolerance': _OptDesc(
            name="Tolerance",
            description="Two cities whose longitude (resp. latitude) differ less than the tolerance can be placed in any two columns (resp. row)."
        ),
        'draw when fail': _OptDesc(
            name="Cities drawn on fail",
            description="Number of new cities a player has to draws when they place a city incorrectly."
        ),
        'draw per mistake': _OptDesc(
            name="Draw for each mistake",
            description="If selected, a player who placed a city incorrectly has to draw cities for each direction that they got wrong."
        ),
        'stop drawing': _OptDesc(
            name="Stop drawing",
            description="When a player has these many cities in their hand, they do not draw new cities even if they play wrong."
        ),
        'end hand': _OptDesc(
            name="Max cities in hand",
            description="When a player has these many cities in their hand, the game ends."
        ),
        'end rounds': _OptDesc(
            name="Max rounds",
            description="The game ends after these many rounds (a negative number means no limit)."
        ),
        'end placed': _OptDesc(
            name="Max cities on board",
            description="When there are these many many cities placed on the board, the game ends (a negative number means no limit)."
        ),
        'empty deck': _OptDesc(
            name="Empty deck",
            description="Number of locations in the deck for which it's considered 'empty', and the game ends."
        ),
        'may swap': _OptDesc(
            name="Allow swapping",
            description="Can a player change a city instead of placing it?"
        ),
        'only sat': _OptDesc(
            name="Only draw placeable",
            description="If enabled, only cities that can be placed somewhere on the board will be drawn."
        ),
        'wrap': _OptDesc(
            name="Wrap longitudes",
            description="If enabled, longitudes 'wrap over' 180 degrees in each direction. For example, Japan (+138) can be placed west of Hawaii (-155)."
        ),
        'turn delay': _OptDesc(
            name="Turn delay",
            description="Wait these many seconds after each turn before moving on to the next player."
        ),
    }


class OptionsIT(Options_):

    _DESCRIPTIONS = {
        'grid size': _OptDesc(
            name="Dimensione mappa",
            description="Numero di celle in ciascuna metà della mappa di gioco (senza contare il centro)."
        ),
        'initial cities': _OptDesc(
            name="Città iniziali",
            description="Numero di città per giocatore all'inizio di una partita."
        ),
        'capitals only': _OptDesc(
            name="Solo capitali",
            description="Usare solo città che sono capitali."
        ),
        Continent.EU.name: _OptDesc(
            description="Usa città in Europa."
        ),
        Continent.AS.name: _OptDesc(
            description="Usa città in Asia."
        ),
        Continent.AF.name: _OptDesc(
            description="Usa città in Africa."
        ),
        Continent.NA.name: _OptDesc(
            description="Usa città in Nordamerica."
        ),
        Continent.SA.name: _OptDesc(
            description="Usa città in Sudamerica."
        ),
        Continent.OC.name: _OptDesc(
            description="Usa città in Oceania."
        ),
        Continent.AN.name: _OptDesc(
            description="Usa città in Antartide."
        ),
        'tolerance': _OptDesc(
            name="Tolleranza",
            description="Due città le cui longitudini (rispettivamente, latitudini) differiscono di meno della tolleranza possono essere piazzate in qualsiasi due colonne (rispettivamente, righe)."
        ),
        'draw when fail': _OptDesc(
            name="Città pescate in caso di errore",
            description="Numero di nuove città un giocatore riceve quando piazza una città in maniera incorretta."
        ),
        'draw per mistake': _OptDesc(
            name="Pescare per errore",
            description="Se questa opzione è selezionata, un giocatore che ha piazzato una città incorrettamente deve pescare città per ciascuna direzione che ha sbagliato."
        ),
        'stop drawing': _OptDesc(
            name="Limite pesca",
            description="Quando un giocatore ha questo numero di città in mano, non pesca nuove città anche se sbaglia."
        ),
        'end hand': _OptDesc(
            name="Massimo numero città",
            description="Quando un giocatore ha questo numero di città in mano, la partita termina."
        ),
        'end rounds': _OptDesc(
            name="Massimo numero turni",
            description="La partita termina passati questo numero di turni (un numero negativo significa che non c'è limite)."
        ),
        'end placed': _OptDesc(
            name="Massimo città piazzate",
            description="Quando questo numero di città sono posizionate sul tavolo di gioco, la partita termina (un numero negativo significa che non c'è limite)."
        ),
        'empty deck': _OptDesc(
            name="Mazzo esaurito",
            description="Numero di città rimanenti nel mazzo per il quale è considerato esaurito, e la partita termina."
        ),
        'may swap': _OptDesc(
            name="Permetti scambio",
            description="I giocatori possono scambiare una città invece di piazzarla?"
        ),
        'only sat': _OptDesc(
            name="Pesca solo piazzabili",
            description="Se questa opzione è selezionata, i giocatori pescano solo città che possono essere piazzate correttamente sul tavolo di gioco da qualche parte."
        ),
        'wrap': _OptDesc(
            name="Continua longitudini",
            description="Se questa opzione è selezionata, le longitudini continuano oltre i 180 gradi in ciascuna direzione. Per esempio, il Giappone (+138) può essere piazzato a ovest delle Hawaii (-155)."
        ),
        'turn delay': _OptDesc(
            name="Pausa tra turni",
            description="Effettua una pausa di questa durata in secondi dopo ogni turno prima di passare al prossimo giocatore."
        ),
    }


if os.environ[ENV_LANGUAGE] == 'EN':
    Options = OptionsEN
elif os.environ[ENV_LANGUAGE] == 'IT':
    Options = OptionsIT
