This is a Python program for tracking habits. It allows users to create, remove, analyze, and modify habits.

Requirements
Python 3.x
Required Python packages:
pandas
datetime
tabulate
time
threading
mysql-connector
questionary

Installation
Clone the repository.
Install the required Python packages using pip:
Copy code
pip install -r requirements.txt
Set up MySQL database with the required tables:
Create a database named habittrackerdb and another database named authentication.
Set up tables in the databases as described in the code (CREATE TABLE queries).
Update the host, user, passwd, and database variables in the code with your MySQL database credentials.

Usage
Run the Python script habit_tracker.py.
Follow the prompts to perform various actions such as creating habits, removing habits, analyzing habits, or modifying habits.

Functionality
Create Habit: Allows users to create a new habit with specified details such as habit name, habit type, start date, etc.
Remove Habit: Enables users to remove a habit from their list.
Analyze Habit:
        This functionality provides various options for analyzing habits:
        View All Habits: Displays a tabulated view of all habits with details such as time since creation, total hours spent, streak, etc.
        Check-off Habits: Allows users to mark a habit as checked-off. If the habit is Daily, it resets the streak if necessary and starts a timer thread. If the habit is Weekly, it does the same but with a different time threshold.
        Longest Streak: Lists habits sorted by the longest streak achieved.
        Latest Streak: Lists habits sorted by the latest streak achieved.
        Habits Struggled the Most: Lists habits sorted by the lowest streak (i.e., habits the user is struggling the most with).
        Habits Struggled the Least: Lists habits sorted by the highest streak (i.e., habits the user is least struggling with).
        List All Daily Habits: Displays only the habits marked as Daily.
        List All Weekly Habits: Displays only the habits marked as Weekly.
Modify Habit: Allows users to modify habit details such as habit name, start date, and habit type.
Shutdown: Exits the program.

Contributors
aaron-sequeira
