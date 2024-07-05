import tkinter as tk
import random
import hashlib

eve_intrusion_probability = 0.2  # Probabilité d'intrusion d'Eve
key_length = 10  # Longueur de la clé à générer
envelope = None  # Identifiant global de l'enveloppe

def generate_key(length):
    key = ""
    for _ in range(length):
        bit = random.randint(0, 1)
        key += str(bit)
    return key

def encode_bits(bits, bases):
    qubits = []
    for i in range(len(bits)):
        bit = int(bits[i])
        base = bases[i]
        if base == 0:
            qubit = "|{}>".format(bit)
        else:
            qubit = "|{}>".format((bit + 1) % 2)
        qubits.append(qubit)
    return qubits

def measure_qubits(qubits, bases):
    measurements = []
    for i in range(len(qubits)):
        qubit = qubits[i]
        base = bases[i]
        measurement = random.randint(0, 1) if base == 0 else random.randint(1, 2) % 2
        measurements.append(measurement)
    return measurements

def intercept_signals(measurements_bob):
    modified_indices = []
    for i in range(len(measurements_bob)):
        if random.random() < eve_intrusion_probability:
            measurements_bob[i] = random.randint(0, 1)  # Eve change la mesure de Bob
            modified_indices.append(i)
    return modified_indices

def extract_secret_key(bases_alice, bases_bob, measurements_bob):
    secret_key_alice = ""
    secret_key_bob = ""
    for i in range(len(bases_alice)):
        base_alice = bases_alice[i]
        base_bob = bases_bob[i]
        measurement_bob = measurements_bob[i]
        if base_alice == base_bob:
            secret_key_alice += str(measurement_bob)
            secret_key_bob += str(measurement_bob)
        else:
            secret_key_alice += "-"
            secret_key_bob += str(random.randint(0, 1))  # Eve effectue une intrusion

    # Ajout de la fonction de hachage pour Alice
    hash_object_alice = hashlib.sha256()
    hash_object_alice.update(secret_key_alice.encode())
    hashed_key_alice = hash_object_alice.hexdigest()

    # Ajout de la fonction de hachage pour Bob
    hash_object_bob = hashlib.sha256()
    hash_object_bob.update(secret_key_bob.encode())
    hashed_key_bob = hash_object_bob.hexdigest()

    return hashed_key_alice, hashed_key_bob, secret_key_alice, secret_key_bob

def detect_intrusion(secret_key_alice, secret_key_bob):
    if secret_key_alice == secret_key_bob:
        return "Aucune intrusion détectée. La clé est partagée avec succès."
    else:
        return f"Intrusion détectée ! La clé a été interceptée par un tiers."

def verify_integrity(secret_key_alice, secret_key_bob):
    subset_length = min(len(secret_key_alice), len(secret_key_bob))
    subset_alice = secret_key_alice[:subset_length]
    subset_bob = secret_key_bob[:subset_length]
    if subset_alice == subset_bob:
        return "Clé partagée avec succès. Aucune interception détectée."
    else:
        return "Intrusion détectée ! La clé a été interceptée par un tiers."

def show_intrusion_message(result, integrity_result):
    result_label.config(text=result + "\n" + integrity_result)

