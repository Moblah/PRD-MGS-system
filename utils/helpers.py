import random
import string

def generate_user_alnum():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))