import sys


# Read in the file
with open('Client.py', 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace('socket.gethostname()', f'\'{sys.argv[1]}\'')

# Write the file out again
with open('Client.py', 'w') as file:
  file.write(filedata)
