import argparse
from argparse import RawDescriptionHelpFormatter as rawhelp
from glpic import Glpi
from glpic import error, handle_parameters, info
import os
from prettytable import PrettyTable
import sys
from textwrap import fill

PARAMHELP = "specify parameter or keyword for rendering (multiple can be specified)"


def confirm(message):
    message = f"{message} [y/N]: "
    try:
        _input = input(message)
        if _input.lower() not in ['y', 'yes']:
            error("Leaving...")
            sys.exit(1)
    except:
        sys.exit(1)
    return


def container_path(path):
    if os.path.exists('/i_am_a_container'):
        if path == '.':
            return '/workdir'
        elif not os.path.isabs(path):
            return f'/workdir/{path}'
    return path


def get_subparser_print_help(parser, subcommand):
    subparsers_actions = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == subcommand:
                subparser.print_help()
                return


def get_subparser(parser, subcommand):
    subparsers_actions = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == subcommand:
                return subparser


def create_reservation(args):
    glpic = Glpi(args.url, args.user, args.token)
    overrides = handle_parameters(args.param)
    computer = args.computer or overrides.get('computer')
    if computer is None:
        error("Missing computer")
        sys.exit(1)
    info(f"Creating reservation for computer {computer}")
    glpic.create_reservation(computer, overrides)


def delete_reservation(args):
    yes = args.yes
    yes_top = args.yes_top
    if not yes and not yes_top:
        confirm("Are you sure?")
    glpic = Glpi(args.url, args.user, args.token)
    for reservation in args.reservations:
        info(f"Deleting reservation {reservation}")
        glpic.delete_reservation(reservation)


def update_reservation(args):
    glpic = Glpi(args.url, args.user, args.token)
    overrides = handle_parameters(args.param)
    reservations = args.reservations
    if not reservations:
        reservations = [r['id'] for r in glpic.list_reservations(overrides=overrides)]
    for reservation in reservations:
        info(f"Updating reservation {reservation}")
        glpic.update_reservation(reservation, overrides=overrides)


def info_computer(args):
    glpic = Glpi(args.url, args.user, args.token)
    overrides = {'computer': args.computer} if args.computer is not None else {}
    overrides.update(handle_parameters(args.param))
    data = glpic.info_computer(overrides)
    for computer in data:
        for key in computer:
            print(f"{key}: {computer[key]}")
        print('-----------------')


def info_reservation(args):
    glpic = Glpi(args.url, args.user, args.token)
    data = glpic.info_reservation(args.reservation)
    for key in data:
        print(f"{key}: {data[key]}")


def list_computers(args):
    glpic = Glpi(args.url, args.user, args.token)
    computerstable = PrettyTable(["Name", "Group", "Serial", "Model", "Memory", "Bmc"])
    for computer in glpic.list_computers(overrides=handle_parameters(args.param)):
        name, serial = computer['Computer.name'], computer['Computer.serial']
        group, memory = computer['Computer.Group.completename'], computer.get('Computer.Item_DeviceMemory.size')
        bmc = computer['Computer.PluginFieldsComputerbmcaddre.bmcaddressfield']
        model = computer['Computer.ComputerModel.name']
        entry = [name, group, serial, model, memory, bmc]
        computerstable.add_row(entry)
    print(computerstable)


def update_computer(args):
    glpic = Glpi(args.url, args.user, args.token)
    for computer in args.computers:
        info(f"Updating computer {computer}")
        glpic.update_computer(computer, overrides=handle_parameters(args.param))


def list_reservations(args):
    glpic = Glpi(args.url, args.user, args.token)
    reservationstable = PrettyTable(["Id", "Item", "Begin", "End", "Comment"])
    for reservation in glpic.list_reservations(overrides=handle_parameters(args.param)):
        _id, begin, end, comment = reservation['id'], reservation['begin'], reservation['end'], reservation['comment']
        comment = fill(comment, width=100)
        reservation_id = reservation['reservationitems_id']
        computer_id = glpic.info_reservation(reservation_id)['items_id']
        reservation_name = glpic.info_computer({'computer': computer_id})[0]['Computer.name']
        entry = [_id, reservation_name, begin, end, comment]
        reservationstable.add_row(entry)
    print(reservationstable)


