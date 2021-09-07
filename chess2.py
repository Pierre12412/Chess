from operator import attrgetter, xor
import time
from consolemenu.console_menu import ConsoleMenu
from consolemenu.items import FunctionItem
from tinydb import TinyDB


players = []


def console_menu():
    menu = ConsoleMenu("Menu de selection", "Choisissez une option")
    function_item1 = FunctionItem('Démarrer un tournois', tournaments_informations)
    function_item2 = FunctionItem('Ajouter un joueur', add_player)
    menu.append_item(function_item1)
    menu.append_item(function_item2)
    menu.show()


class Tournament:
    def __init__(self, name, place, date, cadence, description,
                 round=5, rondes_instances=[], players=players, turn=1,
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
        in_opp = (player1.name, player2.name) in self.opponents
        in_opp2 = (player2.name, player1.name) in self.opponents
        return not in_opp or in_opp2

    def switzerland(self):
        dash = 60*'-'
        '''Met en place le système d'appariement Suisse'''

        # Si c'est la première ronde, on divise en deux groupes, on apparie
        if self.turn == 1:
            round0 = Round(round_name=str(input("Nom de la Ronde 1 : ")))
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
                    (first_part[i].name, second_part[i].name)
                    )
                print(dash)
                print("{:^11s} {:<11s}     s'oppose à {:^11s} {:<11s}"
                      .format(first_part[i].name, first_part[i].surname,
                              second_part[i].name, second_part[i].surname))

                # On ajoute les matchs a la ronde 1
                round0.match_list.append(match)
            # On ajoute la ronde au tournois
            self.rondes_instances.append(round0)
            print(dash)

        else:
            roundx = Round(str(input("Nom de la {}ème ronde : "
                                     .format(self.turn))))
            self.players = sorted(self.players,
                                  key=attrgetter('score', 'ranking'),
                                  reverse=True)
            # On apparie les joueurs par score
            actual = 0
            while actual < len(self.players) and actual + 1 < len(self.players):
                next = actual + 1
                matched = False
                while matched == False:
                    if self.conditions_duo(self.players[actual], self.players[next], roundx):
                        matched = True
                        match = Match(self.players[actual], self.players[next])

                        # On ajoute les matchs a la ronde x
                        roundx.match_list.append(match)
                        self.opponents.append(
                            (self.players[actual].name, self.players[next].name)
                            )
                        print(dash)
                        print("{:^11s} {:<11s}     s'oppose à {:^11s} {:<11s}"
                            .format(self.players[actual].name,
                                    self.players[actual].surname,
                                    self.players[next].name,
                                    self.players[next].surname))
                    else:
                        next += 1

                if next == actual + 1:
                    actual += 2
                else:
                    actual += 1
            print(dash)
            # On ajoute la ronde au tournois
            self.rondes_instances.append(roundx)


    def rounds_score(self):
        '''Affiche proprement en tableau les résultats
        des rondes passées du tournois

        Prend la liste des joueurs et celle des instances de rondes'''

        dash = '-' * (11 * (len(self.rondes_instances)+1) + 15)

        self.players = sorted(self.players,
                              key=attrgetter('score', 'ranking'),
                              reverse=True)

        # Première ligne, on affiche l'en-tête : le nom de(s) ronde(s) et Total
        print('{:>10s}'.format(' '), end=' |')
        for round in self.rondes_instances:
            print('{:^11s}'.format(round.round_name), end='|')
        print('{:^11s}'.format('Total'), end='|')
        print('\n', dash)

        # On affiche le résultat de chaque joueur dans chaque ronde
        for player in self.players:
            round_index = 0
            for round in self.rondes_instances:
                for name_score in round.results:
                    if player.name == name_score[0] and round_index == 0:
                        print('{:<10s}{:>3s}{:^9s}'
                              .format(
                               name_score[0], ' | ', str(name_score[1])),
                              end=' | ')
                        round_index += 1
                    else:
                        if player.name == name_score[0]:
                            print('{:^9s}'
                                  .format(str(name_score[1])), end=' | ')
            print('{:^9s}'.format(str(player.score)), end=' | ')
            print('\n', dash)

    def start_tournament(self):
        '''Démarre le tournois et apparie'''
        while self.turn != self.round:
            if self.turn == 1:
                self.switzerland()
                self.rondes_instances[0].end()
            else:
                self.switzerland()
                self.rondes_instances[self.turn-1].end()

                # Nombre d'appariements max pour un nombre de personne
                # Pour 4 : (4*3)/2 = 6 couples possibles
                if (len(self.opponents)
                   == (len(self.players)*(len(self.players)-1))/2):
                    self.end_tournament()
                    break

            self.turn += 1
            # On affiche le tableau des scores
            self.rounds_score()
        self.end_tournament()

    def end_tournament(self):
        '''Messages et affichage de fin de tournois'''

        self.players = sorted(self.players,
                              key=attrgetter('score', 'ranking'),
                              reverse=True)
        print('Fin du tournois, voici le tableau des scores : ')
        self.rounds_score()
        i = 0
        if self.players[i].score == self.players[i+1].score:
            while (i+1 != len(self.players)) and (
                self.players[i].score == self.players[i+1].score
            ):
                if i == 0:
                    print('Félicitations aux gagnants {}, {}'
                          .format
                          (self.players[i].name, self.players[i+1].name),
                          end='')
                    i += 1
                else:
                    print(', ' + self.players[i+1].name, end='')
                    i += 1
        else:
            print('Félicitations au gagnant : {} {}'
                  .format(self.players[0].name, self.players[0].surname))
        input()