def animate_key(modified_indices):
    global envelope  # Utiliser la variable globale pour l'enveloppe
    # Animation du mouvement de la clé et de l'intrus
    key_canvas.delete("all")
    key_canvas.create_text(200, 50, text="Alice", font=("Arial", 14, "bold"))
    key_canvas.create_text(600, 50, text="Bob", font=("Arial", 14, "bold"))
    eve_text = key_canvas.create_text(400, 150, text="Eve", font=("Arial", 14, "bold"))

    envelope = key_canvas.create_text(200, 80, text="✉️", font=("Arial", 14, "bold"))  # Clé initiale d'Alice

    step_x = 400 / key_length
    step_y = 70 / key_length
    for i in range(key_length):
        key_canvas.move(envelope, step_x, 0)  # Déplacement horizontal de l'enveloppe
        key_canvas.update()
        key_canvas.after(500)  # Pause de 500 millisecondes entre chaque déplacement
        current_position_x = key_canvas.coords(envelope)[0]
        
        # Vérification si Eve intercepte ce paquet
        if current_position_x >= 400 - step_x and current_position_x <= 400 + step_x and i in modified_indices:
            key_canvas.move(envelope, 0, step_y)  # Déplacement vertical vers Eve
            key_canvas.update()
            key_canvas.after(500)
            key_canvas.itemconfig(envelope, fill="orange")  # Change la couleur de l'enveloppe pendant l'interception
            eve_hand = key_canvas.create_text(400, 120, text="✋", font=("Arial", 14, "bold"), fill="red")
            key_canvas.update()
            key_canvas.after(500)  # Pause de 500 millisecondes pour montrer l'interception
            key_canvas.delete(eve_hand)
            key_canvas.itemconfig(envelope, fill="black")  # Remet la couleur initiale après interception
            key_canvas.move(envelope, 0, -step_y)  # Remet l'enveloppe à la position initiale
        key_canvas.update()

def update_intrusion_probability_label():
    intrusion_label.config(text=f"Probabilité d'intrusion d'Eve: {eve_intrusion_probability}")

def generate_keys():
    global envelope  # Utiliser la variable globale pour l'enveloppe

    key_alice = generate_key(key_length)
    key_bases_alice = generate_key(key_length)

    key_bob = generate_key(key_length)
    key_bases_bob = generate_key(key_length)

    qubits_alice = encode_bits(key_alice, key_bases_alice)
   
    measurements_bob = measure_qubits(qubits_alice, key_bases_bob)

    # Interception des signaux par Eve
    modified_indices = intercept_signals(measurements_bob)

    animate_key(modified_indices)

    hashed_key_alice, hashed_key_bob, secret_key_alice, secret_key_bob = extract_secret_key(key_bases_alice, key_bases_bob, measurements_bob)

    result = detect_intrusion(hashed_key_alice, secret_key_bob)
    integrity_result = verify_integrity(hashed_key_alice, secret_key_bob)

    alice_key_label.config(text="Clé secrète d'Alice: " + secret_key_alice)
    hashed_key_alice_label.config(text="Clé secrète hachée d'Alice: " + hashed_key_alice)
    bob_key_label.config(text="Clé secrète de Bob: " + secret_key_bob)
    hashed_key_bob_label.config(text="Clé secrète hachée de Bob: " + hashed_key_bob)
    result_label.config(text=result + "\n" + integrity_result)

    # Vérification de l'intégrité et affichage de la couleur correspondante
    if "Intrusion détectée" in result or "Intrusion détectée" in integrity_result:
        key_canvas.itemconfig(envelope, fill="red")  # Clé finale de Bob (rouge)
    else:
        key_canvas.itemconfig(envelope, fill="green")  # Clé finale de Bob (vert)

# Création de la fenêtre principale
window = tk.Tk()
window.title("Quantum Key Distribution")
window.geometry("800x450")

# Création des widgets
title_label = tk.Label(window, text="Distribution quantique de clé", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

generate_button = tk.Button(window, text="Générer les clés", font=("Arial", 14), command=generate_keys)
generate_button.pack()

intrusion_label = tk.Label(window, text=f"Probabilité d'intrusion d'Eve: {eve_intrusion_probability}", font=("Arial", 12))
intrusion_label.pack()

alice_key_label = tk.Label(window, text="", font=("Arial", 14))
alice_key_label.pack(pady=10)

hashed_key_alice_label = tk.Label(window, text="", font=("Arial", 14))
hashed_key_alice_label.pack(pady=10)

bob_key_label = tk.Label(window, text="", font=("Arial", 14))
bob_key_label.pack(pady=10)

hashed_key_bob_label = tk.Label(window, text="", font=("Arial", 14))
hashed_key_bob_label.pack(pady=10)

result_label = tk.Label(window, text="", font=("Arial", 14))
result_label.pack(pady=20)

key_canvas = tk.Canvas(window, width=800, height=200)
key_canvas.pack()

# Lancement de la boucle principale
window.mainloop()
