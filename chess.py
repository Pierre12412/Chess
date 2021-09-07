from operator import attrgetter
import time


class Tournament:
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

            # i et j sont les index des joueurs à apparier
            # dans la liste self.players
            i = 0
            while (i < len(self.players)
                    and len(self.opponents)
                    != (len(self.players)*(len(self.players)-1))/2):
                j = i
                opp = True  # Par défaut, le joueur j+1 a déjà un adversaire

                # Cas où on a déjà apparié un joueur avec un autre
                # mais on essaye de l'apparier de nouveau
                for match in roundx.match_list:
                    if (match.player1.name == self.players[i].name
                            or
                            match.player2.name
                            == self.players[i].name):
                        i += 1
                        j += 1
                        break

                # On revérifie que le dernier joueur de la liste
                # n'a pas déjà été apparié sinon i et j sont trop grands
                if i < len(self.players) and j+1 < len(self.players):
                    while (j+1 < len(self.players)) and opp:
                        if ((self.players[i].name,
                            self.players[j+1].name)
                            in self.opponents
                            or (self.players[j+1].name,
                            self.players[i].name)
                                in self.opponents):
                            j += 1
                        else:

                            # Cas où on essaye d'apparier un joueur
                            # avec un qui y est déjà avec un autre
                            for match in roundx.match_list:
                                if (match.player1.name ==
                                    self.players[j+1].name
                                    or
                                        match.player2.name
                                        == self.players[j+1].name):
                                    j += 1  # Si il a un adversaire :suivant
                                    continue
                            opp = False  # Le joueur j+1 n'a pas d'adversaire

                    match = Match(self.players[i], self.players[j+1])
                    self.opponents.append(
                        (self.players[i].name, self.players[j + 1].name)
                        )
                    print(dash)
                    print("{:^11s} {:<11s}     s'oppose à {:^11s} {:<11s}"
                          .format(self.players[i].name,
                                  self.players[i].surname,
                                  self.players[j+1].name,
                                  self.players[j+1].surname))

                    # On ajoute les matchs a la ronde x
                    roundx.match_list.append(match)

                else:
                    break

                if j == i:
                    i += 2
                else:
                    # Si le joueur suivant est déjà apparié
                    # on passe à celui d'après
                    for match in roundx.match_list:
                        while (match.player1.name == self.players[i+1].name
                               or
                               match.player2.name == self.players[i+1].name):
                            i += 1
                            if i+1 == len(self.players):
                                break
                    i += 1
            print(dash)
            # On ajoute la ronde au tournois
            self.rondes_instances.append(roundx)

    def rounds_score(self):
        '''Affiche proprement en tableau les résultats
        des rondes passées du tournois'''

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
        while self.turn != self.round:
            if self.turn == 1:
                self.switzerland()
                self.rondes_instances[0].end()
            else:
                self.switzerland()
                self.rondes_instances[self.turn-1].end()
                if (len(self.opponents)
                   == (len(self.players)*(len(self.players)-1))/2):
                    self.end_tournament()
                    break
            self.turn += 1
            # On affiche le tableau des scores
            self.rounds_score()

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


def test():
    Pierre = Player(name='Pierre',
                    surname='Bellegueule',
                    born="30/06/02",
                    gender='M',
                    ranking='1600')

    Lyse = Player(name='Lyse',
                  surname='Bellegueule',
                  born="03/12/00",
                  gender='F',
                  ranking='1199')

    Jean = Player(name='Jean',
                  surname='Kilian',
                  born="03/10/99",
                  gender='M',
                  ranking='1198')

    Marc = Player(name='Marc',
                  surname='Obsule',
                  born="22/10/99",
                  gender='M',
                  ranking='1200')

    Yves = Player(name='Yves',
                  surname='Capoera',
                  born="25/06/95",
                  gender='M',
                  ranking='2511')

    Baton = Player(name='Baton',
                   surname='Iov',
                   born="08/08/55",
                   gender='F',
                   ranking='1050')

    Michel = Player(name='Michel',
                    surname='Cours',
                    born="09/04/71",
                    gender='M',
                    ranking='1000')

    Kevin = Player(name='Kevin',
                   surname='Vanupied',
                   born="06/06/12",
                   gender='M',
                   ranking='1350')

    tournois = Tournament('Open du Touquet', "Le touquet", '04/09/2021',
                          'Blitz', 'Quelques mots pour la déscription',
                          players=[Lyse, Pierre, Jean, Marc,
                                   Yves, Baton, Michel, Kevin])
    tournois.start_tournament()


test()
