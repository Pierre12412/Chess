import time
from operator import attrgetter


class Tournament:
    '''
    Classe des tournois
    -name : Nom
    -place : Lieu
    -date : Date
    -cadence : "Blitz" par exemple
    -round : Nombre de rondes
    -rondes_instances : Liste des instances de rondes
    -players : Liste des joueurs qui participent
    -description : Description du tournois
    -turn : Ronde actuelle
    -opponents : Liste de couple [joueur1,joueur2] qui se sont
                 déjà rencontrés
    '''
    def __init__(self, name, place, date, cadence, description,
                 round=5, rondes_instances=[], players=[], turn=1,
                 opponents=[]):
        self.__init__
        self.name = name
        self.place = place
        self.date = date
        self.cadence = cadence
        self.round = round
        self.rondes_instances = rondes_instances
        self.players = players
        self.description = description
        self.turn = turn
        self.opponents = opponents

    def conditions_duo(self, player1, player2, round):
        '''Conditions à remplir pour que 2 joueurs soient appariés'''
        for match in round.match_list:
            if (match.player1.name == player1.name
                    or match.player2.name == player2.name):
                return False
            if (match.player2.name == player1.name
                    or match.player1.name == player2.name):
                return False
        in_opp = [player1.name, player2.name] in self.opponents
        in_opp2 = [player2.name, player1.name] in self.opponents
        return not (in_opp or in_opp2)

    def start_first_round(self, name, time_start):
        while True:
            if name != 'exit':
                round0 = Round(round_name=name, match_list=[], results=[],
                               time_start=time_start)
                break
            else:
                print("Vous ne pouvez pas sortir d'un tournois non créé")
                continue
        self.players = sorted(self.players,
                              key=attrgetter('ranking'),
                              reverse=True)
        first_part = []
        second_part = []

        for i in range(len(self.players)):
            if i+1 <= len(self.players)/2:
                first_part.append(self.players[i])
            else:
                second_part.append(self.players[i])

        for i in range(len(first_part)):
            match = Match(first_part[i], second_part[i])
            self.opponents.append(
                [first_part[i].name, second_part[i].name]
                )
            # On ajoute les matchs a la ronde 1
            round0.match_list.append(match)

        # On ajoute la ronde au tournois
        self.rondes_instances.append(round0)
        return (first_part, second_part)

    def start_x_round(self, name, time_start):
        # Si ce n'est pas la première ronde,
        # on trie et on apparie
        if name != 'exit':
            roundx = Round(round_name=name, match_list=[], results=[],
                           time_start=time_start)
        else:
            return 'exit'
        self.players = sorted(self.players,
                              key=attrgetter('score', 'ranking'),
                              reverse=True)
        return self.one_against_one(roundx)

    def pair(self, roundx):
        '''
        Appariement Suisse sur les joueurs
        '''
        players = []
        for player in self.players:
            players.append(player)
        while len(players) != 0:
            i = 0
            first = players[i]
            ind1 = i
            second = players[i + 1]
            ind2 = i + 1

            while ([first.name, second.name] in self.opponents
                    or [second.name, first.name] in self.opponents):
                try:
                    i += 1
                    second = players[i + 1]
                    ind2 = i + 1

                except IndexError:
                    second = players[i]
                    ind2 = i
                    break

            match = Match(players[ind1], players[ind2])
            roundx.match_list.append(match)
            self.opponents.append(
                                [players[ind1].name,
                                 players[ind2].name]
                                )
            del players[ind2]
            del players[ind1]

    def one_against_one(self, roundx):
        self.pair(roundx)

        first_part = []
        second_part = []

        for match in roundx.match_list:
            first_part.append(match.player1)
            second_part.append(match.player2)

        # On ajoute la ronde au tournois
        self.rondes_instances.append(roundx)
        return (first_part, second_part)

    def save_tournament(self, db):
        '''Sauvegarde le tournois actuel'''
        tournaments_table = db.table('tournaments')
        rounds_ser = []
        players_ser = []
        match_ser = []
        for ronde in self.rondes_instances:
            match_ser = []
            for match in ronde.match_list:
                serialized_match = {
                    'player1': match.player1.name,
                    'player2': match.player2.name
                }
                match_ser.append(serialized_match)
            serialized_round = {
                'round_name': ronde.round_name,
                'results': ronde.results,
                'match_list': match_ser
            }
            rounds_ser.append(serialized_round)

        for player in self.players:
            serialized_player = {
                'name': player.name,
                'surname': player.surname,
                'born': player.born,
                'gender': player.gender,
                'ranking': player.ranking,
                'score': 0
                }
            players_ser.append(serialized_player)
        serialized_tournament = {
            'name': self.name,
            'place': self.place,
            'date': self.date,
            'cadence': self.cadence,
            'round': self.round,
            'rondes_instances': rounds_ser,
            'players': players_ser,
            'description': self.description,
            'turn': self.turn,
            'opponents': self.opponents
            }
        tournaments_table.insert(serialized_tournament)


class Round:
    '''
    Classe Round:
    -match_list : La liste des matchs de la ronde
    -time_start : L'heure de début
    -time_end : L'heure de fin
    -results : Une lise de [Joueur,Score] des résultats des matchs
    -round_name : Nom de la ronde
    '''
    def __init__(self, round_name, results=[], match_list=[], time_start=None):
        self.match_list = match_list
        self.time_start = time_start
        self.time_end = None
        self.results = results
        self.round_name = round_name


class Match:
    '''
    Classe Match:
    -player1 : Joueur 1
    -player2 : Joueur 2
    '''
    def __init__(self, player1, player2):
        self.score1 = player1.score
        self.score2 = player2.score
        self.player1 = player1
        self.player2 = player2
        tuple1 = [player1, self.score1]
        tuple2 = [player2, self.score2]
        self.match = (tuple1, tuple2)


class Player:
    '''Classe Joueur explicite'''
    def __init__(self, name, surname, born, gender, ranking, score=0):
        self.name = name
        self.surname = surname
        self.born = born
        self.gender = gender
        self.ranking = ranking
        self.score = score
