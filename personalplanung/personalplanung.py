# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta
# from dateutil.relativedelta import relativedelta
# import numpy as np
# from reportlab.lib.pagesizes import letter, landscape
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
# from reportlab.lib import colors
# import io


# def parse_holidays(holiday_string):
#     days = []
#     for d in holiday_string.split(","):
#         if d:
#             if "-" in d:
#                 start, end = map(int, d.split("-"))
#                 days.extend(range(start, end + 1))
#             else:
#                 days.append(int(d))
#     return days


# def german_weekday(date):
#     weekdays_german = [
#         "Montag",
#         "Dienstag",
#         "Mittwoch",
#         "Donnerstag",
#         "Freitag",
#         "Samstag",
#         "Sonntag",
#     ]
#     return weekdays_german[date.weekday()]


# months_to_number = {
#     "Januar": 1,
#     "Februar": 2,
#     "März": 3,
#     "April": 4,
#     "Mai": 5,
#     "Juni": 6,
#     "Juli": 7,
#     "August": 8,
#     "September": 9,
#     "Oktober": 10,
#     "November": 11,
#     "Dezember": 12,
# }

# # Erstellen Sie die Eingabefelder
# month_year = st.selectbox(
#     "Monat und Jahr (z.B. 'August 2023'):",
#     options=list(months_to_number.keys()),
#     help="Wählen Sie den Monat aus der Liste aus.",
#     index=7,
# )
# year = st.text_input("Jahr (z.B. '2023'):", value=datetime.now().strftime("%Y"))
# month_year = f"{month_year} {year}"
# employees = st.text_input(
#     "Mitarbeiterliste (getrennt durch Kommas):",
#     help="Geben Sie die Namen der Mitarbeiter ein, getrennt durch Kommas.",
#     value="Alina,Pauline,Steffi,Luca,Flori,Annina",
# )
# weekday_to_number = {
#     "Montag": 1,
#     "Dienstag": 2,
#     "Mittwoch": 3,
#     "Donnerstag": 4,
#     "Freitag": 5,
#     "Samstag": 6,
#     "Sonntag": 7,
# }

# # Erstellen Sie das Multiselect-Feld mit Wochentagen als Strings
# rest_days = st.multiselect(
#     "Ruhetage:",
#     list(weekday_to_number.keys()),
#     help="Wählen Sie die Ruhetage aus.",
#     default=["Dienstag", "Mittwoch"],
# )
# rest_days = [weekday_to_number[d] for d in rest_days] if rest_days else []

# # Verarbeiten Sie die Eingaben
# employees = employees.split(",") if employees else []

# # Initialisiere die Wörterbücher für die Arbeitszeiten und die Urlaubstage
# work_hours = {}
# holidays = {}
# not_available = {}

# # Wenn die Mitarbeiterliste ausgefüllt ist, erstellen Sie für jeden Mitarbeiter Eingabefelder für die Arbeitszeiten und Urlaubstage
# if employees:
#     for employee in employees:
#         col1, col2, col3,col4 = st.columns(4)
#         with col1:
#             st.write(employee)
#         with col2:
#             work_hours[employee] = st.text_input(
#                 f"Arbeitszeit für {employee}",
#                 help="Geben Sie die typischen Arbeitszeiten für diesen Mitarbeiter ein. \nFormat: 9-17",
#                 value="9-17",
#             )
#         with col3:
#             holidays[employee] = st.text_input(
#                 f"Urlaubstage für {employee}", help="Format in Tagen des Monats: 1-9,21"
#             )
#         with col4:
#             not_available[employee] = st.text_input(
#                 f"Nicht verfügbar für {employee}", help="Format in Tagen des Monats: 1-9,21"
#             )


#     # Verarbeite die Eingaben für Arbeitszeiten und Urlaubstage
#     holidays = {h: parse_holidays(holidays[h]) for h in holidays} if holidays else {}
#     work_hours = {w: work_hours[w] for w in work_hours} if work_hours else {}
#     not_available = {w: parse_holidays(not_available[w]) for w in not_available} if not_available else {}

# # Create DataFrame when button is pressed
# if st.button("Erstelle den Arbeitsplan"):
#     # Create a DataFrame for the month
#     month = datetime.strptime(month_year, "%B %Y")
#     next_month = month + relativedelta(months=1)
#     days = (next_month - month).days
#     df = pd.DataFrame(index=pd.date_range(month, periods=days), columns=employees)

