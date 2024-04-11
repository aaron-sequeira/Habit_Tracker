# Required imports/packages
import pandas as pd 
from datetime import datetime
from tabulate import tabulate
import time
import threading
import mysql.connector
import questionary
import pytest
import unittest

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
# The main class to create a new habit object with a default constructor and multiple methods
class test_Habit(unittest.TestCase):
    """ The Habit Tracker method takes in parameters used for the algorithm and does the conversion
    of time into minutes,hours and days and returns a dictionary """
    def HabitTracker(self,habit,start_date,minutes_wasted,checked,h_type):
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
        sqlformula = "INSERT INTO habits (name,time_Since_Creation,Total_hours,start_Date,minutes_Saved,checked,streak,Habit_Type) VALUES ('"+str(habit)+"','"+str(hours)+"',%s,%s,%s,%s,%s,'"+str(h_type)+"')"
        data = (total_hours,start_date,minutes_Saved,checked,streak)
        mycursor.execute(sqlformula,data)
        mydb.commit()

    """Creates the actual habit by taking in user input and calling on the HabitTracker function
    and appends the HabitTracker function (the dictionary form the function) to a list/array
    called habits"""
    def createhabit(self):
        habit = questionary.text("What is your habit?").ask()
        habit_type = questionary.select("Enter habit type",choices=['Daily','Weekly']).ask()
        year = int(questionary.text('What is the year your habit started?').ask())
        month = int(questionary.text("What is the month your habit started?").ask())
        day = int(questionary.text("What is the day your habit started?").ask()) 
        start_date = datetime(year,month,day,0,0)
        minutes_wasted = int(questionary.text("What is the time your spent during your habit?(in minutes)").ask())
        checked = False
        return self.HabitTracker(habit,start_date,minutes_wasted,checked,habit_type), print("A habit has been created")

    # Removes the habit from the database by inputing the name of the habit
    def removehabit(self):
        habitName = questionary.text("Enter the name of the habit you want to remove").ask()
        mycursor = mydb.cursor()
        mycursor.execute("DELETE FROM habits WHERE name ='"+habitName+"'")
        mydb.commit()
        print ("Habit removed")

    # Removes the habit from the database by inputing the name of the habit into the parameter of the function
    def removehabit_without_input(self,habitName):
        mycursor = mydb.cursor()
        mycursor.execute("DELETE FROM habits WHERE name ='"+habitName+"'")
        mydb.commit()

    """The function sets a timer when a habit is checked-off and is set to true by the user 
    it also adds one to the Day Streak counter and unchecks the habit setting it to false
    while starting a thread habit_Timer_False when the timer goes to 0"""
    def timer_function(self, habitName):
        elapsed_time = 0
        while elapsed_time != 20:
            time.sleep(1)  # Sleep for 1 second
            elapsed_time += 1
            if elapsed_time == 20:
                temp_time = 1 
                cursor = mydb.cursor()
                cursor.execute("SELECT streak FROM habits WHERE name='"+habitName+"'" )
                tm = cursor.fetchall()
                total_Time = temp_time + tm[0][0]
                cursor.execute("UPDATE habits SET streak = '"+str(total_Time)+"' WHERE name = '"+habitName+"'")
                cursor.execute("UPDATE habits SET checked = 0 WHERE name = '"+habitName+"'")
                mydb.commit()
                cursor.execute("SELECT streak FROM habits WHERE name = '"+habitName+"'")
                streak = cursor.fetchall()
                if streak[0][0] == '30':
                    print(f"The habit {habitName} has been on a 30 day streak")
                print(f"The habit {habitName} has been reset")
                cursor.execute("SELECT checked FROM habits WHERE name = '"+habitName+"'")
                data = cursor.fetchall()
                habit_Timer_False = threading.Thread(target=self.timer_function_false,args=[habitName,data])
                habit_Timer_False.start()
                break      

    """This function starts when the timer_function unchecks the habit. The function then sets a timer
    ,the timer keeps on running while the habit is unchecked, when the timer runs-out the habit is 
    said to be broken and is removed from the database using the removehabit_without_input function"""
    def timer_function_false(self,habitName,check):
            elapsed_time = 0
            cursor = mydb.cursor()
            cursor.execute("SELECT checked FROM habits WHERE name = '"+habitName+"'")
            check = cursor.fetchall()
            while check[0][0] != True or check[0][0] != 1:
                cursor.execute("SELECT checked FROM habits WHERE name = '"+habitName+"'")
                check = cursor.fetchall()
                time.sleep(1)  # Sleep for 1 second
                elapsed_time += 1
                if elapsed_time == 25:
                    print(f"\nThe habit {habitName} has been broken and the Streak has been reset")
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE habits SET streak = '0' WHERE name = '"+habitName+"'")
                    mydb.commit()
                    break
    def timer_function_weekly(self, habitName):
        elapsed_time = 0
        while elapsed_time != 50:
            time.sleep(1)  # Sleep for 1 second
            elapsed_time += 1
            if elapsed_time == 49:
                temp_time = 1
                cursor = mydb.cursor()
                cursor.execute("SELECT streak FROM habits WHERE name='"+habitName+"'" )
                tm = cursor.fetchall()
                total_Time = temp_time + tm[0][0]
                cursor.execute("UPDATE habits SET streak = '"+str(total_Time)+"' WHERE name = '"+habitName+"'")
                cursor.execute("UPDATE habits SET checked = 0 WHERE name = '"+habitName+"'")
                mydb.commit()
                print(f"\nThe habit {habitName} has been reset")
                habit_Timer_False_weekly = threading.Thread(target=self.timer_function_false_weekly,args=[habitName])
                habit_Timer_False_weekly.start()
                break          

    def timer_function_false_weekly(self,habitName):
            elapsed_time = 0
            cursor.execute("SELECT checked FROM habits WHERE name = '"+habitName+"'")
            check = cursor.fetchall()
            while check[0][0] != True or check[0][0] != 1:
                cursor.execute("SELECT checked FROM habits WHERE name = '"+habitName+"'")
                check = cursor.fetchall()
                time.sleep(1)  # Sleep for 1 second
                elapsed_time += 1
                if elapsed_time == 50:
                    print(f"The habit {habitName} has been broken and the Streak has been reset")
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE habits SET streak = '0' WHERE name = '"+habitName+"'")
                    mydb.commit()
                    break            
    # This function allows you to view all the current habits in the database        
    def test_viewAllhabits(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT name FROM Habits")
        record = cursor.fetchall()
        expected = [('coding',), ('sleeping',),('biting nails',)]
        assert record == expected

    """This function allows the user to check-off a habit by asking the user to input the name of the
    habit. It searches for the habit till it finds the name and checks-off the habit setting it to true
    and starting the timer_thread which start the timer_function with the argumets as habitName and 
    the habit dictionary itself(i). If the habit is already checked-off, it will say that the habit
    is already checked-off and sends you back to the menu."""
    def checkOff(self,habitName):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT checked FROM habits WHERE name = '"+habitName+"'")
        result = mycursor.fetchone()
        mycursor.execute("SELECT Habit_Type FROM habits WHERE name = '"+habitName+"'")
        h_type = mycursor.fetchall()

        if int(result[0])==False and h_type[0][0] =="Daily":
            mycursor.execute("UPDATE habits SET checked = 1 WHERE name = '"+habitName+"'")
            current_date = datetime.today()
            mycursor.execute("UPDATE habits SET Check_Date = '"+str(current_date)+"' WHERE name='"+habitName+"'")
            mydb.commit()
            print("Updated")
            habit_Timer_True = threading.Thread(target=self.timer_function,args=[habitName])
            habit_Timer_True.start()
        elif int(result[0])==False and h_type[0][0] =="Weekly":
            mycursor.execute("UPDATE habits SET checked = 1 WHERE name = '"+habitName+"'")
            current_date = datetime.today()
            mycursor.execute("UPDATE habits SET Check_Date = '"+str(current_date)+"'")
            mydb.commit()
            print("Updated")
            habit_Timer_True_weekly = threading.Thread(target=self.timer_function_weekly,args=[habitName])
            habit_Timer_True_weekly.start()
        else:
            print("The habit is already checked") 
    # This function finds the habit with the longest streak in a sorted order using tabulate 
    def test_longestStreak(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT name FROM habits ORDER BY streak DESC")
        record = cursor.fetchall()
        expected = [('coding',), ('sleeping',),('biting nails',)]
        assert record == expected
        
    # This function finds the habit with the newest streak in a sorted order using tabulate(the newest habit) 
    def test_latestStreak(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT name FROM habits ORDER BY streak ASC")
        record = cursor.fetchall()
        expected = [('coding',), ('sleeping',),('biting nails',)]
        assert record == expected

    # This function tells the user which habit he is struggling the most with in a sorted order
    def test_most_Struggling_habit(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT name FROM habits ORDER BY streak ASC")
        record = cursor.fetchall()
        expected = [('coding',), ('sleeping',),('biting nails',)]
        assert record == expected

    # This function tells the user which habit he is least struggling with in a sorted order
    def test_least_Struggling_habit(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT name FROM habits ORDER BY streak DESC")
        expected = [('coding',), ('sleeping',),('biting nails',)]
        record = cursor.fetchall()
        assert record == expected

    def test_Daily_habits(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT name FROM habits WHERE Habit_Type = 'Daily'")
        record = cursor.fetchall()
        expected = [('coding',), ('sleeping',)]
        print(record)
        assert  record == expected

    def test_Weekly_habits(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT name FROM habits WHERE Habit_Type = 'Weekly'")
        record = cursor.fetchall()
        expected = [('biting nails',)]
        assert record == expected

    # This function handles the main functionality of the program. It analyzes the task via menu
    def Analyze(self,choice):
        if choice=="View all habits":
            self.test_viewAllhabits()
        if choice=="Check-off habits":
            self.checkOff('coding')
        if choice=="Longest streak":
            self.test_longestStreak()
        if choice=="latest streak": 
            self.test_latestStreak()
        if choice=="habits struggled the most":
            self.test_most_Struggling_habit()
        if choice=="habits struggled the least":
            self.test_least_Struggling_habit()
        if choice=="List all daily habits":
            self.test_Daily_habits()
        if choice=="List all weekly habits":
            self.test_Weekly_habits()
        if choice=="Exit to Main Menu":
            print("You have exited analyzation")

        