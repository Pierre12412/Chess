from operator import attrgetter
import time
from tinydb import TinyDB, where

from models import Player, Tournament, Match, Round
from views import (ask_players, ask_tournament, console_menu,
                   ask_selection_resume,
                   ask_console_tournament, display_player_tournament_error,
                   match_array, ask_results, print_time, raise_exit_error,
                   resume_round_display, selection_menu_report,
                   delete_player_console, informations_player_console,
                   delete_tournament_console, rounds_score,
                   tournament_error_display, tournament_score,
                   ask_name)

# Ensemble des joueurs (chargés au démarrage)
players = []
# Ensemble des tournois (chargés au démarrage)
tournaments = []


def show_console_tournaments():
    global tournaments
    tournaments = []
    load_tournament()
    ask_console_tournament(tournaments, selection_menu_report,
                           remove_tournament)


def save_players():
    '''Sauvegarde les joueurs de la liste "players"'''
    global players
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
    '''Créer un joueur'''
    (name, surname, born,
     gender, ranking) = informations_player_console()
    new = Player(name=name, surname=surname, born=born,
                 gender=gender, ranking=ranking)
    players.append(new)
    save_players()


def del_player():
    '''Supprime un joueur si il n'est pas lié
    à un tournois en base de donnée'''

    can_delete = True
    while True:
        db = TinyDB('db.json')
        players_table = db.table('players')
        names = []
        for player in players:
            names.append(player.name)
        (selection, menu) = delete_player_console(names)
        if selection == len(players):
            menu.exit()
        else:
            for tournament in tournaments:
                for player in tournament.players:
                    if player.name == players[selection].name:
                        display_player_tournament_error(tournament)
                        can_delete = False
            if can_delete:
                players_table.remove(where('name') == names[selection])
                players.pop(selection)
            else:
                continue
        break


def load_players():
    '''Charge tout les joueurs vers la liste "players"
    depuis la base de donnée'''

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
        players.append(Player(name, surname, born, gender, ranking, score))


def load_tournament():
    '''Charge les tournois vers la liste tournaments
    depuis la base de donnée'''

    db = TinyDB('db.json')
    tournaments_table = db.table('tournaments')
    players_no_ser = []
    round_no_ser = []
    player1 = None
    player2 = None
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
                match_no_ser.append(Match(player1, player2))
            round_no_ser.append(Round(round_name,
                                      results,
                                      match_list=match_no_ser))
        players_ser = serial['players']
        players_no_ser = []
        for serial_p in players_ser:
            name = serial_p['name']
            surname = serial_p['surname']
            born = serial_p['born']
            gender = serial_p['gender']
            ranking = serial_p['ranking']
            score = serial_p['score']
            players_no_ser.append(Player(name,
                                         surname,
                                         born,
                                         gender,
                                         ranking,
                                         score))
        name = serial['name']
        description = serial['description']
        turn = serial['turn']
        opponents = serial['opponents']
        tournaments.append(Tournament(name, place,
                                      date, cadence,
                                      description, round,
                                      round_no_ser, players_no_ser,
                                      turn, opponents))


def remove_tournament():
    '''Supprime un tournois de la base de donnée avec un affichage console'''
    global tournaments
    names = []
    for tournament in tournaments:
        names.append(tournament.name)
    selection = delete_tournament_console(names)
    db = TinyDB('db.json')
    table = db.table('tournaments')
    try:
        table.remove(where('name') == names[selection])
        tournaments.pop(selection)
    except IndexError:
        pass
    show_console_tournaments()


def del_tournament(tournament):
    '''Supprime un tournois de la base de donnée sans affichage console'''
    db = TinyDB('db.json')
    table = db.table('tournaments')
    table.remove(where('name') == tournament.name)
    for i in range(len(tournaments)-1):
        if tournaments[i].name == tournament.name:
            tournaments.pop(i)


def resume_tournament():
    '''Permet de reprendre un tournois'''
    names = []
    selections = []
    global tournaments
    tournaments = []
    load_tournament()
    for tournament in tournaments:
        finish = True
        for round in tournament.rondes_instances:
            if len(round.results) != len(tournament.players):
                finish = False
        if len(tournament.rondes_instances) != tournament.round or not finish:
            names.append(tournament.name)
            selections.append(tournament)
    selection = ask_selection_resume(names)

    try:
        to_continue = selections[selection]
        for round in to_continue.rondes_instances:
            for result in round.results:
                [name, surname, score] = result
                for player in to_continue.players:
                    if player.name == name:
                        player.score += score
        for round in to_continue.rondes_instances:
            if (len(round.results) != len(to_continue.players)
               or (len(round.results) == 0 and round.round_name is not None)):
                resume_round_display(round)
                exit_yor = end_round(to_continue, round)
                if exit_yor == 'exit':
                    exit()
                else:
                    to_continue.turn += 1
                    start_tournament(to_continue)
            elif (len(to_continue.rondes_instances) != to_continue.round
                  and round == to_continue.rondes_instances[-1]):
                if len(round.results) < len(to_continue.players):
                    resume_round_display(round)
                    exit_yor = end_round(to_continue, round)
                    if exit_yor == 'exit':
                        exit()
                else:
                    start_tournament(to_continue)
    except IndexError:
        pass


