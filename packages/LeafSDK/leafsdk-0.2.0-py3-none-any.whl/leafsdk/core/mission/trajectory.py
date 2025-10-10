import json
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any, Union, TypeAlias, Sequence
import numpy as np
from leafsdk.core.utils.transform import gps_to_relative_3d, wrap_to_pi, deg2rad
from leafsdk import logger


@dataclass
class Trajectory:
    """
    Represents a generic trajectory segment with polynomial coefficients,
    time scaling, spatial scaling, and rotation metadata.

    Attributes
    ----------
    poly_coeff : np.ndarray
        Polynomial coefficient matrix (3 × N).
    time_scale : float
        Segment total time scaling factor.
    spatial_scale : List[float]
        Spatial scaling factors [sx, sy, sz].
    rotation_axis : List[float]
        Axis of rotation applied to the trajectory.
    rotation_angle : float
        Rotation angle in radians about the rotation axis.
    """
    poly_coeff: np.ndarray
    time_scale: float
    spatial_scale: List[float]
    rotation_axis: List[float]
    rotation_angle: float
    base_time: float = 1.0  # Default base time for position trajectories


class WaypointTrajectory:
    """
    Generate position and yaw trajectories from waypoints and yaw commands.

    Supports two-point canonical trajectories. Multi-point cubic splines
    are not yet implemented.
    """

    EPS = 1e-9
    DEFAULT_YAW_BASE_TIME = 5.0

    def __init__(
        self,
        waypoints: Sequence[Tuple[float, float, float]],
        yaws_deg: Sequence[float],
        speed: Sequence[float],
        yaw_speed: Sequence[float],
        home: Tuple[float, float, float],
        home_yaw: float,
        cartesian: bool,
    ):
        """
        Initialize a WaypointTrajectory.

        Parameters
        ----------
        waypoints : Sequence[Tuple[float, float, float]]
            List of waypoints as (lat, lon, alt) or (x, y, z).
        yaws_deg : Sequence[float]
            List of yaw commands in degrees at each waypoint.
        speed : Sequence[float]
            List of speeds (m/s) for each segment.
        yaw_speed : Sequence[float]
            List of yaw speeds (deg/s) for each segment.
        home : tuple
            Home position reference (lat, lon, alt) or (x, y, z).
        home_yaw : float
            Home yaw reference in radians.
        cartesian : bool
            If True, interpret waypoints as Cartesian; otherwise GPS.
        """
        self.home = home
        self.home_yaw = home_yaw
        self.raw_waypoints = waypoints
        self.cartesian = cartesian
        self.yaws_deg = yaws_deg
        self.speed = speed
        self.yaw_speed = deg2rad(yaw_speed)

        assert len(self.raw_waypoints) == len(self.yaws_deg), "WaypointTrajectory: Waypoints and yaws must have the same length"
        assert len(self.raw_waypoints) == len(self.speed), "WaypointTrajectory: Waypoints and speed must have the same length"
        assert len(self.raw_waypoints) == len(self.yaw_speed), "WaypointTrajectory: Waypoints and yaw_speed must have the same length"

        # Convert to numpy arrays and compute relative waypoints and yaws
        self.relative_yaws = self._convert_yaw_to_relative()
        self.relative_points = (
            self._convert_cartesian_to_relative()
            if cartesian
            else self._convert_gps_to_relative()
        )

        # Generate trajectory primitives
        self.pos_traj = self._generate_traj_primitive_pos()
        self.yaw_traj = self._generate_traj_primitive_yaw()

    def _convert_gps_to_relative(self) -> np.ndarray:
        """
        Convert raw GPS waypoints to relative 3D positions from the home position.

        Returns
        -------
        np.ndarray
            Array of relative coordinates.
        """
        self.home = np.asarray(self.home).reshape(1,3)
        self.raw_waypoints = np.asarray(self.raw_waypoints)
        # Compute positions in cartesian frame relative to home position in LLA frame
        relative_points = np.asarray(
            [gps_to_relative_3d(*self.home, *wp) for wp in self.raw_waypoints]
        )
        relative_home = np.zeros((1, 3))
        relative_points = np.diff(
            np.vstack((relative_home, relative_points)),
            axis=0,  # row-wise differences
            prepend=relative_home
        )

        return relative_points

    def _convert_cartesian_to_relative(self) -> np.ndarray:
        """
        Convert raw Cartesian waypoints to relative positions from the home position.

        Returns
        -------
        np.ndarray
            Array of relative coordinates.
        """
        self.home = np.asarray(self.home).reshape(1,3)
        self.raw_waypoints = np.asarray(self.raw_waypoints)
        relative_points = np.diff(
            np.vstack((self.home, self.raw_waypoints)),
            axis=0,  # row-wise differences
            prepend=self.home
        )

        return relative_points

    def _convert_yaw_to_relative(self) -> np.ndarray:
        """
        Convert raw yaw commands in degrees to relative yaw values in radians,
        normalized to the range [-pi, pi].

        Returns
        -------
        np.ndarray
            Array of relative yaw values in radians.
        """
        self.home_yaw = np.asarray(wrap_to_pi(self.home_yaw))
        yaws_rad = wrap_to_pi(deg2rad(np.asarray(self.yaws_deg)))
        relative_yaws = wrap_to_pi(np.diff(np.append(self.home_yaw, yaws_rad), prepend=self.home_yaw))

        return relative_yaws

    def _canonical_timescale_coeffs(self, m: int) -> np.ndarray:
        """
        Generate canonical time-scaling coefficients for polynomial s(u) on [0,1].

        Parameters
        ----------
        m : int
            Highest derivative order (>=1) constrained to zero at both endpoints.

        Returns
        -------
        np.ndarray
            Polynomial coefficient array of shape (3, n+1).
        """
        if m < 1:
            raise ValueError("m must be >= 1")
        n = 2 * m + 1
        coeffs = np.zeros((3, n + 1), dtype=float)
        from math import comb

        for k in range(m + 1):
            coeffs[0, m + 1 + k] = ((-1) ** k) * comb(m + k, k) * comb(2 * m + 1, m - k)
        return coeffs

    def _generate_traj_primitive_pos(self) -> List[Trajectory]:
        """
        Generate trajectory primitives for position given relative waypoints.

        Returns
        -------
        List[Trajectory]
            List of trajectory segments, one per consecutive waypoint pair.

        Raises
        ------
        ValueError
            If no relative points are available.
        RuntimeError
            If the trajectory origin is not zero.
        """
        if self.relative_points is None or len(self.relative_points) == 0:
            raise ValueError("No relative points available for position trajectory.")

        pts = np.asarray(self.relative_points, dtype=float)

        if not np.allclose(pts[0], np.zeros((1, 3))):
            raise RuntimeError("Position trajectory origin is not (0, 0, 0)!")

        trajectories: List[Trajectory] = []

        for i in range(len(pts) - 1):
            dp = pts[i + 1]
            seg_len_scalar = np.linalg.norm(dp)

            spatial_scale = [seg_len_scalar] * 3
            poly_coeffs = self._canonical_timescale_coeffs(m=4)

            if seg_len_scalar < self.EPS:
                logger.warning(
                    f"Waypoint {i} and {i+1} coincide; skipping static trajectory."
                )
                trajectories.append(None)
                continue
            
            # Time scale based on segment length and speed
            time_scale = seg_len_scalar / self.speed[i]
            reference_dir = np.array([1.0, 0.0, 0.0])
            dp_normalized = dp / seg_len_scalar

            rotation_axis_vec = np.cross(reference_dir, dp_normalized)
            axis_magnitude = np.linalg.norm(rotation_axis_vec)

            if axis_magnitude > self.EPS:
                rotation_axis = (rotation_axis_vec / axis_magnitude).tolist()
                cos_angle = np.clip(np.dot(reference_dir, dp_normalized), -1.0, 1.0)
                rotation_angle = np.arccos(cos_angle)
            else:
                if np.dot(reference_dir, dp_normalized) > 0:
                    rotation_axis = [0.0, 0.0, 1.0]
                    rotation_angle = 0.0
                else:
                    rotation_axis = [0.0, 0.0, 1.0]
                    rotation_angle = np.pi

            trajectories.append(
                Trajectory(
                    poly_coeff=poly_coeffs,
                    time_scale=time_scale,
                    spatial_scale=spatial_scale,
                    rotation_axis=rotation_axis,
                    rotation_angle=rotation_angle,
                )
            )

        return trajectories

    def _generate_traj_primitive_yaw(self) -> List[Trajectory]:
        """
        Generate trajectory primitives for yaw given relative yaw commands.

        Parameters
        ----------
        traj_time : float, optional
            Time scale of the associated position trajectory. If None, default = 1.0.

        Returns
        -------
        List[YawTrajectory]
            List of yaw trajectory segments.

        Raises
        ------
        ValueError
            If no relative yaws are available.
        RuntimeError
            If the yaw trajectory origin is not zero.
        """
        if self.relative_yaws is None or len(self.relative_yaws) == 0:
            raise ValueError("No yaw waypoints available for yaw trajectory.")

        yaw_pts = np.asarray(self.relative_yaws, dtype=float)

        if not np.allclose(yaw_pts[0], np.zeros((1,))):
            raise RuntimeError("Yaw trajectory origin is not (0, 0, 0)!")

        yaw_trajectories: List[Trajectory] = []
        yaw_base_time = self.DEFAULT_YAW_BASE_TIME
        yaw_poly_coeffs = np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.04032, -0.02688, 0.006912, -0.0008064, 0.00003584],
                [0.0] * 10,
                [0.0] * 10,
            ]
        )

        for i in range(len(yaw_pts) - 1):
            target_yaw = yaw_pts[i + 1]

            if abs(target_yaw) < self.EPS:
                logger.warning(f"Yaw {i} and {i+1} coincide; skipping static yaw trajectory.")
                yaw_trajectories.append(None)
                continue

            yaw_time_scale = abs(target_yaw) / self.yaw_speed[i] / yaw_base_time

            yaw_trajectories.append(
                Trajectory(
                    poly_coeff=yaw_poly_coeffs,
                    time_scale=yaw_time_scale,
                    spatial_scale=[target_yaw, 0.0, 0.0],
                    rotation_axis=[0.0, 1.0, 0.0],
                    rotation_angle=-np.pi / 2,
                    base_time=yaw_base_time,
                )
            )

        return yaw_trajectories

    def build_pos_polynomial_trajectory_json(self, trajectory_id: str) -> Tuple[List[str], List[Optional[str]]]:
        """
        Build JSON representations of the polynomial trajectory using position trajectory parameters.

        Parameters
        ----------
        trajectory_id : str
            Identifier for the trajectory.

        Returns
        -------
        Tuple[List[str], List[str or None]]
            List of trajectory segment IDs and their corresponding JSON strings,
            or None if segment length is infinitesimally small.
        """

        traj_ids, traj_json_segs = [], []
        for idx, seg in enumerate(self.pos_traj):
            seg_id = f"{trajectory_id}_pos_seg{idx}"
            if seg is not None:
                traj_json = self._build_polynomial_trajectory_json(
                        poly_coeff=seg.poly_coeff,
                        time_scale=seg.time_scale,
                        trajectory_id=seg_id,
                        rotation_axis=seg.rotation_axis,
                        spatial_scale=seg.spatial_scale,
                        rotation_angle=seg.rotation_angle,
                    )
            else:
                traj_json = None

            traj_ids.append(seg_id)
            traj_json_segs.append(traj_json)

        return traj_ids, traj_json_segs
    
    def build_yaw_polynomial_trajectory_json(self, trajectory_id: str) -> Tuple[List[str], List[Optional[str]]]:
        """
        Build JSON representations of the yaw polynomial trajectory.

        Parameters
        ----------
        trajectory_id : str
            Identifier for the trajectory.

        Returns
        -------
        Tuple[List[str], List[str or None]]
            List of trajectory segment IDs and their corresponding JSON strings,
            or None if segment length is infinitesimally small.
        """

        traj_ids, traj_json_segs = [], []
        for idx, seg in enumerate(self.yaw_traj):
            seg_id = f"{trajectory_id}_yaw_seg{idx}"
            if seg is not None:
                traj_json = self._build_polynomial_trajectory_json(
                        poly_coeff=seg.poly_coeff,
                        time_scale=seg.time_scale,
                        trajectory_id=seg_id,
                        base_time=seg.base_time,
                        rotation_axis=seg.rotation_axis,
                        spatial_scale=seg.spatial_scale,
                        rotation_angle=seg.rotation_angle,
                    )
            else:
                traj_json = None

            traj_ids.append(seg_id)
            traj_json_segs.append(traj_json)

        return traj_ids, traj_json_segs

    def _build_polynomial_trajectory_json(
        self,
        poly_coeff: np.ndarray,
        time_scale: float,
        trajectory_id: str,
        base_time: float = 1.0,
        rotation_axis: List[float] = (1, 0, 0),
        spatial_scale: List[float] = (1, 1, 1),
        trajectory_type: str = "PolynomialTrajectory",
        rotation_angle: float = 0.0,
    ) -> str:
        """
        Build a dictionary and JSON string representing a polynomial trajectory.

        Parameters
        ----------
        poly_coeff : np.ndarray
            Polynomial coefficients (3 × N).
        time_scale : float
            Segment total time scaling factor.
        trajectory_id : str
            Identifier for the trajectory.
        base_time : float, optional
            Base segment duration (default = 1.0).
        rotation_axis : list of float, optional
            Axis of rotation (default = [1, 0, 0]).
        spatial_scale : list of float, optional
            Spatial scaling factors (default = [1, 1, 1]).
        trajectory_type : str, optional
            Trajectory type string (default = "PolynomialTrajectory").
        rotation_angle : float, optional
            Rotation angle in radians (default = 0.0).

        Returns
        -------
        tuple
            (Dictionary with trajectory data, pretty-formatted JSON string).

        Raises
        ------
        ValueError
            If parameters are invalid or inconsistent.
        """
        if base_time <= 0:
            raise ValueError("base_time must be > 0")
        if time_scale <= 0:
            raise ValueError("time_scale must be > 0")
        if len(rotation_axis) != 3:
            raise ValueError("rotation_axis must have length 3")
        if len(spatial_scale) != 3:
            raise ValueError("spatial_scale must have length 3")

        poly_matrix = [list(reversed(row)) for row in poly_coeff]
        if len(poly_matrix) != 3:
            raise ValueError("poly_coeff must have 3 rows")

        n_cols = len(poly_matrix[0])
        for row in poly_matrix[1:]:
            if len(row) != n_cols:
                raise ValueError("All poly_coeff rows must have equal length")

        data = {
            "base_time": float(base_time),
            "rotation_axis": list(rotation_axis),
            "poly_coeff": poly_matrix,
            "spatial_scale": list(spatial_scale),
            "trajectory_id": trajectory_id,
            "trajectory_type": trajectory_type,
            "time_scale": float(time_scale),
            "rotation_angle": float(rotation_angle),
        }

        return json.dumps(data, indent=4)
