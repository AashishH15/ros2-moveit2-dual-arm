import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
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

    virtual_joints_launch = package_path / "launch/static_virtual_joint_tfs.launch.py"

    ld = LaunchDescription(
        [
            DeclareBooleanLaunchArg(
                "db",
                default_value=False,
                description="By default, we do not start a database (it can be large)",
            ),
            DeclareBooleanLaunchArg(
                "debug",
                default_value=False,
                description="By default, we are not in debug mode",
            ),
            DeclareBooleanLaunchArg("use_rviz", default_value=True),
        ]
    )

    if virtual_joints_launch.exists():
        ld.add_action(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(str(virtual_joints_launch)),
            )
        )

    # robot_state_publisher must start first — ros2_control_node waits for /robot_description.
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(package_path / "launch/rsp.launch.py")),
        )
    )

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(package_path / "launch/move_group.launch.py")
            ),
        )
    )

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(package_path / "launch/moveit_rviz.launch.py")
            ),
            condition=IfCondition(LaunchConfiguration("use_rviz")),
        )
    )

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(package_path / "launch/warehouse_db.launch.py")
            ),
            condition=IfCondition(LaunchConfiguration("db")),
        )
    )

    # Delay ros2_control so it receives /robot_description from THIS session's rsp,
    # not a stale publisher from a previous launch.
    ld.add_action(
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package="controller_manager",
                    executable="ros2_control_node",
                    parameters=[
                        moveit_config.robot_description,
                        str(package_path / "config/ros2_controllers.yaml"),
                    ],
                    remappings=[
                        ("/controller_manager/robot_description", "/robot_description"),
                    ],
                    output="screen",
                    additional_env={"DISPLAY": os.environ.get("DISPLAY", "")},
                )
            ],
        )
    )

    ld.add_action(
        TimerAction(
            period=8.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        str(package_path / "launch/spawn_controllers.launch.py")
                    ),
                )
            ],
        )
    )

    return ld
