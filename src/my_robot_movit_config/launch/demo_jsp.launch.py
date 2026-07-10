from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launch_utils import DeclareBooleanLaunchArg


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder(
        "my_robot", package_name="my_robot_movit_config"
    ).to_moveit_configs()
    package_path = moveit_config.package_path

    return LaunchDescription(
        [
            DeclareBooleanLaunchArg("use_rviz", default_value=True),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(package_path / "launch/rsp.launch.py")
                )
            ),
            Node(
                package="my_robot_movit_config",
                executable="plan_animator.py",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(package_path / "launch/move_group.launch.py")
                )
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    str(package_path / "launch/moveit_rviz.launch.py")
                ),
                condition=IfCondition(LaunchConfiguration("use_rviz")),
            ),
        ]
    )
