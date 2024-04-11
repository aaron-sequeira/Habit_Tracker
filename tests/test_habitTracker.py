import pytest
from myfunctions import test_Habit

mf = test_Habit()

def test_viewAllhabits():
    mf.test_viewAllhabits()

def test_Daily_habits():
    mf.test_Daily_habits() 

def test_Weekly_habits():
    mf.test_Weekly_habits() 

def test_longestStreak():
    mf.test_longestStreak()

def test_latestStreak():
    mf.test_latestStreak()

def test_most_Struggling_habit():
    mf.test_most_Struggling_habit() 

def test_least_Struggling_habit():
    mf.test_least_Struggling_habit() 

def test_Analyze():
    mf.Analyze("View all habits") == mf.test_viewAllhabits()

def test_Analyze2():
    mf.Analyze("Check-off habits")  == mf.checkOff('sleeping')

def test_Analyze3():
    mf.Analyze("Longest streak") == mf.test_longestStreak()

def test_Analyze4():
    mf.Analyze("latest streak") == mf.test_latestStreak()

def test_Analyze5():
    mf.Analyze("habits struggled the most") == mf.test_most_Struggling_habit()

def test_Analyze6():
    mf.Analyze("habits struggled the least") == mf.test_least_Struggling_habit()

def test_Analyze7():
    mf.Analyze("List all daily habits") == mf.test_Daily_habits()

def test_Analyze8():
    mf.Analyze("List all weekly habits") == mf.test_Weekly_habits()

