from typing import Callable, Iterable
import cooptools.geometry_utils.vector_utils as vec
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Waypoint:
    end_pos: vec.FloatVec
    is_destination: bool = True
    reservation_provider: Callable[[str, str], bool] = None
    path: Iterable[vec.FloatVec] = None
    id: str = None

    def reserved(self, agent_name: str):
        return self.reservation_provider(self.id, agent_name) if self.reservation_provider else True

    def __str__(self):
        return f"Seg -> wpid: {self.id}, ending at: {self.end_pos}. dest: {self.is_destination}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Waypoint):
            return False

        if self.end_pos == other.end_pos:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.end_pos)

