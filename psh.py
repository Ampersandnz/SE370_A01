# SoftEng 370 Assignment 1
# Python3 shell
# Michael Lo
# mlo450
# 5530588

import os
import string
import signal
import shlex
import sys
import subprocess
from time import sleep

#This class manages the list of recently entered input strings.
class CommandHistory:
	def __init__(self):
		self.commandList = []

	def addCommand(self, command):
		self.commandList.append(command)

	def removeCommand(self, index):
		self.commandList.pop(index - 1)

	def getCommand(self, index):
		return self.commandList[index - 1]

	def setCommand(self, index, command):
		self.commandList[index - 1] = command

	def printCommands(self):
		for i in range(0, len(self.commandList)):
			if(i >= len(self.commandList) - 10):
				print ("%d: %s" % (i + 1, self.commandList[i]))

	@property
	def numCommands(self):
		return len(self.commandList)

#When the key combination CTRL+Z is pressed, the correct shell function is called.
def interceptCTRLZ(signum, frame):
    sc_ctrl_z([""])

#Lists the commands that will be executed by this shell rather than the system.
shellCommandList = ["pwd", "cd", "h", "history", "bg", "fg", "kill", "q", "quit", "exit", "jobs"]

commandHistory = CommandHistory()
jobList = []
homeDir = os.getcwd()

#Intercepts CTRL+Z keypresses to perform our own functionality, rather than this shell being backgrounded.
signal.signal(signal.SIGTSTP, interceptCTRLZ)

#Accepts user input, and runs the commands when they are entered.
def main():
	while (1):
		userInput = input('psh> ')
		if (userInput.strip() != ""):
			doAllCommands(userInput)

#Saves the user's input in history, parses the string into is separate command[s] and arguments, then calls those commands with their respective arguments.
def doAllCommands(userInput):
	commandHistory.addCommand(userInput)
	doCommand(parseInput(userInput))

#Determines if a given command with arguments should be executed by the shell or the system.
def doCommand(command_with_args):
	command = command_with_args[0]

	if isShellCommand(command):
		doShellCommand(command, command_with_args)
	else:
		doSystemCommand(command, command_with_args)

#Calls the relevant shell function for this command, passing in its arguments.
def doShellCommand(command, arguments):
	shellCommands[command](arguments)

#Calls the relevant system command, passing in its arguments.
def doSystemCommand(command, arguments):
	newpid = os.fork()
	amper = False
	if (arguments[len(arguments) - 1] == "&"):
		amper = True
	if (newpid == 0):
		if amper:
			arguments.pop(len(arguments) - 1)



		#IFF PIPE BEING USED
		#https://docs.python.org/3/library/subprocess.html#popen-constructor
#		if (/* piping */):
#			pipe(fildes)
#			if (fork() == 0):
#				# first component of command line
#				close(stdout)
#				dup(fildes[1])
#				close(fildes[1])
#				close(fildes[0])
#				# stdout now goes to pipe
#				# child process does command
#				execlp(command1, command1, 0)
#
#			# second component of command line
#			close(stdin);
#			dup(fildes[0]);
#			close(fildes[0]);
#			close(fildes[1]);
#			# standard input now comes from the pipe






		os.execvp(command, arguments)
		os._exit(1)
	else:
		if not amper:
			os.wait()

#Takes in the full typed string and returns the command split into its component arguments.
def parseInput(userInput):
    lexer = shlex.shlex(userInput, posix=True)
    lexer.whitespace_split = False
    lexer.wordchars += '#$+-,./?@^='
    args = list(lexer)
    return args

#Checks if a given command should be executed by this shell, or simply passed on to the system.
def isShellCommand(command):
	return command in shellCommandList

#Shell command functions follow:

#Print working directory.
def sc_pwd(arguments):
	print(os.getcwd())

#Change directory.
def sc_cd(arguments):
	if (len(arguments) == 1):
		newPath = homeDir

	elif (arguments[1].startswith("..")):
		splitPath = os.getcwd().rsplit("/", 1)
		upOneLevel = splitPath[0]

		if (upOneLevel==""):
			upOneLevel = "/"

		newPath = upOneLevel

		if (arguments[1] != ".."):
			if (newPath == "/"):
				newPath = arguments[1][2:]
			else:
				newPath = newPath + arguments[1][2:]
		
	elif (arguments[1].startswith(".")):
		addToPath = (arguments[1])[1:]
		newPath = os.getcwd() + addToPath

	elif (arguments[1].startswith("/")):
		newPath = arguments[1]

	elif (arguments[1].startswith("~")):
		newPath = os.path.expanduser(arguments[1])

	else:
		newPath = os.getcwd() + "/" + arguments[1]

	if(os.path.isdir(newPath)):
		os.chdir(newPath)
	else:
		print("psh: cd: " + arguments[1] + ": No such file or directory")

#History. With no arguments, returns the last ten commands used. With a numerical argument, calls the command with that index again.
def sc_h(arguments):
	if (arguments[1] == ""):
		commandHistory.printCommands()
	else:
		command = commandHistory.getCommand(int(arguments[1]))
		commandHistory.removeCommand(commandHistory.numCommands)
		doCommand(command)

#Background.
#NOT YET IMPLEMENTED
def sc_bg(arguments):
	return
	
#Foreground.
#NOT YET IMPLEMENTED
def sc_fg(arguments):
	return
	
#Forces a process to stop.
#NOT YET IMPLEMENTED
def sc_kill(arguments):
	#os.kill(process.pid, signal.SIGKILL)
	return
	
#Forces a process to sleep/wait.
#NOT YET IMPLEMENTED
def sc_ctrl_z(arguments):
	return

#Quits this shell
def sc_q(arguments):
	sys.exit()

#Quits this shell
def sc_jobs(arguments):
	return

#Map the inputs to the function blocks.
shellCommands = {
	shellCommandList[0] : sc_pwd,
	shellCommandList[1] : sc_cd,
	shellCommandList[2] : sc_h,
	shellCommandList[3] : sc_h,
	shellCommandList[4] : sc_bg,
	shellCommandList[5] : sc_fg,
	shellCommandList[6] : sc_kill,
	shellCommandList[7] : sc_q,
	shellCommandList[8] : sc_q,
	shellCommandList[9] : sc_q,
	shellCommandList[10] : sc_jobs
}

if __name__ == "__main__":
	main()