from getpass import getpass

def get_username(config):
    return input('Please type the username to set: ')

def get_password(config):
    return getpass('Please enter the password to set: ')

def get_credentials(config):
    try:
        username = config['username']
        password = config['password']
    except KeyError:
        username = get_username(config)
        password = get_password(config)
        config['username'], config['password'] = username, password
    
    config['username'], config['password'] = username, password

    return username, password