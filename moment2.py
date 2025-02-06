
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
from datetime import timedelta


# Ladda dataset
df = pd.read_csv("screentime_analysis.csv")
df["Date"] = pd.to_datetime(df["Date"])
df["Weekday"] = df["Date"].dt.day_name()
df["Month"] = df["Date"].dt.month

# Definiera färgpalett
color_palette = ["#FF6F61", "#4E92B1", "#A4D08C"]

# All output är filtrerad på de tre mest använda apparna

# **1. Total skärmtid per app **
app_usage = df.groupby("App")["Usage (minutes)"].sum().sort_values(ascending=False).head(3)
plt.figure(figsize=(10,6))
app_usage.plot(kind="barh", color=color_palette)  # Använd de definierade färgerna
plt.xlabel("Total skärmtid (minuter)")
plt.title("Total skärmtid per app")
plt.show()

# **2. Genomsnittlig skärmtid per app **
app_avg_usage = df.groupby("App")["Usage (minutes)"].mean().sort_values(ascending=False).head(3)
plt.figure(figsize=(10,6))
app_avg_usage.plot(kind="barh", color=color_palette)  # Använd de definierade färgerna
plt.xlabel("Genomsnittlig skärmtid per app (minuter)")
plt.title("Genomsnittlig skärmtid per app")
plt.show()

# **3. Genomsnittlig skärmtid per vecka per app **
top_apps_weekday = df.groupby("App")["Usage (minutes)"].sum().sort_values(ascending=False).head(3).index
filtered_df_weekday = df[df["App"].isin(top_apps_weekday)]
weekday_app_usage = filtered_df_weekday.groupby(["Weekday", "App"])["Usage (minutes)"].mean().unstack()
weekday_translation = {
    "Monday": "Måndag",
    "Tuesday": "Tisdag",
    "Wednesday": "Onsdag",
    "Thursday": "Torsdag",
    "Friday": "Fredag",
    "Saturday": "Lördag",
    "Sunday": "Söndag"
}
weekday_app_usage.index = weekday_app_usage.index.map(weekday_translation)
weekday_order = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
weekday_app_usage = weekday_app_usage.reindex(weekday_order)

plt.figure(figsize=(12,6))
weekday_app_usage.plot(kind="bar", stacked=False, color=color_palette[:len(weekday_app_usage.columns)])
plt.xlabel("Veckodag")
plt.ylabel("Genomsnittlig skärmtid (minuter)")
plt.title("Genomsnittlig skärmtid per veckodag/app")
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()  # Gör så att diagrammet passar bättre
plt.show()

# **4. Skärmtid över tid (minuter)**
top_apps_time = df.groupby("App")["Usage (minutes)"].sum().sort_values(ascending=False).head(3).index
plt.figure(figsize=(12,6))

for idx, app in enumerate(top_apps_time):
    app_data = df[df["App"] == app]
    app_data.groupby("Date")["Usage (minutes)"].sum().plot(label=app, marker="o", color=color_palette[idx])

plt.xlabel("Datum")
plt.ylabel("Minuter")
plt.title("Total skärmtid över tid (minuter)")
plt.legend()
plt.xticks(rotation=45)
plt.show()

# **5. Sambandsdiagram: Öppningstillfällen/skärmtid**
plt.figure(figsize=(8,6))
for idx, app in enumerate(top_apps_time):
    app_data = df[df["App"] == app]
    sns.scatterplot(x=app_data["Times Opened"], y=app_data["Usage (minutes)"], label=app, alpha=0.7, color=color_palette[idx])
plt.xlabel("Öppningstillfällen")
plt.ylabel("Skärmtid (minuter)")
plt.title("Sambandsdiagram: Öppningstillfällen/skärmtid")
plt.legend()
plt.show()


# **6. Procentandel skrämtid per app (de 3 mest relevanta)**
total_screentime = df["Usage (minutes)"].sum()  # Total screentime
app_percentage = (df.groupby("App")["Usage (minutes)"].sum() / total_screentime) * 100
top_app_percentage = app_percentage.sort_values(ascending=False).head(3)

# **7. Cirkeldiagram procentandel total skärmtid per app
plt.figure(figsize=(8,8))
top_app_percentage.plot(kind="pie", autopct="%1.1f%%", colors=color_palette, legend=False)
plt.title("Procentandel total skärmtid per app")
plt.ylabel("")  # Ta bort ylabel för en renare bild
plt.legend(labels=top_app_percentage.index)
plt.show()

# Skapa en kolumn för vecka
df["Week"] = df["Date"].dt.to_period("W")

# Gruppera användning per vecka och per app
weekly_usage = df.groupby(["Week", "App"])["Usage (minutes)"].sum().reset_index()

# Beräkna total användning per app
total_usage_per_app = weekly_usage.groupby("App")["Usage (minutes)"].sum().reset_index()

# Sortera apparna efter total användning och välj de tre mest använda
top_apps = total_usage_per_app.sort_values(by="Usage (minutes)", ascending=False).head(3)["App"]

# Filtrera datan för de tre mest använda apparna
filtered_usage = weekly_usage[weekly_usage["App"].isin(top_apps)].copy()

# Skapa en numerisk representation av vecka
filtered_usage.loc[:, "Week_numeric"] = (
    (filtered_usage["Week"].dt.year - filtered_usage["Week"].dt.year.min()) * 52 +
    (filtered_usage["Week"].dt.week - filtered_usage["Week"].dt.week.min())
)

# Skapa en figur för att visualisera
plt.figure(figsize=(12, 8))

# För varje app i de tre mest använda apparna, skapa en regressionsmodell och gör förutsägelser
for app in top_apps:
    app_data = filtered_usage[filtered_usage["App"] == app]

    # Definiera X och y för regressionsmodellen
    X = app_data[["Week_numeric"]]
    y = app_data["Usage (minutes)"]

    # Skapa och träna linjär regressionsmodell
    model = LinearRegression()
    model.fit(X, y)

    # Förutsäg framtida veckor
    future_weeks = pd.date_range(app_data["Week"].max().start_time + timedelta(days=1), periods=4, freq="W")
    future_weeks_numeric = (
        (future_weeks.year - app_data["Week"].dt.year.min()) * 52 +
        (future_weeks.isocalendar().week - app_data["Week"].dt.week.min())
    )
    future_weeks_numeric = pd.DataFrame(future_weeks_numeric, columns=["Week_numeric"])

    # Förutsägelser
    future_usage = model.predict(future_weeks_numeric)

    # Plotta historisk skärmtid per vecka för appen
    plt.plot(app_data["Week"].astype(str), app_data["Usage (minutes)"], label=f"Historisk skärmtid ({app})", marker="o")

    # Plotta förutsägelser för framtida veckor
    plt.plot(future_weeks.strftime("%Y-%U"), future_usage, label=f"Förutsägelse för {app} (framtida veckor)", linestyle="--", marker="x")

# Lägg till etiketter och titel
plt.xlabel("Vecka")
plt.ylabel("Total skärmtid (minuter)")
plt.title("Förutsägelse av skärmtid för de 3 mest använda apparna per vecka (Linjär Regression)")
plt.xticks(rotation=45)
plt.legend()

# Visa diagrammet
plt.tight_layout()
plt.show()