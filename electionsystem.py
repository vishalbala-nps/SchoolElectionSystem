import mysql.connector
import getpass
from tabulate import tabulate

# Server Details
host = "localhost"
database = "electionSystem"

#Vars
superuser = False

#Functions
def init_tables():
    try:
        cursor.execute("create table if not exists elections(id int not null unique primary key AUTO_INCREMENT,name varchar(15) not null unique)")
        cursor.execute("create table if not exists candidates(id int not null unique primary key AUTO_INCREMENT,name varchar(15) not null,class int not null,section varchar(1) not null,election int not null,foreign key (election) references elections(id) on delete cascade)")
        cursor.execute("create table if not exists votes(candidate int not null,election int not null,votes int not null,foreign key (election) references elections(id) on delete cascade,foreign key (candidate) references candidates(id) on delete cascade)")
        con.commit()
        return 0
    except mysql.connector.Error as e:
        print("An error occurred! Error:",e)
        return -1
def checkTie(lst):
    ifirst = lst[0]
    tievals = [ifirst]
    for i in range(1,len(lst)):
        if lst[i][4] == ifirst[4]:
            ifirst = lst[i]
            tievals.append(lst[i])
        else:
            break
    return tievals
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
    #Check if user is a superuser
    cursor.execute("select user from mysql.user where super_priv='Y' and user='{0}'".format(username))
    if len(cursor.fetchall()) == 0:
        superuser = False
    else:
        superuser = True
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
            try:
                cursor.execute("select * from elections order by id")
            except Exception as e:
                print("Failed to get list of elections! Error:",e)
                continue
            elections = cursor.fetchall()
            print()
            while True:
                print("Please select election: ")
                for i in elections:
                    print(i[0],". ",i[1],sep="")
                op = input("Enter election id (press enter to go back): ")
                if op == "":
                    break
                else:
                    cursor.execute("select * from candidates where election={0} order by id".format(op))
                    cf = cursor.fetchall()
                    if len(cf) == 0:
                        print("Empty election or invalid election id")
                    else:
                        print("Please select candidate:")
                        for i in cf:
                            print(i[0],". ",i[1],", ",i[2],i[3],sep="")
                        cid = input("Please enter candidate id (enter to go back): ")
                        if cid == "":
                            break
                        else:
                            try:
                                cursor.execute("update votes set votes = votes+1 where candidate={0} and election={1}".format(cid,op))
                                con.commit()
                            except Exception as e:
                                print("Failed to cast vote! Error:",e)
                            else:
                                print("Vote successfully casted")

        elif op == 2 and superuser:
            newu = input("Please enter username: ")
            newp = getpass.getpass("Please enter password: ")
            try:
                cursor.execute("create user '{0}'@'%' identified by '{1}'".format(newu,newp))
                cursor.execute("grant select on {0}.candidates to '{1}'@'%'".format(database,newu))
                cursor.execute("grant select on {0}.elections to '{1}'@'%'".format(database,newu))
                cursor.execute("grant update on {0}.votes to '{1}'@'%'".format(database,newu))
                cursor.execute("grant select,update on {0}.votes to '{1}'@'%'".format(database,newu))
                cursor.execute("grant select(user,super_priv) on mysql.user to '{1}'@'%'".format(database,newu))
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
                    cursor.execute("select * from elections order by id")
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
            print()
            eid = input("Enter election id: ")
            cursor.execute("select name from elections where id={0}".format(eid))
            cf = cursor.fetchall()
            if len(cf) == 0:
                print("Election ID Not found!")
                continue
            while True:
                print("Election name:",cf[0][0])
                print("Manage Candidates: ")
                print("1. Add Candidate")
                print("2. View Candidates")
                print("3. Delete Candidate")
                print("4. Back")
                op = int(input("Enter option: "))
                if op == 1:
                    name = input("Enter candidate name: ")
                    classst = input("Enter class: ")
                    section = input("Enter section: ").upper()
                    try:
                        cursor.execute("insert into candidates(name,class,section,election) values('{0}',{1},'{2}',{3})".format(name,classst,section,eid))
                        con.commit()
                        cursor.execute("select last_insert_id()")
                        cursor.execute("insert into votes(candidate,election,votes) values({0},{1},0)".format(cursor.fetchall()[0][0],eid))
                        con.commit()
                        print("Candidate Added successfully!")
                        print()
                    except Exception as e:
                        print("Failed to add candidate! Error:",e)
                elif op == 2:
                    print()
                    cursor.execute("select id,name,class,section from candidates where election={0} order by id".format(eid))
                    for i in cursor.fetchall():
                        print("Candidate ID:",i[0])
                        print("Candidate name:",i[1])
                        print("Candidate Class and Section: ",i[2],i[3],sep="")
                        print()
                elif op == 3:
                    cid = input("Enter candidate id to remove: ")
                    try:
                        cursor.execute("delete from candidates where id={0} and election={1}".format(cid,eid))
                        con.commit()
                        print("Election deleted successfully")
                    except Exception as e:
                        print("Failed to delete election! Error: ",e)
                elif op == 4:
                    break
                else:
                    print("Invalid option!")
        elif op == 5 and superuser:
            try:
                cursor.execute("select * from elections order by id")
            except Exception as e:
                print("Failed to get list of elections! Error:",e)
                continue
            elections = cursor.fetchall()
            print()
            while True:
                print("Please select election: ")
                for i in elections:
                    print(i[0],". ",i[1],sep="")
                op = input("Enter election id (press enter to go back): ")
                if op == "":
                    break
                else:
                    cursor.execute("select id,name,class,section,votes from candidates,votes where candidates.id=votes.candidate and votes.election={0} order by votes.votes desc".format(op))
                    cf = cursor.fetchall()
                    if len(cf) == 0:
                        print("Empty election or invalid election id")
                    else:
                        print(tabulate(cf,["Candidate ID","Name","Class","Section","No of votes"]))
                    tie = checkTie(cf)
                    if len(tie) == 1:
                        print("Candidate with most votes:")
                        print(tie[0][1]+" of class ",tie[0][2],tie[0][3]," with ",tie[0][4]," votes",sep="")
                    else:
                        print("Results tied between:")
                        for i in range(len(tie)):
                            print(i+1,". ",tie[i][1],sep="")
                        print("These candidates have ",tie[0][4]," votes",sep="")
        elif op == exitval:
            print("Exiting")
            cursor.close()
            con.close()
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