#     # Fill in work hours, holidays, and rest days
#     for employee in employees:
#         # Work hours
#         df[employee] = work_hours[employee]

#         # Holidays
#         if employee in holidays:
#             for day in holidays[employee]:
#                 df.loc[df.index.day == day, employee] = "U"

#         # Not available
#         if employee in not_available:
#             for day in not_available[employee]:
#                 df.loc[df.index.day == day, employee] = "n.V."

#         # Rest days (considering that 0 corresponds to Monday in Python's date.weekday() method)
#         for day in [(d - 1) % 7 for d in rest_days]:
#             df.loc[df.index.weekday == day, employee] = "Ruhe"

#     df.replace(
#         np.nan, "", regex=True, inplace=True
#     )  # Replaces NaN values with an empty string
#     df.index = df.index.map(lambda x: f"{x.day:02d}, {german_weekday(x)}")

#     st.dataframe(df)

#     # Erstellen Sie ein SimpleDocTemplate
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     data = [[month_year] + df.columns.to_list()] + df.reset_index().values.tolist()
#     table = Table(data)

#     style = TableStyle(
#         [
#             ("BACKGROUND", (1, 0), (-1, 0), colors.grey),  # erste Zeile
#             ("TEXTCOLOR", (1, 0), (-1, 0), colors.whitesmoke),
#             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#             ("FONTNAME", (1, 0), (-1, 0), "Helvetica-Bold"),
#             ("FONTSIZE", (1, 0), (-1, 0), 14),
#             ("BACKGROUND", (0, 1), (0, -1), colors.grey),  # erste Spalte
#             ("TEXTCOLOR", (0, 1), (0, -1), colors.whitesmoke),
#             ("ALIGN", (0, 1), (0, -1), "LEFT"),
#             ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
#             ("FONTSIZE", (0, 1), (0, -1), 12),
#             ("BACKGROUND", (1, 1), (-1, -1), colors.beige),  # Rest der Tabelle
#             ("GRID", (0, 0), (-1, -1), 1, colors.black),
#         ]
#     )

#     for i in range(len(data)):
#         for j in range(len(data[i])):
#             if data[i][j] == "Ruhe":
#                 style.add("BACKGROUND", (j, i), (j, i), colors.lightgrey)

#     table.setStyle(style)
#     story = [table]
#     doc.build(story)
#     pdf_data = buffer.getvalue()

#     # Bieten Sie die PDF zum Download an
#     st.download_button(
#         label="PDF herunterladen",
#         data=pdf_data,
#         file_name="Arbeitsplan.pdf",
#         mime="application/pdf",
#     )

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io


def parse_holidays(holiday_string):
    days = []
    for d in holiday_string.split(","):
        if d:
            if "-" in d:
                start, end = map(int, d.split("-"))
                days.extend(range(start, end + 1))
            else:
                days.append(int(d))
    return days


def german_weekday(date):
    weekdays_german = [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag",
        "Samstag",
        "Sonntag",
    ]
    return weekdays_german[date.weekday()]


months_to_number = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}

# Erstellen Sie die Eingabefelder
month_year = st.selectbox(
    "Monat und Jahr (z.B. 'August 2023'):",
    options=list(months_to_number.keys()),
    help="Wählen Sie den Monat aus der Liste aus.",
    index=7,
)
year = st.text_input("Jahr (z.B. '2023'):", value=datetime.now().strftime("%Y"))
month_year = f"{month_year} {year}"
employees = st.text_input(
    "Mitarbeiterliste (getrennt durch Kommas):",
    help="Geben Sie die Namen der Mitarbeiter ein, getrennt durch Kommas.",
    value="Alina,Pauline,Steffi,Luca,Flori,Annina",
)
weekday_to_number = {
    "Montag": 1,
    "Dienstag": 2,
    "Mittwoch": 3,
    "Donnerstag": 4,
    "Freitag": 5,
    "Samstag": 6,
    "Sonntag": 7,
}

# Erstellen Sie das Multiselect-Feld mit Wochentagen als Strings
rest_days = st.multiselect(
    "Ruhetage:",
    list(weekday_to_number.keys()),
    help="Wählen Sie die Ruhetage aus.",
    default=["Dienstag", "Mittwoch"],
)
rest_days = [weekday_to_number[d] for d in rest_days] if rest_days else []

