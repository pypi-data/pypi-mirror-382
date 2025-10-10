from cooptools.sectors import RectGrid
from cooptools.geometry_utils import rect_utils as rect
from cooptools.geometry_utils import polygon_utils as poly
from cooptools.geometry_utils import vector_utils as vec
from typing import Dict, Any, Tuple, List, Callable, Iterable
import cooptools.sectors.sect_utils as sec_u
from cooptools.coopEnum import CardinalPosition
import logging
import matplotlib.patches as patches
from cooptools.colors import Color
from cooptools.plotting import plot_series
from cooptools.protocols import UniqueIdentifier
from cooptools.geometry_utils import rect_utils as rect
from cooptools import common as comm

logger = logging.getLogger(__name__)

ObjInSectorComparer = Callable[[rect.Rect, UniqueIdentifier], bool]


class SectorTree:
    def __init__(self,
                 area_rect: rect.Rect,
                 capacity: int,
                 shape: Tuple[int, int],
                 obj_collider_provider: Callable[[UniqueIdentifier], vec.IterVec],
                 sector_comparer: ObjInSectorComparer = None,
                 parent=None,
                 lvl: int = None,
                 max_lvls: int = None):
        self.parent = parent
        self.children: Dict[Tuple[int, int], SectorTree] = {}
        self.capacity = capacity
        self.grid = RectGrid(shape[0], shape[1])
        self._area = area_rect
        self._client_mapping = {}
        self._last_mapped_pos = {}
        self.lvl = lvl if lvl else 0
        self.max_lvls = max_lvls
        self._object_collider_provider = obj_collider_provider

        comm.verify_val(val=self.capacity, gt=0, error_msg=f"Invalid value for capacity: {self.capacity}")


        lam_default_poly_in_sector_comparer = lambda x, to_check: poly.do_convex_polygons_intersect(
            list(rect.rect_corners(x).values()),
            self._object_collider_provider(to_check))
        self._obj_in_sector_comparer = sector_comparer or lam_default_poly_in_sector_comparer

    def _obj_in_sector(self, sector, id):
        obj_points = self._object_collider_provider(id)

        if len(obj_points) == 1:
            return rect.rect_contains_point(sector, obj_points[0])
        elif len(obj_points) > 1:
            return poly.do_convex_polygons_intersect(
                list(rect.rect_corners(sector).values()),
                obj_points)
        else:
            raise ValueError(f"object needs at least one point")


    def __str__(self):
        return f"{self.DeepMappings}, \n{self.children}"

    def _add_child_layer(self, grid_pos: Tuple[int, int]):
        child_rect = sec_u.sector_rect(
            sector_dims=sec_u.sector_dims(area_dims=(self._area[2], self._area[3]),
                                          sector_def=self.grid.Shape
                                          ),
            sector=grid_pos,
            area_origin=(self._area[0], self._area[1])
        )

        # add a new SectorTree as a child to the grid pos
        self.children[grid_pos] = SectorTree(area_rect=child_rect,
                                             capacity=self.capacity,
                                             obj_collider_provider=self._object_collider_provider,
                                             sector_comparer=self._obj_in_sector_comparer,
                                             shape=self.grid.Shape,
                                             parent=self,
                                             lvl=self.lvl + 1,
                                             max_lvls=self.max_lvls)

        # update clients in child at grid pos. This should happen whenever you add a child. it should iterate the
        # clients at the grid pos and add them to the child layer appropriately
        clients = self._client_mapping.get(grid_pos, None)
        self.children[grid_pos].add_update_clients(clients)

        logger.info(f"child layer added at Lvl {self.lvl}: {grid_pos} with area rect: {child_rect}")

    def _handle_child_layer(self, grid_pos: Tuple[int, int]):

        # capacity has not been reached (mult clients at shared pos are treated as 1). Therefore, we choose not
        # to add a child (or handle). We can return early bc there is not a reason to handle children in this case.
        # Additionally, we do not want to continue if we have reached our max-level depth
        clients = self.ClientMappings.get(grid_pos, None)

        if clients is None \
                or len(clients) <= self.capacity \
                or (self.max_lvls is not None and self.lvl >= self.max_lvls - 1) \
                or self.children.get(grid_pos, None) is not None:
            return False

        # there is no child but capacity is reached. we need to add a child layer to the tree
        if self.children.get(grid_pos, None) is None and len(clients) > self.capacity:
            self._add_child_layer(grid_pos)
            return True

        raise ValueError(f"Coding error... Outside the expected two conditions")

    def add_update_clients(self, clients: Iterable):

        areas = {
            grid_pos:
            sec_u.sector_rect(sector_dims=sec_u.sector_dims(self._area[2:4],
                                                            sector_def=self.grid.Shape),
                              sector=grid_pos,
                              area_origin=self._area[0:2])
            for grid_pos, _ in self.grid.grid_enumerator
        }

        for client in clients:
            if self.lvl == 0:
                logger.info(f"User requests adding [{client}]")

                if not client.__hash__:
                    raise Exception(f"Client {client} must be hashable, but type {type(client)} is not")

            # check if can skip since already up to date
            # TODO: This was implemented w. pos, harder in abstract sense

            # check if already have client in but at a different location
            # TODO: This was implemented w. pos, harder in abstract sense

            # Check which grid_pos client belongs to
            for grid_pos, _ in self.grid.grid_enumerator:
                area = areas[grid_pos]

                # Check if the client is in the sector, and not in any other sectors (handling on-line case)
                if self._obj_in_sector(area, client) and not any(client in v for k, v in self._client_mapping.items()):
                    self._client_mapping.setdefault(grid_pos, set()).add(client)
                    logger.info(f"client [{client}] added to Lvl {self.lvl}: {grid_pos}")

                    # handle child lvl
                    layer_added = self._handle_child_layer(grid_pos)

                    if not layer_added and self.children.get(grid_pos, None) is not None:
                        self.children[grid_pos].add_update_clients([client])
        return self

    def remove_clients(self, clients: Iterable):
        for client in clients:
            # if not a member, early out
            if client not in self._last_mapped_pos.keys():
                return

            logger.info(f"removing client [{client}] from {self.lvl}: {self._last_mapped_pos[client]}")

            # delete from last mapped
            del self._last_mapped_pos[client]

            # delete from client mappings
            for grid_pos, clients in self._client_mapping.items():
                if client in clients:
                    clients.remove(client)

            # handle children
            to_remove = []
            for pos, child in self.children.items():
                # remove client from child
                child.remove_clients(client)

                # remove child if empty
                positions = set([pos for client, pos in child.ClientsPos.items()])
                if len(positions) <= self.capacity:
                    to_remove.append(pos)

            for child in to_remove:
                del self.children[child]
        return self

    def _sector_corners_nearby(self, radius: float, pt: Tuple[float, float]):
        ret = {}
        for pos, sector_rect in self.MySectors.items():
            corners = rect.rect_corners(sector_rect)

            tl = self._within_radius_of_point(corners[CardinalPosition.TOP_LEFT], radius=radius, pt=pt)
            tr = self._within_radius_of_point(corners[CardinalPosition.TOP_RIGHT], radius, pt)
            bl = self._within_radius_of_point(corners[CardinalPosition.BOTTOM_LEFT], radius, pt)
            br = self._within_radius_of_point(corners[CardinalPosition.BOTTOM_RIGHT], radius, pt)
            ret[pos] = sum([tl, tr, bl, br])

        return ret

    def _within_radius_of_point(self, check: Tuple[float, float], radius: float, pt: Tuple[float, float]):
        return vec.distance_between(check, pt) <= radius

    def _sectors_potentially_overlaps_radius(self, radius: float, pt: Tuple[float, float]):
        ret = {}
        for pos, sector_area in self.MySectors.items():
            ret[pos] = False

            # determine if the bounding circle of my area plus the radius given to check is more than the distance
            # between the center of my area and the point to be checked. If the combined distance of the two radius's is
            # smaller than the distance between center and pt, we can safely assume that the area of the sector does NOT
            # intersect with the area being checked. However if it is larger, there is a potential that the area falls
            # within the checked area
            if rect.bounding_circle_radius(sector_area) + radius >= vec.distance_between(pt,
                                                                                         rect.rect_center(sector_area)):
                ret[pos] = True
        return ret

    @property
    def ClientMappings(self) -> Dict[Tuple[int, int], set[Any]]:
        return self._client_mapping

    @property
    def Clients(self) -> List[UniqueIdentifier]:
        return list(set(comm.flattened_list_of_lists(v for v in self.ClientMappings.values())))


    @property
    def DeepMappings(self) -> Dict[Tuple[int, int], set[Any]]:
        return {
            k: (list(v), self.children[k].Area, self.children[k].DeepMappings) if k in self.children else (list(v), {})
            for k, v in self.ClientMappings.items()
        }

    @property
    def JsonableDeepMappings(self) -> Dict[str, Dict]:
        return {
            str(k): (list(v), self.children[k].Area, self.children[k].JsonableDeepMappings) if k in self.children else (
            list(v), {})
            for k, v in self.ClientMappings.items()
        }

    @property
    def MySectors(self) -> Dict[Tuple[float, float], rect.Rect]:
        mine = {}
        sec_def = sec_u.rect_sector_attributes((self._area[2], self._area[3]), self.grid.Shape)
        for pos, _ in self.grid.grid_enumerator:
            _rect = (
                pos[0] * sec_def[0] + self._area[0],
                pos[1] * sec_def[1] + self._area[1],
                sec_def[0],
                sec_def[1]
            )

            mine[pos] = _rect

        return mine

    @property
    def Sectors(self) -> Dict[Tuple[float, float], rect.Rect]:
        childrens = {}
        for pos, child in self.children.items():
            childrens.update({f"{pos}/{k}": v for k, v in child.Sectors.items()})

        return {**self.MySectors, **childrens}

    @property
    def Area(self) -> rect.Rect:
        return self._area

    def plot(self,
             ax,
             fig,
             nearby_pt: Tuple[float, float] = None,
             radius: float = None,
             pt_color: Color = None):

        plot_series([point for client, point in self.ClientsPos.items()],
                    ax=ax,
                    color=pt_color,
                    fig=fig,
                    series_type='scatter',
                    zOrder=4)

        if nearby_pt is not None and radius is not None:
            nearbys = self.nearby_clients(pt=nearby_pt, radius=radius)
            # near_x_s = [point[0] for client, point in nearbys.items()]
            # near_y_s = [point[1] for client, point in nearbys.items()]
            plot_series([point for client, point in nearbys.items()], ax=ax, color=pt_color,
                        series_type='scatter', zOrder=4)
            # ax.scatter(near_x_s, near_y_s,)

        for _, sector in self.Sectors.items():
            rect = patches.Rectangle((sector[0], sector[1]), sector[2], sector[3], linewidth=1, edgecolor='r',
                                     facecolor='none')
            ax.add_patch(rect, )

    @property
    def ClientsPos(self) -> Dict[Any, Tuple[float, float]]:
        return self._last_mapped_pos

    @property
    def CoLocatedClients(self) -> Dict:
        ret = {}

        for grid_pos, clients in self.ClientMappings.items():
            gpcc = None

            for client in clients:
                ret.setdefault(client, set())


                if grid_pos in self.children:
                    if gpcc is None:
                        gpcc = self.children[grid_pos].CoLocatedClients

                    ret[client] = ret[client].union(gpcc[client])

                else:
                    ret[client] = ret[client].union(set([x for x in clients if x != client]))
        return ret


