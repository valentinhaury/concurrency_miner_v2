import pm4py


# ------------------------------------------------------------
# Dateien
# ------------------------------------------------------------

INPUT_FILE = "../../src/developement_utilities/data/bpi_challenges/BPI_Challenge_2017.xes"
OUTPUT_FILE = "../../src/developement_utilities/data/bpi_challenges/BPI2017_W_START_COMPLETE.xes"


# ------------------------------------------------------------
# XES einlesen
# ------------------------------------------------------------

print("Lese XES-Log...")

df = pm4py.read_xes(INPUT_FILE)

print(f"Original: {len(df):,} Events")


# ------------------------------------------------------------
# Filtern
# ------------------------------------------------------------
#
# Bedingungen:
#   1. Activity beginnt mit "W_"
#   2. Lifecycle ist START oder COMPLETE
#

filtered_df = df[
    df["concept:name"].astype(str).str.startswith("W_")
    &
    df["lifecycle:transition"].isin(["start", "complete"])
].copy()


# ------------------------------------------------------------
# Informationen ausgeben
# ------------------------------------------------------------

print(f"Gefiltert: {len(filtered_df):,} Events")

print("\nEnthaltene Activities:")

activities = sorted(
    filtered_df["concept:name"].unique()
)

for activity in activities:
    print(f"  {activity}")

print(f"\nAnzahl Activities: {len(activities)}")

print("\nLifecycle-Transitions:")

print(
    filtered_df["lifecycle:transition"]
    .value_counts()
)


# ------------------------------------------------------------
# DataFrame wieder in EventLog umwandeln
# ------------------------------------------------------------

filtered_log = pm4py.convert_to_event_log(filtered_df)


# ------------------------------------------------------------
# XES speichern
# ------------------------------------------------------------

pm4py.write_xes(
    filtered_log,
    OUTPUT_FILE
)

print(f"\nXES gespeichert unter:")
print(OUTPUT_FILE)