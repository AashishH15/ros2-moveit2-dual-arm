#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from moveit_msgs.msg import DisplayTrajectory
from sensor_msgs.msg import JointState


class PlanAnimator(Node):
  def __init__(self):
    super().__init__('plan_animator')
    self.publisher = self.create_publisher(JointState, 'joint_states', 10)
    self.create_subscription(
      DisplayTrajectory,
      '/move_group/display_planned_path',
      self.on_plan,
      10,
    )
    self.timer = None
    self.joint_names = []
    self.points = []
    self.index = 0

  def on_plan(self, msg):
    if not msg.trajectory:
      return

    joint_trajectory = msg.trajectory[0].joint_trajectory
    if not joint_trajectory.points:
      return

    self.joint_names = list(joint_trajectory.joint_names)
    self.points = list(joint_trajectory.points)
    self.index = 0

    if self.timer is not None:
      self.timer.cancel()

    self.timer = self.create_timer(0.05, self.publish_next)

  def publish_next(self):
    if self.index >= len(self.points):
      if self.timer is not None:
        self.timer.cancel()
      return

    point = self.points[self.index]
    joint_state = JointState()
    joint_state.header.stamp = self.get_clock().now().to_msg()
    joint_state.name = self.joint_names
    joint_state.position = list(point.positions)
    self.publisher.publish(joint_state)
    self.index += 1


def main():
  rclpy.init()
  node = PlanAnimator()
  rclpy.spin(node)
  node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()
