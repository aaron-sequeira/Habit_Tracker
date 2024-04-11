# Required imports/packages
import pandas as pd 
from datetime import datetime
from tabulate import tabulate
import time
import threading
# The main class to create a new habit object with a default constructor and multiple methods
class Habit:
    """ The Habit Tracker method takes in parameters used for the algorithm and does the conversion
    of time into minutes,hours and days and returns a dictionary """
    def HabitTracker(self,habit,start_date,minutes_wasted,checked):
        streak = 0
        time_After_Check = 0
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
        return {"Habit": habit,"time_Since_Creation":hours,"Total_hours":total_hours,"start_Date": start_date,
                "minutes_Saved": minutes_Saved,"checked": checked, "Day_streak": streak,"TAC": time_After_Check}
    
    """Creates the actual habit by taking in user input and calling on the HabitTracker function
    and appends the HabitTracker function (the dictionary form the function) to a list/array
    called habits"""
    def createhabit(self):
        habit = input("What is your habit: ")
        year = int(input("Enter the year your habit started: "))
        month = int(input("Enter the month your habit started: "))
        day = int(input("Enter the day your habit started: ")) 
        start_date = datetime(year,month,day,0,0)
        minutes_wasted = int(input("Enter the time your spent during your habit: "))
        return habits.append(self.HabitTracker(habit,start_date,minutes_wasted,checked=False)), print("A habit has been created")

    # Removes the habit from the database by inputing the name of the habit
    def removehabit(self):
        habitName = input("Enter the name of the habit you want to remove: ")
        for i in habits:
            if i["Habit"] == habitName:
                habits.remove(i)
                print(habitName+" has been removed")
    
    # Removes the habit from the database by inputing the name of the habit into the parameter of the function
    def removehabit_without_input(self,habitName):
        for i in habits:
            if i["Habit"] == habitName:
                habits.remove(i)

    """The function sets a timer when a habit is checked-off and is set to true by the user 
    it also adds one to the Day Streak counter and unchecks the habit setting it to false
    while starting a thread habit_Timer_False when the timer goes to 0"""
    def timer_function(self, habitName,habit):
        elapsed_time = 10
        while elapsed_time != 0:
            time.sleep(1)  # Sleep for 1 second
            elapsed_time -= 1
            if elapsed_time == 1:
                if habit['Day_streak'] == 24:
                    print(f"\nThe habit {habitName} is on a 15 day steak")
                habit['Day_streak'] += 1
                print(f"\nThe habit {habitName} has been reset")
                habit['checked'] = False
                habit_Timer_False = threading.Thread(target=self.timer_function_false,args=[habitName,habit])
                habit_Timer_False.start()
                break      

    """This function starts when the timer_function unchecks the habit. The function then sets a timer
    ,the timer keeps on running while the habit is unchecked, when the timer runs-out the habit is 
    said to be broken and is removed from the database using the removehabit_without_input function"""
    def timer_function_false(self,habitName,habit):
            elapsed_time = 0
            while habit['checked'] != True:
                time.sleep(1)  # Sleep for 1 second
                elapsed_time += 1
                habit["TAC"] += elapsed_time
                if elapsed_time == 25:
                    print(f"\nThe habit {habitName} has been broken and removed")
                    self.removehabit_without_input(habitName)
                    break
            
    # This function allows you to view all the current habits in the database        
    def viewAllhabits(self,habits):
        df = pd.DataFrame(habits)
        print(tabulate(df,headers='keys',tablefmt="fancy_grid"))

    """This function allows the user to check-off a habit by asking the user to input the name of the
    habit. It searches for the habit till it finds the name and checks-off the habit setting it to true
    and starting the timer_thread which start the timer_function with the argumets as habitName and 
    the habit dictionary itself(i). If the habit is already checked-off, it will say that the habit
    is already checked-off and sends you back to the menu."""
    def checkOff(self,habits):
        habitName = input("Enter the name of the habit you want to check-off: ")
        for i in habits:
            if i["Habit"] == habitName:
                if i["checked"] == False:
                    i['checked'] = True          
                    print(habitName+" is Checked-off")
                    print("You can check of "+habitName+" Once per day")
                    self.viewAllhabits(habits)  
                    timer_thread = threading.Thread(target=self.timer_function,args=[habitName,i])
                    timer_thread.start()
                else:
                    print(f"Habit {habitName} has already been check-off")          
            else:
                print(f'Habit {habitName} Not found')
         
    # This function finds the habit with the longest streak in a sorted order using tabulate 
    def longestStreak(self,habit):
        df = pd.DataFrame(habit)
        df.sort_values(by='Day_streak',ascending=False,inplace=True)
        print(tabulate(df,headers='keys',tablefmt="psql"))
        
    # This function finds the habit with the newest streak in a sorted order using tabulate(the newest habit) 
    def latestStreak(self,habits):
        df = pd.DataFrame(habits)
        df.sort_values(by='Day_streak',ascending=True,inplace=True)
        print(tabulate(df,headers='keys',tablefmt="psql")) 

    # This function tells the user which habit he is struggling the most with in a sorted order
    def most_Struggling_habit(self,habits):
        df = pd.DataFrame(habits)
        df.sort_values(by='TAC',ascending=False,inplace=True)
        print(tabulate(df,headers='keys',tablefmt="psql"))

    # This function tells the user which habit he is least struggling with in a sorted order
    def least_Struggling_habit(self,habits):
        df = pd.DataFrame(habits)
        df.sort_values(by='TAC',ascending=True,inplace=True)
        print(tabulate(df,headers='keys',tablefmt="psql"))

    # This function handles the main functionality of the program. It analyzes the task via menu
    def Analyze(self,habits):
        loop = 0
        while loop != 4:
            print("1.View all habits")
            print("2.Check-off habits")
            print("3.Longest streak")
            print("4.latest streak")
            print("5.habits struggled the most in a month")
            print("6.habits struggled the least in a month")
            print("7.Back")
            choice = int(input("Enter your choice: "))
            if choice==1:
                self.viewAllhabits(habits)
            if choice==2:
                self.checkOff(habits)
            if choice==3:
                self.longestStreak(habits)
            if choice==4:
                self.latestStreak(habits)
            if choice==5:
                self.most_Struggling_habit(habits)
            if choice==6:
                self.least_Struggling_habit(habits)
            if choice==7:
                print("You have exited analyzation")
                break

# This is the main core of the code. It is the main function which helps the user handle his habits
if __name__ == '__main__':
    habit = Habit()   
    loop = 0
    habits = [] # List of all habits
    while loop != 5:
        print("1.Add a habit")
        print("2.Delete a habit")
        print("3.Analyze")
        print("4.Exit")
        choice = int(input("Enter a choice: "))
        if choice == 1:
            habit.createhabit()
            for i in habits:
                if i['checked'] == False:
                        habitName = i['Habit'] 
                        habit_Timer_False = threading.Thread(target=habit.timer_function_false,args=[habitName,i])
                        habit_Timer_False.start()
        if choice == 2:
            habit.removehabit()
        if choice == 3:
            habit.Analyze(habits)
        if choice == 4:
            print("Shutdown")
            break
        