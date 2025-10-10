import cooptools.geometry_utils.vector_utils as vec
from cooptools.physics.movement import Velocity, Acceleration
from cooptools.transform import Transform
import logging
from typing import Iterable, List, Tuple
from cooptools.physics.kinematic import GoalSeeker
from cooptools.physics.waypoint import Waypoint

logger = logging.getLogger(__name__)


class WaypointFollower:
    def __init__(self,
                 name: str,
                 initial_transform: Transform,
                 max_acceleration: float,
                 initial_velocity: Velocity = None,
                 initial_acceleration: Acceleration = None,
                 initial_goal: vec.FloatVec = None,
                 history_len: int = None,
                 velocity_magnitude_bounds: Tuple[float, float] = None
                 ):
        self._goal_seeker = GoalSeeker(
            name=name,
            initial_transform=initial_transform,
            max_acceleration=max_acceleration,
            initial_velocity=initial_velocity,
            initial_acceleration=initial_acceleration,
            initial_goal=initial_goal,
            history_len=history_len,
            velocity_magnitude_bounds=velocity_magnitude_bounds
        )

        self.waypoints: List[Waypoint] = []

    @property
    def Name(self) -> str:
        return self._goal_seeker.Name

    @property
    def Transform(self) -> Transform:
        return self._goal_seeker.Transform

    @property
    def Velocity(self) -> Velocity:
        return self._goal_seeker.Velocity

    @property
    def Acceleration(self) -> Acceleration:
        return self._goal_seeker.Acceleration

    def add_waypoints(self, waypoints: Iterable[Waypoint], index: int = -1):
        if index < 0 or index > len(self.waypoints):
            self.waypoints += waypoints
            logger.info(f"Appending waypoints to agent {self.Name}: {waypoints}")
        else:
            self.waypoints[index:index] = waypoints
            logger.info(f"Adding waypoints to agent {self.Name} at index [{index}]: {waypoints}")

    def get_next_waypoint(self) -> Waypoint:
        if len(self.waypoints) > 1:
            segment = self.waypoints[1]
            return segment
        else:
            return None

    def get_next_destination(self) -> Waypoint:
        if len(self.waypoints) > 1:
            destination = next(x for x in self.waypoints if x.is_destination)
            return destination
        else:
            return None

    def get_segments_to_next_destination(self):
        segments = []
        if len(self.waypoints) > 0:
            for x in self.waypoints:
                segments.append(x)
                if x.is_destination:
                    break

            return segments
        else:
            return None

    def length_remaining_for_agent(self):
        current_segment = self.waypoints[1]
        length_of_remaining_segments = vec.vector_len(vec.vector_between(self.Position.Vector, current_segment.end_pos))

        last = current_segment
        for ii in range(2, len(self.waypoints)):
            next = self.waypoints[ii]
            length = vec.vector_len(vec.vector_between(last.end_pos, next.end_pos))
            length_of_remaining_segments += length

        return length_of_remaining_segments

    def agent_last_pos(self):
        return self.waypoints[-1].end_pos if len(self.waypoints) > 0 else self.Position

    def update(self,
               delta_time_ms: int,
               new_waypoints: vec.IterVec = None,
               close_enough_tolerance: float = 0.001,
               slow_enough_tolerance: float = 0.001,
               stop_rotating_threshold: int = 10
               ) -> bool:
        if new_waypoints:
            self.add_waypoints(waypoints=new_waypoints)

        if len(self.waypoints) > 0:
            reached = self._goal_seeker.update(
                delta_time_ms=delta_time_ms,
                goal_pos=self.waypoints[0].end_pos,
                close_enough_tolerance=close_enough_tolerance,
                slow_enough_tolerance=slow_enough_tolerance,
                stop_rotating_threshold = stop_rotating_threshold
            )

            if reached:
                logger.info(f"\'{self.Name}\' reached waypoint {self.waypoints[0].end_pos}")
                self.waypoints.pop(0)

            return reached
    def stop(self):
        self._goal_seeker.stop()
if __name__ == "__main__":
    from cooptools.timeTracker.timeTracker import TimeTracker
    import logging
    from cooptools.loggingHelpers import BASE_LOG_FORMAT

    logging.basicConfig(level=logging.INFO, format=BASE_LOG_FORMAT)
    logging.getLogger('cooptools.physics.kinematic').setLevel(logging.WARN)
    import random as rnd


    def test_1():
        wf = WaypointFollower(
            name='Coop',
            initial_transform=Transform(
                translation=(0, 0)),
            max_acceleration=5
        )

        tt = TimeTracker()
        printtt = TimeTracker()
        goal = (0, 100)
        wf.add_waypoints(waypoints=[
            Waypoint(
                end_pos=goal,
                is_destination=True
            )
        ])

        rnd.seed(0)
        while True:
            reached = wf.update(delta_time_ms=tt.Delta_MS)
            # logger.info(f"{wf.Transform.Translation} -- {wf.Velocity} -- {wf.Acceleration}")
            # tt.update(delta_ms=1)
            tt.update()
            printtt.update()
            if printtt.AccumulatedS > 5:
                logger.info(f"{wf.Transform.Translation} -- {wf.Velocity} -- {wf.Acceleration}")
                printtt =  TimeTracker()

            if reached:
                wf.add_waypoints(waypoints=[
                    Waypoint(
                        end_pos=(rnd.randint(0, 100), rnd.randint(0, 100))
                    )
                ])


    test_1()