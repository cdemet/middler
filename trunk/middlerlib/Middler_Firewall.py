#!/usr/bin/env python

#######################
# Variable definitions
#######################

operating_system = "nyd"

####################################################################################################
### Firewall/routing setup, to route packets and capture connections                               #
####################################################################################################


def redirectIPFWstart():
  """This functions starts up the ipfw forwarding so that as this machine routes traffic, it redirects port 80 traffic to itself."""

  # Set up firewall to grab port 80 traffic flowing through this machine and send it
  # to the proxy.

  # For debugging, to avoid running this program as root, we redirect traffic destined to
  # 127.0.0.1 port 80 to port 8080.
  #
  #ipfw add 1000 fwd 127.0.0.1,8080 tcp from any to 127.0.0.1 dst-port 80 in via lo0


  # Run ipfw list, so we can look for a rule that starts with 01000
  ipfw_cmd=os.popen("/sbin/ipfw list","r")
  ipfw_lines=ipfw_cmd.readlines()
  ipfw_cmd.close()

  found_line=0
  for line in ipfw_lines:
    if re.match(r"^01000 fwd 127\.0\.0\.1\,8080 tcp from any to any dst-port 80 in via lo0",line):
      found_line=1

  if not found_line:
    ipfw_modify=os.popen("/sbin/ipfw add 1000 fwd 127.0.0.1,8080 tcp from any to any dst-port 80 in via lo0")

  found_line

def redirectIPFWstop():
  # Run ipfw list, so we can look for a rule that starts with 01000
  ipfw_cmd=os.popen("/sbin/ipfw list","r")
  ipfw_lines=ipfw_cmd.readlines()
  ipfw_cmd.close()

  found_line=0
  for line in ipfw_lines:
    if re.match(r"^01000 fwd 127\.0\.0\.1\,8080 tcp from any to any dst-port 80 in via en1",line):
      found_line=1

  if found_line:
    ipfw_modify=os.popen("/sbin/ipfw del 1000")

  found_line

def redirectIPTablesStart():
  os.system("iptables -t nat -N MIDDLERNAT")
  os.system("iptables -t nat -A PREROUTING -j MIDDLERNAT")
  os.system("iptables -t nat -I MIDDLERNAT -p tcp --dport 80 -j REDIRECT --to-ports 8080")
  
def redirectIPTablesStop():

  # TODO-Medium: write a routine to find the jump to the MIDDLERNAT rule first, so we can entirely remove
  # all traces of the MIDDLERNAT rule instead of just rendering it ineffective.
  os.system("iptables -t nat -D MIDDLERNAT 1")

  ##############################
  # Packet Routing             #
  ##############################

def startRedirection():

  # Activate forwarding on the operating system kernel.
  debug_log("Activating forwarding\n")
  try:
    uname_cmd=popen(r"uname -s")
    uname_operating_system = uname_cmd.readline()
    uname_cmd.close()

    # Check if we're on OS X.
    if uname_operating_system == r"Darwin":
      # Store O/S
      operating_system = "OSX"
      # Activate forwarding on Darwin via sysctl
      os.system(r"sysctl -w net.inet.ip.forwarding=1")
      # Set up the firewall
      redirectIPFWstart()
    # Next check if we're on Linux
    elif uname_operating_system == r"Linux":
      operating_system - "Linux"
      # Activate packet forwarding via proc
      os.system(r"echo 1>/proc/sys/net/ipv4/ip_forward")
      redirectIPTablesStart()
    # Next check if we're on Windows (Cygwin)
    elif uname_operating_system[0:5] == r"CYGWIN":
      operating_system - "Windows"
      print "ERROR: routing and network redirection code does not yet run on Windows"
      

  except:
    exit

def stopRedirection():
  if operating_system == r"OSX":
    redirectIPFWstop()
  elif operating_system == r"Linux":
    redirectIPTablesStop()
  elif operating_system == r"CYGWIN":
    print "ERRROR: routing redirection cannot be halted on Windows yet..."