# Complete state of the humanoid robot
# Combines joint state with base pose and safety status

std_msgs/Header header

# Joint information
humanoid_msgs/JointState joint_state

# Base pose and velocity
geometry_msgs/Pose base_pose      # Position and orientation
geometry_msgs/Twist base_twist    # Linear and angular velocity

# Safety status
bool emergency_stop               # True if e-stop is active