# Verarbeiten Sie die Eingaben
employees = employees.split(",") if employees else []

# Initialisiere die Wörterbücher für die Arbeitszeiten und die Urlaubstage
work_hours = {}
holidays = {}
not_available = {}

# Wenn die Mitarbeiterliste ausgefüllt ist, erstellen Sie für jeden Mitarbeiter Eingabefelder für die Arbeitszeiten und Urlaubstage
if employees:
    for employee in employees:
        col1, col2, col3,col4 = st.columns(4)
        with col1:
            st.write(employee)
        with col2:
            work_hours[employee] = st.text_input(
                f"Arbeitszeit für {employee}",
                help="Geben Sie die typischen Arbeitszeiten für diesen Mitarbeiter ein. \nFormat: 9-17",
                value="9-17",
            )
        with col3:
            holidays[employee] = st.text_input(
                f"Urlaub für {employee}", help="Format in Tagen des Monats: 1-9,21"
            )
        with col4:
            not_available[employee] = st.text_input(
                f"{employee}: Nicht verfügbar", help="Format in Tagen des Monats: 1-9,21"
            )

    # Verarbeite die Eingaben für Arbeitszeiten und Urlaubstage
    holidays = {h: parse_holidays(holidays[h]) for h in holidays} if holidays else {}
    work_hours = {w: work_hours[w] for w in work_hours} if work_hours else {}
    not_available = {w: parse_holidays(not_available[w]) for w in not_available} if not_available else {}

# Create DataFrame when button is pressed
if st.button("Erstelle den Arbeitsplan"):
    # Create a DataFrame for the month
    month = datetime.strptime(month_year, "%B %Y")
    next_month = month + relativedelta(months=1)
    days = (next_month - month).days
    df = pd.DataFrame(index=pd.date_range(month, periods=days), columns=employees)

    # Fill in work hours, holidays, and rest days
    for employee in employees:
        # Work hours
        df[employee] = work_hours[employee]

        # Holidays
        if employee in holidays:
            for day in holidays[employee]:
                df.loc[df.index.day == day, employee] = "U"

        # Not available
        if employee in not_available:
            for day in not_available[employee]:
                df.loc[df.index.day == day, employee] = "n.v."

        # Rest days (considering that 0 corresponds to Monday in Python's date.weekday() method)
        for day in [(d - 1) % 7 for d in rest_days]:
            df.loc[df.index.weekday == day, employee] = "Ruhe"

    df.replace(
        np.nan, "", regex=True, inplace=True
    )  # Replaces NaN values with an empty string
    df.index = df.index.map(lambda x: f"{x.day:02d}, {german_weekday(x)}")

    st.dataframe(df)

    # Erstellen Sie ein SimpleDocTemplate
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    data = [[month_year] + df.columns.to_list()] + df.reset_index().values.tolist()
    table = Table(data)

    style = TableStyle(
        [
            ("BACKGROUND", (1, 0), (-1, 0), colors.grey),  # erste Zeile
            ("TEXTCOLOR", (1, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (1, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (1, 0), (-1, 0), 14),
            ("BACKGROUND", (0, 1), (0, -1), colors.grey),  # erste Spalte
            ("TEXTCOLOR", (0, 1), (0, -1), colors.whitesmoke),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (0, -1), 12),
            ("BACKGROUND", (1, 1), (-1, -1), colors.beige),  # Rest der Tabelle
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == "Ruhe":
                style.add("BACKGROUND", (j, i), (j, i), colors.lightgrey)
            if data[i][j] == "n.V.":
                style.add("BACKGROUND", (j, i), (j, i), colors.lightgrey)
            if data[i][j] == "U":
                style.add("BACKGROUND", (j, i), (j, i), colors.lightgreen)
        if "Samstag" in data[i][0] or "Sonntag" in data[i][0]:
            style.add("BACKGROUND", (0, i), (-1, i), colors.salmon)

    table.setStyle(style)
    story = [table]
    doc.build(story)
    pdf_data = buffer.getvalue()

    # Bieten Sie die PDF zum Download an
    st.download_button(
        label="PDF herunterladen",
        data=pdf_data,
        file_name="Arbeitsplan.pdf",
        mime="application/pdf",
    )
