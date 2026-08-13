#CHATGPT 2026-08-13
import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from zoneinfo import ZoneInfo


# ============================================================
# EINSTELLUNGEN
# ============================================================

INPUT_FILE = "../data/input.xlsx"
OUTPUT_FILE = "../data/input.xes"

# Zeitzone der Daten
TIMEZONE = "Europe/Berlin"

# XES Namespace
XES_NS = "http://www.xes-standard.org/"

ET.register_namespace("", XES_NS)


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def xes_tag(tag):
    """Erzeugt ein XES XML-Tag mit Namespace."""
    return f"{{{XES_NS}}}{tag}"


def format_xes_datetime(value):
    """
    Wandelt Datum/Zeit in das gewünschte XES-Format um:
    2026-08-01T08:15:00.000+02:00
    """

    if pd.isna(value):
        return "1970-01-01T00:00:00.000+01:00"

    # Bereits datetime?
    if isinstance(value, pd.Timestamp):
        dt = value.to_pydatetime()
    elif isinstance(value, datetime):
        dt = value
    else:
        dt = pd.to_datetime(value).to_pydatetime()

    # Falls keine Zeitzone vorhanden ist:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(TIMEZONE))
    else:
        dt = dt.astimezone(ZoneInfo(TIMEZONE))

    return dt.isoformat(timespec="milliseconds")


def format_xes_date(value):
    """
    Datum für REG_DATE.
    """

    if pd.isna(value):
        return "1970-01-01T00:00:00.000+01:00"

    dt = pd.to_datetime(value).to_pydatetime()

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(TIMEZONE))
    else:
        dt = dt.astimezone(ZoneInfo(TIMEZONE))

    return dt.isoformat(timespec="milliseconds")


def add_string(parent, key, value):
    """Fügt ein XES string-Attribut hinzu."""

    element = ET.SubElement(
        parent,
        xes_tag("string")
    )

    element.set("key", key)
    element.set("value", str(value))

    return element


def add_date(parent, key, value):
    """Fügt ein XES date-Attribut hinzu."""

    element = ET.SubElement(
        parent,
        xes_tag("date")
    )

    element.set("key", key)
    element.set("value", value)

    return element


# ============================================================
# EXCEL EINLESEN
# ============================================================

df = pd.read_excel(INPUT_FILE)


# ============================================================
# SPALTEN PRÜFEN
# ============================================================

required_columns = [
    "CASE_ID",
    "AMOUNT_REQ",
    "REG_DATE",
    "TIMESTAMP",
    "ACTIVITY",
    "LIFECYCLE",
    "RESOURCE"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        "Folgende Spalten fehlen in Excel: "
        + ", ".join(missing_columns)
    )


# ============================================================
# DATEN VORBEREITEN
# ============================================================

df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
df["REG_DATE"] = pd.to_datetime(df["REG_DATE"])

# Chronologische Reihenfolge innerhalb eines Cases
df = df.sort_values(
    ["CASE_ID", "TIMESTAMP"]
)


# ============================================================
# XES LOG ERSTELLEN
# ============================================================

log = ET.Element(
    xes_tag("log"),
    {
        "xes.version": "1.0",
        "xes.features": "nested-attributes",
        "openxes.version": "1.0RC7"
    }
)


# ============================================================
# EXTENSIONS
# ============================================================

extensions = [
    (
        "Metadata_Time",
        "meta_time",
        "http://www.xes-standard.org/meta_time.xesext"
    ),
    (
        "Lifecycle",
        "lifecycle",
        "http://www.xes-standard.org/lifecycle.xesext"
    ),
    (
        "Metadata_Lifecycle",
        "meta_life",
        "http://www.xes-standard.org/meta_life.xesext"
    ),
    (
        "Organizational",
        "org",
        "http://www.xes-standard.org/org.xesext"
    ),
    (
        "Metadata_Organizational",
        "meta_org",
        "http://www.xes-standard.org/meta_org.xesext"
    ),
    (
        "Time",
        "time",
        "http://www.xes-standard.org/time.xesext"
    ),
    (
        "Metadata_Concept",
        "meta_concept",
        "http://www.xes-standard.org/meta_concept.xesext"
    ),
    (
        "3TU metadata",
        "meta_3TU",
        "http://www.xes-standard.org/meta_3TU.xesext"
    ),
    (
        "Concept",
        "concept",
        "http://www.xes-standard.org/concept.xesext"
    ),
    (
        "General metadata",
        "meta_general",
        "http://www.xes-standard.org/meta_general.xesext"
    ),
    (
        "Semantic",
        "semantic",
        "http://www.xes-standard.org/semantic.xesext"
    )
]

