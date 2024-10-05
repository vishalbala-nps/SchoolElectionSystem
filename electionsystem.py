import mysql.connector
import getpass

# Server Details
host = "localhost"
database = "electionSystem"

#Vars
superuser = False

#Functions
def init_tables():
    try:
        cursor.execute("create table if not exists elections(id int not null unique primary key AUTO_INCREMENT,name varchar(15) not null unique)")
        cursor.execute("create table if not exists candidates(id int not null unique primary key,name varchar(15) not null,class int not null,section varchar(1) not null,election int not null,foreign key (election) references elections(id))")
        cursor.execute("create table if not exists votes(id int not null unique primary key,election_id int not null,votes int not null,foreign key (election_id) references elections(id))")
        con.commit()
        return 0
    except mysql.connector.Error as e:
        print("An error occurred! Error:",e)
        return -1
username =  input("Please enter username: ")
password =  getpass.getpass('Please enter password: ') #Used to get a password from user (so that password is not shown)

try:
    con = mysql.connector.connect(host=host,user=username,passwd=password,database=database)
    cursor = con.cursor()
    print("Logged in to database")
    #Check the tables
    cursor.execute("show tables")
    if len(cursor.fetchall()) != 3:
        print("Creating tables")
        if init_tables() != 0:
            exit()
    #Check if user can access votes table, if yes, a superuser or else a voter
    try:
        cursor.execute("select * from votes")
    except mysql.connector.Error as e:
        superuser = False
    else:
        superuser = True
        cursor.fetchall()
    while True:
        print()
        print("Menu: ")
        print("1. Start voting")
        if superuser:
            exitval = 6
            print("2. Add a voter")
            print("3. Manage Elections")
            print("4. Manage Candidates")
            print("5. Manage Results")
            print("6. Exit")
        else:
            exitval = 2
            print("2. Exit")
        op = int(input("Enter option: "))
        if op == 1:
            pass
        elif op == 2 and superuser:
            newu = input("Please enter username: ")
            newp = getpass.getpass("Please enter password: ")
            try:
                cursor.execute("create user '{0}'@'%' identified by '{1}'".format(newu,newp))
                cursor.execute("grant select on {0}.candidates to '{1}'@'%'".format(database,newu))
                cursor.execute("grant select on {0}.elections to '{1}'@'%'".format(database,newu))
                cursor.execute("grant update on {0}.votes to '{1}'@'%'".format(database,newu))
                con.commit()
            except Exception as e:
                print("Failed to add user:",e)
            else:
                print("Voter added successfully")
        elif op == 3 and superuser:
            print()
            while True:
                print("Manage elections: ")
                print("1. Add Election")
                print("2. View Elections")
                print("3. Delete Election")
                print("4. Back")
                op = int(input("Enter option: "))
                if op == 1:
                    electionName = input("Enter election name: ")
                    try:
                        cursor.execute("insert into elections(name) values('{0}')".format(electionName))
                        con.commit()
                        cursor.execute("select last_insert_id()")
                        print("Election Added successfully! Election ID is: ",cursor.fetchall()[0][0])
                        print()
                    except Exception as e:
                        print("Failed to add election! Error:",e)
                elif op == 2:
                    print()
                    cursor.execute("select * from elections")
                    for i in cursor.fetchall():
                        print("Election ID:",i[0])
                        print("Election name:",i[1])
                        print()
                elif op == 3:
                    electionId = input("Enter election id to remove:")
                    try:
                        cursor.execute("delete from elections where id={0}".format(electionId))
                        con.commit()
                        print("Election deleted successfully")
                    except Exception as e:
                        print("Failed to delete election! Error: ",e)
                elif op == 4:
                    break
                else:
                    print("Invalid option!")
        elif op == 4 and superuser:
            print("add candidate")
        elif op == 5 and superuser:
            print("view result")
        elif op == exitval:
            print("Exiting")
            exit()
        else:
            print("Invalid option!")
except mysql.connector.Error as e:
    if e.errno == 1045: #1045 is auth error
        print("Invalid Credentials! Please check username and password and try again")
    elif e.errno == 1049: #1049 is db not found error
        print("Database not found! Please create it")
    else:
        print("Unknown error:",e)