if __name__ == "__main__":
    from cooptools.randoms import a_string
    import random as rnd
    import matplotlib.pyplot as plt
    import time
    from pprint import pprint
    from cooptools.common import flattened_list_of_lists
    from cooptools.loggingHelpers import BASE_LOG_FORMAT

    logging.basicConfig(format=BASE_LOG_FORMAT, level=logging.INFO)

    rnd.seed(0)


    def assemble(shape: Tuple = (2, 2),
                 area: Tuple = (0, 0, 400, 400)):
        _rect = area

        obj_areas = {
            "1": list(rect.rect_corners((100, 100, 99, 10)).values()),
            "2": list(rect.rect_corners((100, 100, 10, 99)).values()),
            "3": list(rect.rect_corners((150, 150, 100, 100)).values()),
        }

        qt = SectorTree(area_rect=_rect,
                        shape=shape,
                        # sector_comparer=lambda x, id: poly.do_convex_polygons_intersect(x, obj_areas[id]),
                        obj_collider_provider=lambda x: obj_areas[x],
                        capacity=1,
                        max_lvls=3)

        qt.add_update_clients(clients=["1"])
        qt.add_update_clients(clients=["2"])
        qt.add_update_clients(clients=["3"])

        return qt

    def test_2x2_3clients():
        qt = assemble((2, 2))

        assert len(qt.Clients) == 3
        dms = qt.DeepMappings
        assert dms[(1, 1)][0] == ['3']
        assert dms[(1, 0)][0] == ['3']
        assert dms[(0, 1)][0] == ['3']

        l00 = dms[(0, 0)][2]
        assert len(l00) == 4
        assert set(l00[(0, 0)][0]) == set(['1', '2'])

        assert set(l00[(0, 1)][0]) == set(['1', '2'])
        assert set(l00[(1, 0)][0]) == set(['1', '2'])
        assert set(l00[(1, 1)][0]) == set(['1', '2', '3'])

        l00_00 = l00[(0, 0)]
        l00_01 = l00[(0, 1)]
        l00_10 = l00[(1, 0)]
        l00_11 = l00[(1, 1)]

        assert set(l00_00[2][(1, 1)][0]) == set(['1', '2'])
        assert set(l00_01[2][(1, 0)][0]) == set(['1', '2'])
        assert set(l00_01[2][(1, 1)][0]) == set(['2'])
        assert set(l00_10[2][(0, 1)][0]) == set(['1', '2'])
        assert set(l00_10[2][(1, 1)][0]) == set(['1'])
        assert set(l00_11[2][(0, 0)][0]) == set(['1', '2', '3'])
        assert set(l00_11[2][(0, 1)][0]) == set(['2', '3'])
        assert set(l00_11[2][(1, 0)][0]) == set(['1', '3'])
        assert set(l00_11[2][(1, 1)][0]) == set(['3'])

    def test_3x3_3clients():
        qt = assemble((3, 3),
                      area=(0, 0, 200, 200))

        dms = qt.DeepMappings


        assert (0, 0) not in dms.keys()
        assert (0, 1) not in dms.keys()
        assert (1, 0) not in dms.keys()

        l11 = dms[(1, 1)]
        l12 = dms[(1, 2)]
        l21 = dms[(2, 1)]
        l22 = dms[(2, 2)]
        assert set(l11[0]) == set(['1', '2'])

        assert (0, 0) not in l11[2].keys()
        assert (0, 1) not in l11[2].keys()
        assert (1, 0) not in l11[2].keys()
        assert (2, 0) not in l11[2].keys()
        assert (0, 2) not in l11[2].keys()

        l11_11 = l11[2][(1, 1)]
        l11_12 = l11[2][(1, 2)]
        l11_21 = l11[2][(2, 1)]

        assert set(l11_11[0]) == set(['1', '2'])
        assert set(l11_12[0]) == set(['2'])
        assert set(l11_21[0]) == set(['1'])

        l11_11_11 = l11_11[2][(1, 1)]
        l11_11_12 = l11_11[2][(1, 2)]
        l11_11_21 = l11_11[2][(2, 1)]
        l11_11_22 = l11_11[2][(2, 2)]

        assert set(l11_11_11[0]) == set(['1', '2'])
        assert set(l11_11_12[0]) == set(['1', '2'])
        assert set(l11_11_21[0]) == set(['1', '2'])
        assert set(l11_11_22[0]) == set(['1', '2'])

        assert set(l12[0]) == set(['2'])
        assert set(l21[0]) == set(['1'])
        assert set(l22[0]) == set(['3'])

        # pprint(dms)

        clc = qt.CoLocatedClients

        assert clc['1'] == set(['2'])
        assert clc['2'] == set(['1'])
        assert clc['3'] == set()
        # pprint(clc)




    def test2():
        _rect = (0, 0, 400, 400)
        t0 = time.perf_counter()

        obj_areas = {
            ii: list(rect.rect_corners(rect.rect_gen(_rect, max_w=100, max_h=100)).values()) for ii in range(10)
        }
        sc = lambda x, to_check: poly.do_convex_polygons_intersect(list(rect.rect_corners(x).values()),
                                                                   obj_areas[to_check])
        qt = SectorTree(area_rect=_rect,
                        # sector_comparer=sc,
                        obj_collider_provider=lambda id: obj_areas[id],
                        shape=(3, 3),
                        capacity=1,
                        max_lvls=2).add_update_clients(
            [ii for ii, check in obj_areas.items()]
        )

        dm = qt.DeepMappings
        pprint(dm)

        pprint(qt.CoLocatedClients)
        # for pos, mappings in dm.items():
        #     mine, subs = mappings
        #     all_subbd = flattened_list_of_lists([v[0] for k, v in subs.items()], unique=True)
        #
        #     if any(x not in all_subbd for x in mine):
        #         raise ValueError(f"Missing sUBS!")


    # test_2x2_3clients()
    # test_3x3_3clients()
    test2()