def list_users(args):
    glpic = Glpi(args.url, args.user, args.token)
    userstable = PrettyTable(["Id", "Name", "Last Login"])
    for user in glpic.list_users(overrides=handle_parameters(args.param)):
        _id, name, last_login = user['id'], user['name'], user['last_login']
        entry = [_id, name, last_login]
        userstable.add_row(entry)
    print(userstable)


def cli():
    """

    """
    # PARAMETERS_HELP = 'specify parameter or keyword for rendering (multiple can be specified)'
    parser = argparse.ArgumentParser(description='Glpi client')
    parser.add_argument('-t', '--token')
    parser.add_argument('-u', '-U', '--url')
    parser.add_argument('-user')
    subparsers = parser.add_subparsers(metavar='', title='Available Commands')

    create_desc = 'Create Object'
    create_parser = subparsers.add_parser('create', description=create_desc, help=create_desc, aliases=['add'])
    create_subparsers = create_parser.add_subparsers(metavar='', dest='subcommand_create')

    reservationcreate_desc = 'Create Reservation'
    reservationcreate_epilog = None
    reservationcreate_parser = create_subparsers.add_parser('reservation', description=reservationcreate_desc,
                                                            help=reservationcreate_desc,
                                                            epilog=reservationcreate_epilog, formatter_class=rawhelp)
    reservationcreate_parser.add_argument('-f', '--force', action='store_true',
                                          help='Delete existing reservation if needed')
    reservationcreate_parser.add_argument('-P', '--param', action='append', help=PARAMHELP, metavar='PARAM')
    reservationcreate_parser.add_argument('computer', metavar='COMPUTER', nargs='?')
    reservationcreate_parser.set_defaults(func=create_reservation)

    delete_desc = 'Delete Object'
    delete_parser = subparsers.add_parser('delete', description=delete_desc, help=delete_desc, aliases=['remove'])
    delete_parser.add_argument('-y', '--yes', action='store_true', help='Dont ask for confirmation', dest="yes_top")
    delete_subparsers = delete_parser.add_subparsers(metavar='', dest='subcommand_delete')

    reservationdelete_desc = 'Delete Reservation'
    reservationdelete_epilog = None
    reservationdelete_parser = delete_subparsers.add_parser('reservation', description=reservationdelete_desc,
                                                            help=reservationdelete_desc,
                                                            epilog=reservationdelete_epilog, formatter_class=rawhelp,
                                                            aliases=['reservations'])
    reservationdelete_parser.add_argument('-a', '--all', action='store_true', help='Delete all reservations')
    reservationdelete_parser.add_argument('-y', '--yes', action='store_true', help='Dont ask for confirmation')
    reservationdelete_parser.add_argument('reservations', metavar='CLUSTERS', nargs='*')
    reservationdelete_parser.set_defaults(func=delete_reservation)

    info_desc = 'Info Object'
    info_parser = subparsers.add_parser('info', description=info_desc, help=info_desc)
    info_subparsers = info_parser.add_subparsers(metavar='', dest='subcommand_info')

    computerinfo_desc = 'Info Computer'
    computerinfo_epilog = None
    computerinfo_parser = info_subparsers.add_parser('computer', description=computerinfo_desc, help=computerinfo_desc,
                                                     epilog=computerinfo_epilog, formatter_class=rawhelp)
    computerinfo_parser.add_argument('-P', '--param', action='append', help=PARAMHELP, metavar='PARAM')
    computerinfo_parser.add_argument('computer', metavar='COMPUTER', nargs='?')
    computerinfo_parser.set_defaults(func=info_computer)

    reservationinfo_desc = 'Info Reservation'
    reservationinfo_epilog = None
    reservationinfo_parser = info_subparsers.add_parser('reservation', description=reservationinfo_desc,
                                                        help=reservationinfo_desc,
                                                        epilog=reservationinfo_epilog, formatter_class=rawhelp)
    reservationinfo_parser.add_argument('reservation', metavar='RESERVATION')
    reservationinfo_parser.set_defaults(func=info_reservation)

    list_desc = 'List Object'
    list_parser = subparsers.add_parser('list', description=list_desc, help=list_desc, aliases=['get'])
    list_subparsers = list_parser.add_subparsers(metavar='', dest='subcommand_list')

    computerlist_desc = 'List Computers'
    computerlist_parser = argparse.ArgumentParser(add_help=False)
    computerlist_parser.set_defaults(func=list_computers)
    computerlist_parser.add_argument('-P', '--param', action='append', help=PARAMHELP, metavar='PARAM')
    list_subparsers.add_parser('computer', parents=[computerlist_parser], description=computerlist_desc,
                               help=computerlist_desc, aliases=['computers'])

    reservationlist_desc = 'List Reservations'
    reservationlist_parser = argparse.ArgumentParser(add_help=False)
    reservationlist_parser.set_defaults(func=list_reservations)
    reservationlist_parser.add_argument('-P', '--param', action='append', help=PARAMHELP, metavar='PARAM')
    list_subparsers.add_parser('reservation', parents=[reservationlist_parser], description=reservationlist_desc,
                               help=reservationlist_desc, aliases=['reservations'])

    userlist_desc = 'List Users'
    userlist_parser = argparse.ArgumentParser(add_help=False)
    userlist_parser.set_defaults(func=list_users)
    userlist_parser.add_argument('-P', '--param', action='append', help=PARAMHELP, metavar='PARAM')
    list_subparsers.add_parser('user', parents=[userlist_parser], description=userlist_desc,
                               help=userlist_desc, aliases=['users'])

    update_desc = 'Update Object'
    update_parser = subparsers.add_parser('update', description=update_desc, help=update_desc)
    update_subparsers = update_parser.add_subparsers(metavar='', dest='subcommand_update')

    computerupdate_desc = 'Update Computer'
    computerupdate_epilog = None
    computerupdate_parser = update_subparsers.add_parser('computer', description=computerupdate_desc,
                                                         help=computerupdate_desc,
                                                         epilog=computerupdate_epilog, formatter_class=rawhelp,
                                                         aliases=['computers'])
    computerupdate_parser.add_argument('-P', '--param', action='append', help=PARAMHELP, metavar='PARAM')
    computerupdate_parser.add_argument('computers', metavar='RESERVATIONS', nargs='*')
    computerupdate_parser.set_defaults(func=update_computer)

    reservationupdate_desc = 'Update Reservation'
    reservationupdate_epilog = None
    reservationupdate_parser = update_subparsers.add_parser('reservation', description=reservationupdate_desc,
                                                            help=reservationupdate_desc,
                                                            epilog=reservationupdate_epilog, formatter_class=rawhelp,
                                                            aliases=['reservations'])
    reservationupdate_parser.add_argument('-P', '--param', action='append', help=PARAMHELP, metavar='PARAM')
    reservationupdate_parser.add_argument('reservations', metavar='RESERVATIONS', nargs='*')
    reservationupdate_parser.set_defaults(func=update_reservation)

    if len(sys.argv) == 1:
        parser.print_help()
        os._exit(0)
    args = parser.parse_args()
    if not hasattr(args, 'func'):
        for attr in dir(args):
            if attr.startswith('subcommand_') and getattr(args, attr) is None:
                split = attr.split('_')
                if len(split) == 2:
                    subcommand = split[1]
                    get_subparser_print_help(parser, subcommand)
                elif len(split) == 3:
                    subcommand = split[1]
                    subsubcommand = split[2]
                    subparser = get_subparser(parser, subcommand)
                    get_subparser_print_help(subparser, subsubcommand)
                os._exit(0)
        os._exit(0)
    args.func(args)


if __name__ == '__main__':
    cli()
