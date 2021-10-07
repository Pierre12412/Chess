from consolemenu.console_menu import ConsoleMenu
from consolemenu.items import FunctionItem
from consolemenu.selection_menu import SelectionMenu
from operator import attrgetter


def ask_tournament(players):
    '''Demande les informations nécessaires pour débuter un tournois'''

    print('Vous pouvez quitter à tout moment en tappant exit \n')
    while True:
        try:
            nb_round = int(input('Combien de rondes voulez-vous ?'
                                 ' {} rondes possibles \n'
                                 .format(str(len(players)-1))))
            if nb_round > len(players)-1 or nb_round < 0:
                raise ValueError
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
    return (date, place, name, cadence, description, nb_round)


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
    dash = 100 * '-'
    if selection == 0:
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
    elif selection == 1:
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
    elif selection == 2:
        for round in tournament.rondes_instances:
            print(round.round_name)
            print(dash)
            for result in round.results:
                print('{:^10}{:^10}'.format(result[0], result[2]))
            print(dash)
        input()
    elif selection == 3:
        for round in tournament.rondes_instances:
            print(round.round_name)
            print(dash)
            for match in round.match_list:
                print("{} s'opposait à {}".format(
                     match.player1.name, match.player2.name)
                     )
                print(dash)
        input()
    else:
        menu.exit()
        ask_console_tournament()


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
