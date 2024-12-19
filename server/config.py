import socket

# Server configuration
SERVER_PORT = 67
CLIENT_PORT = 68
BUFFER_SIZE = 1024

# Example IP pool from which the DHCP server can assign IPs
ip_pool = [
    "192.168.1.100",
    "192.168.1.101",
    "192.168.1.102"
]

# Lease duration (time in seconds that the client can use the assigned IP address)
lease_duration = 3600  # Default lease time set to 1 hour (3600 seconds)

# Server's IP address, retrieved dynamically
server_ip = socket.gethostbyname(socket.gethostname())  # Get the local IP address of the server

# Lease table: Keeps track of active leases and expiry times
# Example format: lease_table = {client_address: (ip, lease_expiry, xid, mac_address)}
lease_table = {}
discover_cache={}

# Logging configurations (Optional for better debugging)
log_file = "dhcp_server.log"  # Path to log file
log_level = "INFO"  # Log level: INFO, DEBUG, ERROR, etc.
