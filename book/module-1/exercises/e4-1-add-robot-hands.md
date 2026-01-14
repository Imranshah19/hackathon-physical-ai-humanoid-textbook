# Exercise 4.1: Add Robot Hands

**Chapter**: 4 - Robot Description with URDF/XACRO
**Difficulty**: Intermediate
**Time**: 45 minutes

---

## Objective

Extend the humanoid URDF by adding hands to the forearms using XACRO macros.

## Requirements

1. Create a `hand.xacro` macro with:
   - Palm link (box geometry)
   - Wrist joint (fixed or revolute)
   - Parameters for left/right prefix

2. Hands should:
   - Attach to the forearm links
   - Have visual, collision, and inertial properties
   - Use consistent materials

3. Verify:
   - URDF validates with `check_urdf`
   - Hands visible in RViz2
   - TF tree shows hand frames

## Specifications

| Property | Value |
|----------|-------|
| Palm width | 0.08 m |
| Palm depth | 0.03 m |
| Palm length | 0.10 m |
| Palm mass | 0.3 kg |
| Wrist joint type | Fixed (simplified) |

## Starter Code

Create `humanoid_description/urdf/macros/hand.xacro`:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Hand dimensions -->
  <xacro:property name="palm_width" value="0.08"/>
  <xacro:property name="palm_depth" value="0.03"/>
  <xacro:property name="palm_length" value="0.10"/>
  <xacro:property name="palm_mass" value="0.3"/>

  <!-- Hand macro -->
  <xacro:macro name="hand" params="prefix parent">

    <!-- TODO: Create palm link -->
    <link name="${prefix}_hand">
      <!-- Visual -->

      <!-- Collision -->

      <!-- Inertial -->

    </link>

    <!-- TODO: Create wrist joint -->
    <joint name="${prefix}_wrist" type="fixed">
      <!-- Parent/child -->

      <!-- Origin -->

    </joint>

  </xacro:macro>

</robot>
```

## Integration

Add to `humanoid.urdf.xacro`:

```xml
<!-- Include hand macro -->
<xacro:include filename="$(find humanoid_description)/urdf/macros/hand.xacro"/>

<!-- Instantiate hands -->
<xacro:hand prefix="left" parent="left_forearm"/>
<xacro:hand prefix="right" parent="right_forearm"/>
```

## Verification

```bash
# Generate URDF
cd ~/humanoid_ros2_ws/src/humanoid_description/urdf
xacro humanoid.urdf.xacro > humanoid.urdf

# Validate
check_urdf humanoid.urdf
# Should show: left_hand, right_hand links

# Visualize
ros2 launch humanoid_description display.launch.py

# Check TF
ros2 run tf2_tools view_frames
# Should show hand frames in tree
```

## Expected Output

```
robot name is: humanoid
---------- Successfully Parsed XML ---------------
root Link: base_link has 5 child(ren)
    child(1):  head
    child(2):  left_upper_arm
        child(1):  left_forearm
            child(1):  left_hand    # NEW
    child(3):  right_upper_arm
        child(1):  right_forearm
            child(1):  right_hand   # NEW
    ...
```

## Hints

<details>
<summary>Hint 1: Joint origin</summary>

The wrist joint should be at the end of the forearm:
```xml
<origin xyz="0 0 ${-forearm_length}" rpy="0 0 0"/>
```
</details>

<details>
<summary>Hint 2: Inertia for box</summary>

```xml
<xacro:box_inertia mass="${palm_mass}"
                   width="${palm_width}"
                   depth="${palm_depth}"
                   height="${palm_length}"/>
```
</details>

---

## Bonus Challenges

1. **Articulated fingers**: Add 3 finger links per hand with revolute joints
2. **Gripper joint**: Make wrist joint revolute with limits
3. **Mesh hands**: Import STL mesh for realistic hand geometry
