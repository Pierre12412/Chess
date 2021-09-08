from operator import attrgetter
import time
import consolemenu
from consolemenu.console_menu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem
from consolemenu.selection_menu import SelectionMenu
from tinydb import TinyDB


players = []
tournaments = []


def show_data(tournament):
    a_list=["Afficher tous les joueurs par ordre alphabétique", "- par classement", "Afficher tous les tours", "Afficher tous les matchs"]

    menu = SelectionMenu(a_list,'Tournois : {}'.format(tournament.name))

    menu.show()

    menu.join()

    selection = menu.selected_option
    dash = 20* '-'
    if selection == 0:
        list_name = []
        for player in tournament.players:
            list_name.append(player.name)
        list_name.sort()
        for name in list_name:
            print(name)
            print(dash)
    elif selection == 1:
        classement_sort = tournament.players
        classement_sort = sorted(classement_sort,
                              key=attrgetter('ranking'),
                              reverse=True)
        for player in classement_sort:
            print('{:^10}{:^10}'.format(player.name,player.ranking))
            print(dash)
    elif selection == 2:
        for round in tournament.rondes_instances:
            print(round.round_name)
            print(dash)
            for result in round.results:
                print('{:^10}{:^10}'.format(result[0],result[1]))
            print(dash)
    elif selection == 3:
        for round in tournament.rondes_instances:
            print(round.round_name)
            print(dash)
            for match in round.match_list:
                print("{} s'opposait à {}".format(match.player1.name,match.player2.name))
                print(dash)
    else:
        menu.exit()
    input()


def console_menu():
    menu = ConsoleMenu("Menu de selection", "Choisissez une option")
    function_item1 = FunctionItem('Démarrer un tournois', tournaments_informations)
    function_item2 = FunctionItem('Ajouter un joueur', add_player)

    menu_reports = ConsoleMenu("Menu de Rapports", "Choisissez un rapport")
    submenu_reports = SubmenuItem('Rapports', menu_reports,menu=menu)

    load_tournament()

    tournaments_menu = ConsoleMenu('Tournois')
    for tournament in tournaments:
        name = tournament.name
        item = FunctionItem(name, show_data, args=[tournament])
        tournaments_menu.append_item(item)
    submenu_item = SubmenuItem("Menu des tournois", tournaments_menu, menu=menu_reports)

    menu_reports.append_item(submenu_item)

    menu.append_item(function_item1)
    menu.append_item(function_item2)
    menu.append_item(submenu_reports)
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
        if ((player1.name,player2.name) in self.opponents) or ((player2.name,player1.name) in self.opponents):
            return False
        for match in round.match_list:
            if match.player1.name == player1.name or match.player2.name == player2.name:
                return False
            if match.player2.name == player1.name or match.player1.name == player2.name:
                return False
        in_opp = (player1.name, player2.name) in self.opponents
        in_opp2 = (player2.name, player1.name) in self.opponents
        return not (in_opp or in_opp2)

    def switzerland(self):
        dash = 60*'-'
        '''Met en place le système d'appariement Suisse'''

        # Si c'est la première ronde, on divise en deux groupes, on apparie
        if self.turn == 1:
            round0 = Round(round_name=str(input("Nom de la Ronde 1 : ")),match_list=[],results=[])
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
                                     .format(self.turn))),match_list=[],results=[])
            self.players = sorted(self.players,
                                  key=attrgetter('score', 'ranking'),
                                  reverse=True)
            
            if roundx.round_name == 'Ronde 3':
                self.save_tournament()
                exit()
            # On apparie les joueurs par score
            actual = 0
            while actual < len(self.players) and actual + 1 < len(self.players):
                next = actual + 1
                matched = False
                while matched == False and (next < len(self.players)):
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
            if len(roundx.match_list) != (len(self.players)/2):
                print('Problème')
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
        self.save_tournament()
        console_menu()

    def save_tournament(self):
        db = TinyDB('db.json')
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

        for player in players:
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
    def __init__(self, round_name, results=[], match_list=[]):
        self.match_list = match_list
        self.time_start = time.strftime('%H:%M')
        print('Heure de début de ronde : {}'.format(self.time_start))
        self.time_end = None
        self.results = results
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
            'score': player.score
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
        score = serial['score']
        players.append(Player(name, surname, born, gender, ranking,score))


def load_tournament():
    db = TinyDB('db.json')
    tournaments_table = db.table('tournaments')
    players_no_ser = []
    round_no_ser = []
    match_no_ser = []
    serialized_tournaments = tournaments_table.all()
    for serial in serialized_tournaments:
        place = serial['place']
        date = serial['date']
        cadence = serial['cadence']
        round = serial['round']
        rondes_instances = serial['rondes_instances']
        round_no_ser = []
        for ronde in rondes_instances:
            match_no_ser = []
            round_name = ronde['round_name']
            results = ronde['results']
            match_list = ronde['match_list']
            for match in match_list:
                for player in players:
                    if match['player1'] == player.name:
                        player1 = player
                    if match['player2'] == player.name:
                        player2 = player
                match_no_ser.append(Match(player1,player2))
            round_no_ser.append(Round(round_name,results,match_list=match_no_ser))
        players_ser = serial['players']
        players_no_ser = []
        for serial_p in players_ser:
            name = serial_p['name']
            surname = serial_p['surname']
            born = serial_p['born']
            gender = serial_p['gender']
            ranking = serial_p['ranking']
            score = serial_p['score']
            players_no_ser.append(Player(name,surname,born,gender,ranking,score))
        name = serial['name']
        description = serial['description']
        turn = serial['turn']
        opponents = serial['opponents']
        tournaments.append(Tournament(name,place,date,cadence,description,round,round_no_ser,players_no_ser,turn,opponents))


def start():
    load_players()
    console_menu()


def tournaments_informations():
    if len(players) < 4:
        print('Trop peu de gens pour faire un tournois...')
        input()
        console_menu()
    name = str(input('Nom du tournois\n'))
    place = str(input('Lieu du tournois\n'))
    date = str(input('Date du tournois \n'))
    cadence = str(input('Cadence du tournois\n'))
    description = str(input('Description du tournois\n'))
    tournois = Tournament(name, place, date, cadence, description,rondes_instances=[])
    tournois.start_tournament()


start()


