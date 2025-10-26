#!/usr/bin/env python3
import lgpio
import sys
import time

# Standard-Chip (Pi 5 hat oft Chip 0 für Haupt-GPIOs)
chip = 0

# Prüfe, ob genügend Argumente übergeben wurden
if len(sys.argv) != 3:
    print("Fehler: Benötigt 2 Argumente: <gpio_pin> <zustand: 0 oder 1>")
    sys.exit(1)

try:
    # Lese Argumente
    gpio_pin = int(sys.argv[1])
    zustand = int(sys.argv[2])

    # Zustand validieren
    if zustand not in [0, 1]:
        raise ValueError("Zustand muss 0 oder 1 sein")

except ValueError as e:
    print(f"Fehler: Ungültige Argumente - {e}")
    sys.exit(1)

h = None # Initialisiere h außerhalb des try-Blocks
try:
    # Öffne den GPIO Chip
    h = lgpio.gpiochip_open(chip)

    # Konfiguriere den Pin als Ausgang
    # Flags=2 setzt den Pin initial auf den gewünschten Zustand, vermeidet kurzes togglen
    lgpio.gpio_claim_output(h, gpio_pin, zustand)

    # Der Zustand wurde bereits beim claim gesetzt, aber zur Sicherheit nochmal schreiben
    # lgpio.gpio_write(h, gpio_pin, zustand)

    #print(f"GPIO {gpio_pin} auf {zustand} gesetzt.") # Optional: Für Debugging in Node-RED
    time.sleep(0.05) # Kurze Pause, um sicherzustellen, dass der Befehl verarbeitet wird

except Exception as e:
    print(f"Fehler beim Schalten von GPIO {gpio_pin}: {e}")
    # Gib einen anderen Exit-Code zurück, um den Fehler in Node-RED zu signalisieren
    sys.exit(2)

finally:
    # Ressourcen freigeben
    if h is not None:
         try:
             # Wichtig: Pin freigeben, damit er wieder verwendet werden kann
             lgpio.gpio_free(h, gpio_pin)
             lgpio.gpiochip_close(h)
             #print("GPIO freigegeben und Chip geschlossen.") # Optional
         except Exception as e_close:
             print(f"Warnung: Fehler beim Freigeben/Schließen des GPIO: {e_close}")
    # Exit Code 0 signalisiert Erfolg
    sys.exit(0)