'''top_score.py
i intend to make a code that tries to check for existing scores and store new ones.
'''
import os

current = os.path.dirname(os.path.realpath(__file__))
p_exist = True
#if a score file exists we'll go into sorting scores, otherwise skip it
try:
    read_scores = open(f"{current}/score.txt", "r", encoding="UTF-8")
except FileNotFoundError:
    p_exist = False

scorage = []

if p_exist == True:
    listo = read_scores.readlines()
    for j in range(len(listo)):
        listo[j].split()
        #splitting wasn't working with one list so splitting into another
        scorage.append(listo[j].split())
    read_scores.close()
for z in range(len(scorage)):
    #changin numbers to integers for math
    scorage[z][0] = int(scorage[z][0])
    scorage[z][2] = int(scorage[z][2])


init = input("What are your initials?: ")
scorio = int(input("what was your score?: "))
new_score = [int(6), init, int(scorio)]
scorage.append(new_score)

length_list = len(scorage)
#adding blank scores if none exist
while length_list < 5:
    blank = [length_list, "AAA", int(0000)]
    scorage.append(blank)
    length_list = len(scorage)


for i in range(len(scorage)-1):
    for j in range(1,len(scorage)):
        # having it sort by checking values and rearranging by first number
        if scorage[-j][2] > scorage[-j-1][2]:
            scorage[-j][0] = scorage[-j-1][0]
            scorage[-j-1][0] -= 1
            #popping out my list value as a side variable to preserve during rearranging
            sidestep = scorage[-j-1]
            scorage[-j-1] = scorage[-j]
            scorage[-j] = sidestep

#it was easier to let it go into the nagatives to sort and fix it after
#it's chaotic but it works
for i in range(len(scorage)):
    scorage[i][0] = int(i+1)

#keeping the list to top 5
while len(scorage) > 5:
    scorage.remove(scorage[-1])

write_scores =  open(f"{current}/score.txt", "w", encoding="UTF-8")
for i in range(len(scorage)):
    #seting a line to the first element in list
    liney = (scorage[i])
    #converting to string for joining
    for j in range(len(liney)):
        liney[j] = str(liney[j])
    liney = " ".join(liney)
    #it outputs the same format as i told it to take in
    print(liney, file = write_scores)
write_scores.close()