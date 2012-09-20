#The four bytes prior to the start of a string is a byte defining how long that
#string is.  Simple enough.
#FTL files save the names of the starting crew, and apparently the current crew.
#Starting crew: names are after race.  Current crew: names before race.
#Scan for the following strings: "human", "energy", "mantis", "engi", and
#probably "slug", "rock", "crystal"
#Discount that instance if there is a name immediately following
#(That is to say: a length-byte, three empty bytes, and a name)
#Rewind four bytes, then scan backward until you encounter NUL.
#Rewind three more bytes, and that's the starting point.
#Take in the new name, record size, edit length byte.
#Three NULs, then the name, then the rest.
#Fifteen character limit for names.

import sys
import os


#teststring: Checks whether the given string indicates the presence of a race
#name, and thus whether a character name will be nearby.
def teststring(instring):
    if instring[0:5] == "human":
        return 5
    if instring[0:6] == "energy":
        return 6
    if instring[0:6] == "mantis":
        return 6
    if instring[0:4] == "engi":
        return 4
    if instring[0:4] == "slug":
        return 4
    if instring[0:4] == "rock":
        return 4
    if instring[0:7] == "crystal":
        return 7
    
    return 0
#end teststring

#Converts a number from 1-15 into its hex digit (as a string).
#Useful because those are the valid name lengths.
#There's got to be a better way to do this.
def tohex(number):
    if number == 1:
        return "\x01"
    if number == 2:
        return "\x02"
    if number == 3:
        return "\x03"
    if number == 4:
        return "\x04"
    if number == 5:
        return "\x05"
    if number == 6:
        return "\x06"
    if number == 7:
        return "\x07"
    if number == 8:
        return "\x08"
    if number == 9:
        return "\x09"
    if number == 10:
        return "\x0a"
    if number == 11:
        return "\x0b"
    if number == 12:
        return "\x0c"
    if number == 13:
        return "\x0d"
    if number == 14:
        return "\x0e"
    if number == 15:
        return "\x0f"
    
    return "uh-oh"
#end tohex

print "FTLNameEdit v1.0.  Searching for your FTL save file...\n\n\n"

#I think this bit is the only platform-specific thing that's needed...
if sys.platform.startswith("linux"):
    savefileDirectory = os.path.expanduser("~/.local/share/FasterThanLight/")
elif sys.platform.startswith("win"):
    savefileDirectory = os.path.expanduser("~/My Documents/My Games/FasterThanLight/")
elif sys.platform.startswith("darwin"):
    savefileDirectory = os.path.expanduser("~/Library/Application Support/FasterThanLight")

saveExists = os.path.exists(savefileDirectory + "continue.sav")
backupExists = os.path.exists(savefileDirectory + "continue.sav.bak")

#No save and no preexisting backup, so abort.
if not saveExists and not backupExists:
    print "Hey, there's no FTL save file!  What are you trying to pull?"
    print "Press enter to continue..."
    raw_input()
    sys.exit()

#No save, but a backup exists.  Ask if it should be restored.
if not saveExists:
    while True:
        print "No existing FTL save file, but FTLNameEdit-generated backup detected."
        print "Restore it? (y/n)"
        response = raw_input().lower()
        if response == "y":
            os.chdir(savefileDirectory)
            os.rename("continue.sav.bak", "continue.sav")
            print "Backup restored.  Press enter to continue..."
            raw_input()
            sys.exit()
        elif response == "n":
            print "Okay, then.  FTLNameEdit exiting."
            print "Press enter to continue..."
            raw_input()
            sys.exit()
        else:
            print "That was neither a \"y\" nor an \"n\".  Come on, you're smarter than that.\n"

#We have both a save file and a backup.  The savefile *might* have been
#corrupted by the renaming process, so ask if the backup should be
#restored.
if saveExists and backupExists:
    while True:
        print "Both a save file and a FTLNameEdit-generated backup exist."
        print "Do you want to [r]estore the backup, [c]ontinue renaming characters,"
        print "or [a]bort the program?"
        response = raw_input().lower()
        if response == "r":
            os.chdir(savefileDirectory)
            os.rename("continue.sav.bak", "continue.sav")
            print "Backup restored.  Press enter to continue..."
            raw_input()
            sys.exit()
        elif response == "c":
            break
        elif response == "a":
            print "Okay, then.  FTLNameEdit exiting."
            print "Press enter to continue..."
            raw_input()
            sys.exit()
        else:
            print "\nOkay, let's try that again, only this time you enter a \"r\", a \"c\", or an \"a\".\n"

