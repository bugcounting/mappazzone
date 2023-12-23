"""This module provides support for UI messages in multiple languages."""

import os
import logging

from .constants import ENV_LANGUAGE


class EmptyMessages:  # pylint: disable=too-few-public-methods
    """A dictionary of UI messages, whose keys are message names."""

    def __getitem__(self, message_name: str) -> str:
        return self._MESSAGES[message_name]

    def __init__(self):
        logger = logging.getLogger(__name__)
        # If there exist an attribute _TRANSLATIONS, use it to update _MESSAGES.
        try:
            for key, message in self._TRANSLATIONS.items():
                if key in self._MESSAGES:
                    self._MESSAGES[key] = message
                else:
                    logger.error("Message '%s' not found.", key)
        except AttributeError:
            pass

    _MESSAGES = {
        'app name': '',
        'player name': '',
        'whose turn': '',
        'add player': '',
        'options': '',
        'start game': '',
        'show rules': '',
        'back to main': '',
        'quit': '',
        'place instructions': '',
        'swap instructions': '',
        'direction east': '',
        'direction west': '',
        'direction null': '',
        'direction north': '',
        'direction south': '',
        'game over rounds': '',
        'game over score': '',
        'game over hand': '',
        'game over placed': '',
        'game over deck': '',
        'how to play': '',
    }


class MessagesEN(EmptyMessages):  # pylint: disable=too-few-public-methods
    """Dictionary of UI messages in English."""

    _TRANSLATIONS = {
        'app name': 'Mappazzone!',
        'player name': 'Player {}',
        'whose turn': '{} to play!',
        'add player': 'Add player',
        'options': 'Options',
        'start game': 'Start game',
        'show rules': 'How to play?',
        'back to main': 'Back to main',
        'quit': 'Quit',
        'place instructions': (
            'Click on a location and then on an empty cell on the board to place it.'
        ),
        'swap instructions': 'Double-click on a location to swap it with one in the deck.',
        'direction east': 'E',
        'direction west': 'W',
        'direction null': '',
        'direction north': 'N',
        'direction south': 'S',
        'game over rounds': 'The game is over after reaching the maximum number of rounds.',
        'game over score': 'The game is over after a player has placed all their locations.',
        'game over hand': 'The game is over after a player has too many locations in their hand.',
        'game over placed': (
            'The game is over after a maximum number of locations have been placed on the board.'
        ),
        'game over deck': 'The game is over because the deck is empty.',
        'how to play': """
        Mappazzone is a geolocalization board game.

        At the beginning of a game, a location is drawn from the deck
        and placed in the center of the board. The location's
        geographical coordinates (longitude and latitude) are shown.

        Each player also receives a number of locations from the deck,
        with their coordinates hidden. In each turn, a player can
        either try to place one of their location on the board or, if
        swapping is allowed by the options, they can swap one of their
        locations with a new one from the deck.

        A location can only be placed on the board in a valid
        position, that is one that is consistent with the coordinates
        of the other locations on the board. Namely, all locations in
        columns to the left of the placement position must have
        longitudes that are less than or equal to the placed
        location's; all locations in columns to the right of the
        placement position must have longitudes that are greater than
        or equal to the placed location's; all locations in rows above
        the placement position must have latitudes that are greater
        than or equal to the placed location's; and all locations in
        rows below the placement position must have latitudes that are
        less than or equal to the placed location's. Note that two
        locations whose coordinates differ less than the chosen value
        of tolerance can be placed on any two rows or columns relative
        to each other.

        If a player places a location in their hand in a valid
        position, it stays on the board. If a player places a location
        in their hand in a position that is invalid, the location is
        discarded and the player draws a number of new locations from
        the deck. In either case, the game then moves on to next
        player.

        The game continues until a player places all their locations
        correctly, they reach a certain maximum number of locations in
        their hand, all locations in the deck have been used, or a
        certain maximum number of turns have elapsed. When the game
        ends, the player with the fewest locations in their hand wins
        the game. If two players have the same number of locations in
        their hand at the end of the game, the player who correctly
        placed the larger number of locations on the board during the
        game wins.

        Remember that longitudes are positive numbers to the east of
        the prime meridian; and latitudes are positive numbers to the
        north of the equator. The game follows this coordinate system;
        therefore, for instance, you cannot place a location in Japan
        (longitude 138 E) to the west (left) of a location in Hawaii
        (longitude -155 W), even though you can reach Japan from
        Hawaii traveling west.
        """,
    }


