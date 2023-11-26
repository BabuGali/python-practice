"""
The Chinese Zodiac consists of these 12 animals in order:
Rat Ox Tiger Rabbit Dragon Snake Horse Goat Monkey Rooster Dog Pig

Each year has an associated zodiac animal, and the cycle repeats every 12 years.

Knowing that the year 1900 is the year of the Rat, find the zodiac for the given n years.

"""
z=["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake","Horse", "Goat","Monkey", "Rooster","Dog", "Pig"]
year= int(input())
print(z[((year-1900)%12)])

