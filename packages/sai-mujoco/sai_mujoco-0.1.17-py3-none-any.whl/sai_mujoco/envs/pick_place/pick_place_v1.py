import mujoco
import numpy as np

from sai_mujoco.envs.base.base_v1 import BaseEnv_v1
from sai_mujoco.robots.base.v1 import GripperPart_v1
from sai_mujoco.utils.v0.rotations import mat2euler


def goal_distance(goal_a, goal_b):
    """Calculate the Euclidean distance between two goals.

    Args:
        goal_a (np.ndarray): First goal position
        goal_b (np.ndarray): Second goal position

    Returns:
        float: Euclidean distance between the two goals
    """
    assert goal_a.shape == goal_b.shape
    return np.linalg.norm(goal_a - goal_b, axis=-1)


class PickAndPlace_v1(BaseEnv_v1):
    r"""

        ## Description
        A Pick and place environment designed for object lifting. The task is to control the robot arm to reach, grasp, and lift a single cube from
        the table surface, and then place it accurately at a designated target position.

        ## Observation Space
        The observation space consists of the following parts (in order):

        - *qpos:* Position values of the robot's body parts. The dimensionality depends on the robot's joint configuration.
        - *qvel:* The velocities of these individual body parts (their derivatives). The dimensionality depends on the robot's joint configuration.
        - *gripper_pos (3 elements):* The end effector's position in the world frame.
        - *object_pos (3 elements):* The object's position in the world frame.
        - *pos_rel_gripper_object (3 elements):* The object's position in the end effector frame.
        - *vel_rel_gripper_object (3 elements):* The object's velocity in the end effector frame.
        - *object_rot (3 elements):* The object's rotation (euler angles) in the world frame.
        - *object_velp (3 elements):* The object's linear velocity in the world frame.
        - *object_velr (3 elements):* The object's rotational velocity in the world frame.
        - *target_pos (3 elements):* The target position in the world frame.
        - *target_rot (3 elements):* The target rotation in the world frame.

        The order of elements in the observation space related to the environment is as follows -

        | Num | Observation                        | Min  | Max | Type (Unit)              |
        | --- | -----------------------------------| ---- | --- | ------------------------ |
        | 0   | x-coordinate of gripper position   | -Inf | Inf | position (m)             |
        | 1   | y-coordinate of gripper position   | -Inf | Inf | position (m)             |
        | 2   | z-coordinate of gripper position   | -Inf | Inf | position (m)             |
        | 3   | x-coordinate of object position    | -Inf | Inf | position (m)             |
        | 4   | y-coordinate of object position    | -Inf | Inf | position (m)             |
        | 5   | z-coordinate of object position    | -Inf | Inf | position (m)             |
        | 6   | x rel pos of object in gripper     | -Inf | Inf | position (m)             |
        | 7   | y rel pos of object in gripper     | -Inf | Inf | position (m)             |
        | 8   | z rel pos of object in gripper     | -Inf | Inf | position (m)             |
        | 9   | x rel vel of object in gripper     | -Inf | Inf | linear velocity (m/s)    |
        | 10  | y rel vel of object in gripper     | -Inf | Inf | linear velocity (m/s)    |
        | 11  | z rel vel of object in gripper     | -Inf | Inf | linear velocity (m/s)    |
        | 12  | roll of object                     | -Inf | Inf | rotation (rad)           |
        | 13  | pitch of object                    | -Inf | Inf | rotation (rad)           |
        | 14  | yaw of object                      | -Inf | Inf | rotation (rad)           |
        | 15  | x velocity of object               | -Inf | Inf | linear velocity (m/s)    |
        | 16  | y velocity of object               | -Inf | Inf | linear velocity (m/s)    |
        | 17  | z velocity of object               | -Inf | Inf | linear velocity (m/s)    |
        | 18  | x angular velocity of object       | -Inf | Inf | angular velocity (rad/s) |
        | 19  | y angular velocity of object       | -Inf | Inf | angular velocity (rad/s) |
        | 20  | z angular velocity of object       | -Inf | Inf | angular velocity (rad/s) |
        | 21  | x-coordinate of target             | -Inf | Inf | position (m)             |
        | 22  | y-coordinate of target             | -Inf | Inf | position (m)             |
        | 23  | z-coordinate of target             | -Inf | Inf | position (m)             |
        | 24  | roll of target                     | -Inf | Inf | rotation (rad)           |
        | 25  | pitch of target                    | -Inf | Inf | rotation (rad)           |
        | 26  | yaw of target                      | -Inf | Inf | rotation (rad)           |

        ## Rewards

        The environment supports two reward types that can be specified during initialization:

        ### Dense Reward (default)
        The dense reward components include:

        - `reach`: Encourages the gripper to move closer to the object by assigning higher reward as the distance between the gripper and object decreases.
        - `grasp`: Rewards successful grasping of the object with a binary reward.
        - `lift`: Encourages the gripper to lift the object by assigning higher reward as the distance between the gripper and object decreases.
        - `place`: Rewards successful placement of the object at the target location with a binary reward.
        - `timestep`: Penalizes the agent for taking more timesteps to complete the task.

        ### Sparse Reward
        When `reward_type="sparse"` is specified during initialization, the reward becomes:
            - `1.0` if the object is successfully placed at the target location
            - `0.0` otherwise

        `info` contains the success parameter if the given episode succeeded.

        ## Episode End
        ### Termination

        The current episode should terminate based on termination criteria defined as follow:
            1. If the distance between object and target is less than threshold (0.05)

        ### Truncation
        The default duration of an episode is 500 timesteps.

        ## Arguments
        The environment accepts the following parameters during initialization:

        - `reward_type` (str, optional): Specifies the reward type. Options are:
            - `"dense"` (default): Provides continuous reward based on distances
            - `"sparse"`: Provides binary reward (1.0 for success, 0.0 otherwise)

        Env provides the parameter to modify the start state of the robot upon reset.
        It can be applied during `gymnasium.make` by changing deterministic_reset (bool).
    ."""

    env_name: str = "pick_place/v1"
    scene_name: str = "v0/base_scene"
    single_robot = True

    default_camera_config = {
        "trackbodyid": -1,
        "lookat": [0.5, 0.5, 0.5],
        "distance": 3.5,
        "elevation": -30,
        "azimuth": 135,
    }

    reward_config = {
        "reach": 0.1,
        "grasp": 0.35,
        "lift": 0.3,
        "place": 100.0,
        "timestep": -0.2,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reward_type = kwargs.get("reward_type", "dense")

        if self.reward_type == "sparse":
            self.reward_config = {"success_bonus": 1.0}

    def _setup_references(self):
        super()._setup_references()

        self.ee_site_name = self.robots[0]._arms["left_arm"].gripper.site_name
        self.ee_site_id = self.sim.model.site_name2id(self.ee_site_name)
        self.object_geom = "object0_geom"

    def _reset_internal(self):
        """
        Reset the environment to an initial state.
        """
        super()._reset_internal()

        self._sample_object()
        self.goal_pos = self._sample_goal()

    def _render_callback(self):
        """Update the visualization of the target site."""
        sites_offset = (self.sim.data.site_xpos - self.sim.model._model.site_pos).copy()
        site_id = mujoco.mj_name2id(
            self.sim.model._model, mujoco.mjtObj.mjOBJ_SITE, "target0"
        )
        self.sim.model._model.site_pos[site_id] = self.goal_pos - sites_offset[site_id]
        self.sim.forward()

    def _get_env_obs(self):
        """
        Collects and returns the current environment observation.

        This function gathers the relevant physical states of the main entities
        in the pick and place simulation environment—namely, the end effector, object,
        and the target—and concatenates their positions and orientation into a single
        observation vector.

        Specifically, it retrieves:
            - The 3D position of the gripper (`gripper_pos`)
            - The 3D relative position between gripper and object (`pos_rel_gripper_object`)
            - The 3D relative linear velocity between gripper and object (`vel_rel_gripper_object`)
            - The orientation of the object in Euler angles (`object_rot`)
            - The 3D linear velocity of the object (`object_velp`)
            - The 3D angular velocity of the object (`object_velr`)
            - The 3D position of the target (`target_pos`)
            - The orientation of the target in Euler angles (`target_rot`)

        The final observation is a 27-dimensional float32 NumPy array:
            [gripper_x, gripper_y, gripper_z,
            gripper_obj_dx, gripper_obj_dy, gripper_obj_dz,
            gripper_obj_vx, gripper_obj_vy, gripper_obj_vz,
            object_euler_x, object_euler_y, object_euler_z,
            object_vx, object_vy, object_vz,
            object_wx, object_wy, object_wz,
            target_x, target_y, target_z,
            target_euler_x, target_euler_y, target_euler_z]

        Returns
        -------
        obs : np.ndarray of shape (27,), dtype np.float32
            The concatenated observation vector representing the positions and
            orientation of key environment elements.
        """
        gripper_pos = self.sim.data.get_site_xpos(self.ee_site_name)
        gripper_velp = self.sim.data.get_site_xvelp(self.ee_site_name)

        object_pos = self.sim.data.get_site_xpos("object0")
        object_rot = mat2euler(self.sim.data.get_site_xmat("object0"))

        object_velp = self.sim.data.get_site_xvelp("object0")
        object_velr = self.sim.data.get_site_xvelr("object0")

        target_pos = self.sim.data.get_site_xpos("target0")
        target_rot = mat2euler(self.sim.data.get_site_xmat("target0"))

        pos_rel_gripper_object = gripper_pos - object_pos

        vel_rel_gripper_object = object_velp - gripper_velp

        return np.concatenate(
            [
                gripper_pos,
                object_pos,
                pos_rel_gripper_object,
                vel_rel_gripper_object,
                object_rot,
                object_velp,
                object_velr,
                target_pos,
                target_rot,
            ],
            dtype=np.float32,
        )

    def _get_info(self):
        """Get additional information about the environment state.

        Returns:
            dict: Additional information dictionary
        """
        return {
            "success": self._is_success(
                self.sim.data.get_site_xpos("object0"), self.goal_pos
            )
        }

    def compute_terminated(self):
        """
        Determines whether the current episode should terminate based on task conditions.

        This function checks for the termination criteria in the pick and place environment:
            1. If the distance between object and target is less than threshold (0.05)

        Returns
        -------
        terminated : bool
            `True` if any of the termination conditions are met; otherwise `False`.
        """
        object_pos = self.sim.data.get_site_xpos("object0")
        target_pos = self.sim.data.get_site_xpos("target0")
        return self._is_success(object_pos, target_pos)

    def compute_reward(self):
        """
        Computes and returns individual reward components for the current simulation state.

        The reward components include:

        1. `timestep`: Penalizes the agent for taking more timesteps to complete the task.
        2. `reach`: Encourages the gripper to move closer to the object using hyperbolic tangent scaling.
        3. `grasp`: Rewards successful grasping of the object with a binary reward.
        4. `lift`: Encourages lifting the object toward the target using hyperbolic tangent scaling.
        5. `place`: Rewards successful placement of the object at the target location with a binary reward.

        Returns
        -------
        raw_reward : dict
            A dictionary mapping each reward term name (str) to its corresponding scalar value (float).
            These are raw values and not yet combined into a scalar total reward.
        """
        if self.reward_type == "sparse":
            return self._compute_sparse_reward()
        else:
            return self._compute_dense_reward()

    def _compute_sparse_reward(self):
        """Compute sparse reward for the current simulation state."""
        return {
            "success_bonus": 1.0
            if self._is_success(self.sim.data.get_site_xpos("object0"), self.goal_pos)
            else 0.0,
        }

    def _compute_dense_reward(self):
        """Compute dense reward for the current simulation state."""
        gripper_pos = self.sim.data.get_site_xpos(self.ee_site_name)
        object_pos = self.sim.data.get_site_xpos("object0")
        target_pos = self.sim.data.get_site_xpos("target0")

        gripper_object_dist = goal_distance(gripper_pos, object_pos)
        object_target_dist = goal_distance(object_pos, target_pos)

        is_success = 1.0 if self._is_success(object_pos, target_pos) else 0.0

        reach_reward = 1 - np.tanh(10 * gripper_object_dist)

        is_grasp = self._check_grasp(
            self.robots[0]._grippers["left_arm_gripper"], self.object_geom
        )

        grasp_reward = 1.0 if is_grasp else 0.0

        lift_reward = (1 - np.tanh(10 * object_target_dist)) * is_grasp

        place_reward = 1.0 if is_success else 0.0

        raw_reward = {
            "timestep": 1.0,
            "reach": reach_reward,
            "grasp": grasp_reward,
            "lift": lift_reward,
            "place": place_reward,
        }
        return raw_reward

    def _sample_goal(self):
        """Sample a new goal position and orientation.

        Returns:
            np.array: (goal_pos) where goal_pos is the position
        """
        object_xpos = self.sim.data.get_site_xpos("object0")
        goal_pos = np.array([0.75, 0, 0.68])
        goal_pos[2] = object_xpos[2] + self.np_random.uniform(0, 0.3)
        while np.linalg.norm(goal_pos[:2] - object_xpos[:2]) < 0.2:
            goal_pos[0] += self.np_random.uniform(-0.05, 0.25)
            goal_pos[1] += self.np_random.uniform(-0.25, 0.25)
        return goal_pos.copy()

    def _is_success(self, achieved_goal, desired_goal, distance_threshold=0.05):
        """Check if the achieved goal is close enough to the desired goal.

        Args:
            achieved_goal (np.ndarray): The achieved goal position
            desired_goal (np.ndarray): The desired goal position

        Returns:
            float: 1.0 if successful, 0.0 otherwise
        """
        d = goal_distance(achieved_goal, desired_goal)
        return bool(d < distance_threshold)

    def _sample_object(self):
        """Sample a new initial position for the object.

        Returns:
            bool: True if successful
        """
        object_xpos = self.sim.data.get_site_xpos("object0")
        object_x = object_xpos[0] + self.np_random.uniform(-0.1, 0.35)
        object_y = object_xpos[1] + self.np_random.uniform(-0.2, 0.2)
        object_xpos[:2] = np.array([object_x, object_y])
        object_qpos = self.sim.data.get_joint_qpos("object0:joint")
        assert object_qpos.shape == (7,)
        object_qpos[:2] = object_xpos[:2]
        self.sim.data.set_joint_qpos("object0:joint", object_qpos)
        self.sim.forward()
        return True

    def _check_grasp(self, gripper, object_geoms):
        """
        Checks whether the specified gripper as defined by @gripper is grasping the specified object in the environment.
        If multiple grippers are specified, will return True if at least one gripper is grasping the object.

        By default, this will return True if at least one geom in both the "left_fingerpad" and "right_fingerpad" geom
        groups are in contact with any geom specified by @object_geoms. Custom gripper geom groups can be
        specified with @gripper as well.

        Args:
            gripper (GripperModel or str or list of str or list of list of str or dict): If a MujocoModel, this is specific
                gripper to check for grasping (as defined by "left_fingerpad" and "right_fingerpad" geom groups). Otherwise,
                this sets custom gripper geom groups which together define a grasp. This can be a string
                (one group of single gripper geom), a list of string (multiple groups of single gripper geoms) or a
                list of list of string (multiple groups of multiple gripper geoms), or a dictionary in the case
                where the robot has multiple arms/grippers. At least one geom from each group must be in contact
                with any geom in @object_geoms for this method to return True.
            object_geoms (str or list of str or MujocoModel): If a MujocoModel is inputted, will check for any
                collisions with the model's contact_geoms. Otherwise, this should be specific geom name(s) composing
                the object to check for contact.

        Returns:
            bool: True if the gripper is grasping the given object
        """
        # Convert object, gripper geoms into standardized form
        o_geoms = [object_geoms] if type(object_geoms) is str else object_geoms

        if isinstance(gripper, GripperPart_v1):
            g_geoms = [
                gripper.important_geoms["left_fingerpad"],
                gripper.important_geoms["right_fingerpad"],
            ]
        elif type(gripper) is str:
            g_geoms = [[gripper]]
        elif isinstance(gripper, dict):
            assert all([isinstance(gripper[arm], GripperPart_v1) for arm in gripper]), (
                "Invalid gripper dict format!"
            )
            return any(
                [self._check_grasp(gripper[arm], object_geoms) for arm in gripper]
            )
        else:
            # Parse each element in the gripper_geoms list accordingly
            g_geoms = [
                [g_group] if type(g_group) is str else g_group for g_group in gripper
            ]

        # Search for collisions between each gripper geom group and the object geoms group
        for g_group in g_geoms:
            if not self.check_contact(g_group, o_geoms):
                return False
        return True