class MessagesIT(EmptyMessages):  # pylint: disable=too-few-public-methods
    """Dictionary of UI messages in Italian."""

    _TRANSLATIONS = {
        'app name': 'Mappazzone!',
        'player name': 'Giocatore {}',
        'whose turn': 'Gioca {}!',
        'add player': 'Aggiungi giocatore',
        'options': 'Opzioni',
        'start game': 'Inizia partita',
        'show rules': 'Come si gioca?',
        'back to main': 'Menu principale',
        'quit': 'Esci',
        'place instructions': (
            'Clicca su una città e poi su una cella vuota nel tavolo di gioco per piazzarla.'
        ),
        'swap instructions': 'Fai doppio clic su una città per scambiarla con una dal mazzo.',
        'direction east': 'E',
        'direction west': 'O',
        'direction null': '',
        'direction north': 'N',
        'direction south': 'S',
        'game over rounds': 'La partita è finita dopo che sono passati il numero massimo di turni.',
        'game over score': (
            'La partita è finita dopo che un giocatore ha piazzato tutte le sue città.'
        ),
        'game over hand': 'La partita è finita dopo che un giocatore ha troppe città in mano.',
        'game over placed': (
            'La partita è finita dopo che il numero massimo di città '
            'sono state piazzate sul tavolo di gioco.'
        ),
        'game over deck': 'La partita è finita perché il mazzo è esaurito.',
        'how to play': """
        Mappazzone è un gioco di geolocalizzazione.

        All'inizio di una partita, una città viene pescata dal mazzo e
        piazzata al centro del tavolo di gioco. Le coordinate
        geografiche della città (longitudine e latitudine) sono
        visibili.

        Ogni giocatore pesca anche un numero di città dal mazzo, le
        cui coordinate sono nascoste. In ogni turno, un giocatore può
        provare a piazzare una delle sue città sul tavolo di gioco,
        oppure, se lo scambio è consentito dalle opzioni, può
        scambiare una delle sue città con un'altra a caso dal mazzo.

        Una città può essere piazzata sul tavolo da gioco solo in una
        posizione valida, ossia una posizione che è consistente con le
        coordinate delle altre città sul tavolo. Precisamente, tutte
        le città in colonne a sinistra della posizione di piazzamento
        devono avere una longitudine minore o uguale a quella della
        città piazzata; le città in colonne a destra della posizione
        di piazzamento devono avere una longitudine maggiore o uguale
        a quella della città piazzata; le città in righe sotto alla
        posizione di piazzamento devono avere una latitudine minore o
        uguale a quella della città piazzata; e le città in righe
        sopra alla posizione di piazzamento devono avere una
        latitudine maggiore o uguale a quella della città piazzata. Si
        noti che due città le cui coordinate differiscono di meno del
        valore di tolleranza scelto nelle opzioni possono essere
        posizionate su due righe o colonne in qualunque ordine
        relativo.

        Se un giocatore piazza una città in una posizione valida, la
        città rimane sul tavolo da gioco. Se un giocatore piazza una
        città in una posizione invalida, la città è rimossa e il
        giocatore pesca un certo numero di città nuove dal mazzo. In
        entrambi i casi, la partita continua passando il turno al
        prossimo giocatore.

        Una partita continua finché un giocatore riesce a piazzare
        tutte le sue città correttamente, oppure rimangono con un
        certo numreo di città in mano, oppure tutte le città nel mazzo
        sono state usate, oppure un certo numero massimo di turni sono
        trascorsi. Quando una partita termina, il giocatore con meno
        città ancora in mano vince. Se due giocatori hanno lo stesso
        numero di città in mano alla fine di una partita, il giocatore
        che ha piazzato correttamente, nel corso della partita, il
        maggior numero di città vince.

        Si ricordi che valori positivi di longitudine corrispondono a
        posizioni a est del meridiano primo; e valori positivi di
        latitudine corrispondono a posizioni a nord dell'equatore. Il
        gioco si basa su queste convenzioni; pertanto, per esempio,
        non è possibile piazzare una città in Giappone (longitudine
        138 E) a ovest (sinistra) di una città nelle Hawaii
        (longitudine -155 O), anche se in realtà si può raggiungere il
        Giappone viaggiando dalle Hawaii in direzione ovest.
        """,
    }


if os.environ[ENV_LANGUAGE] == 'EN':
    Messages = MessagesEN
elif os.environ[ENV_LANGUAGE] == 'IT':
    Messages = MessagesIT
