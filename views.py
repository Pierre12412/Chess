from consolemenu.console_menu import ConsoleMenu
from consolemenu.items import FunctionItem
from consolemenu.selection_menu import SelectionMenu
from operator import attrgetter


def ask_tournament():
    '''Demande les informations nécessaires pour débuter un tournois'''
    print('Tournois de 4 Rondes')
    print('Vous pouvez quitter à tout moment en tappant exit')

    while True:
        try:
            name = str(input('Nom du tournois\n'))
            if name == '':
                raise ValueError
            place = str(input('Lieu du tournois\n'))
            if place == '':
                raise ValueError
            date = str(input('Date du tournois \n'))
            if date == '':
                raise ValueError
            cadence = str(input('Cadence du tournois\n'))
            if cadence == '':
                raise ValueError
            description = str(input('Description du tournois\n'))
            break
        except ValueError:
            print("Réponse non valide")
    return (date, place, name, cadence, description, 4)


def ask_players(players):
    while True:
        res = []
        names = []
        for player in players:
            names.append(player.name)
        names.append('Ok')
        while 'Ok' in names or len(res) < 8:
            participants = 'Les participants actuellement sont :'
            if len(res) == 0:
                participants += ' Personne '
            else:
                i = 0
                for player in res:
                    i += 1
                    if i % 5 == 0 and i != 0:
                        participants += '\n'
                    participants += ' {},'.format(player.name)
            menu = SelectionMenu(names, participants)
            menu.show(show_exit_option=False)
            menu.join()
            selection = menu.selected_option
            menu.exit()
            for player in players:
                if player.name == names[selection]:
                    res.append(player)
            if (names[selection] == 'Ok' and len(res) < 8):
                continue
            names.remove(names[selection])
        menu.exit()
        if len(res) % 2 == 1:
            print("Nombre de personne impair, réctifiez !")
            input()
            continue
        else:
            return res


def console_menu(tournaments_informations, add_player,
                 del_player, resume_tournament, show_console_tournament,
                 players):
    '''Menu Principal'''

    menu = ConsoleMenu("Menu de selection", "Choisissez une option")
    function_item1 = FunctionItem('Démarrer un tournois',
                                  tournaments_informations, should_exit=True)
    function_item3 = FunctionItem('Ajouter un joueur', add_player)
    function_item5 = FunctionItem('Liste des joueurs',
                                  show_players, args=[players])
    function_item4 = FunctionItem('Supprimer un joueur', del_player)

    submenu_reports = FunctionItem('Rapports', show_console_tournament)

    function_item2 = FunctionItem('Reprendre un tournois', resume_tournament)

    menu.append_item(function_item1)
    menu.append_item(function_item2)
    menu.append_item(function_item3)
    menu.append_item(function_item4)
    menu.append_item(function_item5)
    menu.append_item(submenu_reports)
    menu.should_exit = True
    menu.show()


def ask_selection_resume(names):
    menu = SelectionMenu(names, 'Quel tournois continuer ?')
    menu.should_exit = True
    menu.show()
    return menu.selected_option


def ask_console_tournament(tournaments, selection_menu_report,
                           remove_tournament):
    tournaments_menu = ConsoleMenu('Tournois')
    for tournament in tournaments:
        name = tournament.name
        item = FunctionItem(name, selection_menu_report, args=[tournament])
        tournaments_menu.append_item(item)
    tournaments_menu.append_item(FunctionItem('Supprimer un tournois',
                                              remove_tournament,
                                              should_exit=True))
    tournaments_menu.show()


def selection_menu_report(tournament):

    func_dict = {
        0: display_players_infos,
        1: display_players_sorted,
        2: display_round_results,
        3: display_matches
    }

    print(tournament.description, '\n'*3)
    a_list = ["Afficher tous les joueurs par ordre alphabétique",
              "- par classement",
              "Afficher tous les tours",
              "Afficher tous les matchs"]
    menu = SelectionMenu(a_list, 'Le tournois à eu lieu à {} le '
                                 '{} en cadence {}'
                                 .format(tournament.place,
                                         tournament.date,
                                         tournament.cadence))
    menu.show()
    menu.join()
    selection = menu.selected_option
    if selection in range(0, 4):
        func_dict[selection](tournament)
    else:
        menu.exit()


