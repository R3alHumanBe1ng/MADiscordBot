import re
import psycopg2
from typing import List, Literal

import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

conn = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="pass",
                        port="5432")
cur = conn.cursor()

tracks = ["CAIRO TOWER FINISH", "ANCIENT WONDERS", "GEZIRA ISLAND", "A KINGS REVIVAL", "SUBTERRANEAN DASH",
          "PHARAOH GAMES", "THOUSAND MINARETS", "NILE RIVER", "URBAN BLAZE", "SCENIC ROUTE", "BACKBURNER",
          "EGYPTIAN WONDER", "FROZEN ROUTE", "DOWNHILL RUN", "LANDSLIDE", "CLIFFHANGER", "CAVE HEAT", "ASPHALT CAVE",
          "DIPPING DOWN", "FREEFALL", "LEAP OF FAITH", "MOUNTAIN POLES", "SNOW VAULT", "THE LAND OF SNOW", "LARGE HILL",
          "BUDDING START", "INDUSTRIAL REVOLUTION", "KITA RUN", "NAMBA PARK", "RAT RACE", "MOAT FINALE", "MEIJI RUSH",
          "REFINED FINISH", "NANIWA TOUR", "WELCOME TO OSAKA", "SAKURA CASTLE", "ALTERNATE ROUTE", "ANCIENT ROME",
          "CAPITAL OF THE WORLD", "PANTHEON SPLIT", "THE ETERNAL CITY", "COMPLETE TOUR", "TIBER STREAM",
          "SAINT PETER KICKOFF", "TIBER CROSS", "ROMAN TUMBLE", "ROMAN BYROADS", "BREAD AND CIRCUSES", "BRIDGE VIEW",
          "BRIDGE FINALE", "CITY DASH", "RAILROAD BUSTLE", "CITY BY THE BAY", "DOWNTOWN RISE", "STREETS OF SF",
          "ROLLER COASTER RIDE", "WATERSIDE", "TUNNEL JAM", "THE TUNNEL", "RUSH MINUTE", "ANCIENT RUINS", "LIGHTHOUSE",
          "THE FREEDOM ROUTE", "GHOST SHIPS", "WINDMILLS", "THE ENCHANTED ISLAND", "WILDLANDS", "THE CAVE",
          "ROCKY VALLEY", "THE PATH OF THE WIND", "DOUBLE ROUNDABOUT", "NANJING STROLL", "FUTURE ROAD",
          "THE PEARL OF THE ORIENT", "PARIS OF THE EAST", "SHOPPING SPREE", "SHEN CITY", "REACH FOR THE SKY",
          "PUDONG RISE", "PEOPLE SQUARE DASH", "ISLAND TOUR", "BEACH LANDING", "HELL VALE", "HOTEL ROAD", "RESORT DASH",
          "THUNDERING START", "ALL-INCLUSIVE", "PARADISE RESORT", "ISLET RACE", "PIER PRESSURE", "CANYON LAUNCH",
          "GOLD RUSH", "NAVAJO NATION", "ITS A TWISTER", "ROLLING MOTORWAY", "TRANSCONTINENTAL RACE", "TRAINSPOTTER",
          "TIME TRAVEL", "US WILDERNESS", "WHIRLWIND CURVE", "HAY BAIL", "COVERED BRIDGE", "URBAN EXODUS",
          "THE CITY THAT NEVER SLEEPS", "UPTOWN", "LEAPS & BOUNDS", "AIR DROPPED", "FRIENDLY NEIGHBORHOOD",
          "WALL STREET RIDE", "SUBWAY SURFING", "QUANTUM JUMPS", "ZEPPELIN RACE", "SIGHT SEEING", "A RUN IN THE PARK",
          "DESERT DRIFT", "DAM BUSTER", "DESERT LIFE", "DESERT RUN", "THE NARROWS", "BRIDGE TO BRIDGE",
          "HAIRPIN SPRINT", "THE CURVE", "WINDING ROAD", "SPRINT FINISH", "STRAIGHT SPRINT", "AUCKLAND TRACK",
          "INDUSTRIAL RUN", "STARTING GRID", "OUT OF BOUNDS", "STRAIGHTS & HAIRPINS", "UNDER CONSTRUCTION",
          "THE CIRCUIT", "LA BOCA", "WATER RUN", "OLD CITY", "TO THE DOCKS", "CROSSTOWN", "THROUGH THE PARK",
          "CROSSTOWN RIVALS", "HARBOR RUN", "FOOTBALL & POLITICS", "NEW CITY", "ROUND THE CITY", "PURPLE BOULEVARD",
          "STADIUM LAP", "CITY CRUISE", "BIG PASSIONS", "JOURNEY TO THE CENTER", "THROUGH THE CENTER",
          "ESCAPE THE LAVA", "COASTAL ICE", "ICY LOOP", "SLIPPERY WHEN ICY", "VOLCANO RUN", "ICE ROAD CIRCUIT",
          "FIRE & ICE", "ICE BREAKERS", "OUT OF THE CENTER", "ICEBERGS & LAVA", "COASTAL LOOP",
          "AIRPORT ESCAPE", "PARIS CIRCLE", "TO THE SEINE", "METROPOLITAIN", "THROUGH THE CITY", "PARASOL RUN",
          "ARC DE TRIOMPHE", "BRIDGES OF PARIS", "SACRED HEART", "ALONG THE SEINE", "TO THE EIFFEL", "NOTRE DAME",
          "METRO", "HILLTOP VILLAGE", "CASTLE CREST", "TIMELESS PATHWAY", "OVER THE HILLS", "FOREST HEIGHTS",
          "VINEYARD TOWNSCAPE", "FULL JOURNEY", "RIVERSIDE CITADEL", "VERSATILE TRAIL", "FULL CIRCUIT ODYSSEY",
          "RIVERINE LAUNCH", "PATHWAY TO PROGRESS", "AIRBORNE SURGE", "SOARING HEIGHTS", "SKYBORNE ODYSSEY",
          "FUTURE HYMN", "SPARKLING RUSH", "BEYOND BOUNDARIES", "TUNNEL THRILLS", "ROCKETING TO THE FUTURE",
          "BOLT OF SPEED", "WIND OF CHANGE", "WAVE RIDER", "NIGHTTIME THRILLS", "CONCERT COASTLINE",
          "OCTO HORIZON ROUTE", "FUNFAIR FRENZY", "ISLAND ADVENTURE", "HILLTOP HAVOC", "AQUARIUM SPRINT", "URBAN RUSH",
          "FESTIVAL RUSH", "SPIREBOUND SURGE", "VELOCITY HUNT", "SKYWARD BREAKER", "WINDCUT HEIGHTS",
          "ROOFTOP ROULETTE", "VERTIGO", "EDGE RUNNER", "WINDSHADOW WARP", "URBAN CURVES"]

