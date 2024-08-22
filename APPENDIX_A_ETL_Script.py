import os
import fastf1
import fastf1.core
from datetime import datetime
import pandas as pd
from psycopg2 import sql
import psycopg2


# Define cache directory
CACHE_DIR = '/opt/airflow/dags/fastf1_cache/'
data_dir = '/opt/airflow/dags/data/'
staging_db_params = {
        "dbname": "F1_Staging",
        "user": "airflow",
        "password": "airflow",
        "host": "10.128.15.202",
        "port": "5432",
    }

production_db_params = {
        "dbname": "F1_Warehouse",
        "user": "airflow",
        "password": "airflow",
        "host": "10.128.15.202", 
        "port": "5432",
    }


# Create cache directory if it doesn't exist
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Initialize FastF1 with cache
fastf1.Cache.enable_cache(CACHE_DIR)


def extract_sessions_to_file(year):
    """
    Fetches the event schedule for the specified year and processes each event to 
    extract session information.

    Parameters:
    year (int): The year for which the schedule is to be fetched.

    Returns:
    List: A list containing session information for all events in the specified year.    
    """
    try:
        # Fetch all events in the specified year
        event_schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        print(f"Failed to fetch event schedule for year {year}: {e}")
        return None

    sessions = []

    for _, row in event_schedule.iterrows():
        try:
            event_sessions = get_sessions(row)
            sessions.extend(event_sessions)
        except Exception as e:
            print(f"Failed to process sessions for {row['EventName']}: {e}")
            continue

    sessions_df = pd.DataFrame(sessions)
    #mini = sessions[0:50]
    #sessions_df = pd.DataFrame(mini)

    # Save to CSV 
    sessions_df.to_csv(f"{data_dir}sessions.csv", index=False)
    return sessions
    #return mini
    
    
def get_sessions(schedule):
    sessions = []
    for i in range(1, 6):
        if schedule[f"Session{i}"] != "None":
            dat = schedule[f"Session{i}DateUtc"]
            # Convert the Timestamp to a string
            # utc_timestamp_str = dat.strftime('%Y-%m-%d %H:%M:%S %Z')  #2021-03-12 07:00:00
            utc_timestamp_str = dat.strftime("%Y-%m-%d %H:%M:%S")
            # Parse the string to a datetime object
            date_obj = datetime.strptime(utc_timestamp_str, "%Y-%m-%d %H:%M:%S")
            sessions.append(
                {
                    "year": date_obj.year,
                    "event_OfficialName": schedule[f"OfficialEventName"],
                    "event_name": schedule[f"EventName"],
                    "event_format": schedule[f"EventFormat"],
                    "event_date": schedule[f"EventDate"],
                    "event_location": schedule[f"Location"],
                    "race_id": schedule[f"RoundNumber"],
                    "session_name": schedule[f"Session{i}"],
                    "time": schedule[f"Session{i}DateUtc"],
                }
            )

    return sessions

def fetch_events_results(sessions):
    
    event_results = []

    # Get the event schedule for the specified year
    for sess in sessions:
        try:
            _session = fastf1.get_session(
                sess["year"], sess["event_name"], sess["session_name"]
            )
            _session.load()
            # for result in _session.results:
            for indx, result in _session.results.iterrows(): 
                event_results.append(
                    {
                        "year": sess["year"],
                        "event": sess["event_name"],
                        "event_date": sess["event_date"],
                        "event_roundnumber": sess["race_id"],
                        "session": sess["session_name"], 
                        "driver_number": result["DriverNumber"],                       
                        "driver_id": result["DriverId"],                        
                        "driver_fullname": result["FullName"],
                        "driver_BroadcastName": result["BroadcastName"],
                        "driver_Abbreviation": result["Abbreviation"],
                        "driver_HeadshotUrl": result["HeadshotUrl"],
                        "team_id": result["TeamId"],
                        "team_name": result["TeamName"],
                        "team_color": result["TeamColor"],
                        "position": result["Position"],
                        "points": result["Points"],
                        "Q1_duration": result["Q1"],
                        "Q2_duration": result["Q2"],
                        "Q3_duration": result["Q3"],
                        "Status": result["Status"]                        
                    }
                )
        except Exception as e:
            print(
                f"Error loading session for {sess['event_name']} ({sess['year']}): {e}"
            )

    # Convert to DataFrame
    event_results_df = pd.DataFrame(event_results)    
    event_results_df.to_csv(f"{data_dir}compact_results.csv", index=False)
    return event_results