def display_players_infos(tournament):
    dash = 100 * '-'
    list_name = []
    for player in tournament.players:
        list_name.append(player.name)
    list_name.sort()
    print('{:^10}{:^20}{:^20}{:^10}{:^10}'
          .format('Prénom', 'Nom', 'Naissance',
                  'Genre', 'Classement'))
    print(dash)
    for name in list_name:
        for player in tournament.players:
            if player.name == name:
                print('{:^10}{:^20}{:^20}{:^10}{:^10}'
                      .format(player.name,
                              player.surname,
                              player.born,
                              player.gender,
                              player.ranking))
                print(dash)
    input()


def display_players_sorted(tournament):
    dash = 100 * '-'
    classement_sort = tournament.players
    classement_sort = sorted(classement_sort,
                             key=attrgetter('ranking'),
                             reverse=True)
    print('{:^10}{:^20}{:^20}{:^10}{:^20}'
          .format('Prénom', 'Nom', 'Naissance',
                  'Genre', 'Classement'))
    print(dash)
    for player in classement_sort:
        print('{:^10}{:^20}{:^20}{:^10}{:^20}'
              .format(player.name,
                      player.surname,
                      player.born,
                      player.gender,
                      player.ranking))
        print(dash)
    input()


def display_round_results(tournament):
    dash = 100 * '-'
    for round in tournament.rondes_instances:
        print(dash)
        for result in round.results:
            print('{:^10}{:^10}'.format(result[0], result[2]))
        print(dash)
    input()


def display_matches(tournament):
    dash = 100 * '-'
    for round in tournament.rondes_instances:
        print(round.round_name)
        print(dash)
        for match in round.match_list:
            print("{} s'opposait à {}".format(
                    match.player1.name, match.player2.name)
                  )
            print(dash)
    input()


def show_players(players):
    dash = '-'*100
    print(dash)
    print('{:^10}{:^20}{:^20}{:^10}{:^20}'.format('Prénom', 'Nom', 'Naissance',
                                                  'Genre', 'Classement'))
    print(dash)
    for player in players:
        print('{:^10}{:^20}{:^20}{:^10}{:^20}'.format(player.name,
                                                      player.surname,
                                                      player.born,
                                                      player.gender,
                                                      player.ranking))
        print(dash)
    input('Appuyez sur entrée pour revenir au menu principal')


def delete_player_console(names):
    menu = SelectionMenu(names, 'Quel joueur supprimer ?')
    menu.show()
    menu.join()
    return (menu.selected_option, menu)


def delete_tournament_console(names):
    menu = SelectionMenu(names, 'Quel tournois à supprimer ?')
    menu.show()
    return menu.selected_option


def informations_player_console():
    while True:
        try:
            name = str(input('Prénom du joueur à ajouter \n'))
            if name == '':
                raise ValueError
            surname = str(input('Nom du joueur à ajouter\n'))
            if surname == '':
                raise ValueError
            born = str(input('Date de naissance du joueur à ajouter\n'))
            if born == '':
                raise ValueError
            gender = str(input("Genre du joueur à ajouter ('M' ou 'F')\n"))
            if gender == '':
                raise ValueError
            ranking = int(input("Classement du joueur à ajouter\n"))
            if ranking == '':
                raise ValueError
            break
        except ValueError:
            print('Information obligatoire ou incorrecte, veuillez réessayer')
    return (name, surname, born, gender, ranking)