def start_tournament(tournament):
    '''Démarre le tournois et apparie'''
    while (tournament.turn != tournament.round+1 and
           tournament.turn != len(tournament.players)):
        exit_yorn2 = switzerland(tournament)
        exit_yorn = None
        if tournament.turn == 1 and exit_yorn2 != 'exit':
            exit_yorn = end_round(tournament, tournament.rondes_instances[0])
        else:
            if exit_yorn2 != 'exit':
                exit_yorn = (end_round(tournament, tournament
                             .rondes_instances[tournament.turn-1]))
        if exit_yorn == 'exit' or exit_yorn2 == 'exit':
            del_tournament(tournament)
            tournament.save_tournament(db=TinyDB('db.json'))
            exit()

            # Nombre d'appariements max pour un nombre de personne
            # Pour 4 : (4*3)/2 = 6 couples possibles
        if (len(tournament.opponents)
                == (len(tournament.players)*(len(tournament.players)-1))/2):
            end_tournament(tournament)
            break

        tournament.turn += 1
        # On affiche le tableau des scores
        rounds_score(tournament)
    end_tournament(tournament)


def end_round(tournament, round):
    exit_yor = ask_result(round)
    if exit_yor != 'exit':
        round.time_end = time.strftime('%H:%M')
        print_time('end', round.time_end)
    else:
        del_tournament(tournament)
        tournament.save_tournament(db=TinyDB('db.json'))
        return exit_yor


def end_tournament(tournament):
    '''Messages et affichage de fin de tournois'''

    tournament.players = sorted(tournament.players,
                                key=attrgetter('score', 'ranking'),
                                reverse=True)
    tournament_score(tournament)
    del_tournament(tournament)
    tournament.save_tournament(db=TinyDB('db.json'))
    for player in tournament.players:
        player.score = 0
    console_menu(tournaments_informations, add_player,
                 del_player, resume_tournament, show_console_tournaments,
                 players)


def tournaments_informations():
    '''Créer un tournois'''
    global players
    if len(players) < 8:
        tournament_error_display()
        console_menu(tournaments_informations, add_player,
                     del_player, resume_tournament,
                     show_console_tournaments, players)
    infos = ask_tournament()
    player = ask_players(players)
    (date, place, name, cadence, description, nb_round) = infos
    tournois = Tournament(name, place,
                          date, cadence,
                          description, rondes_instances=[],
                          round=nb_round, players=player,
                          opponents=[])
    start_tournament(tournois)


def switzerland(tournament):
    '''Met en place le système d'appariement Suisse'''
    # Si c'est la première ronde, on divise en deux groupes, on apparie
    if tournament.turn == 1:
        while True:
            name = ask_name(tournament.turn)
            if name == 'exit':
                raise_exit_error()
                continue
            break
        time_start = time.strftime('%H:%M')
        print_time('start', time_start)
        fs = tournament.start_first_round(name, time_start)
        (first_part, second_part) = fs
        match_array(first_part, second_part)
    else:
        name = ask_name(tournament.turn)
        time_start = time.strftime('%H:%M')
        exit = tournament.start_x_round(name, time_start)
        if exit != 'exit':
            (first_part, second_part) = exit
            match_array(first_part, second_part)
        return exit


def ask_result(round):
    for match in round.match_list:
        already_played = False
        for result in round.results:
            [name, surname, score] = result
            if ((name == match.player1.name and
                surname == match.player1.surname)
                or
                (name == match.player2.name and
                    match.player2.surname == surname)):
                already_played = True
        if not already_played:
            (result_1, result_2) = ask_results(match)
            if result_1 == -1:
                return 'exit'
            round.results.append([match.player1.name,
                                  match.player1.surname, result_1])
            round.results.append([match.player2.name,
                                  match.player2.surname, result_2])


def start():
    '''Démarre le programme'''
    load_players()
    load_tournament()
    console_menu(tournaments_informations, add_player,
                 del_player, resume_tournament,
                 show_console_tournaments, players)


start()