def fetch_session_results(sessions):
    """
    Fetches event results for a given list of sessions and saves them to a CSV file.
    
    Parameters:
    sessions (list): A list of session dictionaries, each containing 'year', 
    'event_name', and 'session_name'.
    
    Returns:
    list: A list of dictionaries containing event results.
    """        
    event_results = []

    for sess in sessions:
        try:
            _session = fastf1.get_session(
                sess["year"], sess["event_name"], sess["session_name"]
            )
            _session.load()
            
            # Ensure results are available and in DataFrame format
            if isinstance(_session.results, pd.DataFrame):
                for _, result in _session.results.iterrows(): 
                    event_results.append(
                        {
                            "year": sess["year"],
                            "event": sess["event_name"],
                            "event_date": sess["event_date"],
                            "event_roundnumber": sess["race_id"],
                            "session": sess["session_name"], 
                            "driver_number": result["DriverNumber"],                       
                            "driver_id": result["DriverId"],                        
                            "driver_fullname": result["FullName"],
                            "driver_BroadcastName": result["BroadcastName"],
                            "driver_Abbreviation": result["Abbreviation"],
                            "driver_HeadshotUrl": result["HeadshotUrl"],
                            "team_id": result["TeamId"],
                            "team_name": result["TeamName"],
                            "team_color": result["TeamColor"],
                            "position": result["Position"],
                            "points": result["Points"],
                            "Q1_duration": result["Q1"],
                            "Q2_duration": result["Q2"],
                            "Q3_duration": result["Q3"],
                            "Status": result["Status"]                 
                        }
                    )
            else:
                print(f"No valid results for {sess['event_name']} ({sess['year']}).")
                
        except Exception as e:
            print(
                f"Error loading session for {sess['event_name']} ({sess['year']}): {e}"
            )

    # Convert to DataFrame
    event_results_df = pd.DataFrame(event_results)    

    # Save to CSV
    event_results_df.to_csv(f"{data_dir}compact_results.csv", index=False)
    
    return event_results

def EXTRACT_DATA(year:int):
    # Data extraction phase
    sessions = extract_sessions_to_file(year)
    fetch_session_results(sessions)