def rounds_score(tournament):
    '''Affiche proprement en tableau les résultats
    des rondes passées du tournois

    Utilise la liste des joueurs et celle des instances de rondes'''

    dash = '-' * (11 * (len(tournament.rondes_instances)+1) + 30)

    tournament.players = sorted(tournament.players,
                                key=attrgetter('score', 'ranking'),
                                reverse=True)

    # Première ligne, on affiche l'en-tête : le nom de(s) ronde(s) et Total
    print('{:>23s}'.format(' '), end=' |')
    for round in tournament.rondes_instances:
        print('{:^11s}'.format(round.round_name), end='|')
    print('{:^11s}'.format('Total'), end='|')
    print('\n', dash)

    # On affiche le résultat de chaque joueur dans chaque ronde
    for player in tournament.players:
        round_index = 0
        for round in tournament.rondes_instances:
            for name_score in round.results:
                if (player.name == name_score[0]
                        and player.surname == name_score[1]
                        and round_index == 0):
                    print('{:<10s}{:>3s}{:<10s}{:>3s}{:^9s}'
                          .format(
                           name_score[0], ' | ', name_score[1], ' | ',
                           str(name_score[2])),
                          end=' | ')
                    round_index += 1
                else:
                    if (player.name == name_score[0]
                            and player.surname == name_score[1]):
                        print('{:^9s}'
                              .format(str(name_score[2])), end=' | ')
        print('{:^9s}'.format(str(player.score)), end=' | ')
        print('\n', dash)


def tournament_score(tournament):
    print('Fin du tournois, voici le tableau des scores : ')
    rounds_score(tournament)
    i = 0
    if tournament.players[i].score == tournament.players[i+1].score:
        while (i+1 != len(tournament.players)) and (
            tournament.players[i].score == tournament.players[i+1].score
        ):
            if i == 0:
                print('Félicitations aux gagnants {}, {}'
                      .format
                      (tournament.players[i].name,
                       tournament.players[i+1].name),
                      end='')
                i += 1
            else:
                print(', ' + tournament.players[i+1].name, end='')
                i += 1
    else:
        print('Félicitations au gagnant : {} {}'
              .format(tournament.players[0].name,
                      tournament.players[0].surname))
    input()


def display_player_tournament_error(tournament):
    print('Vous ne pouvez pas supprimer ce joueur, '
          'il fait parti du tournois : {}'
          .format(tournament.name))
    print('Supprimez le tournois dans la base de donnée '
          'pour supprimer ce joueur')
    input()


def resume_round_display(round):
    dash = 50*'-'
    print('Reprise au round : {}'.format(round.round_name))
    print('\n')
    print(dash)
    for match in round.match_list:
        print('{:^13}{:^13}{:^13}'.format(
                                        match.player1.name,
                                        "s'oppose à",
                                        match.player2.name))
        print(dash)
    input('Appuyez sur une entrée pour rentrer les résultats...\n')


def ask_results(match):
    '''Demande le résultat du match actuel'''
    while True:
        result = str(input("Entrez le résultat du match "
                           "entre {} et {} "
                           "('1/2', '1-0' ou '0-1') \n"
                           .format(match.player1.name,
                                   match.player2.name)))
        if result == "1/2":
            match.player1.score += 0.5
            match.player2.score += 0.5
            return (0.5, 0.5)
        elif result == "1-0":
            match.player1.score += 1
            return (1, 0)
        elif result == '0-1':
            match.player2.score += 1
            return (0, 1)
        elif result == 'exit':
            return(-1, -1)
        else:
            print("Ce n'est pas un résultat valide, réessayez")
            continue


def tournament_error_display():
    print('Trop peu de gens pour faire un tournois...')
    input()


def ask_name(number_round: int):
    return str(input("Nom de la Ronde {} : ".format(number_round)))


def match_array(first_part, second_part):
    dash = 60*'-'
    for i in range(len(first_part)):
        print(dash)
        print("{:^11s} {:<11s}     s'oppose à {:^11s} {:<11s}"
              .format(first_part[i].name, first_part[i].surname,
                      second_part[i].name, second_part[i].surname))
    print(dash)
    input('Appuyez sur une entrée pour rentrer les résultats...\n')


def print_time(startend, time):
    if startend == 'start':
        print('Heure de début de ronde : {}'.format(time))
    else:
        print('Heure de fin de ronde : {}'.format(time))


def raise_exit_error():
    print("Vous ne pouvez pas sortir d'un tournois non créé")