cars = ["MITSUBISHI LANCER EVOLUTION", "BMW Z4 LCI E89", "CHEVROLET CAMARO LT", "NISSAN LEAF NISMO RC",
        "NISSAN 370Z NISMO", "VOLKSWAGEN XL SPORT CONCEPT", "DS AUTOMOBILES DS E-TENSE",
        "DODGE CHALLENGER 392 HEMI SCAT PACK", "PORSCHE 718 CAYMAN", "LOTUS ELISE SPRINT 220", "FORD SHELBY GT350R",
        "PORSCHE 911 TARGA 4S", "GINETTA G60", "HONDA CIVIC TYPE-R", "PORSCHE TAYCAN TURBO S", "TVR GRIFFITH",
        "MAZDA FURAI", "DODGE CHALLENGER SRT8", "BMW 3.0 CSL HOMMAGE", "CHEVROLET CAMARO ZL1 50TH EDITION",
        "LOTUS EVORA SPORT 410", "MERCEDES-BENZ AMG GT S", "BMW M4 GTS", "REZVANI BEAST X", "DODGE VIPER ACR",
        "FORD SHELBY GR-1", "PININFARINA H2 SPEED", "ARTEGA SCALO SUPERELLETRA", "ACURA 2017 NSX", "MASERATI ALFIERI",
        "VENCER SARTHE", "PORSCHE 718 CAYMAN GT4 CLUBSPORT", "ARRINERA HUSSARYA 33", "PORSCHE 911 GTS COUPE",
        "ASTON MARTIN DB11", "EXOTIC RIDES W70", "JAGUAR F-TYPE SVR", "PORSCHE 911 GT1 EVOLUTION", "FORD GT",
        "LAMBORGHINI ASTERION", "CADILLAC CIEN CONCEPT", "ITALDESIGN ZEROUNO", "FERRARI 488 GTB", "GLICKENHAUS 003S",
        "FERRARI F12TDF", "CHEVROLET CORVETTE GRAND SPORT", "ASTON MARTIN VANTAGE GT12", "SIN R1 550", "APOLLO N",
        "MERCEDES-BENZ SLR MCLAREN", "ASTON MARTIN DBS SUPERLEGGERA", "LAMBORGHINI HURACAN EVO SPYDER",
        "PORSCHE CARRERA GT", "PORSCHE 911 GT3 RS", "LOTUS EVIJA", "ASTON MARTIN VULCAN", "NISSAN GT-R NISMO",
        "FERRARI J50", "DODGE VIPER GTS", "FERRARI LAFERRARI", "MCLAREN P1", "LAMBORGHINI AVENTADOR SV COUPE",
        "FERRARI 812 SUPERFAST", "CHEVROLET CORVETTE ZR1", "VLF FORCE 1 V10", "PORSCHE 918 SPYDER",
        "VANDA ELECTRICS DENDROBIUM", "MCLAREN 570S SPIDER", "LAMBORGHINI AVENTADOR J", "PORSCHE 911 GT2 RS CLUBSPORT",
        "PAGANI HUAYRA BC", "FERRARI LAFERRARI APERTA", "GENTY AKYLONE", "TECHRULES AT96 TRACK VERSION",
        "LAMBORGHINI CENTENARIO", "FERRARI FXX K", "ICONA VULCANO TITANIUM", "W MOTORS LYKAN HYPERSPORT",
        "LAMBORGHINI EGOISTA", "TRION NEMESIS", "MCLAREN SENNA", "LAMBORGHINI TERZO MILLENNIO",
        "W MOTORS FENYR SUPERSPORT", "ZENVO TS1 GT ANNIVERSARY", "AUTOMOBILI PININFARINA BATTISTA", "KOENIGSEGG REGERA",
        "BUGATTI CHIRON", "KOENIGSEGG JESKO", "RIMAC NEVERA", "LAMBORGHINI GALLARDO LP 560-4", "LAMBORGHINI VENENO",
        "LAMBORGHINI SIAN FKP 37", "LAMBORGHINI SC18", "MCLAREN F1 LM", "CHEVROLET CORVETTE C7.R",
        "CHEVROLET CORVETTE STINGRAY", "FORD GT MK II", "BXR BAILEY BLADE GT1", "SSC TUATARA",
        "ASTON MARTIN VALHALLA CONCEPT CAR", "JAGUAR C-X75", "BENTLEY MULLINER BACALAR", "BENTLEY CONTINENTAL GT3",
        "MCLAREN SPEEDTAIL", "APEX AP-0", "FERRARI F40", "FERRARI 599XX EVO", "FERRARI ENZO FERRARI",
        "FERRARI 488 GTB CHALLENGE EVO", "FERRARI F8 TRIBUTO", "FERRARI SF90 STRADALE", "BMW I8 ROADSTER", "APOLLO IE",
        "PEUGEOT ONYX", "CITROËN GT BY CITROEN", "BUGATTI LA VOITURE NOIRE", "BUGATTI DIVO",
        "LAMBORGHINI HURACAN SUPER TROFEO EVO", "INFINITI PROJECT BLACK S", "ACURA NSX GT3 EVO", "NIO EP9",
        "ASPARK OWL", "INFERNO AUTOMOBILI INFERNO", "ITALDESIGN DAVINCI", "ATS AUTOMOBILI CORSA RRTURBO",
        "PAGANI IMOLA", "MAZZANTI EVANTRA MILLECAVALLI", "LAMBORGHINI ESSENZA SCV12",
        "LAMBORGHINI MURCIELAGO LP 640 ROADSTER", "FERRARI ROMA", "VOLKSWAGEN W12 COUPE", "ZENVO TSR-S",
        "ASTON MARTIN VALKYRIE", "RENAULT R.S. 01", "ASTON MARTIN VICTOR", "BUGATTI VEYRON 16.4 GRAND SPORT VITESSE",
        "ASTON MARTIN V12 SPEEDSTER", "HENNESSEY VENOM F5", "LAMBORGHINI AVENTADOR SVJ ROADSTER",
        "PAGANI ZONDA HP BARCHETTA", "MCLAREN ELVA", "LAMBORGHINI SC20", "RIMAC CONCEPT ONE", "VOLKSWAGEN ELECTRIC R",
        "RAESR TACHYON SPEED", "DRAKO GTE", "RENAULT TREZOR", "TOROIDION 1MW", "ARASH AF10", "KOENIGSEGG GEMERA",
        "NARAN HYPER COUPE", "NISSAN GTR-50 ITALDESIGN", "GLICKENHAUS 007S", "PAGANI ZONDA R", "SALEEN S1", "ULTIMA RS",
        "MCLAREN GT", "LOTUS EMIRA", "JAGUAR XJ220S TWR", "MCLAREN SENNA GTR", "ASTON MARTIN ONE77", "VISION 1789",
        "TUSHEK TS 900 RACER PRO", "ARASH AF8 FALCON EDITION", "PURITALIA BERLINETTA", "BRABHAM BT62",
        "BOLWELL MK X NAGARI 500", "LAMBORGHINI COUNTACH 25TH ANNIVERSARY", "LAMBORGHINI MIURA CONCEPT",
        "LAMBORGHINI DIABLO GT", "LAMBORGHINI REVENTON ROADSTER", "LAMBORGHINI SESTO ELEMENTO",
        "LAMBORGHINI COUNTACH LPI 800-4", "FERRARI MONZA SP1", "RENAULT DEZIR", "PAGANI HUAYRA R", "MCLAREN 765LT",
        "BUGATTI EB110", "BUGATTI CENTODIECI", "BENTLEY CONTINENTAL GT SPEED", "PRAGA R1",
        "INFERNO AUTOMOBILI SETTIMO CERCHIO", "AJLANI DRAKUMA", "NISSAN R390 GT1", "GLICKENHAUS 004C", "PEUGEOT SR1",
        "KOENIGSEGG AGERA RS", "CHRYSLER ME412", "BUGATTI BOLIDE", "ARES S1", "PORSCHE BOXSTER 25TH", "PEUGEOT 9X8",
        "MCLAREN 650S GT3", "FARADAY FFZERO1", "KOENIGSEGG CCXR", "MASERATI MC12", "FV FRANGIVENTO SORPASSO GT3",
        "JAGUAR XJR-9", "KTM X-BOW GTX", "KEPLER MOTION", "TORINO DESIGN SUPER SPORT", "SPANIA GTA 2015 GTA SPANO",
        "MERCEDES-BENZ MERCEDES-AMG GT BLACK SERIES", "MCLAREN 600LT SPIDER", "DONKERVOORT D8 GTO INDIVIDUAL SERIES",
        "FERRARI F50", "LAMBORGHINI REVUELTO", "JAGUAR XE SV PROJECT 8", "APOLLO EVO", "DE TOMASO P72",
        "PORSCHE 935 (2019)", "PORSCHE PANAMERA TURBO S", "MERCEDES-BENZ CLK-GTR", "BMW M4 GT3",
        "NISSAN 370Z NEON EDITION", "JAGUAR XJR-15", "MCLAREN SOLUS GT", "NOBLE M600 SPEEDSTER", "SALEEN S7 TWIN TURBO",
        "KOENIGSEGG CC850", "DEUS VAYANNE", "BUGATTI CHIRON SUPER SPORT 300+", "RIMAC CONCEPT S",
        "FORD MUSTANG MACH-E1400", "MCLAREN ARTURA", "MASERATI MC20", "MERCEDES-BENZ 2022 SHOWCAR VISION AMG",
        "LAMBORGHINI INVENCIBLE", "DEVEL SIXTEEN", "FERRARI 296 GTB", "ASTON MARTIN DBS GT ZAGATO",
        "FORD TEAM FORDZILLA P1", "LAMBORGHINI HURACAN STO", "FERRARI DAYTONA SP3", "PAGANI UTOPIA COUPE",
        "ALFA ROMEO GIULIA GTAM", "ATS AUTOMOBILI GT", "W MOTORS LYKAN NEON", "FORMULA E GEN 2 ASPHALT EDITION",
        "FV FRANGIVENTO ASFANE", "ZENVO AURORA TUR", "ASTON MARTIN VANTAGE V12 2022", "PORSCHE 911 CARRERA RS 3.8",
        "LAMBORGHINI SC63", "DE TOMASO P900", "LOTUS E-R9", "MASERATI MC20 GT2", "ASTON MARTIN DB12",
        "MCMURTRY SPEIRLING", "NISSAN GT-R NEON EDITION", "BUGATTI CHIRON PUR SPORT", "LAMBORGHINI AUTENTICA",
        "PORSCHE MISSION R", "KOENIGSEGG JESKO ABSOLUT", "FORD MUSTANG RTR SPEC 5 10TH ANNIVERSARY",
        "FORD GT FRANKIE EDITION", "FERRARI SF90 XX STRADALE", "TVR SAGARIS", "ASTON MARTIN VALOUR",
        "LAMBORGHINI TEMERARIO", "MERCEDES-BENZ VISION ONE-ELEVEN", "BUGATTI MISTRAL", "CZINGER 21C",
        "AUTOMOBILI PININFARINA BATTISTA EDIZIONE NINO FARINA", "RIMAC NEVERA TIME ATTACK",
        "PORSCHE 911 TURBO 50 YEARS", "PININFARINA TEOREMA", "MCLAREN SABRE", "FORD SHELBY SUPER SNAKE",
        "JAGUAR XKR-S GT", "DS AUTOMOBILES DS E-TENSE PERFORMANCE", "RAESR TARTARUS", "FERRARI 449P MODIFICATA",
        "KIMERA EVO37", "FV FRANGIVENTO GT65", "PRAGA BOHEMA", "PORSCHE 911 50 YEARS PORSCHE DESIGN",
        "HTT LOCUS PLÉTHORE LC750", "LEGO TECHNIC CHEVROLET CORVETTE STINGRAY"]

