import shutil

def command_exists(name: str):
    """checks if a specific bash command exists"""
    return shutil.which(name) is not None
