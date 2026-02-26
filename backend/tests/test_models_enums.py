"""
Tests for profile enums, validation helpers, and option lists.
"""

import pytest
from src.models.enums import (
    SoftwareBackground,
    HardwareAccess,
    ExperienceLevel,
    SOFTWARE_OPTIONS,
    HARDWARE_OPTIONS,
    EXPERIENCE_OPTIONS,
    ProfileOption,
    get_all_profile_options,
    validate_software_background,
    validate_hardware_access,
    validate_experience_level,
)


# ---------------------------------------------------------------------------
# SoftwareBackground
# ---------------------------------------------------------------------------

class TestSoftwareBackgroundEnum:
    def test_python_value(self):
        assert SoftwareBackground.PYTHON == "python"

    def test_cpp_value(self):
        assert SoftwareBackground.CPP == "cpp"

    def test_javascript_value(self):
        assert SoftwareBackground.JAVASCRIPT_TYPESCRIPT == "javascript_typescript"

    def test_ros_value(self):
        assert SoftwareBackground.ROS_ROS2 == "ros_ros2"

    def test_matlab_value(self):
        assert SoftwareBackground.MATLAB == "matlab"

    def test_none_learning_value(self):
        assert SoftwareBackground.NONE_LEARNING == "none_learning"

    def test_is_string_subclass(self):
        assert isinstance(SoftwareBackground.PYTHON, str)

    def test_count(self):
        assert len(SoftwareBackground) == 6

    def test_all_values_unique(self):
        values = [e.value for e in SoftwareBackground]
        assert len(values) == len(set(values))


# ---------------------------------------------------------------------------
# HardwareAccess
# ---------------------------------------------------------------------------

class TestHardwareAccessEnum:
    def test_simulation_only_value(self):
        assert HardwareAccess.SIMULATION_ONLY == "simulation_only"

    def test_humanoid_robot_value(self):
        assert HardwareAccess.HUMANOID_ROBOT == "humanoid_robot"

    def test_nvidia_jetson_value(self):
        assert HardwareAccess.NVIDIA_JETSON == "nvidia_jetson"

    def test_raspberry_pi_value(self):
        assert HardwareAccess.RASPBERRY_PI == "raspberry_pi"

    def test_count(self):
        assert len(HardwareAccess) == 8

    def test_all_values_unique(self):
        values = [e.value for e in HardwareAccess]
        assert len(values) == len(set(values))


# ---------------------------------------------------------------------------
# ExperienceLevel
# ---------------------------------------------------------------------------

class TestExperienceLevelEnum:
    def test_beginner_value(self):
        assert ExperienceLevel.BEGINNER == "beginner"

    def test_intermediate_value(self):
        assert ExperienceLevel.INTERMEDIATE == "intermediate"

    def test_advanced_value(self):
        assert ExperienceLevel.ADVANCED == "advanced"

    def test_count(self):
        assert len(ExperienceLevel) == 3

    def test_is_string_subclass(self):
        assert isinstance(ExperienceLevel.BEGINNER, str)


# ---------------------------------------------------------------------------
# validate_software_background
# ---------------------------------------------------------------------------

class TestValidateSoftwareBackground:
    def test_single_valid_value(self):
        assert validate_software_background(["python"]) is True

    def test_multiple_valid_values(self):
        assert validate_software_background(["python", "cpp", "ros_ros2"]) is True

    def test_all_valid_values(self):
        all_vals = [e.value for e in SoftwareBackground]
        assert validate_software_background(all_vals) is True

    def test_invalid_value(self):
        assert validate_software_background(["ruby"]) is False

    def test_mixed_valid_and_invalid(self):
        assert validate_software_background(["python", "unknown_lang"]) is False

    def test_empty_list_is_valid(self):
        assert validate_software_background([]) is True

    def test_case_sensitive(self):
        assert validate_software_background(["Python"]) is False


# ---------------------------------------------------------------------------
# validate_hardware_access
# ---------------------------------------------------------------------------

