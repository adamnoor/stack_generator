from cli_functions import *


def get_position(position):
    conn = sqlite3.connect('football.sqlite')
    cur = conn.cursor()
    players = []
    player_objects = cur.execute("SELECT DISTINCT " + position + " FROM current")

    for element in player_objects:
        players.append(element[0])
    
    return players


def get_flex():
    conn = sqlite3.connect('football.sqlite')
    cur = conn.cursor()
    players = []
    player_objects = cur.execute('''
        
        SELECT DISTINCT rb1 FROM current
            UNION 
        SELECT DISTINCT rb2 FROM current
            UNION 
        SELECT DISTINCT wr1 FROM current
            UNION 
        SELECT DISTINCT wr2 FROM current
            UNION 
        SELECT DISTINCT wr3 FROM current
            UNION 
        SELECT DISTINCT te FROM current
            UNION 
        SELECT DISTINCT fx FROM current
            UNION 
        SELECT DISTINCT dst FROM current
    ''')

    for element in player_objects:
        players.append(element[0])
    
    
    return players


def get_player_array(plyr_list):
    for i, element in enumerate (plyr_list):
        print("Select " + str(i) + " to include " + element)

    user_input = input("Select players to include (separate by comma): ").split(",")
    players = []
    for element in user_input:
        if plyr_list[int(element)] not in players:
            print(plyr_list)
            players.append([plyr_list[int(element)]])

    return players


def set_included_players(qb, flex_array):
    players = []
    if qb is not None:
        players.append([qb])
    if len(flex_array) > 0:
        for element in flex_array:
            players.append(element)
    return players


def set_excluded_players(included, all):
    all_players = []
    for element in all:
        if element not in included:
            all_players.append(element)
    for i, element in enumerate (all_players):
        print("Select " + str(i) + " to exclude " + element)
    user_input = input("Select players to exclude (separate by comma): ").split(",")
    players = []
    for element in user_input:
        if all_players[int(element)] not in players:
            players.append([all_players[int(element)]])

    return players


def filter_array(incl_plyrs, excl_plyrs):
    conn = sqlite3.connect('football.sqlite')
    cur = conn.cursor()

    select_statement = '''

    SELECT 
    qb, rb1, rb2, wr1, wr2, wr3, te, fx, dst, budget, projection 
    FROM current
    WHERE 
    '''

    if len(incl_plyrs) > 0:
        select_statement = select_statement + ''' EXISTS (
            SELECT name FROM included_players WHERE name = QB OR name = RB1 or name = RB2 or name = WR1 or name = WR2 or name = WR3 or name = TE or name = FX or name = DST) '''

    if len(excl_plyrs) > 0:
        select_statement = select_statement + ''' NOT EXISTS (
            SELECT name FROM excluded_players WHERE name = QB OR name = RB1 or name = RB2 or name = WR1 or name = WR2 or name = WR3 or name = TE or name = FX or name = DST) '''

    select_statement = "WITH t AS (" + select_statement + ") SELECT qb, rb1, rb2, wr1, wr2, wr3, te, fx, dst, budget, projection FROM t"

    all_rosters = cur.execute(select_statement).fetchall()

    if len(all_rosters) > 1:
        cur.execute('DROP TABLE IF EXISTS current')
        cur.execute('''
        CREATE TABLE current (
            
            "qb" TEXT,
            "rb1" TEXT,
            "rb2" TEXT,
            "wr1" TEXT,
            "wr2" TEXT,
            "wr3" TEXT,
            "te" TEXT,
            "fx" TEXT,
            "dst" TEXT,
            "budget" REAL,
            "projection" REAL
        )
        ''')

        insert_records = "INSERT INTO current (qb, rb1, rb2, wr1, wr2, wr3, te, fx, dst, budget, projection) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.executemany(insert_records, all_rosters)
        conn.commit()
       
        

        
        return True

    else:
       
        print("This restriction doesn't yield any rosters.  Try again.")
        return False


def add_to_table_new(typ, plyr_list):
    conn = sqlite3.connect('football.sqlite')
    cur = conn.cursor()
    # print("Getting a list of players to " + type + "...")
    cur.execute('DROP TABLE IF EXISTS ' + typ + 'd_players')
    cur.execute('''
    CREATE TABLE ''' + typ + '''d_players (

        "name" TEXT
    )
    ''')

    print(plyr_list[len(plyr_list) - 1])

    insert_records = "INSERT INTO " + typ + "d_players (name) VALUES(?)"

    cur.executemany(insert_records, [plyr_list[len(plyr_list) - 1]])
    conn.commit()
    # print("you are trying to " + type + " " + str(plyr_list[len(plyr_list)-1][0]))
    print(plyr_list)


def run_guided():

    initialize_current_table()
    all_qbs = get_position("qb")
    all_flex = get_flex()
    print("Select a Quarterback")
    qb = get_player_selection("include", all_qbs)
    flex_included = get_player_array(all_flex)
    included_players = set_included_players(qb, flex_included)
    excluded_players = set_excluded_players(flex_included, all_flex)
    #add_to_table("include", included_players)
    
    # add_to_table_new("exclude", excluded_players)
    #write to excluded table
    print_rosters = True
    print("Filtering all of the excluded players... ")
    print("")

    for element in excluded_players:
        temp = []
        print(element)
        temp.append(element)
        add_to_table_new("exclude", temp)
        print_rosters = filter_array([], temp)

    for element in included_players:
        temp = []
        print(element)
        temp.append(element)
        add_to_table_new("include", temp)
        print_rosters = filter_array(temp, [])

        
    if print_rosters:
        count = get_count()
        print("This combination yeilded " + str(count) + " rosters")
        write_rosters_to_csv()
    print("")
    user_input = int(input("Press 0 to create another stack, press 1 to quit: "))
    if user_input == 0:
        run_guided()
    else:
        print("The script has terminated")
    
   