#Time to get to work.
os.chdir(savefileDirectory)

print "Note: FTLNameEdit will generate a backup of your save file to be used in case"
print "the renaming process corrupts it.  To restore the backup, simply run"
print "FTLNameEdit again and you'll be asked whether you want the backup restored."
print "Please use this power only for good."

#First, rename the save file.  This original version won't be touched.
os.rename("continue.sav", "continue.sav.bak")
savefile = open("continue.sav.bak", "r+b")
newfile = open("continue.sav", "w+b")

#The locations of the length bytes for each name.
startpoints = []
#The original names.  These will be displayed to the user.
oldnames = []

#Extract the names and locations thereof from the save.
for i in range (0,os.path.getsize("continue.sav.bak")):
    savefile.seek(i)
    toTest = savefile.read(7)
    
    raceLength = teststring(toTest)
    
    if raceLength == 0:
        continue
        
    #Make sure the next byte is a NUL, so we're not editing starting crew.
    #Crude hack, but I'm about 99% sure it should work.
    savefile.seek(i+raceLength)
    if savefile.read(1) != "\x00":
        continue
    
    #Figure out how long the name is.
    nameLength = 0
    while True:
        savefile.seek(i - 5 - nameLength)
        if savefile.read(1) != "\x00":
            nameLength = nameLength + 1
        else:
            break
    
    #Add the starting point and original name to the appropriate lists.
    startpoints.append(i - 4 - nameLength)
    savefile.seek(i - 4 - nameLength)
    oldnames.append(savefile.read(nameLength))
    
    continue

#Generate the list of new names, to be filled by the user.
newnames = []
for i in range(0,len(oldnames)):
    newnames.append("")

while True:
    print "\n\nThe following names were found:"
    for i in range(0,len(oldnames)):
        if newnames[i] == "":
            print "\t" + str(i+1) + ": " + oldnames[i]
        else:
            print "\t" + str(i+1) + ": " + oldnames[i] + " ---> " + newnames[i]
    print "Enter a number to change a character's name, or q when you're ready to quit."
    response = raw_input()
    #We got a number.  Get the new name:
    if response.isdigit():
        responseNumber = int(response)
        if responseNumber < 1:
            print "I'm not sure why you'd think there'd be a crewmember with *that* number..."
            continue
        elif responseNumber > len(oldnames) + 1:
            print "There, uh, aren't that many crew members.  Try again?"
            continue
        print "Enter " + oldnames[responseNumber-1] + "'s new name (15 character limit, blank to abort):"
        newname = raw_input()
        if len(newname) > 15:
            print "\nI did say 15 character limit; try counting next time."
            continue
        if newname == oldnames[responseNumber-1]:
            newname = ""
        newnames[responseNumber-1] = newname
        continue
    elif response.lower() == "q":
        break
    else:
        print "\nThat was not even *slightly* a number or the letter \"q\".  Work with me, here...\n"
#And with that, we have all the names.

#Now, construct the actual save file.
#Structure of a character:
#[stuff]
#lengthbyte, NUL, NUL, NUL
#name
#lengthbyte, NUL, NUL, NUL
#race
#[stuff]
#etc.
for i in range(0,len(oldnames)):
    if i == 0:
        address = 0
    else:
        address = startpoints[i-1] + len(oldnames[i-1])
    savefile.seek(address)
    buf = savefile.read(startpoints[i] - address - 4)
    newfile.write(buf)
    
    nameToWrite = ""
    if newnames[i] == "":
        nameToWrite = oldnames[i]
    else:
        nameToWrite = newnames[i]
    hexdigit = tohex(len(nameToWrite))
    newfile.write(hexdigit)
    newfile.write("\x00\x00\x00"+nameToWrite)

savefile.seek(startpoints[-1] + len(oldnames[-1]))
buf = savefile.read()
newfile.write(buf)

print "Crew renamed!  Press enter to continue..."
raw_input()