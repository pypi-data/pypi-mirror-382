import os
import keyring

target_keyring = keyring.get_keyring()

current_user = os.getenv("USERNAME") or os.getenv("USER")

