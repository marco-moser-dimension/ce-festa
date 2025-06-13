# generate_hashes.py (VERSIONE CORRETTA E TESTATA)

import streamlit_authenticator as stauth

# Lista delle password in chiaro che vuoi crittografare
passwords_in_chiaro = ['ce-festa2025-admin', 'ce-festa2025']

# Crea un oggetto Hasher
hasher = stauth.Hasher()

print("Copia e incolla questi hash nel tuo file secrets.toml:")
print("-" * 50)

# Itera su ogni password e calcola il suo hash
for password in passwords_in_chiaro:
    # Il metodo corretto è .hash()
    hashed_password = hasher.hash(password)
    print(f"Password: '{password}'")
    print(f"Hash:     '{hashed_password}'")
    print("-" * 50)