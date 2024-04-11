# Required imports/packages
import pandas as pd 
from datetime import datetime
from tabulate import tabulate
import time
import threading
import mysql.connector
import questionary

mydb = mysql.connector.connect(
    #host ip
    host="127.0.0.1",
    #user
    user="root",
    #Server password
    passwd='#############',
    #current database
    database="habittrackerdb"
)

auth = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd='#############',
    database="authentication"
)

# The main class to create a new habit object with a default constructor and multiple methods
class Habit:
    #This is a non parameterized constructor That is used for users to login or register to an account
    def __init__(self):
        loop = 0
        while loop != 4:
            choice = questionary.select("Welcome to habit tracker",choices=['login','register']).ask()
            if choice  == 'login':
                self.username = questionary.text("Enter your username").ask()
                self.password = questionary.password("Enter your password").ask()
                cursor = auth.cursor()
                cursor.execute("SELECT username, passwords FROM logindata")
                data = cursor.fetchall()
                for user,passwd in data:
                    if self.username == user and self.password == passwd:
                        status = 'Success'
                        break
                    else:
                        status = 'fail'
                if status == 'Success':
                    print('Login Successful')
                    loop = 4
                elif status == 'fail':
                    print('Invalid Username or Password Please try again.')
                else:
                    print("Error")

            if choice == 'register':
                    self.register()
                
    #This is the register function to create an account for your habits by sending request to the database
    def register(self):
        username = questionary.text("Enter your username").ask()
        password = questionary.password("Enter your password").ask()
        cursor = auth.cursor()
        hcursor = mydb.cursor()
        cursor.execute("INSERT INTO logindata (username, passwords) VALUES('"+str(username)+"','"+str(password)+"')")
        hcursor.execute("CREATE TABLE "+username+" (name VARCHAR(255),time_Since_Creation VARCHAR(255),Total_hours INTEGER(255),start_Date DATE,minutes_Saved INTEGER(255),checked BOOLEAN,streak INTEGER,Habit_Type VARCHAR(255),Check_date DATE)")
        mydb.commit()
        auth.commit()
        print("Account created successfully")

    """ The Habit Tracker method takes in parameters used for the algorithm and does the conversion
    of time into minutes,hours and days and returns a dictionary """
    def HabitTracker(self,habit,start_date,minutes_wasted,checked,h_type,clname):
        streak = 0
        time_Elapsed = (datetime.now() - start_date).total_seconds()
        hours = round(time_Elapsed / 60 / 60,1)
        days = round(hours / 24, 2)
        minutes_Saved = round(days * minutes_wasted)
        total_hours = round(hours)
        if hours > 72:
            hours = str(days) + ' days'
        else:
            hours = str(hours) + ' hours'
        """TAC means Time after checked. It is used to calculate how long it has been since last check
        And to check which habit is struggling the most"""
        mycursor = mydb.cursor()
        sqlformula = "INSERT INTO "+clname+" (name,time_Since_Creation,Total_hours,start_Date,minutes_Saved,checked,streak,Habit_Type) VALUES ('"+str(habit)+"','"+str(hours)+"',%s,%s,%s,%s,%s,'"+str(h_type)+"')"
        data = (total_hours,start_date,minutes_Saved,checked,streak)
        mycursor.execute(sqlformula,data)
        mydb.commit()

    """Creates the actual habit by taking in user input and calling on the HabitTracker function
    and appends the HabitTracker function (the dictionary form the function) to a list/array
    called habits"""
    def createhabit(self,clname):
        status =''
        habit = questionary.text("What is your habit?").ask()
        habit_type = questionary.select("Enter habit type",choices=['Daily','Weekly']).ask()
        try:    
            year = int(questionary.text('What is the year your habit started?').ask())
            month = int(questionary.text("What is the month your habit started?").ask())
            day = int(questionary.text("What is the day your habit started?").ask()) 
            minutes_wasted = int(questionary.text("What is the time your spent during your habit?(in minutes)").ask())
        except ValueError:
            status = 'fail'
        if status == 'fail':
            print("Please enter valid inputs.")
        else:
            start_date = datetime(year,month,day,0,0)
            checked = False
            return self.HabitTracker(habit,start_date,minutes_wasted,checked,habit_type,clname), print("A habit has been created")

    # Removes the habit from the database by inputing the name of the habit
    def removehabit(self,clname):
        cursor = mydb.cursor()  
        loop = 0
        while loop != 4:
            name = ['Exit']
            cursor.execute("SELECT name FROM "+clname+"")    
            names = cursor.fetchall()
            for i in names:
                name.append(i[0])
            choice = questionary.select("Enter your choice", choices=name).ask()
            if "Exit" == choice:
                print("Exited Successfully!")
                break
            if choice in name:
                cursor.execute("DELETE FROM "+clname+" WHERE name ='"+str(choice)+"'")
                mydb.commit()
                print ("Habit removed")

    """The function sets a timer when a habit is checked-off and is set to true by the user 
    it also adds one to the Day Streak counter and unchecks the habit setting it to false
    while starting a thread habit_Timer_False when the timer goes to 0"""
    def timer_function(self, habitName,clname):
        elapsed_time = 0
        while elapsed_time != 20:
            time.sleep(1)  # Sleep for 1 second
            elapsed_time += 1
            if elapsed_time == 20:
                temp_time = 1 
                cursor = mydb.cursor()
                cursor.execute("SELECT streak FROM "+clname+" WHERE name='"+habitName+"'" )
                tm = cursor.fetchall()
                total_Time = temp_time + tm[0][0]
                cursor.execute("UPDATE "+clname+" SET streak = '"+str(total_Time)+"' WHERE name = '"+habitName+"'")
                cursor.execute("UPDATE "+clname+" SET checked = 0 WHERE name = '"+habitName+"'")
                mydb.commit()
                cursor.execute("SELECT streak FROM "+clname+" WHERE name = '"+habitName+"'")
                streak = cursor.fetchall()
                if streak[0][0] == '30':
                    print(f"The habit {habitName} has been on a 30 day streak")
                print(f"The habit {habitName} has been reset")
                cursor.execute("SELECT checked FROM "+clname+" WHERE name = '"+habitName+"'")
                data = cursor.fetchall()
                habit_Timer_False = threading.Thread(target=self.timer_function_false,args=[habitName,data,clname])
                habit_Timer_False.start()
                break      

    """This function starts when the timer_function unchecks the habit. The function then sets a timer
    ,the timer keeps on running while the habit is unchecked, when the timer runs-out the habit is 
    said to be broken and the streak is reset"""
    def timer_function_false(self,habitName,check,clname):
            elapsed_time = 0
            cursor = mydb.cursor()
            cursor.execute("SELECT checked FROM "+clname+" WHERE name = '"+habitName+"'")
            check = cursor.fetchall()
            while check[0][0] != True or check[0][0] != 1:
                cursor.execute("SELECT checked FROM "+clname+" WHERE name = '"+habitName+"'")
                check = cursor.fetchall()
                time.sleep(1)  # Sleep for 1 second
                elapsed_time += 1
                if elapsed_time == 25:
                    print(f"\nThe habit {habitName} has been broken and the Streak has been reset")
                    cursor.execute("UPDATE "+clname+" SET streak = '0' WHERE name = '"+habitName+"'")
                    mydb.commit()
                    break
                    
    """The function weekly sets a timer when a habit is checked-off and is set to true by the user 
    it also adds one to the Day Streak counter and unchecks the habit setting it to false
    while starting a thread habit_Timer_False_Weekly when the timer goes to 0"""
    def timer_function_weekly(self, habitName,clname):
        elapsed_time = 0
        while elapsed_time != 50:
            time.sleep(1)  # Sleep for 1 second
            elapsed_time += 1
            if elapsed_time == 49:
                temp_time = 1
                cursor = mydb.cursor()
                cursor.execute("SELECT streak FROM "+clname+" WHERE name='"+habitName+"'" )
                tm = cursor.fetchall()
                total_Time = temp_time + tm[0][0]
                cursor.execute("UPDATE "+clname+" SET streak = '"+str(total_Time)+"' WHERE name = '"+habitName+"'")
                cursor.execute("UPDATE "+clname+" SET checked = 0 WHERE name = '"+habitName+"'")
                mydb.commit()
                print(f"\nThe habit {habitName} has been reset")
                habit_Timer_False_weekly = threading.Thread(target=self.timer_function_false_weekly,args=[habitName,clname])
                habit_Timer_False_weekly.start()
                break          
                
    """This function starts when the timer_function_Weekly unchecks the habit. The function then sets a timer
    ,the timer keeps on running while the habit is unchecked, when the timer runs-out the habit is 
    said to be broken and the streak is reset"""
    def timer_function_false_weekly(self,habitName,clname):
            elapsed_time = 0
            cursor = mydb.cursor()
            cursor.execute("SELECT checked FROM "+clname+" WHERE name = '"+habitName+"'")
            check = cursor.fetchall()
            while check[0][0] != True or check[0][0] != 1:
                cursor.execute("SELECT checked FROM "+clname+" WHERE name = '"+habitName+"'")
                check = cursor.fetchall()
                time.sleep(1)  # Sleep for 1 second
                elapsed_time += 1
                if elapsed_time == 50:
                    print(f"The habit {habitName} has been broken and the Streak has been reset")
                    cursor.execute("UPDATE "+clname+" SET streak = '0' WHERE name = '"+habitName+"'")
                    mydb.commit()
                    break            
    # This function allows you to view all the current habits in the database        
    def viewAllhabits(self,clname):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM "+clname+"")
        records = cursor.fetchall()
        header = ['Habits','time_Since_Creation','hours','Date','minutes_Saved','Checked','Streak','Type','Check_Date']
        df = pd.DataFrame(records)
        print(tabulate(df,headers=header,tablefmt="fancy_grid"))

    """This function allows the user to check-off a habit by asking the user to input the name of the
    habit. It searches for the habit till it finds the name and checks-off the habit setting it to true
    and check the habit type to start the timer_thread which starts the timer_function with the argumets as habitName and 
    the username depending on the habit type the functions differ. If the habit is already checked-off, it will say that the habit
    is already checked-off and sends you back to the menu."""
    def checkOff(self,clname):
        mycursor = mydb.cursor()
        loop = 0
        while loop != 4:
            mycursor.execute("SELECT name FROM "+clname+"")
            names = mycursor.fetchall()
            name = ['Exit']
            for i in names:
                name.append(i[0])
                choice = questionary.select("Enter the name of the habit you want to check-off",choices=name).ask()
            
            if choice == "Exit":
                break
            if choice in name:   
                mycursor.execute("SELECT checked FROM "+clname+" WHERE name = '"+choice+"'")
                result = mycursor.fetchone()
                mycursor.execute("SELECT Habit_Type FROM "+clname+" WHERE name = '"+choice+"'")
                h_type = mycursor.fetchall()

                if int(result[0])==False and h_type[0][0] =="Daily":
                    mycursor.execute("UPDATE "+clname+" SET checked = 1 WHERE name = '"+choice+"'")
                    current_date = datetime.today()
                    mycursor.execute("UPDATE "+clname+" SET Check_Date = '"+str(current_date)+"' WHERE name='"+choice+"'")
                    mydb.commit()
                    print("Updated")
                    habit_Timer_True = threading.Thread(target=self.timer_function,args=[choice,clname])
                    habit_Timer_True.start()
                elif int(result[0])==False and h_type[0][0] =="Weekly":
                    mycursor.execute("UPDATE "+clname+" SET checked = 1 WHERE name = '"+choice+"'")
                    current_date = datetime.today()
                    mycursor.execute("UPDATE "+clname+" SET Check_Date = '"+str(current_date)+"'")
                    mydb.commit()
                    print("Updated")
                    habit_Timer_True_weekly = threading.Thread(target=self.timer_function_weekly,args=[choice,clname])
                    habit_Timer_True_weekly.start()
                else:
                    print("The habit is already checked") 
                    return None
    # This function finds the habit with the longest streak in a sorted order using tabulate 
    def longestStreak(self,clname):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM "+clname+" ORDER BY streak DESC")
        header = ['Habits','time_Since_Creation','hours','Date','minutes_Saved','Checked','Streak','Type','Check_Date']
        record = cursor.fetchall()
        df = pd.DataFrame(record)
        print(tabulate(df,headers=header,tablefmt="fancy_grid"))
        
    # This function finds the habit with the newest streak in a sorted order using tabulate(the newest habit) 
    def latestStreak(self,clname):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM "+clname+" ORDER BY streak ASC")
        header = ['Habits','time_Since_Creation','hours','Date','minutes_Saved','Checked','Streak','Type','Check_Date']
        record = cursor.fetchall()
        df = pd.DataFrame(record)
        print(tabulate(df,headers=header,tablefmt="fancy_grid")) 

    # This function tells the user which habit he is struggling the most with in a sorted order
    def most_Struggling_habit(self,clname):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM "+clname+" ORDER BY streak ASC")
        header = ['Habits','time_Since_Creation','hours','Date','minutes_Saved','Checked','Streak','Type','Check_Date']
        record = cursor.fetchall()
        df = pd.DataFrame(record)
        print(tabulate(df,headers=header,tablefmt="fancy_grid"))

    # This function tells the user which habit he is least struggling with in a sorted order
    def least_Struggling_habit(self,clname):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM "+clname+" ORDER BY streak DESC")
        header = ['Habits','time_Since_Creation','hours','Date','minutes_Saved','Checked','Streak','Type','Check_Date']
        record = cursor.fetchall()
        df = pd.DataFrame(record)
        print(tabulate(df,headers=header,tablefmt="fancy_grid"))
    #This function tells the user which habits are in the catagory of daily habits 
    def Daily_habits(self,clname):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM "+clname+" WHERE Habit_Type = 'Daily'")
        record = cursor.fetchall()
        header = ['Habits','time_Since_Creation','hours','Date','minutes_Saved','Checked','Streak','Type','Check_Date']
        df = pd.DataFrame(record)
        print(tabulate(df,headers=header,tablefmt="fancy_grid"))
    #This function tells the user which habits are in the catagory of weekly habits 
    def Weekly_habits(self,clname):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM "+clname+" WHERE Habit_Type = 'Weekly'")
        record = cursor.fetchall()
        header = ['Habits','time_Since_Creation','hours','Date','minutes_Saved','Checked','Streak','Type','Check_Date']
        df = pd.DataFrame(record)
        print(tabulate(df,headers=header,tablefmt="fancy_grid"))

    #This function helps modify the data given by the user 
    def Modify(self,clname):
        cursor = mydb.cursor()
        loop = 0
        loop2 = 0
        while loop != 4:
            cursor.execute("SELECT name FROM "+clname+"")
            names = cursor.fetchall()
            name = ['Exit']
            for i in names:
                name.append(i[0])
            choice = questionary.select("Enter your choice", choices=name).ask()
            if "Exit" == choice:
                print("Exited Successfully!")
                break
            if choice in name:
                while loop2 != 4:
                    selection = questionary.select("Enter the statistic you want to modify",
                                                choices=['Habit name','start Date','Habit type','Back']).ask()
                    if selection == "Habit name":
                        newName = questionary.text("What is the new Name?").ask()
                        cursor.execute("UPDATE "+clname+" SET name = '"+newName+"' WHERE name = '"+choice+"'")
                        mydb.commit()
                    
                    if selection == "start Date":
                        status = ''
                        try: 
                            year = int(questionary.text('What is the year your habit started?').ask())
                            month = int(questionary.text("What is the month your habit started?").ask())
                            day = int(questionary.text("What is the day your habit started?").ask())    
                            minutes_wasted = int(questionary.text("What is the time your spent during your habit?(in minutes)").ask())
                            start_date = datetime(year,month,day,0,0)
                        except ValueError:
                            status = 'fail'
                        if status == 'fail':
                            print("Please enter valid inputs.")
                        else:
                            time_Elapsed = (datetime.now() - start_date).total_seconds()
                            hours = round(time_Elapsed / 60 / 60,1)
                            days = round(hours / 24, 2)
                            minutes_Saved = round(days * minutes_wasted)
                            total_hours = round(hours)
                            if hours > 72:
                                hours = str(days) + ' days'
                            else:
                                hours = str(hours) + ' hours'
                            cursor.execute("UPDATE "+clname+" SET time_Since_Creation = '"+hours+"',Total_hours = '"+str(total_hours)+"',minutes_Saved = '"+str(minutes_Saved)+"',start_Date = '"+str(start_date)+"' WHERE name = '"+choice+"' ")
                            mydb.commit()

                    if selection == "Habit type":
                        habit_t = questionary.select("Choose your habit type",
                                                     choices=['Daily','Weekly']).ask() 
                        cursor.execute("UPDATE "+clname+" SET Habit_Type = '"+habit_t+"' WHERE name = '"+choice+"'")   
                        mydb.commit()
                    if selection == "Back":
                        break
                    
    # This function handles the main functionality of the program. It analyzes the task via menu
    def Analyze(self,clname):
        loop = 0
        while loop != 4:
            choice = questionary.select("Enter your choice",
                                        choices=["View all habits","Check-off habits","Longest streak","latest streak","habits struggled the most","habits struggled the least","List all daily habits","List all weekly habits","Exit to Main Menu"]).ask()
            if choice=="View all habits":
                self.viewAllhabits(clname)
            if choice=="Check-off habits":
                self.checkOff(clname)
            if choice=="Longest streak":
                self.longestStreak(clname)
            if choice=="latest streak": 
                self.latestStreak(clname)
            if choice=="habits struggled the most":
                self.most_Struggling_habit(clname)
            if choice=="habits struggled the least":
                self.least_Struggling_habit(clname)
            if choice=="List all daily habits":
                self.Daily_habits(clname)
            if choice=="List all weekly habits":
                self.Weekly_habits(clname)
            if choice=="Exit to Main Menu":
                print("You have exited analyzation")
                break

# This is the main core of the code. It is the main function which helps the user handle his habits and initializes the constructor
if __name__ == '__main__':
    habit = Habit()   
    loop = 0

    while loop != 5:
        choice = questionary.select("Enter your choice",
                                    choices=["Create Habit","Remove Habit","Analyze Habit","Modify habit","Shutdown"]).ask()
        if choice == "Create Habit":
            habit.createhabit(habit.username)
        if choice == "Remove Habit":
            habit.removehabit(habit.username)
        if choice == "Analyze Habit":
            habit.Analyze(habit.username)
        if choice == "Modify habit":
            habit.Modify(habit.username)
        if choice == 'Shutdown':
            print("Shutdown")
            break
        