for name, prefix, uri in extensions:

    ET.SubElement(
        log,
        xes_tag("extension"),
        {
            "name": name,
            "prefix": prefix,
            "uri": uri
        }
    )


# ============================================================
# GLOBAL TRACE ATTRIBUTES
# ============================================================

global_trace = ET.SubElement(
    log,
    xes_tag("global"),
    {"scope": "trace"}
)

add_date(
    global_trace,
    "REG_DATE",
    "1970-01-01T00:00:00.000+01:00"
)

add_string(
    global_trace,
    "AMOUNT_REQ",
    "UNKNOWN"
)

add_string(
    global_trace,
    "concept:name",
    "UNKNOWN"
)


# ============================================================
# GLOBAL EVENT ATTRIBUTES
# ============================================================

global_event = ET.SubElement(
    log,
    xes_tag("global"),
    {"scope": "event"}
)

add_date(
    global_event,
    "time:timestamp",
    "1970-01-01T00:00:00.000+01:00"
)

add_string(
    global_event,
    "lifecycle:transition",
    "UNKNOWN"
)

add_string(
    global_event,
    "concept:name",
    "UNKNOWN"
)


# ============================================================
# CLASSIFIER
# ============================================================

ET.SubElement(
    log,
    xes_tag("classifier"),
    {
        "name": "Activity classifier",
        "keys": "concept:name lifecycle:transition"
    }
)

ET.SubElement(
    log,
    xes_tag("classifier"),
    {
        "name": "Resource classifier",
        "keys": "org:resource"
    }
)


# ============================================================
# TRACES UND EVENTS
# ============================================================

for case_id, case_df in df.groupby("CASE_ID", sort=False):

    first_row = case_df.iloc[0]

    # --------------------------------------------------------
    # TRACE
    # --------------------------------------------------------

    trace = ET.SubElement(
        log,
        xes_tag("trace")
    )

    # concept:name = CASE_ID
    add_string(
        trace,
        "concept:name",
        case_id
    )

    # AMOUNT_REQ
    add_string(
        trace,
        "AMOUNT_REQ",
        first_row["AMOUNT_REQ"]
    )

    # REG_DATE
    add_date(
        trace,
        "REG_DATE",
        format_xes_date(first_row["REG_DATE"])
    )

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    for _, row in case_df.iterrows():

        event = ET.SubElement(
            trace,
            xes_tag("event")
        )

        # Aktivität
        add_string(
            event,
            "concept:name",
            row["ACTIVITY"]
        )

        # Lifecycle
        add_string(
            event,
            "lifecycle:transition",
            row["LIFECYCLE"]
        )

        # Resource
        if not pd.isna(row["RESOURCE"]):
            add_string(
                event,
                "org:resource",
                row["RESOURCE"]
            )

        # Timestamp
        add_date(
            event,
            "time:timestamp",
            format_xes_datetime(row["TIMESTAMP"])
        )


# ============================================================
# XML SCHÖN FORMATIEREN
# ============================================================

xml_bytes = ET.tostring(
    log,
    encoding="UTF-8",
    xml_declaration=True
)

pretty_xml = minidom.parseString(
    xml_bytes
).toprettyxml(
    indent="    ",
    encoding="UTF-8"
)


# ============================================================
# DATEI SCHREIBEN
# ============================================================

with open(
    OUTPUT_FILE,
    "wb"
) as file:

    file.write(pretty_xml)


print(
    f"XES-Datei erfolgreich erstellt: {OUTPUT_FILE}"
)