class Round:
    def __init__(self, round_name, results=[]):
        self.match_list = []
        self.time_start = time.strftime('%H:%M')
        print('Heure de début de ronde : {}'.format(self.time_start))
        self.time_end = None
        self.results = []
        self.round_name = round_name

    def end(self):
        '''Demande le résultat de tout les matchs de la ronde actuelle'''
        input('Appuyez sur une entrée pour rentrer les résultats...\n')
        for match in self.match_list:
            (result_1, result_2) = match.result()
            self.results.append([match.player1.name, result_1])
            self.results.append([match.player2.name, result_2])
        self.time_end = time.strftime('%H:%M')
        print('Heure de fin de ronde : {}'.format(self.time_end))


class Match:
    def __init__(self, player1, player2):
        self.score1 = player1.score
        self.score2 = player2.score
        self.player1 = player1
        self.player2 = player2
        tuple1 = [player1, self.score1]
        tuple2 = [player2, self.score2]
        self.match = (tuple1, tuple2)

    def result(self):
        '''Demande le résultat du match actuel'''
        while True:
            result = str(input("Entrez le résultat du match "
                               "entre {} et {} "
                               "('1/2', '1-0' ou '0-1') \n"
                               .format(self.player1.name, self.player2.name)))
            if result == "1/2":
                self.player1.score += 0.5
                self.player2.score += 0.5
                return (0.5, 0.5)
            elif result == "1-0":
                self.player1.score += 1
                return (1, 0)
            elif result == '0-1':
                self.player2.score += 1
                return (0, 1)
            else:
                print("Ce n'est pas un résultat valide, réessayez")
                continue


class Player:
    def __init__(self, name, surname, born, gender, ranking, score=0):
        self.name = name
        self.surname = surname
        self.born = born
        self.gender = gender
        self.ranking = ranking
        self.score = score


def save_players(players=players):
    db = TinyDB('db.json')
    players_table = db.table('players')
    players_table.truncate()  
    for player in players:
        serialized_player = {
            'name': player.name,
            'surname': player.surname,
            'born': player.born,
            'gender': player.gender,
            'ranking': player.ranking,
            'score': 0
            }
        players_table.insert(serialized_player)


def add_player():
    name = str(input('Prénom du joueur à ajouter \n'))
    surname = str(input('Nom du joueur à ajouter\n'))
    born = str(input('Date de naissance du joueur à ajouter\n'))
    gender = str(input("Genre du joueur à ajouter ('M' ou 'F')\n"))
    ranking = str(input("Classement du joueur à ajouter\n"))
    new = Player(name=name, surname=surname, born=born,
                 gender=gender, ranking=ranking)
    players.append(new)
    save_players()


def load_players():
    db = TinyDB('db.json')
    players_table = db.table('players')
    serialized_players = players_table.all()
    for serial in serialized_players:
        name = serial['name']
        surname = serial['surname']
        born = serial['born']
        gender = serial['gender']
        ranking = serial['ranking']
        players.append(Player(name, surname, born, gender, ranking))


def start():
    load_players()
    console_menu()


def tournaments_informations():
    name = str(input('Nom du tournois\n'))
    place = str(input('Lieu du tournois\n'))
    date = str(input('Date du tournois \n'))
    cadence = str(input('Cadence du tournois'))
    description = str(input('Description du tournois'))
    tournois = Tournament(name, place, date, cadence, description)
    tournois.start_tournament()


start()


# tournois = Tournament('Open du Touquet', "Le touquet", '04/09/2021',
#                       'Blitz', 'Quelques mots pour la déscription',
#                       players=[Lyse, Pierre, Jean, Marc,
#                                Yves, Baton, Michel, Kevin])

# def test():
#     Pierre = Player(name='Pierre',
#                     surname='Bellegueule',
#                     born="30/06/02",
#                     gender='M',
#                     ranking='1600')

#     Lyse = Player(name='Lyse',
#                   surname='Bellegueule',
#                   born="03/12/00",
#                   gender='F',
#                   ranking='1199')

#     Jean = Player(name='Jean',
#                   surname='Kilian',
#                   born="03/10/99",
#                   gender='M',
#                   ranking='1198')

#     Marc = Player(name='Marc',
#                   surname='Obsule',
#                   born="22/10/99",
#                   gender='M',
#                   ranking='1200')

#     Yves = Player(name='Yves',
#                   surname='Capoera',
#                   born="25/06/95",
#                   gender='M',
#                   ranking='2511')

#     Baton = Player(name='Baton',
#                    surname='Iov',
#                    born="08/08/55",
#                    gender='F',
#                    ranking='1050')

#     Michel = Player(name='Michel',
#                     surname='Cours',
#                     born="09/04/71",
#                     gender='M',
#                     ranking='1000')

#     Kevin = Player(name='Kevin',
#                    surname='Vanupied',
#                    born="06/06/12",
#                    gender='M',
#                    ranking='1350')



# tournois.start_tournament()