timeRegex = re.compile(r"(\d:)?[0-5][0-9](\.(\d){1,3})?")

bot = commands.Bot(command_prefix="!", intents=intents)

def element_exists(uid, track, car):
    cur.execute('''
        SELECT EXISTS (
            SELECT 1
            FROM table1
            WHERE uid = %s AND track = %s AND car = %s
        )''', (uid, track, car))
    return cur.fetchone()[0]

def time_sorting_key(row):
    return int(row[4][:1])*60000 + int(row[4][2:4])*1000 + int(row[4][5:])

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

async def user_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=user.display_name, value=str(user.id))
        for user in interaction.guild.members if current.lower() in user.display_name.lower() or current.lower() in user.global_name.lower() or current.lower() in user.name.lower()
    ]

async def car_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=car, value=car)
        for car in cars if current.lower() in car.lower()
    ]


async def track_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=track, value=track)
        for track in tracks if current.lower() in track.lower()
    ]


@bot.tree.command(name="set_time", description="Set your best time for track + car")
@app_commands.describe(track="the track driven")
@app_commands.describe(car="the car used")
@app_commands.autocomplete(track=track_autocomplete, car=car_autocomplete)
@app_commands.describe(time="your time (format: X:XX.XXX)")
async def setTime(interaction: discord.Interaction, track: str, car: str, time: str):
    if track not in tracks:
        await interaction.response.send_message("Invalid Track", ephemeral=True)
    elif car not in cars:
        await interaction.response.send_message("Invalid Car", ephemeral=True)
    else:
        time = timeRegex.search(time)
        if time is None:
            await interaction.response.send_message("Invalid Time", ephemeral=True)
        time = time.group()
        if ':' not in time:
            time = '0:' + time
        if '.' not in time:
            time = time + '.000'
        while len(time) < 8:
            time = time + '0'

        if element_exists(str(interaction.user.id), track, car):
            cur.execute("""
                                UPDATE table1
                                SET time = %s
                                WHERE uid = %s AND track = %s AND car = %s;
                                """,
                        (time, str(interaction.user.id), track, car))
        else:
            cur.execute("""
                        INSERT INTO table1 (uid, track, car, time)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (str(interaction.user.id), track, car, time))
        conn.commit()
        await interaction.response.send_message(f"{interaction.user.mention} set time {time} for {track} with {car}")

@bot.tree.command(name="show_times", description="Display times based on inputs")
@app_commands.describe(user="select a user (optional)")
@app_commands.describe(track="select a track (optional)")
@app_commands.describe(car="select a car (optional)")
@app_commands.autocomplete(user=user_autocomplete, track=track_autocomplete, car=car_autocomplete)
async def showTimes(interaction: discord.Interaction, user: str = None, track: str = None, car: str = None):
    if user is not None and bot.get_user(int(user)) not in bot.users:
        await interaction.response.send_message("Invalid User", ephemeral=True)
    elif track is not None and track not in tracks:
        await interaction.response.send_message("Invalid Track", ephemeral=True)
    elif car is not None and car not in cars:
        await interaction.response.send_message("Invalid Car", ephemeral=True)

    if user is None and track is None and car is None:
        await interaction.response.send_message("Must have at least one input", ephemeral=True)
    elif user is None and ((track is not None and car is None) or (track is None and car is not None)):
        await interaction.response.send_message("This input must be used with at least one other", ephemeral=True)

    if track is None and car is None:
        cur.execute("""
        SELECT *
        FROM table1
        WHERE uid = %s;
        """, (user,))
        ts = cur.fetchall()
        ts.sort(key=lambda a: ord(a[2][0])*100 + ord(a[3][0]))
        await interaction.response.send_message("# " + bot.get_user(int(user)).mention +
        "\n\n".join(f"\n**{row[2]}**\n{row[3]}\n*{row[4]}*"
        for row in ts))
    elif car is None:
        cur.execute("""
        SELECT *
        FROM table1
        WHERE uid = %s AND track = %s;
        """, (user, track))
        ts = cur.fetchall()
        ts.sort(key=lambda a: a[3])
        await interaction.response.send_message("# " + bot.get_user(int(user)).mention + ", " + track +
        "\n\n".join(f"\n**{row[3]}**\n*{row[4]}*"
        for row in ts))
    elif track is None:
        cur.execute("""
        SELECT *
        FROM table1
        WHERE uid = %s AND car = %s;
        """, (user, car))
        ts = cur.fetchall()
        ts.sort(key=lambda a: a[2])
        await interaction.response.send_message("# " + bot.get_user(int(user)).mention + ", " + car +
        "\n\n".join(f"\n**{row[2]}**\n*{row[4]}*"
        for row in ts))
    elif user is None:
        cur.execute("""
        SELECT *
        FROM table1
        WHERE track = %s AND car = %s;
        """, (track, car))
        ts = cur.fetchall()
        ts.sort(key=time_sorting_key)
        await interaction.response.send_message("# " + track + ", " + car +
        "\n\n".join(f"\n**{bot.get_user(int(row[1])).mention}**\n*{row[4]}*"
        for row in ts))


bot.run('MTMzMTM2MTYxNjA4Nzg3NTYwNA.GcU68R.EcstzgVVyMJjAcjDRSCHh0mbJasdJhAzQlgyJ4')
