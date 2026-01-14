# State of multiple joints
# Similar to sensor_msgs/JointState but simplified for humanoid

string[] joint_names        # Names of joints
float64[] positions         # Current positions in radians
float64[] velocities        # Current velocities in rad/s
float64[] efforts           # Current efforts in Nm
builtin_interfaces/Time stamp  # Timestamp of reading