class TestValidateHardwareAccess:
    def test_single_valid_value(self):
        assert validate_hardware_access(["simulation_only"]) is True

    def test_multiple_valid_values(self):
        assert validate_hardware_access(["raspberry_pi", "nvidia_jetson"]) is True

    def test_all_valid_values(self):
        all_vals = [e.value for e in HardwareAccess]
        assert validate_hardware_access(all_vals) is True

    def test_invalid_value(self):
        assert validate_hardware_access(["laptop"]) is False

    def test_empty_list_is_valid(self):
        assert validate_hardware_access([]) is True

    def test_case_sensitive(self):
        assert validate_hardware_access(["Simulation_Only"]) is False


# ---------------------------------------------------------------------------
# validate_experience_level
# ---------------------------------------------------------------------------

class TestValidateExperienceLevel:
    def test_beginner_valid(self):
        assert validate_experience_level("beginner") is True

    def test_intermediate_valid(self):
        assert validate_experience_level("intermediate") is True

    def test_advanced_valid(self):
        assert validate_experience_level("advanced") is True

    def test_invalid_value(self):
        assert validate_experience_level("expert") is False

    def test_empty_string_invalid(self):
        assert validate_experience_level("") is False

    def test_case_sensitive(self):
        assert validate_experience_level("Beginner") is False


# ---------------------------------------------------------------------------
# get_all_profile_options
# ---------------------------------------------------------------------------

class TestGetAllProfileOptions:
    def test_returns_three_categories(self):
        opts = get_all_profile_options()
        assert set(opts.keys()) == {"softwareBackground", "hardwareAccess", "experienceLevel"}

    def test_software_background_count_matches_options_list(self):
        opts = get_all_profile_options()
        assert len(opts["softwareBackground"]) == len(SOFTWARE_OPTIONS)

    def test_hardware_access_count_matches_options_list(self):
        opts = get_all_profile_options()
        assert len(opts["hardwareAccess"]) == len(HARDWARE_OPTIONS)

    def test_experience_level_count_matches_options_list(self):
        opts = get_all_profile_options()
        assert len(opts["experienceLevel"]) == len(EXPERIENCE_OPTIONS)

    def test_each_option_has_value_label_description(self):
        opts = get_all_profile_options()
        for category in opts.values():
            for option in category:
                assert "value" in option, f"Missing 'value' in {option}"
                assert "label" in option, f"Missing 'label' in {option}"
                assert "description" in option, f"Missing 'description' in {option}"

    def test_software_option_values_are_valid_enum_members(self):
        opts = get_all_profile_options()
        valid = {e.value for e in SoftwareBackground}
        for opt in opts["softwareBackground"]:
            assert opt["value"] in valid

    def test_hardware_option_values_are_valid_enum_members(self):
        opts = get_all_profile_options()
        valid = {e.value for e in HardwareAccess}
        for opt in opts["hardwareAccess"]:
            assert opt["value"] in valid

    def test_experience_option_values_are_valid_enum_members(self):
        opts = get_all_profile_options()
        valid = {e.value for e in ExperienceLevel}
        for opt in opts["experienceLevel"]:
            assert opt["value"] in valid

    def test_option_labels_are_non_empty_strings(self):
        opts = get_all_profile_options()
        for category in opts.values():
            for option in category:
                assert isinstance(option["label"], str)
                assert len(option["label"]) > 0


# ---------------------------------------------------------------------------
# ProfileOption namedtuple
# ---------------------------------------------------------------------------

class TestProfileOption:
    def test_namedtuple_fields(self):
        opt = ProfileOption(value="python", label="Python", description="A description")
        assert opt.value == "python"
        assert opt.label == "Python"
        assert opt.description == "A description"

    def test_options_lists_contain_profile_option_instances(self):
        for opt in SOFTWARE_OPTIONS:
            assert isinstance(opt, ProfileOption)
        for opt in HARDWARE_OPTIONS:
            assert isinstance(opt, ProfileOption)
        for opt in EXPERIENCE_OPTIONS:
            assert isinstance(opt, ProfileOption)