def fetch_and_save_telemetry_data(sessions, output_dir="./data/telemetry"):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for sess in sessions:
        try:
            _session = fastf1.get_session(
                sess["year"], sess["event_name"], sess["session_name"]
            )
            _session.load()

            for drv in _session.drivers:
                driver_number = _session.get_driver(drv)["DriverNumber"]
                telemetry = _session.laps.pick_driver(driver_number).get_telemetry()

                # Convert telemetry data to DataFrame
                telemetry_df = pd.DataFrame(telemetry)
                # Define the filename for the CSV
                csv_filename = f"{sess['year']}_{sess['event_name']}_{sess['session_name']}_{drv}.csv"
                csv_filepath = os.path.join(output_dir, csv_filename)

                # Save the telemetry DataFrame to a CSV file
                telemetry_df.to_csv(csv_filepath, index=False)

                print(f"Saved telemetry data for driver {drv} to {csv_filepath}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print("Telemetry data fetching and saving complete.")

def fetch_and_save_track_info(sessions, output_file="./data/track_info.csv"):
    track_info_list = []

    for sess in sessions:
        try:
            _session = fastf1.get_session(
                sess["year"], sess["event_name"], sess["session_name"]
            )
            _session.load()

            event = _session.event

            # Get circuit information
            circuit_info = _session.get_circuit_info()
            # Extract specific details
            # track_name = circuit_info.circuitName
            # location = circuit_info.Location
            # track_length = circuit_info.Length
            # number_of_turns = circuit_info.NumberOfTurns

            # print(f"Track Name: {track_name}")
            # print(f"Location: {location}")
            # print(f"Track Length: {track_length} km")
            # print(f"Number of Turns: {number_of_turns}")

            print(f"Event = {event}")

            track_info = {
                "year": sess["year"],
                "event_name": sess["event_name"],
                "country": event.get("Country", "Unknown"),
                "location": event.get("Location", "Unknown"),
                "track_name": event.get("OfficialEventName", "Unknown"),
                "track_id": event.get("EventId", "Unknown"),
                "number_of_laps": event.get("NumberOfLaps", "Unknown"),
                "track_length_km": event.get("TrackLength", "Unknown"),
                "first_grand_prix": event.get("FirstGrandPrix", "Unknown"),
                "lap_record": event.get("LapRecord", "Unknown"),
                "event_date": event.get("EventDate", "Unknown"),
            }
            track_info_list.append(track_info)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    # Convert to DataFrame
    track_info_df = pd.DataFrame(track_info_list)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save to CSV
    track_info_df.to_csv(output_file, index=False)

    print(f"Track information saved to {output_file}")

def read_csv(csv_file):
    """Read data from a CSV file into a pandas DataFrame."""
    df = pd.read_csv(f"{data_dir}{csv_file}")
    
    # Convert columns with datetime type
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            df[col] = pd.to_datetime(df[col])  # Ensure datetime format    
        elif 'duration' in col.lower():
            df[col] = pd.to_timedelta(df[col])  # Ensure timedelta
            df[col] = df[col].fillna(pd.Timedelta(0))
    
    return df

def map_dtype(dtype):
    """Map pandas dtype to PostgreSQL data type."""
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    elif pd.api.types.is_timedelta64_dtype(dtype):
        return "INTERVAL"
    else:
        return "TEXT"

def create_table(table_name, df):
    """Create the table in the PostgreSQL database if it doesn't exist."""    
    conn = psycopg2.connect(**staging_db_params)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    create_table_query = sql.SQL(
        """
        CREATE TABLE IF NOT EXISTS {table} (
            {columns}
        )
    """
    ).format(
        table=sql.Identifier(table_name),
        columns=sql.SQL(", ").join(
            sql.SQL("{} {}").format(
                sql.Identifier(col), sql.SQL(map_dtype(df[col].dtype))
            )
            for col in df.columns
        ),
    )
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

def clear_staging_tables():
    """
    Drops the 'sessions' and 'results' tables from the staging database.
    """
    # Connect to PostgreSQL database    
    conn = psycopg2.connect(**staging_db_params)
    cursor = conn.cursor()

    # Drop the 'sessions' table if it exists
    try:
        cursor.execute("DROP TABLE IF EXISTS sessions")
        print("Table 'sessions' dropped successfully.")
    except Exception as e:
        print(f"An error occurred while dropping 'sessions' table: {e}")
    
    # Drop the 'results' table if it exists
    try:
        cursor.execute("DROP TABLE IF EXISTS results")
        print("Table 'results' dropped successfully.")
    except Exception as e:
        print(f"An error occurred while dropping 'results' table: {e}")

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

def insert_data_to_db(table, df):
    """Insert session data from DataFrame into the PostgreSQL sessions table."""
    # Connect to PostgreSQL database    
    conn = psycopg2.connect(**staging_db_params)
    cursor = conn.cursor()
    
    # Insert DataFrame rows into the table
    for _, row in df.iterrows():
        insert_query = sql.SQL(
            """
            INSERT INTO {table} ({columns}) VALUES ({values})
        """
        ).format(
            table=sql.Identifier(table),
            columns=sql.SQL(", ").join(map(sql.Identifier, df.columns)),
            values=sql.SQL(", ").join(sql.Placeholder() * len(df.columns)),
        )
        cursor.execute(insert_query, tuple(row))

    # Commit the transaction and close the connection
    conn.commit()
    cursor.close()
    conn.close()

def insert_sessions():

    csv_file = "sessions.csv"  # Path to your CSV file
    
    # Read sessions from CSV
    #sessions_df = read_sessions_from_csv(csv_file)
    sessions_df = read_csv(csv_file)

    # Create sessions table if it doesn't exist    
    create_table("sessions", sessions_df.head(1))

    # Insert session data into the database
    print("Inserting DATA . .  . . . ")
    # insert_sessions_to_db(engine, sessions_df)
    insert_data_to_db("sessions", sessions_df)

    print("Session data has been successfully inserted into the Staging table.")

def insert_results():

    csv_file = "compact_results.csv"  
    
    # Read sessions from CSV
    results_df = read_csv(csv_file)

    # Create sessions table if it doesn't exist    
    create_table("results", results_df.head(1))

    # Insert session data into the database
    print("Inserting DATA . .  . . . ")
    # insert_sessions_to_db(engine, sessions_df)
    insert_data_to_db("results", results_df)

    print("Result data has been successfully inserted into the PostgreSQL table.")

def MOVE_DATA_2_STAGING():

    clear_staging_tables()

    insert_sessions()
    
    insert_results()

def select_unique_race_ids(conn):   
    
    try:       
        cursor = conn.cursor()

        # Define the query to select unique race_id values
        query = sql.SQL("SELECT DISTINCT ON (race_id) * FROM public.sessions ORDER BY race_id, event_date")

        # Execute the query
        cursor.execute(query)

        # Fetch all the unique race_id values
        races = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        

        return races

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return None

def select_sessions(conn, race_id):   
    
    try:       
        cursor = conn.cursor()

       # Define the query to select rows by race_id
        query = sql.SQL("SELECT * FROM public.sessions WHERE race_id = %s")

        # Execute the query with the race_id parameter
        cursor.execute(query, (race_id,))

        # Fetch all the unique race_id values
        _sessions = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()        

        return _sessions
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return None

def select_session_results(conn, year, roundNumber, sessionName):
    try:
        # Create a cursor using the connection
        cursor = conn.cursor()

        # Define the query to select rows from the 'results' table based on the given parameters
        query = sql.SQL("""
            SELECT * FROM public.results
            WHERE year = %s AND event_roundNumber = %s AND session = %s
        """)

        # Execute the query with the provided parameters
        cursor.execute(query, (year, roundNumber, sessionName))

        # Fetch the results
        session_results = cursor.fetchall()

        # Fetch the column names
        colnames = [desc[0] for desc in cursor.description]

        # Convert the results to a pandas DataFrame
        session_results_df = pd.DataFrame(session_results, columns=colnames)

        # Close the cursor
        cursor.close()

        return session_results_df

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return None    

def insert_race_dimension(conn,race):
    #Transform race data
    round_number = race[6]
    schedule_name = race[1]
    location = race[5]
    year = race[0]
    date = race[8]

    try:
        with conn.cursor() as cursor:
            # Insert into RaceDimension and return the generated ID
            cursor.execute("""
                INSERT INTO RaceDimension (round_number, schedule_name, location, year, date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT unique_round_year 
                    DO UPDATE SET round_number = EXCLUDED.round_number
                RETURNING id;
            """, (round_number, schedule_name, location, year, date))
            
            # Fetch the generated id
            race_id = cursor.fetchone()[0]
            
            conn.commit()
            return race_id

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None

def insert_session_dimension(conn,_session, race_id):  
    #Transform data
    session_name = _session[7]
    time = _session[8]        
    try:
        with conn.cursor() as cursor:
            # Insert into SessionDimension and return the generated ID  
                cursor.execute("""
                    INSERT INTO SessionDimension (session_name, time, race_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT ON CONSTRAINT session_race_unique 
                        DO UPDATE SET session_name = EXCLUDED.session_name
                    RETURNING id;
                """, (session_name, time, race_id))
                
                # Fetch the generated id
                session_id = cursor.fetchone()[0]
                conn.commit()
                return session_id

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None

def insert_team_dimension(conn,team):  
    #Transform data
    team_id = team['team_id']
    team_name = team['team_name']        
    team_color = team['team_color']        
    try:
        with conn.cursor() as cursor:
            # Insert into SessionDimension and return the generated ID  
                cursor.execute("""
                    INSERT INTO TeamDimension (team_id, team_name, team_color)
                    VALUES (%s, %s, %s)
                    ON CONFLICT ON CONSTRAINT team_id_unique 
                        DO UPDATE SET team_name = EXCLUDED.team_name
                    RETURNING team_id;
                """, (team_id, team_name, team_color))
                
                # Fetch the generated id
                team_id = cursor.fetchone()[0]
                conn.commit()
                return team_id

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None

def insert_driver_dimension(conn,driver):  
    #Transform data
    driver_id = driver['driver_id']
    driver_number = driver['driver_number']        
    full_name = driver['driver_fullname']        
    name_abbreviation = driver['driver_Abbreviation']        
    broadcast_name = driver['driver_BroadcastName']        
    headshot_url = driver['driver_HeadshotUrl']        
    team_id = driver['team_id']        
    try:
        with conn.cursor() as cursor:
            # Insert into SessionDimension and return the generated ID  
                cursor.execute("""
                    INSERT INTO driverdimension (driver_id, driver_number, full_name, name_abbreviation, broadcast_name, headshot_url, team_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT driver_id_unique 
                        DO UPDATE SET name_abbreviation = EXCLUDED.name_abbreviation                        
                    RETURNING driver_id;
                """, (driver_id, driver_number, full_name, name_abbreviation, broadcast_name, headshot_url, team_id))
                
                # Fetch the generated id
                driver_id = cursor.fetchone()[0]
                conn.commit()                

                return driver_id

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None

def insert_race_result_fact(conn,race, session, team,driver, df ):  
    #Transform data
    points = df['points']
    position = df['position']
    if pd.isna(points) or pd.isna(position):
        points = 0
        position = 0

    try:
        with conn.cursor() as cursor:
            # Insert into SessionDimension and return the generated ID  
                cursor.execute("""
                    INSERT INTO raceresultsfact (race_id, session_id, driver_id, team_id, "position", points)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT ON CONSTRAINT session_driver_unique DO NOTHING;
                """, (race, session, driver,team, position, points))
                
                # Fetch the generated id
                #driver_id = cursor.fetchone()[0]
                conn.commit()
                return None

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
        return None

def TRANSFORM_LOAD():

    warehouse_conn = psycopg2.connect(**production_db_params)    
    staging_conn = psycopg2.connect(**staging_db_params)    

    #Migrate_RaceDimension()
    #Select Unique(raceID) FROM sessions table
    races = select_unique_race_ids(staging_conn)
    for race in races:
        #for each raceID, create a raceDimension record if it does not already exist
        race_id = insert_race_dimension(warehouse_conn, race)
            #for each raceDimension created, Select sessions with that raceID/roundnumber
        _sessions = select_sessions(staging_conn,race[6])
        for sess in _sessions:
            #Create SessionDimension records if it does not already exist.
            sess_id = insert_session_dimension(warehouse_conn,sess,race_id)
            #Select results for this session
            _sessions_results_df = select_session_results(staging_conn,year=sess[0],roundNumber=race[6], sessionName=sess[7], )
            #Create TeamDimension
            #Select Unique Teams            
            unique_teams_df = _sessions_results_df[['team_id', 'team_name', 'team_color']].drop_duplicates()
            for _, team in unique_teams_df.iterrows():
                #create Teams
                team_id = insert_team_dimension(warehouse_conn,team)
                #For each team select all drivers that took part in the session 
                drivers_df = _sessions_results_df.loc[(_sessions_results_df['team_id'] == team['team_id']) & ( _sessions_results_df['session'] == sess[7]) & ( _sessions_results_df['event_roundnumber'] == race[6]) ]          
                for _, drv in drivers_df.iterrows():
                    #Create each driver
                    driver_id = insert_driver_dimension(warehouse_conn,drv)
                    #result = df.loc[(df['Age'] > 25) & (df['City'] == 'Los Angeles')]
                    race_result = insert_race_result_fact(warehouse_conn, race=race_id,session=sess_id, team=team_id,driver=driver_id,df=drv)
                    #driver_result = _sessions_results_df.loc[(_sessions_results_df['driver_id'] == drv['driver_id'])]
                    print(driver_id)

    

def main():

    EXTRACT_DATA(2023)  # Data extraction phase

    MOVE_DATA_2_STAGING() # Data Staging Phase

    TRANSFORM_LOAD()     #Transformation and loading Phase



if __name__ == "__main__":
    main()
