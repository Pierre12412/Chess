from operator import attrgetter
import time


class Tournament:
    def __init__(self, name, place, date, cadence, description,
                 round=4, rondes_instances=[], players=[], turn=0):
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

    def switzerland(self):
        # Met en place le système d'appariement Suisse

        while self.turn != self.round:

            # Si c'est la première ronde, on divise en deux groupes, on apparie
            if self.turn == 0:
                round0 = Round(input("Nom de la Ronde 0 : "))
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
                    round0.match_list.append(match)
                self.turn += 1
                round0.end()
            else:
                roundx = Round(input("Nom de la {}ère ronde : "
                                     .format(self.turn)))
                self.players = sorted(self.players,
                                      key=attrgetter('score', 'ranking'),
                                      reverse=True)
                i = 0
                while i != len(self.players):
                    match = Match(self.players[i], self.players[i+1])
                    roundx.match_list.append(match)
                    i += 2
                self.turn += 1
                roundx.end()

            # On affiche le tableau des scores
            self.score_array()

    def score_array(self):
        '''Affiche le tableau des scores au moment de l'appel'''

        print('---------------------------')
        for player in self.players:
            print('{}                 {}'
                  .format(player.name, player.score))
        print('---------------------------')

    def __str__(self):
        return ('{} qui a lieu à {} le {} en cadence {}'
                .format(self.name, self.place, self.date, self.cadence))


class Round:
    def __init__(self, round_name):
        self.match_list = []
        self.time_start = time.strftime('%H:%M')
        print('Heure de début de ronde : {}'.format(self.time_start))
        self.time_end = None

    def end(self):
        for match in self.match_list:
            match.result()
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
        result = input("Entrez le résultat du match "
                       "entre {} et {} "
                       "('1/2', '1-0' ou '0-1') \n"
                       .format(self.player1.name, self.player2.name))
        if result == "1/2":
            self.player1.score += 0.5
            self.player2.score += 0.5
        elif result == "1-0":
            self.player1.score += 1
        else:
            self.player2.score += 1

    def __str__(self):
        return ('Match qui oppose {} au score '
                'de {} avec {} au score de {}'
                .format(self.player1.name, self.score1,
                        self.player2.name, self.score2))


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
                  surname='Marc',
                  born="03/10/99",
                  gender='M',
                  ranking='1198')

    Marc = Player(name='Marc',
                  surname='Marc',
                  born="22/10/99",
                  gender='M',
                  ranking='1200')

    tournois = Tournament('Open du Touquet', "Le touquet", '04/09/2021',
                          'Blitz', 'Quelques mots pour la déscription',
                          players=[Lyse, Pierre, Jean, Marc])
    tournois.switzerland()


test()
