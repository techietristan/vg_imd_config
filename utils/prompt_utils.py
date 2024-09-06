from getpass import getpass

def get_username(config: dict) -> str:
    return input('Please type the username to set: ')

def get_password(config: dict) -> str:
    password = getpass('Please enter the password to set: ')
    confirm_password = getpass('Please enter the password again: ')

    if password == confirm_password:
        return password
    else:
        print("Passwords do not match. Please try again.")
        get_password(config)

def get_credentials(config: dict) -> tuple:
    try:
        username = config['username']
        password = config['password']
    except KeyError:
        username = get_username(config)
        password = get_password(config)
        config['username'], config['password'] = username, password
    
    config['username'], config['password'] = username, password

    return username, password