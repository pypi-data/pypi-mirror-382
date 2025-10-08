from colorama import init, Fore, Style


def print_instruction(msg: str):
    print(Fore.BLUE + msg + Style.RESET_ALL)


def print_info(msg: str):
    print(Fore.CYAN + msg + Style.RESET_ALL)


def print_success(msg: str):
    print(Fore.GREEN + msg + Style.RESET_ALL)


def print_warning(msg: str):
    print(Fore.YELLOW + msg + Style.RESET_ALL)


def print_error(msg: str):
    print(Fore.RED + msg + Style.RESET_ALL)


def print_title(msg: str):
    print(Fore.WHITE + Style.BRIGHT + msg + Style.RESET_ALL)
