# Command for a single joint
# Used to send position, velocity, or effort targets

string joint_name           # Name of the joint (e.g., "head_pan")
float64 position            # Target position in radians
float64 velocity            # Target velocity in rad/s
float64 effort              # Target effort (torque) in Nm
builtin_interfaces/Time stamp  # Timestamp of command
