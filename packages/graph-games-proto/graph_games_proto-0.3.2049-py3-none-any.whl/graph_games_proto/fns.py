import logging
import random
from uuid import uuid4
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, List, Optional, Set, TypeVar, Generic, Union
from uuid import UUID
import json
from multipledispatch import dispatch
from functools import reduce
from pyrsistent import PClass, field
from pyrsistent import v, pvector, PVector
import numpy as np
from functools import cmp_to_key
from itertools import combinations as itertools_combinations, chain
from collections import deque

DEFAULT_ALLOTTED_SECONDS = 12
INITIAL_ALLOTTED_SECONDS = 22

class NoAction(PClass):
    pass

class RouteDiscardAction(PClass):
    pass

class DrawUnitDeckAction(PClass):
    pass

class DrawUnitFaceupAction(PClass):
    pass

class ClaimPointAction(PClass):
    pass

class MovePiecesToPathAction(PClass):
    pass


class TrueType(PClass):
    pass

class FalseType(PClass):
    pass


def generate_uuid_with_rng(rng):
    # uuid4 uses 128 bits, but we need 16 bytes (128 bits) for the UUID
    # Generate 16 random bytes using the seeded rng
    random_bytes = bytes(rng.getrandbits(8) for _ in range(16))
    # Create a UUID from the random bytes
    return UUID(bytes=random_bytes, version=4)


def getbooltype(bool):
    if bool:
        return TrueType()
    return FalseType()


class FrozenLenScore(PClass):
    length = field(type=int)
    score = field(type=int)
    def __todict__(self):
        return {
            "len": self.length,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenLenScore(
            length=d["len"],
            score=d["score"]
        )


class Hook(PClass):
    uuid = field(type=str)
    name = field(type=str)
    when = field(type=str)
    code = field(type=str)
    def __todict__(self):
        return {
            "uuid": str(self.uuid),
            "name": self.name,
            "when": self.when,
            "code": self.code,
        }
    @staticmethod
    def __fromdict__(d):
        return Hook(
            uuid=str(d["uuid"]),
            name=d["name"],
            when=d["when"],
            code=d["code"],
        )


class FrozenLink2(PClass):
    num = field(type=int)
    uuid = field(type=str)
    c1 = field(type=str)
    c2 = field(type=str)
    length = field(type=int)
    width = field(type=int)
    special1 = field(type=bool)
    special2 = field(type=bool)
    score = field(type=int)  # Default score to 0
    def __todict__(self):
        return {
            "num": self.num,
            "uuid": str(self.uuid),
            "c1": str(self.c1),
            "c2": str(self.c2),
            "length": self.length,
            "width": self.width,
            "special1": self.special1,
            "special2": self.special2,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenLink2(
            num=d["num"],
            uuid=str(d["uuid"]),
            c1=str(d["c1"]),
            c2=str(d["c2"]),
            length=d["length"],
            width=d["width"],
            special1=d["special1"],
            special2=d["special2"],
            score=d["score"],
        )


# Implementing the following Julia function:
# struct ScoreDiff
#     a::Int
#     b::Int
# end
class ScoreDiff(PClass):
    a = field(type=int)
    b = field(type=int)
    def __todict__(self):
        return {
            "a": self.a,
            "b": self.b,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreDiff(
            a=d["a"],
            b=d["b"]
        )


class RouteStatus(PClass):
    route_uuid = field(type=str)
    completed = field(type=bool)
    def __todict__(self):
        return {
            "route_uuid": self.route_uuid,
            "completed": self.completed,
        }
    @staticmethod
    def __fromdict__(d):
        return RouteStatus(
            route_uuid=d["route_uuid"],
            completed=d["completed"]
        )


# Implementing the following Julia function:
# struct QValueFormula
#     q_num::Union{Nothing,Int}
#     score_diff::ScoreDiff
#     function QValueFormula(formula)
#         new(formula.q_num, ScoreDiff(formula.score_diff...))
#     end
# end
class QValueFormula(PClass):
    q_num = field(type=(int, type(None)), initial=None)  # Union{Nothing,Int}
    score_diff = field(type=ScoreDiff)  # ScoreDiff
    def __todict__(self):
        return {
            "q_num": self.q_num,
            "score_diff": self.score_diff.__todict__()
        }
    @staticmethod
    def __fromdict__(d):
        return QValueFormula(
            q_num=d.get("q_num"),
            score_diff=ScoreDiff.__fromdict__(d["score_diff"])
        )


# Implementing the following Julia function:
# struct QValueTrajectories
#     scores::Vector{Vector{Int}}
#     q_values::Vector{Int}
#     formulas::Vector{QValueFormula}
#     states::Vector{State}
#     actions::Vector{Action}
# end
class QValueTrajectories(PClass):
    scores = field(type=list)  # List[List[int]]
    q_values = field(type=list)  # List[int]
    formulas = field(type=list)  # List[QValueFormula]
    states_no_terminal = field(type=list)  # List[State]
    actions = field(type=list)  # List[Action]
    def __todict__(self):
        return {
            "scores": self.scores,
            "q_values": self.q_values,
            "formulas": [f.__todict__() for f in self.formulas],
            "states_no_terminal": [s.__todict__() for s in self.states_no_terminal],
            "actions": [a.__todict__() for a in self.actions],
        }
    @staticmethod
    def __fromdict__(d):
        return QValueTrajectories(
            scores=d["scores"],
            q_values=d["q_values"],
            formulas=[QValueFormula.__fromdict__(f) for f in d["formulas"]],
            states_no_terminal=[State.__fromdict__(s) for s in d["states_no_terminal"]],
            actions=[AltAction.__fromdict__(a) for a in d["actions"]],
        )



# Implementing the following Julia function:
# struct CapturedPoint
#     player_num::Int
#     point_uuid::UUID
# end
class CapturedPoint(PClass):
    player_num = field(type=int)
    point_uuid = field(type=str)
    def __todict__(self):
        return {
            "player_num": self.player_num,
            "point_uuid": str(self.point_uuid),
        }
    @staticmethod
    def __fromdict__(d):
        return CapturedPoint(
            player_num=d["player_num"],
            point_uuid=d["point_uuid"]
        )


# Implementing the following Julia function:
# struct CapturedSegment
#     player_num::Int
#     segment_uuid::UUID
# end
class CapturedSegment(PClass):
    player_num = field(type=int)
    segment_uuid = field(type=str)
    def __todict__(self):
        return {
            "player_num": self.player_num,
            "segment_uuid": str(self.segment_uuid),
        }
    @staticmethod
    def __fromdict__(d):
        return CapturedSegment(
            player_num=d["player_num"],
            segment_uuid=d["segment_uuid"]
        )


class FrozenPoint2(PClass):
    num = field(type=int)
    uuid = field(type=str)
    def __todict__(self):
        return {
            "num": self.num,
            "uuid": self.uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenPoint2(
            num=d["num"],
            uuid=d["uuid"]
        )


class FrozenCluster(PClass):
    uuid = field(type=str)
    points = field(type=list)  # List[UUID]
    score = field(type=int)
    # uuid: UUID
    # points: List[UUID]
    # score: int
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "points": self.points,
            "score": self.score,
        }



# Implementing the following Julia function:
# @kwdef struct FrozenSegment
#     uuid::UUID
#     link_uuid::UUID
#     unit_uuid::Union{Nothing,UUID}
#     path_idx::Int
#     idx::Int
# end
class FrozenSegment(PClass):
    uuid = field(type=str)
    link_uuid = field(type=str)
    unit_uuid = field(type=(str, type(None)), initial=None)
    path_idx = field(type=int)
    idx = field(type=int)
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "link_uuid": self.link_uuid,
            "unit_uuid": self.unit_uuid,
            "path_idx": self.path_idx,
            "idx": self.idx,
            "pieces": [p.__todict__() for p in self.pieces],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenSegment(
            uuid=d["uuid"],
            link_uuid=d["link_uuid"],
            unit_uuid=d.get("unit_uuid"),  # Handle None case
            path_idx=d["path_idx"],
            idx=d["idx"],
            pieces=[Piece.__fromdict__(p) for p in d["pieces"]]
        )


# Implementing the following Julia function:
# struct OrderedSegment
#     path_segment_num::Int
#     segment
# end
class OrderedSegment(PClass):
    path_segment_num = field(type=int)
    segment = field(type=FrozenSegment)  # UUID
    def __todict__(self):
        return {
            "path_segment_num": self.path_segment_num,
            "segment": self.segment.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return OrderedSegment(
            path_segment_num=d["path_segment_num"],
            segment=FrozenSegment.__fromdict__(d["segment"])
        )


# Implementing the following Julia function:
# struct SegmentStatus
#     path_num::Int
#     path_segment_num::Int
#     captured_by_me::Bool
#     captured_by_other::Bool
#     available_to_me::Bool
#     status::String
#     segment
# end
class SegmentStatus(PClass):
    path_idx = field(type=int)
    path_num = field(type=int)
    path_segment_num = field(type=int)
    captured_by_me = field(type=bool)
    captured_by_other = field(type=bool)
    available_to_me = field(type=bool)
    status = field(type=str)
    segment = field(type=FrozenSegment)  # UUID
    def __todict__(self):
        return {
            "path_idx": self.path_idx,
            "path_num": self.path_num,
            "path_segment_num": self.path_segment_num,
            "captured_by_me": self.captured_by_me,
            "captured_by_other": self.captured_by_other,
            "available_to_me": self.available_to_me,
            "status": self.status,
            "segment": self.segment.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return SegmentStatus(
            path_idx=d["path_idx"],
            path_num=d["path_num"],
            path_segment_num=d["path_segment_num"],
            captured_by_me=d["captured_by_me"],
            captured_by_other=d["captured_by_other"],
            available_to_me=d["available_to_me"],
            status=d["status"],
            segment=FrozenSegment.__fromdict__(d["segment"])
        )


# Implementing the following Julia function:
# struct OrderedFullfillment
#     segment_num::Int
#     unit_card_num::Int
# end
class OrderedFullfillment(PClass):
    segment_num = field(type=int)
    unit_card_num = field(type=int)
    def __todict__(self):
        return {
            "segment_num": self.segment_num,
            "unit_card_num": self.unit_card_num,
        }
    @staticmethod
    def __fromdict__(d):
        return OrderedFullfillment(
            segment_num=d["segment_num"],
            unit_card_num=d["unit_card_num"]
        )

# Implementing the following Julia function:
# struct PathStatus
#     num::Int
#     fulfillable::Bool
#     segment_statuses::Vector{SegmentStatus}
#     sample_fulfillment::Vector{OrderedFullfillment}
# end
class PathStatus(PClass):
    idx = field(type=int)
    num = field(type=int)
    fulfillable = field(type=bool)
    segment_statuses = field(type=list)  # List[SegmentStatus]
    sample_fulfillment = field(type=list)  # List[OrderedFullfillment]
    def __todict__(self):
        return {
            "idx": self.idx,
            "num": self.num,
            "fulfillable": self.fulfillable,
            "segment_statuses": [x.__todict__() for x in self.segment_statuses],
            "sample_fulfillment": [x.__todict__() for x in self.sample_fulfillment],
        }
    @staticmethod
    def __fromdict__(d):
        return PathStatus(
            idx=d["idx"],
            num=d["num"],
            fulfillable=d["fulfillable"],
            segment_statuses=[SegmentStatus.__fromdict__(x) for x in d["segment_statuses"]],
            sample_fulfillment=[OrderedSegment.__fromdict__(x) for x in d["sample_fulfillment"]]
        )


# Implementing the following Julia function:
# @kwdef struct FrozenLinkPath
#     is_mixed::Bool
#     segments::Vector{FrozenSegment}
# end
class FrozenLinkPath(PClass):
    is_mixed = field(type=bool)
    segments = field(type=list)  # List[FrozenSegment]
    def __todict__(self):
        return {
            "is_mixed": self.is_mixed,
            "segments": [x.__todict__() for x in self.segments],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenLinkPath(
            is_mixed=d["is_mixed"],
            segments=[FrozenSegment.__fromdict__(x) for x in d["segments"]]
        )


@dataclass(frozen=True)
class FrozenPath:
    num: int
    link_num: int
    start_point_uuid: str
    end_point_uuid: str
    start_point_num: int
    end_point_num: int
    path: FrozenLinkPath
    def __todict__(self):
        return {
            "num": self.num,
            "link_num": self.link_num,
            "start_point_uuid": self.start_point_uuid,
            "end_point_uuid": self.end_point_uuid,
            "start_point_num": self.start_point_num,
            "end_point_num": self.end_point_num,
            "path": self.path.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenPath(
            num=d["num"],
            link_num=d["link_num"],
            start_point_uuid=d["start_point_uuid"],
            end_point_uuid=d["end_point_uuid"],
            start_point_num=d["start_point_num"],
            end_point_num=d["end_point_num"],
            path=FrozenLinkPath.__fromdict__(d["path"])
        )


class FrozenSetting(PClass):
    name = field(type=str)
    value_json = field(type=str)
    # name: str
    # value_json: str
    def __todict__(self):
        return {
            "name": self.name,
            "value_json": self.value_json,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenSetting(
            name=d["name"],
            value_json=d["value_json"]
        )


class FrozenDeckUnit2(PClass):
    num = field(type=int)
    quantity = field(type=int)
    is_wild = field(type=bool)
    unit_uuid = field(type=str)
    def __todict__(self):
        return {
            "num": self.num,
            "quantity": self.quantity,
            "is_wild": self.is_wild,
            "unit_uuid": self.unit_uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenDeckUnit2(
            num=d["num"],
            quantity=d["quantity"],
            is_wild=d["is_wild"],
            unit_uuid=d["unit_uuid"]
        )


@dataclass(frozen=True)
class FrozenBoardConfigDataclass:
    deck_units: List[FrozenDeckUnit2]
    len_scores: List[FrozenLenScore]
    links: List[FrozenLink2]
    clusters: List[FrozenCluster]
    points: List[FrozenPoint2]
    board_paths: List[FrozenPath]
    settings: List[FrozenSetting]


class FrozenRoute(PClass):
    num = field(type=int)
    uuid = field(type=str)
    point_a_uuid = field(type=str)
    point_b_uuid = field(type=str)
    score = field(type=int)
    start_num = field(type=int)
    end_num = field(type=int)
    def __todict__(self):
        return {
            "num": self.num,
            "uuid": self.uuid,
            "point_a_uuid": self.point_a_uuid,
            "point_b_uuid": self.point_b_uuid,
            "score": self.score,
            "start_num": self.start_num,
            "end_num": self.end_num,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenRoute(
            num=d["num"],
            uuid=d["uuid"],
            point_a_uuid=d["point_a_uuid"],
            point_b_uuid=d["point_b_uuid"],
            score=d["score"],
            start_num=d["start_num"],
            end_num=d["end_num"]
        )


class FrozenPieceTemplate(PClass):
    uuid = field(type=str)
    idx = field(type=int)
    has_player = field(type=bool)
    quantity = field(type=int)
    seed = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "idx": self.idx,
            "has_player": self.has_player,
            "quantity": self.quantity,
            "seed": self.seed,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenPieceTemplate(
            uuid=d["uuid"],
            idx=d["idx"],
            has_player=d["has_player"],
            quantity=d["quantity"],
            seed=d["seed"],
        )
    

class FrozenDekCard(PClass):
    uuid = field(type=str)
    idx = field(type=int)
    quantity = field(type=int)
    resource_uuid = field(type=(str, type(None)), initial=None)
    goal_uuid = field(type=(str, type(None)), initial=None)
    is_wild = field(type=bool)
    dek_uuid = field(type=str)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "idx": self.idx,
            "quantity": self.quantity,
            "resource_uuid": self.resource_uuid,
            "goal_uuid": self.goal_uuid,
            "is_wild": self.is_wild,
            "dek_uuid": self.dek_uuid
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenDekCard(
            uuid=d["uuid"],
            idx=d["idx"],
            quantity=d["quantity"],
            resource_uuid=d["resource_uuid"],
            goal_uuid=d["goal_uuid"],
            is_wild=d["is_wild"],
            dek_uuid=d["dek_uuid"]
        )


class FrozenDek(PClass):
    uuid = field(type=str)
    idx = field(type=int)
    seed = field(type=int)
    dek_cards = field(type=list)  # List[FrozenDekCard]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "idx": self.idx,
            "seed": self.seed,
            "dek_cards": [card.__todict__() for card in self.dek_cards],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenDek(
            uuid=d["uuid"],
            idx=d["idx"],
            seed=d["seed"],
            dek_cards=[FrozenDekCard.__fromdict__(card) for card in d["dek_cards"]],
        )
    

class FrozenBonus(PClass):
    uuid = field(type=str)
    code = field(type=str)
    score = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "code": self.code,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenBonus(
            uuid=d["uuid"],
            code=d["code"],
            score=d["score"],
        )


class FrozenGoal(PClass):
    uuid = field(type=str)
    description = field(type=(str, type(None)), initial=None)
    node_uuids = field(type=(list, type(None)), initial=None)  # List[str]
    edge_uuids = field(type=(list, type(None)), initial=None)
    region_uuids = field(type=(list, type(None)), initial=None)
    score = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "node_uuids": self.node_uuids,
            "edge_uuids": self.edge_uuids,
            "region_uuids": self.region_uuids,
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenGoal(
            uuid=d["uuid"],
            node_uuids=d["node_uuids"],
            edge_uuids=d["edge_uuids"],
            region_uuids=d["region_uuids"],
            score=d["score"]
        )


class FrozenBoardConfig(PClass):
    bonuses = field(type=list)  # List[FrozenBonus]
    goals = field(type=list)  # List[FrozenGoal]
    deks = field(type=list)  # List[FrozenDek]
    piece_templates = field(type=list)  # List[FrozenPieceTemplate]
    routes = field(type=list)  # List[FrozenRoute]
    deck_units = field(type=list)  # List[FrozenDeckUnit2]
    settings = field(type=list)  # List[FrozenSetting]
    points = field(type=list)  # List[FrozenPoint2]
    clusters = field(type=list)  # List[FrozenCluster]
    board_paths = field(type=list)  # List[FrozenPath]
    len_scores = field(type=list)  # List[FrozenLenScore]
    links = field(type=list)  # List[FrozenLink2]
    hooks = field(type=list)  # List[Hook]
    def __todict__(self):
        return {
            "bonuses": [b.__todict__() for b in self.bonuses],
            "goals": [g.__todict__() for g in self.goals],
            "deks": [d.__todict__() for d in self.deks],
            "piece_templates": [x.__todict__() for x in self.piece_templates],
            "routes": [x.__todict__() for x in self.routes],
            "deck_units": [x.__todict__() for x in self.deck_units],
            "settings": [x.__todict__() for x in self.settings],
            "points": [x.__todict__() for x in self.points],
            "clusters": [x.__todict__() for x in self.clusters],
            "board_paths": [x.__todict__() for x in self.board_paths],
            "len_scores": [x.__todict__() for x in self.len_scores],
            "links": [x.__todict__() for x in self.links],
            "hooks": [x.__todict__() for x in self.hooks],
        }
    @staticmethod
    def __fromdict__(d):
        return FrozenBoardConfig(
            bonuses=[FrozenBonus.__fromdict__(x) for x in d['bonuses']],
            goals=[FrozenGoal.__fromdict__(x) for x in d['goals']],
            deks=[FrozenDek.__fromdict__(x) for x in d['deks']],
            piece_templates=[FrozenPieceTemplate.__fromdict__(x) for x in d['piece_templates']],
            routes = initfrozenroutes(d),
            deck_units = getdeckunits(d['deck_units']),
            settings = getsettings(d['settings']),
            points = getpoints(d["points"]),
            clusters = getclusters(d["clusters"]),
            board_paths = getboardpaths(d["board_paths"]),
            len_scores=[FrozenLenScore.__fromdict__(x) for x in d['len_scores']],
            links=[FrozenLink2.__fromdict__(x) for x in d['links']],
            hooks=[Hook.__fromdict__(x) for x in d.get('hooks', [])]
        )


@dispatch(dict)
def initboardconfig(d):
    return FrozenBoardConfig.__fromdict__(d)


class StaticBoardConfig(PClass):
    uuid = field(type=str)
    board_config = field(type=FrozenBoardConfig)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "board_config": self.board_config.__todict__()
        }
    @staticmethod
    def __fromdict__(d):
        return StaticBoardConfig(
            uuid=d["uuid"],
            board_config=FrozenBoardConfig.__fromdict__(d["board_config"])
        )


@dispatch(dict)
def initfrozenroutes(d):
    pointuuids2nums = {p['uuid']: n for n, p in enumerate(d['points'])}
    return [
        FrozenRoute(
            num=i+1,
            uuid=r['uuid'],
            point_a_uuid=r['point_a_uuid'],
            point_b_uuid=r['point_b_uuid'],
            score=r['score'],
            start_num=pointuuids2nums[r['point_a_uuid']],
            end_num=pointuuids2nums[r['point_b_uuid']],
        )
        for i, r in enumerate(d['routes'])
    ]


MAX_PATH_LENGTH = 100

# Implementing the following Julia function:
# function getfrozenpathscores(b::FrozenBoardConfig)
#     d = Dict()
#     for x in b.len_scores
#         d[x.len] = x.score
#     end
#     [get(d, i, 0) for i in collect(1:MAX_PATH_LENGTH)]
# end
@dispatch(FrozenBoardConfig)
def getfrozenpathscores(b):
    d = {x.length: x.score for x in b.len_scores}
    return [d.get(i, 0) for i in range(1, MAX_PATH_LENGTH + 1)]


# Sample json data
# {"board_paths": [
#         {
#             "num": 1,
#             "path": {
#                 "is_mixed": false,
#                 "segments": [
#                     {
#                         "idx": 0,
#                         "uuid": "54fe6576-13a1-445a-ba19-dd1809798cea",
#                         "path_idx": 0,
#                         "link_uuid": "0e90684e-d9ab-4d31-bb12-33ab4e11c91a",
#                         "unit_uuid": null
#                     }
#                 ]
#             },
#             "link_num": 1,
#             "end_point_num": 6,
#             "start_point_num": 8
#         },
# ]}
def getboardpaths(d):
    return [
        FrozenPath(
            num=x['num'],
            link_num=x['link_num'],
            start_point_uuid=x['start_point_uuid'],
            end_point_uuid=x['end_point_uuid'],
            start_point_num=x['start_point_num'],
            end_point_num=x['end_point_num'],
            path=getlinkpath(x['path']),
        )
        for x in d
    ]


def getlinkpath(d):
    return FrozenLinkPath(
        is_mixed=d['is_mixed'],
        segments=getsegments(d['segments']),
    )


def getsegments(d):
    return [
        FrozenSegment(
            idx=x['idx'],
            uuid=x['uuid'],
            path_idx=x['path_idx'],
            link_uuid=x['link_uuid'],
            unit_uuid=x['unit_uuid'],
            pieces=[],
        )
        for x in d
    ]


def getclusters(d):
    return [
        FrozenCluster(
            uuid=x['uuid'],
            points=[p for p in x['points']],
            score=x['score'],
        )
        for n, x in enumerate(d)
    ]


def getpoints(d):
    return [
        FrozenPoint2(
            num=n,
            uuid=x['uuid'],
        )
        for n, x in enumerate(d)
    ]

def getsettings(d):
    return [
        BoardSetting(
            name=x['name'],
            value_json=x['value_json'],
        )
        for n, x in enumerate(d)
    ]


def getdeckunits(d):
    return [
        FrozenDeckUnit2(
            num=x['num'],
            quantity=x['quantity'],
            is_wild=x['is_wild'],
            unit_uuid=x['unit_uuid']
        )
        for n, x in enumerate(d)
    ]


class BoardSetting(PClass):
    name = field(type=str)
    value_json = field(type=str)
    def __todict__(self):
        return {
            "name": self.name,
            "value_json": self.value_json,
        }




class Fig(PClass):
    # TODO: the two fields below should just be a "StaticBoardConfig" object
    static_board_config_uuid = field(type=str)
    board_config = field(type=FrozenBoardConfig)
    path_scores = field(type=list)  # List[int]
    # graph = field(type=int)
    # path_scores = field(type=int)
    # graph: BoardGraph
    # path_scores: List[int]
    def __todict__(self):
        return {
            "static_board_config_uuid": self.static_board_config_uuid,
            "board_config": self.board_config.__todict__(),
            "path_scores": self.path_scores,
        }
    @staticmethod
    def __fromdict__(d):
        return initfig(
            d["static_board_config_uuid"], 
            FrozenBoardConfig.__fromdict__(d["board_config"]),
        )


@dispatch(str, FrozenBoardConfig)
def initfig(static_board_config_uuid, board_config):
    return Fig(
        static_board_config_uuid=static_board_config_uuid,
        board_config=board_config,
        path_scores=getfrozenpathscores(board_config),
    )


class GameConfig(PClass):
    uuid = field(type=str)
    started_at = field(type=str)
    num_players = field(type=int)
    fig = field(type=Fig)
    seed = field(type=int) 
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "started_at": self.started_at,
            "num_players": self.num_players,
            "fig": self.fig.__todict__(),
            "seed": self.seed,
        }
    @staticmethod
    def __fromdict__(d):
        return GameConfig(
            uuid=d["uuid"],
            started_at=d["started_at"],
            num_players=d["num_players"],
            fig=Fig.__fromdict__(d["fig"]),
            seed=d["seed"]
        )


class ActionDrawUnit:
   def __init__(self):
       pass


class PublicPlayer(PClass):
    idx = field(type=int)
    pieces = field(type=list)  # List[Piece]
    deck_counts = field(type=list)
    piece_template_counts = field(type=list)
    def __todict__(self):
        return {
            "idx": self.idx,
            "pieces": self.pieces,
            "deck_counts": list(self.deck_counts),
            "piece_template_counts": list(self.piece_template_counts),
        }
    @staticmethod
    def __fromdict__(d):
        return PublicPlayer(
            idx=d["idx"],
            pieces=d["pieces"],
            deck_counts=list(d["deck_counts"]),
            piece_template_counts=list(d["piece_template_counts"]),
        )


class Player(PClass):
    idx = field(type=int)
    pieces = field(type=list)  # List[Piece]
    cards = field(type=list)  # List[Card]
    discard_tray = field(type=list)  # List[Card]
    def __todict__(self):
        return {
            "idx": self.idx,
            "pieces": self.pieces,
            "cards": self.cards,
            "discard_tray": self.discard_tray,
        }
    @staticmethod
    def __fromdict__(d):
        return Player(
            idx=d["idx"],
            pieces=d["pieces"],
            cards=d["cards"],
            discard_tray=d["discard_tray"]
        )
    
class GoalCompletion(PClass):
    goal_uuid = field(type=str)
    complete = field(type=bool, initial=False)
    def __todict__(self):
        return {
            "goal_uuid": self.goal_uuid,
            "complete": self.complete,
        }
    @staticmethod
    def __fromdict__(d):
        return GoalCompletion(
            goal_uuid=d["goal_uuid"],
            complete=d.get("complete")
        )


class PlayerGraph(PClass):
    player_idx = field(type=int)
    neighbors = field(type=list)  # List[List[int]]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "neighbors": self.neighbors,
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerGraph(
            player_idx=d["player_idx"],
            neighbors=d["neighbors"],
        )


class PlayerNode(PClass):
    player_idx = field(type=int)
    node_idx = field(type=int)
    neighbors = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "node_idx": self.node_idx,
            "neighbors": self.neighbors,
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerNode(
            player_idx=d["player_idx"],
            node_idx=d["node_idx"],
            neighbors=d["neighbors"]
        )


class PrivatePlayerScore(PClass):
    items = field(type=list)  # List[ScoreItem2]
    total = field(type=int)
    def __todict__(self):
        return {
            "items": [x.__todict__() for x in self.items], 
            "total": self.total,
        }
    @staticmethod
    def __fromdict__(d):
        return PrivatePlayerScore(
            items=[ScoreItem2.__fromdict__(x) for x in d["items"]],
            total=d["total"]
        )


class PrivateState(PClass):
    my_history = field(type=list)  # List[Action2]
    player_score = field(type=PrivatePlayerScore)
    player = field(type=Player)
    legal_actions_3 = field(type=list)  # List[LegalAction]
    goal_completions = field(type=list, initial=[])  # List[GoalCompletion]
    def __todict__(self):
        return {
            "my_history": [x.__todict__() for x in self.my_history],
            "player_score": self.player_score.__todict__(),
            "player": self.player.__todict__(),
            "legal_actions_3": [x.__todict__() for x in self.legal_actions_3],
            "goal_completions": [x.__todict__() for x in self.goal_completions],
        }
    @staticmethod
    def __fromdict__(d):
        return PrivateState(
            my_history=[Action2.__fromdict__(x) for x in d["my_history"]],
            player_score=PrivatePlayerScore.__fromdict__(d["player_score"]),
            player=Player.__fromdict__(d["player"]),
            legal_actions_3=[LegalAction.__fromdict__(x) for x in d["legal_actions_3"]],
            goal_completions=[GoalCompletion.__fromdict__(x) for x in d["goal_completions"]],
        )


class PublicDeck(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    units = field(type=list)  # List[Card]
    facedown_stack_len = field(type=int)
    discard_len = field(type=int)
    faceup_spots = field(type=list)  # List[Card]
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "units": [unit.__todict__() for unit in self.units],
            "facedown_stack_len": self.facedown_stack_len,
            "discard_len": self.discard_len,
            "faceup_spots": self.faceup_spots,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicDeck(
            idx=d["idx"],
            uuid=d["uuid"],
            units=[Card.__fromdict__(card) for card in d["units"]],
            facedown_stack_len=d["facedown_stack_len"],
            discard_len=d["discard_len"],
            faceup_spots=d["faceup_spots"],
        )


class ActionKeepOptional(PClass):
    card_uuids = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionKeepOptional(
            card_uuids=d["card_uuids"]
        )
    

class LegalActionKeep(PClass):
    deck_idx = field(type=int)
    min = field(type=(int, type(None)), initial=None)  # Optional[int]
    max = field(type=(int, type(None)), initial=None)  # Optional[int]
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "min": self.min,
            "max": self.max,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionKeep(
            deck_idx=d["deck_idx"],
            min=d.get("min"),  # Handle None case
            max=d.get("max"),  # Handle None case
        )
    @staticmethod
    def get_default_action(legal_action, state, submitted_at):
        discard_tray = state.players[legal_action.player_idx].discard_tray
        deck_idx = legal_action.keep.deck_idx
        card_uuids_matching_deck = [
            card_uuid for card_uuid in discard_tray 
            if state.kernel.carduuid2deckidx[card_uuid] == deck_idx
        ]
        num_cards = len(card_uuids_matching_deck)
        actual_min = 0 if legal_action.keep.min is None else legal_action.keep.min
        actual_max = num_cards if legal_action.keep.max is None else min(legal_action.keep.max, num_cards)
        rand_num_chosen = state.rng.randint(actual_min, actual_max)
        card_uuids = card_uuids_matching_deck[0:rand_num_chosen]
        return Action2(
            submitted_at=submitted_at,
            legal_action=legal_action,
            keep=ActionKeep(
                card_uuids=card_uuids
            )
        )
    

class LegalActionDiscard(PClass):
    deck_idx = field(type=int)
    min = field(type=(int, type(None)), initial=None)  # Optional[int]
    max = field(type=(int, type(None)), initial=None)  # Optional[int]
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "min": self.min,
            "max": self.max,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionDiscard(
            deck_idx=d["deck_idx"],
            min=d.get("min"),  # Handle None case
            max=d.get("max")  # Handle None case
        )
    @staticmethod
    def get_default_action(legal_action, state, submitted_at):
        discard_tray = state.players[legal_action.player_idx].discard_tray
        deck_idx = legal_action.discard.deck_idx
        card_uuids_matching_deck = [
            card_uuid for card_uuid in discard_tray 
            if state.kernel.carduuid2deckidx[card_uuid] == deck_idx
        ]
        num_cards = len(card_uuids_matching_deck)
        actual_min = 0 if legal_action.discard.min is None else legal_action.discard.min
        actual_max = num_cards if legal_action.discard.max is None else min(legal_action.discard.max, num_cards)
        rand_num_chosen = state.rng.randint(actual_min, actual_max)
        card_uuids = card_uuids_matching_deck[0:rand_num_chosen]
        return Action2(
            submitted_at=submitted_at,
            legal_action=legal_action,
            discard=ActionDiscard(
                card_uuids=card_uuids
            )
        )


class PublicActionMovePiecesToPathOptional(PClass):
    piece_uuids = field(type=list)  # List[str]
    card_uuids = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "piece_uuids": self.piece_uuids,
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicActionMovePiecesToPathOptional(
            piece_uuids=d["piece_uuids"],
            card_uuids=d["card_uuids"]
        )


class ActionMovePiecesToPathOptional(PClass):
    piece_uuids = field(type=list)  # List[str]
    card_uuids = field(type=list)  # List[str]
    def get_public(self, state):
        return PublicActionMovePiecesToPathOptional(
            piece_uuids=self.piece_uuids,
            card_uuids=self.card_uuids,
        )
    def __todict__(self):
        return {
            "piece_uuids": self.piece_uuids,
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionMovePiecesToPathOptional(
            piece_uuids=d["piece_uuids"],
            card_uuids=d["card_uuids"]
        )
    

class PublicLegalActionMovePiecesToPath(PClass):
    path_idx = field(type=int)
    def __todict__(self):
        return {
            "path_idx": self.path_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicLegalActionMovePiecesToPath(
            path_idx=d["path_idx"]
        )


class LegalActionMovePiecesToPath(PClass):
    path_idx = field(type=int)
    default = field(type=ActionMovePiecesToPathOptional)  # Optional[MovePiecesToPathAction]
    def get_public(self, state):
        return PublicLegalActionMovePiecesToPath(
            path_idx=self.path_idx,
        )
    def __todict__(self):
        return {
            "path_idx": self.path_idx,
            "default": self.default.__todict__(),
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionMovePiecesToPath(
            path_idx=d["path_idx"],
            default=ActionMovePiecesToPathOptional.__fromdict__(d["default"])
        )
    @staticmethod
    def get_default_action(legal_action, state, submitted_at):
        return Action2(
            submitted_at=submitted_at,
            legal_action=legal_action,
            move_pieces_to_path=legal_action.move_pieces_to_path.default
        )


    
class LegalActionFaceupDraw(PClass):
    deck_idx = field(type=int)
    card_uuid = field(type=str)
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "card_uuid": self.card_uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionFaceupDraw(
            deck_idx=d["deck_idx"],
            card_uuid=d["card_uuid"],
        )
    @staticmethod
    def get_default_action(legal_action, state, submitted_at):
        return Action2(
            submitted_at=submitted_at,
            legal_action=legal_action,
        )



class LegalActionDraw(PClass):
    deck_idx = field(type=int)
    quantity = field(type=int)
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "quantity": self.quantity,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionDraw(
            deck_idx=d["deck_idx"],
            quantity=d["quantity"]
        )
    @staticmethod
    def get_default_action(legal_action, state, submitted_at):
        return Action2(
            submitted_at=submitted_at,
            legal_action=legal_action,
        )


class LegalActionDrawDiscard(PClass):
    deck_idx = field(type=int)
    quantity = field(type=int)
    min = field(type=(int, type(None)), initial=None)  # Optional[int]
    max = field(type=(int, type(None)), initial=None)  # Optional[int]
    def get_public(self, state):
        return self
    def __todict__(self):
        return {
            "deck_idx": self.deck_idx,
            "quantity": self.quantity,
            "min": self.min,
            "max": self.max,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalActionDrawDiscard(
            deck_idx=d["deck_idx"],
            quantity=d["quantity"],
            min=d.get("min"),  # Handle None case
            max=d.get("max")  # Handle None case
        )
    @staticmethod
    def get_default_action(legal_action, state, submitted_at):
        return Action2(
            submitted_at=submitted_at,
            legal_action=legal_action,
        )


class PublicLegalAction(PClass):
    player_idx = field(type=int)
    name = field(type=str)
    discard = field(type=(LegalActionDiscard, type(None)), initial=None)  # LegalActionDiscard
    keep = field(type=(LegalActionKeep, type(None)), initial=None)  # LegalActionKeep
    draw = field(type=(LegalActionDraw, type(None)), initial=None)  # LegalActionDraw
    draw_discard = field(type=(LegalActionDrawDiscard, type(None)), initial=None)  # LegalActionDrawDiscard
    faceup_draw = field(type=(LegalActionFaceupDraw, type(None)), initial=None)  # LegalActionFaceupDraw
    move_pieces_to_path = field(type=(PublicLegalActionMovePiecesToPath, type(None)), initial=None)  # PublicLegalActionMovePiecesToPath
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "name": self.name,
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "draw": self.draw.__todict__() if self.draw else None,
            "draw_discard": self.draw_discard.__todict__() if self.draw_discard else None,
            "faceup_draw": self.faceup_draw.__todict__() if self.faceup_draw else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicLegalAction(
            player_idx=d["player_idx"],
            name=d["name"],
            discard=LegalActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=LegalActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            draw=LegalActionDraw.__fromdict__(d["draw"]) if d.get("draw") else None,
            draw_discard=LegalActionDrawDiscard.__fromdict__(d["draw_discard"]) if d.get("draw_discard") else None,
            faceup_draw=LegalActionFaceupDraw.__fromdict__(d["faceup_draw"]) if d.get("faceup_draw") else None,
            move_pieces_to_path=LegalActionMovePiecesToPath.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
        )


class LegalAction(PClass):
    player_idx = field(type=int)
    name = field(type=str)
    title = field(type=(str, type(None)), initial=None)  # Optional[str]
    instruction = field(type=(str, type(None)), initial=None)  # Optional[str]
    allotted_seconds = field(type=int, initial=INITIAL_ALLOTTED_SECONDS)  # int
    allotted_since_action_idx = field(type=int, initial=-1)  # int
    btn_text = field(type=(str, type(None)), initial=None)  # Optional[str]
    discard = field(type=(LegalActionDiscard, type(None)), initial=None)  # LegalActionDiscard
    keep = field(type=(LegalActionKeep, type(None)), initial=None)  # LegalActionKeep
    draw = field(type=(LegalActionDraw, type(None)), initial=None)  # LegalActionDraw
    draw_discard = field(type=(LegalActionDrawDiscard, type(None)), initial=None)  # LegalActionDrawDiscard
    faceup_draw = field(type=(LegalActionFaceupDraw, type(None)), initial=None)  # LegalActionFaceupDraw
    move_pieces_to_path = field(type=(LegalActionMovePiecesToPath, type(None)), initial=None)  # LegalActionMovePiecesToPath
    auto_preferred = field(type=bool, initial=False)  # bool
    def get_default_action(self, state):
        submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.discard:
            return LegalActionDiscard.get_default_action(self, state, submitted_at)
        if self.keep:
            return LegalActionKeep.get_default_action(self, state, submitted_at)
        if self.draw:
            return LegalActionDraw.get_default_action(self, state, submitted_at)
        if self.draw_discard:
            return LegalActionDrawDiscard.get_default_action(self, state, submitted_at)
        if self.faceup_draw:
            return LegalActionFaceupDraw.get_default_action(self, state, submitted_at)
        if self.move_pieces_to_path:
            return LegalActionMovePiecesToPath.get_default_action(self, state, submitted_at)
        return None
    def get_public(self, state):
        return PublicLegalAction(
            player_idx=self.player_idx,
            name=self.name,
            discard=self.discard.get_public(state) if self.discard else None,
            keep=self.keep.get_public(state) if self.keep else None,
            draw=self.draw.get_public(state) if self.draw else None,
            draw_discard=self.draw_discard.get_public(state) if self.draw_discard else None,
            faceup_draw=self.faceup_draw.get_public(state) if self.faceup_draw else None,
            move_pieces_to_path=self.move_pieces_to_path.get_public(state) if self.move_pieces_to_path else None,
        )
    def __eq__(self, other):
        return self.__todict__() == other.__todict__()
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "name": self.name,
            "title": self.title,
            "instruction": self.instruction,
            "allotted_seconds": self.allotted_seconds,
            "allotted_since_action_idx": self.allotted_since_action_idx,
            "btn_text": self.btn_text,
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "draw": self.draw.__todict__() if self.draw else None,
            "draw_discard": self.draw_discard.__todict__() if self.draw_discard else None,
            "faceup_draw": self.faceup_draw.__todict__() if self.faceup_draw else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
            "auto_preferred": self.auto_preferred,
        }
    @staticmethod
    def __fromdict__(d):
        return LegalAction(
            player_idx=d["player_idx"],
            name=d["name"],
            title=d.get("title"),  # Handle None case
            instruction=d.get("instruction"),  # Handle None case
            allotted_seconds=d.get("allotted_seconds", DEFAULT_ALLOTTED_SECONDS),  # Handle None case
            allotted_since_action_idx=d.get("allotted_since_action_idx", -1),  # Handle None case
            btn_text=d.get("btn_text"),  # Handle None case
            discard=LegalActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=LegalActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            draw=LegalActionDraw.__fromdict__(d["draw"]) if d.get("draw") else None,
            draw_discard=LegalActionDrawDiscard.__fromdict__(d["draw_discard"]) if d.get("draw_discard") else None,
            faceup_draw=LegalActionFaceupDraw.__fromdict__(d["faceup_draw"]) if d.get("faceup_draw") else None,
            move_pieces_to_path=LegalActionMovePiecesToPath.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
            auto_preferred=d.get("auto_preferred"),  # Handle None case
        )


class PublicActionDiscard(PClass):
    deck_idxs = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "deck_idxs": self.deck_idxs,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicActionDiscard(
            deck_idxs=d["deck_idxs"]
        )


class ActionDiscard(PClass):
    card_uuids = field(type=list)  # List[int]
    def get_public(self, state):
        return PublicActionDiscard(
            deck_idxs=[state.kernel.carduuid2deckidx[card_uuid] for card_uuid in self.card_uuids]
        )
    def __todict__(self):
        return {
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionDiscard(
            card_uuids=d["card_uuids"]
        )


class PublicActionKeep(PClass):
    deck_idxs = field(type=list)  # List[int]
    def __todict__(self):
        return {
            "deck_idxs": self.deck_idxs,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicActionKeep(
            deck_idxs=d["deck_idxs"]
        )


class ActionKeep(PClass):
    card_uuids = field(type=list)  # List[int])
    def get_public(self, state):
        return PublicActionKeep(
            deck_idxs=[state.kernel.carduuid2deckidx[card_uuid] for card_uuid in self.card_uuids]
        )
    def __todict__(self):
        return {
            "card_uuids": self.card_uuids,
        }
    @staticmethod
    def __fromdict__(d):
        return ActionKeep(
            card_uuids=d["card_uuids"]
        )


class PublicAction(PClass):
    submitted_at = field(type=str)
    player_idx = field(type=int)
    name = field(type=str)
    legal_action = field(type=PublicLegalAction)
    discard = field(type=(PublicActionDiscard, type(None)), initial=None)  # PublicActionDiscard
    keep = field(type=(PublicActionKeep, type(None)), initial=None)  # PublicActionKeep
    move_pieces_to_path = field(type=(PublicActionMovePiecesToPathOptional, type(None)), initial=None)  # PublicActionMovePiecesToPathOptional)
    def __todict__(self):
        return {
            "submitted_at": self.submitted_at,
            "player_idx": self.player_idx,
            "name": self.name,
            "legal_action": self.legal_action.__todict__(),
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicAction(
            submitted_at=d["submitted_at"],
            player_idx=d["player_idx"],
            name=d["name"],
            legal_action=PublicLegalAction.__fromdict__(d["legal_action"]),
            discard=PublicActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=PublicActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            move_pieces_to_path=PublicActionMovePiecesToPathOptional.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
        )


class Action2(PClass):
    submitted_at = field(type=str)  # str
    legal_action = field(type=LegalAction) 
    discard = field(type=(ActionDiscard, type(None)), initial=None)  # ActionDiscard
    keep = field(type=(ActionKeep, type(None)), initial=None)  # ActionKeep
    move_pieces_to_path = field(type=(ActionMovePiecesToPathOptional, type(None)), initial=None)  # ActionMovePiecesToPath
    def get_public(self, state):
        return PublicAction(
            submitted_at=self.submitted_at,
            player_idx=self.legal_action.player_idx,
            name=self.legal_action.name,
            legal_action=self.legal_action.get_public(state),
            discard=self.discard.get_public(state) if self.discard else None,
            keep=self.keep.get_public(state) if self.keep else None,
            move_pieces_to_path=self.move_pieces_to_path.get_public(state) if self.move_pieces_to_path else None,
        )
    def __todict__(self):
        return {
            "submitted_at": self.submitted_at,
            "legal_action": self.legal_action.__todict__(),
            "discard": self.discard.__todict__() if self.discard else None,
            "keep": self.keep.__todict__() if self.keep else None,
            "move_pieces_to_path": self.move_pieces_to_path.__todict__() if self.move_pieces_to_path else None,
        }
    @staticmethod
    def __fromdict__(d):
        return Action2(
            submitted_at=d["submitted_at"],
            legal_action=LegalAction.__fromdict__(d["legal_action"]),
            discard=ActionDiscard.__fromdict__(d["discard"]) if d.get("discard") else None,
            keep=ActionKeep.__fromdict__(d["keep"]) if d.get("keep") else None,
            move_pieces_to_path=ActionMovePiecesToPathOptional.__fromdict__(d["move_pieces_to_path"]) if d.get("move_pieces_to_path") else None,
        )


class Deck(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    units = field(type=list)  # List[Card]
    facedown_stack = field(type=list)  # List[str]
    discard = field(type=list)  # List[str]
    faceup_spots = field(type=list)  # List[str]
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "units": [unit.__todict__() for unit in self.units],
            "facedown_stack": self.facedown_stack,
            "discard": self.discard,
            "faceup_spots": self.faceup_spots,
        }
    @staticmethod
    def __fromdict__(d):
        return Deck(
            idx=d["idx"],
            uuid=d["uuid"],
            units=[], # TODO: Card.__fromdict__(card) for card in d["cards"]
            facedown_stack=d["facedown_stack"],
            discard=d["discard"],
            faceup_spots=d["faceup_spots"],
        )




class Card(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    dek_card_uuid = field(type=str)
    is_wild = field(type=bool)
    deck_idx = field(type=int)
    resource_uuid = field(type=(str, type(None)), initial=None)
    goal_uuid = field(type=(str, type(None)), initial=None)
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "dek_card_uuid": self.dek_card_uuid,
            "is_wild": self.is_wild,
            "deck_idx": self.deck_idx,
            "resource_uuid": self.resource_uuid,
            "goal_uuid": self.goal_uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return Card(
            idx=d["idx"],
            uuid=d["uuid"],
            dek_card_uuid=d["dek_card_uuid"],
            is_wild=d["is_wild"],
            deck_idx=d["deck_idx"],
            resource_uuid=d["resource_uuid"],
            goal_uuid=d["goal_uuid"],
        )


class PieceTemplate(PClass):
    uuid = field(type=str)
    name = field(type=str)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
        }
    @staticmethod
    def __fromdict__(d):
        return PieceTemplate(
            uuid=d["uuid"],
            name=d["name"]
        )


class Piece(PClass):
    uuid = field(type=str)
    pile_idx = field(type=int)
    player_idx = field(type=int)
    piece_template_idx = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "pile_idx": self.pile_idx,
            "player_idx": self.player_idx,
            "piece_template_idx": self.piece_template_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return Piece(
            uuid=d["uuid"],
            pile_idx=d["pile_idx"],
            player_idx=d["player_idx"],
            piece_template_idx=d["piece_template_idx"],
        )
    

class Pile(PClass):
    player_idx = field(type=(int, type(None)), initial=None)
    num_pieces = field(type=int, initial=0)
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "num_pieces": self.num_pieces,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Pile(
            player_idx=d["player_idx"],
            num_pieces=d["num_pieces"],
            pieces=d["pieces"],
        )
    

class Segment2(PClass):
    uuid = field(type=str)
    unit_uuid = field(type=(str, type(None)), initial=None)  # Optional[str]
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "unit_uuid": self.unit_uuid,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Segment2(
            uuid=d["uuid"],
            unit_uuid=d["unit_uuid"],
            pieces=d["pieces"],
        )


class Path2(PClass):
    uuid = field(type=str)
    idx = field(type=int)
    edge_uuid = field(type=str)
    segments = field(type=list)  # List[Segment]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "idx": self.idx,
            "edge_uuid": self.edge_uuid,
            "segments": [segment.__todict__() for segment in self.segments],
        }
    @staticmethod
    def __fromdict__(d):
        return Path2(
            uuid=d["uuid"],
            idx=d["idx"],
            edge_uuid=d["edge_uuid"],
            segments=[Segment2.__fromdict__(segment) for segment in d["segments"]],
        )


class BiEdge(PClass):
    uuid = field(type=str)
    start_point_uuid = field(type=str)
    end_point_uuid = field(type=str)
    node_1_uuid = field(type=str)
    node_2_uuid = field(type=str)
    node_1_idx = field(type=int)
    node_2_idx = field(type=int)
    paths = field(type=list)  # List[Path2]
    score = field(type=int)
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "start_point_uuid": self.start_point_uuid,
            "end_point_uuid": self.end_point_uuid,
            "node_1_uuid": self.node_1_uuid,
            "node_2_uuid": self.node_2_uuid,
            "node_1_idx": self.node_1_idx,
            "node_2_idx": self.node_2_idx,
            "paths": [path.__todict__() for path in self.paths],
            "score": self.score,
        }
    @staticmethod
    def __fromdict__(d):
        return BiEdge(
            uuid=d["uuid"],
            start_point_uuid=d["start_point_uuid"],
            end_point_uuid=d["end_point_uuid"],
            node_1_uuid=d["node_1_uuid"],
            node_2_uuid=d["node_2_uuid"],
            node_1_idx=d["node_1_idx"],
            node_2_idx=d["node_2_idx"],
            paths=[Path2.__fromdict__(path) for path in d["paths"]],
            score=d["score"],
        )


class Node(PClass):
    idx = field(type=int)
    uuid = field(type=str)
    name = field(type=str)
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "idx": self.idx,
            "uuid": self.uuid,
            "name": self.name,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Node(
            idx=d["idx"],
            uuid=d["uuid"],
            name=d["name"],
            pieces=d["pieces"],
        )
    

class Region(PClass):
    uuid = field(type=str)
    node_uuids = field(type=list)  # List[str]
    pieces = field(type=list)  # List[Piece]
    def __todict__(self):
        return {
            "uuid": self.uuid,
            "node_uuids": self.node_uuids,
            "pieces": self.pieces,
        }
    @staticmethod
    def __fromdict__(d):
        return Region(
            uuid=d["uuid"],
            node_uuids=d["node_uuids"],
            pieces=d["pieces"],
        )
    

class LongestTrailBonusPlayerStatus(PClass):
    length = field(type=int)
    def __todict__(self):
        return {
            "length": self.length,
        }
    @staticmethod
    def __fromdict__(d):
        return LongestTrailBonusPlayerStatus(
            length=d["length"]
        )


class BonusPlayerStatus(PClass):
    player_idx = field(type=int)
    score = field(type=int)
    longest_trail = field(type=(LongestTrailBonusPlayerStatus, type(None)), initial=None)  # Optional[LongestTrailBonusPlayerStatus]
    def __todict__(self):
        return {
            "player_idx": self.player_idx,
            "score": self.score,
            "longest_trail": self.longest_trail.__todict__() if self.longest_trail else None,
        }
    @staticmethod
    def __fromdict__(d):
        return BonusPlayerStatus(
            player_idx=d["player_idx"],
            score=d["score"],
            longest_trail=LongestTrailBonusPlayerStatus.__fromdict__(d["longest_trail"]) if d.get("longest_trail") else None,
        )


class BonusStatus(PClass):
    bonus_uuid = field(type=str)
    winners = field(type=list)
    player_statuses = field(type=list)  # List[BonusPlayerStatus|None]
    def __todict__(self):
        return {
            "bonus_uuid": self.bonus_uuid,
            "winners": self.winners,
            "player_statuses": [status.__todict__() for status in self.player_statuses],
        }
    @staticmethod
    def __fromdict__(d):
        return BonusStatus(
            bonus_uuid=d["bonus_uuid"],
            winners=d["winners"],
            player_statuses=[BonusPlayerStatus.__fromdict__(status) for status in d.get("player_statuses", [])],
        )


class StateKernel(PClass):
    rng = field(type=random.Random)
    game_config = field(type=GameConfig)
    edges = field(type=list)  # List[BiEdge]
    nodes = field(type=list)  # List[Node]
    regions = field(type=list)  # List[Region]
    decks = field(type=list)  # List[Deck]
    piles = field(type=list)  # List[Pile]
    players = field(type=list)  # List[Player]
    player_idxs = field(type=list)  # List[int]
    history = field(type=list)  # List[PublicAction]
    idx2path = field(type=list)  # List[Path2]
    pieceuuid2piece = field(type=dict)  # Dict[str, Piece]
    edgeuuid2idx = field(type=dict)  # Dict[str, int]
    carduuid2card = field(type=dict)  # Dict[str, Card]
    edgetuple2uuid = field(type=dict)  # Dict[Tuple[int, int], str]
    nodeuuid2idx = field(type=dict)  # Dict[str, int]
    carduuid2deckidx = field(type=dict)  # Dict[str, int]
    bonusuuid2bonusidx = field(type=dict)  # Dict[str, int]
    starting_decks = field(type=list)  # List[Deck]
    starting_piles = field(type=list) # List[Pile]
    goals = field(type=list)  # List[FrozenGoal]
    last_to_play = field(type=(int, type(None)), initial=None)
    player_graphs_3 = field(type=list)  # List[PlayerGraph]
    def __todict__(self):
        return {
            "rng": rng2json(self.rng),
            "game_config": self.game_config.__todict__(),
            "edges": [edge.__todict__() for edge in self.edges],
            "nodes": [node.__todict__() for node in self.nodes],
            "regions": [region.__todict__() for region in self.regions],
            "decks": [deck.__todict__() for deck in self.decks],
            "piles": [pile.__todict__() for pile in self.piles],
            "players": [player.__todict__() for player in self.players],
            "player_idxs": self.player_idxs,
            "history": [action.__todict__() for action in self.history],
            "idx2path": [v.__todict__() for v in self.idx2path],
            "pieceuuid2piece": {k: v.__todict__() for k, v in self.pieceuuid2piece.items()},
            "edgeuuid2idx": self.edgeuuid2idx,
            "carduuid2card": {k: v.__todict__() for k, v in self.carduuid2card.items()},
            "edgetuple2uuid": [{"k": list(k), "v": v} for k, v in self.edgetuple2uuid.items()],
            "nodeuuid2idx": self.nodeuuid2idx,
            "carduuid2deckidx": self.carduuid2deckidx,
            "bonusuuid2bonusidx": self.bonusuuid2bonusidx,
            "starting_decks": [deck.__todict__() for deck in self.starting_decks],
            "starting_piles": [pile.__todict__() for pile in self.starting_piles],
            "goals": [goal.__todict__() for goal in self.goals],
            "last_to_play": self.last_to_play,
            "player_graphs_3": [x.__todict__() for x in self.player_graphs_3],
        }
    @staticmethod
    def __fromdict__(d):
        return StateKernel(
            rng=json2rng(d["rng"]),
            game_config=GameConfig.__fromdict__(d["game_config"]),
            edges=[BiEdge.__fromdict__(edge) for edge in d["edges"]],
            nodes=[Node.__fromdict__(n) for n in d["nodes"]],
            regions=[Region.__fromdict__(r) for r in d["regions"]],
            decks=[Deck.__fromdict__(deck) for deck in d["decks"]],
            piles=[Pile.__fromdict__(pile) for pile in d["piles"]],
            players=[Player.__fromdict__(player) for player in d["players"]],
            player_idxs=d["player_idxs"],
            history=[PublicAction.__fromdict__(action) for action in d["history"]],
            idx2path=[Path2.__fromdict(v) for v in d["idx2path"]],
            pieceuuid2piece={k: Piece.__fromdict(v) for k, v in d["pieceuuid2piece"].items()},
            edgeuuid2idx=d["edgeuuid2idx"],
            carduuid2card={k: Card.__fromdict(v) for k, v in d["carduuid2card"].items()},
            edgetuple2uuid={tuple(item["k"]): item["v"] for item in d["edgetuple2uuid"]},
            nodeuuid2idx=d["nodeuuid2idx"],
            carduuid2deckidx=d["carduuid2deckidx"],
            bonusuuid2bonusidx=d["bonusuuid2bonusidx"],
            starting_decks=[Deck.__fromdict__(x) for x in d["starting_decks"]],
            starting_piles=[Pile.__fromdict__(x) for x in d["starting_piles"]],
            goals=[FrozenGoal.__fromdict__(goal) for goal in d["goals"]],
            last_to_play=d.get("last_to_play"),
            player_graphs_3=[PlayerGraph.__fromdict__(x) for x in d["player_graphs_3"]],
        )


def init_state_kernel(**kwargs):
    rng = kwargs.get('rng')
    game_config = kwargs.get('game_config')
    fig = game_config.fig
    board_config = fig.board_config
    nodes = kwargs.get('nodes', [])
    edges = kwargs.get('edges', [])
    idx2path = []
    edgeuuid2idx = {edge.uuid: idx for idx, edge in enumerate(edges)}
    for edge in edges:
        for path in edge.paths:
            idx2path.append(path)
    pieceuuid2piece = {}
    for piece_template in board_config.piece_templates:
        if piece_template.has_player:
            for player_idx in range(game_config.num_players):
                pieces = generate_pieces(piece_template, player_idx)
                for piece in pieces:
                    pieceuuid2piece[piece.uuid] = piece

    carduuid2deckidx = {}
    carduuid2card = {}
    for dek in board_config.deks:
        cards = generate_cards(dek)
        for card in cards:
            carduuid2card[card.uuid] = card
            carduuid2deckidx[card.uuid] = dek.idx

    nodeuuid2idx = {node.uuid: idx for idx, node in enumerate(board_config.points)}
    edges = get_edges(rng, board_config, nodeuuid2idx)
    edgetuple2uuid = {}
    for edge in edges:
        node_1_idx = nodeuuid2idx[edge.node_1_uuid]
        node_2_idx = nodeuuid2idx[edge.node_2_uuid]
        edge_tuple = (min(node_1_idx, node_2_idx), max(node_1_idx, node_2_idx))
        edgetuple2uuid[edge_tuple] = edge.uuid

    bonuses = game_config.fig.board_config.bonuses
    bonusuuid2bonusidx = {bonus.uuid: idx for idx, bonus in enumerate(bonuses)}
    
    player_graphs_3 = calc_player_graphs3(nodes, edges, pieceuuid2piece, game_config)

    return StateKernel(
        rng=rng,
        game_config=game_config,
        edges=edges,
        nodes=kwargs.get('nodes', []),
        regions=kwargs.get('regions', []),
        decks=kwargs.get('decks', []),
        piles=kwargs.get('piles', []),
        players=kwargs.get('players'),
        player_idxs=kwargs.get('player_idxs'),
        history=kwargs.get('history', []),
        idx2path=idx2path,
        edgeuuid2idx=edgeuuid2idx,
        carduuid2card=carduuid2card,
        pieceuuid2piece=pieceuuid2piece,
        edgetuple2uuid=edgetuple2uuid,
        nodeuuid2idx=nodeuuid2idx,
        carduuid2deckidx=carduuid2deckidx,
        bonusuuid2bonusidx=bonusuuid2bonusidx,
        starting_decks=kwargs.get('starting_decks', []),
        starting_piles=kwargs.get('starting_piles', []),
        goals=kwargs.get('goals', []),
        player_graphs_3=player_graphs_3,
    )


class State(PClass):
    kernel = field(type=StateKernel)

    # Identity - these fields should be in the kernel (can only be changed in "get_initial_state" and "get_next_state")
    # The struture should be this: uuid2segment, uuid2edge, uuid2path, uuid2region, uuid2node

    # Memoized
    legal_actions_3 = field(type=list)  # List[LegalAction]
    bonus_statuses_3 = field(type=list)  # List[BonusStatus]
    player_scores_3 = field(type=list)  # List[PlayerScore2]
    winners = field(type=list)  # List[int]

    def __todict__(self):
        return {
            "kernel": self.kernel.__todict__(),
            "bonus_statuses_3": [status.__todict__() for status in self.bonus_statuses_3],
            "player_scores_3": [x.__todict__() for x in self.player_scores_3],
            "legal_actions_3": [x.__todict__() for x in self.legal_actions_3],
        }
    @staticmethod
    def __fromdict__(d):
        return State(
            kernel=StateKernel.__fromdict__(d["kernel"]),
            bonus_statuses_3=[BonusStatus.__fromdict__(x) for x in d["bonus_statuses_3"]],
            player_scores_3=[PlayerScore2.__fromdict__(x) for x in d["player_scores_3"]],
            legal_actions_3=[LegalAction.__fromdict__(x) for x in d["legal_actions_3"]],
        )


# Implementing the following Julia function:
# getnumroutecards(f::Fig) = length(f.board_config.routes)
@dispatch(Fig)
def getnumroutecards(f):
    return len(f.board_config.routes) if f and f.board_config else 0


# Implementing the following Julia function:
# [x.quantity for x in f.board_config.deck_units] |> sum
@dispatch(Fig)
def gettotaldeckcards(f):
    return sum(x.quantity for x in f.board_config.deck_units) if f and f.board_config else 0
    

# Implementing the following Julia function:
# function shuffledeck(deck_size::Int, seed::Int)
#     shuffledeck(collect(1:deck_size), seed)
# end
@dispatch(int, object)
def shuffledeck(deck_size, rng):
    deck = list(range(1, deck_size + 1))
    return shuffledeck(deck, rng)


# Implementing the following Julia function:
# function shuffledeck(deck::Vector{Int}, seed::Int)
#     shuffle(MersenneTwister(seed), deck)
# end
@dispatch(list, object)
def shuffledeck(deck, rng):
    shuffled_deck = deck.copy()
    rng.shuffle(shuffled_deck)
    return shuffled_deck


class QValueLearningPolicy(PClass):
    qvalue_fn = field()
    epsilon = field(type=float, initial=0.1)  # Epsilon for exploration


class RandoPolicy:
   def __init__(self):
       pass


# Functions  


# Implementing the following GraphQL type:
# type PlayerScore {
# 	breakdown: [ScoreItem]!
# 	total: Int!
# }
class PlayerScore(PClass):
    breakdown = field(type=list)  # List[ScoreItem]
    total = field(type=int)
    def __todict__(self):
        return {
            "breakdown": [x.__todict__() for x in self.breakdown], 
            "total": self.total,
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerScore(
            breakdown=[ScoreItem.__fromdict__(x) for x in d["breakdown"]],
            total=d["total"]
        )


class PublicPlayerScore(PClass):
    items = field(type=list)  # List[ScoreItem2]
    total = field(type=int)
    def __todict__(self):
        return {
            "items": [x.__todict__() for x in self.items], 
            "total": self.total,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicPlayerScore(
            items=[ScoreItem2.__fromdict__(x) for x in d["items"]],
            total=d["total"]
        )


class ScoreItemBonus(PClass):
    bonus_uuid = field(type=str)
    def __todict__(self):
        return {
            "bonus_uuid": self.bonus_uuid,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreItemBonus(
            bonus_uuid=d["bonus_uuid"],
        )


class ScoreItemGoal(PClass):
    goal_uuid = field(type=str)
    complete = field(type=bool)
    def __todict__(self):
        return {
            "goal_uuid": self.goal_uuid,
            "complete": self.complete,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreItemGoal(
            goal_uuid=d["goal_uuid"],
            complete=d["complete"],
        )
    

class ScoreItemOwnsPath(PClass):
    path_idx = field(type=int)
    edge_uuid = field(type=str)
    length = field(type=int)
    def __todict__(self):
        return {
            "path_idx": self.path_idx,
            "edge_uuid": self.edge_uuid,
            "length": self.length,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreItemOwnsPath(
            path_idx=d["path_idx"],
            edge_uuid=d["edge_uuid"],
            length=d["length"],
        )


class ScoreItem2(PClass):
    amount = field(type=int)
    description = field(type=(str, type(None)), initial=None)
    owns_path = field(type=(ScoreItemOwnsPath, type(None)), initial=None)  # Optional[ScoreItemOwnsPath]
    goal = field(type=(ScoreItemGoal, type(None)), initial=None)  # Optional[FrozenGoal]
    bonus = field(type=(ScoreItemBonus, type(None)), initial=None)  # Optional[FrozenGoal] 
    def __todict__(self):
        return {
            "amount": self.amount,
            "description": self.description,
            "owns_path": self.owns_path.__todict__() if self.owns_path else None,
            "goal": self.goal.__todict__() if self.goal else None,
            "bonus": self.bonus.__todict__() if self.bonus else None,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreItem2(
            amount=d["amount"],
            description=d.get("description"),  # Handle None case
            owns_path=ScoreItemOwnsPath.__fromdict__(d["owns_path"]) if d.get("owns_path") else None,
            goal=ScoreItemGoal.__fromdict__(d["goal"]) if d.get("goal") else None,
            bonus=ScoreItemBonus.__fromdict__(d["bonus"]) if d.get("bonus") else None,
        )


class PlayerScore2(PClass):
    public_items = field(type=list)  # List[ScoreItem2]
    private_items = field(type=list)  # List[ScoreItem2]
    def __todict__(self):
        return {
            "public_items": [x.__todict__() for x in self.public_items], 
            "private_items": [x.__todict__() for x in self.private_items],
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerScore2(
            public_items=[ScoreItem2.__fromdict__(x) for x in d["public_items"]],
            private_items=[ScoreItem2.__fromdict__(x) for x in d["private_items"]],
        )


# Implementing the following GraphQL type:
# type ScoreItem {
# 	amount: Int!
# 	code_idx: Int!
# 	json: String
# }
class ScoreItem(PClass):
    amount = field(type=int)
    code_idx = field(type=int)
    def __todict__(self):
        return {
            "amount": self.amount, 
            "code_idx": self.code_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return ScoreItem(
            amount=d["amount"],
            code_idx=d["code_idx"]
        )


class AllottedTime(PClass):
    seconds = field(type=int)
    since_action_idx = field(type=int)
    def __todict__(self):
        return {
            "seconds": self.seconds,
            "since_action_idx": self.since_action_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return AllottedTime(
            seconds=d["seconds"],
            since_action_idx=d["since_action_idx"],
        )


class RemainingAllottedTime(PClass):
    seconds = field(type=int)
    remaining_seconds = field(type=int)
    since_action_idx = field(type=int)
    def __todict__(self):
        return {
            "seconds": self.seconds,
            "remaining_seconds": self.remaining_seconds,
            "since_action_idx": self.since_action_idx,
        }
    @staticmethod
    def __fromdict__(d):
        return RemainingAllottedTime(
            seconds=d["seconds"],
            remaining_seconds=d["remaining_seconds"],
            since_action_idx=d["since_action_idx"],
        )


class PublicState(PClass):
    deadlines = field(type=list)  # List[RemainingAllottedTime|None]
    game_started_at = field(type=str)
    allotted_times = field(type=list)
    all_pieces = field(type=list)  # List[Piece]
    to_play_2 = field(type=list)  # List[int]
    bonus_statuses = field(type=list)  # List[BonusStatus]
    starting_decks = field(type=list)  # List[Deck]
    starting_piles = field(type=list)  # List[Pile]
    history = field(type=list)  # List[PublicAction]
    player_scores = field(type=list)  # List[PublicPlayerScore]
    player_graphs = field(type=list)  # List[PlayerGraph]
    goals = field(type=list)  # List[Goal]
    nodes = field(type=list)  # List[Node]
    edges = field(type=list)  # List[BiEdge]
    regions = field(type=list) # List[Region]
    decks = field(type=list)  # List[PublicDeck]
    piles = field(type=list)  # List[Pile]
    player_idxs = field(type=list)  # List[int]
    players = field(type=list)  # List[PublicPlayer]
    last_to_play = field(type=(int, type(None)), initial=None)
    winners = field(type=list)
    terminal = field(type=bool)
    def __todict__(self):
        return {
            "deadlines": [deadline.__todict__() if deadline else None for deadline in self.deadlines],
            "game_started_at": self.game_started_at,
            "allotted_times": [allotted_time.__todict__() if allotted_time else None for allotted_time in self.allotted_times], # List[AllottedTime|None]
            "all_pieces": [piece.__todict__() for piece in self.all_pieces],
            "to_play_2": self.to_play_2,
            "bonus_statuses": [bs.__todict__() for bs in self.bonus_statuses],
            "starting_decks": [deck.__todict__() for deck in self.starting_decks],
            "starting_piles": [pile.__todict__() for pile in self.starting_piles],
            "history": [x.__todict__() for x in self.history],
            "player_scores": [x.__todict__() for x in self.player_scores],
            "player_graphs": [x.__todict__() for x in self.player_graphs],
            "goals": [goal.__todict__() for goal in self.goals],
            "nodes": [node.__todict__() for node in self.nodes],
            "edges": [edge.__todict__() for edge in self.edges],
            "regions": [region.__todict__() for region in self.regions],
            "decks": [deck.__todict__() for deck in self.decks],
            "piles": [pile.__todict__() for pile in self.piles],
            "player_idxs": self.player_idxs,
            "players": [x.__todict__() for x in self.players],
            "last_to_play": self.last_to_play,
            "winners": self.winners,
            "terminal": self.terminal,
        }
    @staticmethod
    def __fromdict__(d):
        return PublicState(
            deadlines=[RemainingAllottedTime.__fromdict__(x) for x in d["deadlines"]],
            game_started_at=d["game_started_at"],
            allotted_times=[AllottedTime.__fromdict__(x) if x else None for x in d["allotted_times"]], # List[AllottedTime|None]
            all_pieces=[Piece.__fromdict__(x) for x in d["all_pieces"]],
            to_play_2=d["to_play_2"],
            bonus_statuses=[BonusStatus.__fromdict__(x) for x in d["bonus_statuses"]],
            starting_decks=[Deck.__fromdict__(x) for x in d["starting_decks"]],
            starting_piles=[Pile.__fromdict__(x) for x in d["starting_piles"]],
            history=[PublicAction.__fromdict__(x) for x in d["history"]],
            player_scores=[PublicPlayerScore.__fromdict__(x) for x in d["player_scores"]],
            player_graphs=[PlayerGraph.__fromdict__(x) for x in d["player_graphs"]],
            goals=[FrozenGoal.__fromdict__(goal) for goal in d["goals"]],
            nodes=[Node.__fromdict__(n) for n in d["nodes"]],
            edges=[BiEdge.__fromdict__(e) for e in d["edges"]],
            regions=[Region.__fromdict__(r) for r in d["regions"]],
            decks=[PublicDeck.__fromdict__(deck) for deck in d["decks"]],
            piles=[Pile.__fromdict__(x) for x in d["piles"]],
            player_idxs=d["player_idxs"],
            players=[PublicPlayer.__fromdict__(x) for x in d["players"]],
            last_to_play=d.get("last_to_play"),
            winners=d["winners"],
            terminal=d["terminal"],
        )


class PlayerState(PClass):
    public = field(type=PublicState)
    private = field(type=PrivateState)
    def __todict__(self):
        return {
            "public": self.public.__todict__(),
            "private": self.private.__todict__()
        }
    @staticmethod
    def __fromdict__(d):
        return PlayerState(
            public=PublicState.__fromdict__(d["public"]),
            private=PrivateState.__fromdict__(d["private"])
        )


def autoplay(seed, fig, num_players, policy, log=False):
    game_config = initgameconfig(str(uuid4()), "2025-01-01 00:00:00", fig, num_players, seed)
    s = getinitialstate(game_config)
    actions = []
    try:

        while not isterminal(s):
            if log:
                printstate(s)
            a = getnextaction(s, policy)
            s = getnextstate2(s, a)
            actions.append(a)
        
        if (log):
            printstate(s)
        
    except Exception as e:
        logging.error(f"Something went wrong: {str(e)}", exc_info=True)
    finally:
        return (game_config, actions, s)


def get_regions(board_config):
    return [] # TODO: None for now (need to modify BoardConfig to include regions)


def get_nodes(board_config):
    if board_config and board_config.points:
        return [
            Node(idx=idx, uuid=node.uuid, name=f"{idx}", pieces=[]) 
            for idx, node in enumerate(board_config.points)
        ]
    return []


def get_edges(rng, board_config, nodeuuid2idx):
    edges = []
    

    for link_idx, link in enumerate(board_config.links):
        node_1_idx=nodeuuid2idx[link.c1]
        node_2_idx=nodeuuid2idx[link.c2]
        matching_board_paths = [p for p in board_config.board_paths if p.link_num == link.num]

        paths = []
        for matching_board_path in matching_board_paths:
            path_idx = matching_board_path.num - 1
            segments = [
                Segment2(uuid=s.uuid, unit_uuid=s.unit_uuid, pieces=[]) for s in matching_board_path.path.segments
            ]
            path = Path2(
                uuid=str(generate_uuid_with_rng(rng)), 
                idx=path_idx, 
                edge_uuid=link.uuid,
                segments=segments,
            )
            paths.append(path)
        
        if len(paths) == 0:
            print(f"len(board_config.board_paths) = {len(board_config.board_paths)}")
            print("len(board_config.links) =", len(board_config.links))
            raise ValueError(f"No paths found for link {link.uuid} with nodes {link.c1} and {link.c2} and link number {link.num}")

        edges.append(
            BiEdge(
                uuid=link.uuid, 
                start_point_uuid=link.c1, 
                end_point_uuid=link.c2,
                node_1_uuid=link.c1, 
                node_2_uuid=link.c2, 
                node_1_idx=node_1_idx, 
                node_2_idx=node_2_idx, 
                paths=paths, 
                score=link.score
            )
        )

    return edges


def generate_pieces(piece_template, player_idx):
    piece_template_rng = getrng(piece_template.seed + player_idx)
    return [
        Piece(
            uuid=str(generate_uuid_with_rng(piece_template_rng)),
            piece_template_idx=piece_template.idx,
            pile_idx=player_idx,
            player_idx=player_idx
        ) for _ in range(piece_template.quantity)
    ]


def generate_cards(dek):
    cards = []
    idx = 0
    rng = getrng(dek.seed)
    for dek_card in dek.dek_cards:
        for _ in range(dek_card.quantity):
            card = Card(
                idx=idx,
                dek_card_uuid=dek_card.uuid,
                uuid=str(generate_uuid_with_rng(rng)),
                deck_idx=dek.idx,
                is_wild=dek_card.is_wild,
                resource_uuid=dek_card.resource_uuid,
                goal_uuid=dek_card.goal_uuid,
            )
            cards.append(card)
            idx += 1

    return cards


@dispatch(Fig, str)
def getsettingvalue(f, setting_name):
    for setting in f.board_config.settings:
        if setting.name == setting_name:
            return json.loads(setting.value_json)
    return None


@dispatch(State, str)
def getsettingvalue(s, setting_name):
    return getsettingvalue(s.kernel.game_config.fig, setting_name)


@dispatch(GameConfig)
def getinitialstate(game_config):
    rng = getrng(game_config.seed)
    board_config = game_config.fig.board_config
    nodes = get_nodes(board_config)

    piles = []
    for piece_template in board_config.piece_templates:
        if piece_template.has_player:
            for player_idx in range(game_config.num_players):
                pieces = generate_pieces(piece_template, player_idx)
                pile = Pile(
                    player_idx=player_idx,
                    num_pieces=piece_template.quantity,
                    pieces=[piece.uuid for piece in pieces],
                )
                piles.append(pile)

    decks = []
    for dek in board_config.deks:
        cards = generate_cards(dek)
        deck_obj = Deck(
            uuid=dek.uuid,
            idx=dek.idx,
            units=[],
            faceup_spots=[],
            discard=[],
            facedown_stack=[card.uuid for card in cards],
        )
        decks.append(deck_obj)

    # bonuses = game_config.fig.board_config.bonuses
    # bonus_statuses = [
    #     BonusStatus(
    #         bonus_uuid=bonus.uuid, 
    #         winners=[],
    #         player_statuses=[
    #             BonusPlayerStatus(
    #                 player_idx=player_idx,
    #                 score=0,
    #                 longest_trail=None,
    #             )
    #             for player_idx in range(game_config.num_players)
    #         ]
    #     ) 
    #     for bonus in bonuses
    # ]

    # state = State(
    #     bonus_statuses=bonus_statuses,
    #     history=[],
    #     player_scores=[PlayerScore2(public_items=[], private_items=[]) for _ in range(game_config.num_players)],
    #     player_graphs=[
    #         PlayerGraph(
    #             player_idx=player_idx, 
    #             neighbors=[[] for _ in range(len(nodes))]
    #         ) for player_idx in range(game_config.num_players)
    #     ],
    #     nodes = nodes,
    #     edges = edges,
    #     regions = get_regions(board_config),
    #     legal_actions_3=[],
    #     piles=piles,
    #     players=[Player(idx=idx, pieces=[], cards=[], discard_tray=[]) for idx in range(game_config.num_players)],
    #     player_idxs=list(range(game_config.num_players)),
    #     decks=decks,
    #     rng=rng,
    #     last_to_play=None,
    #     winners=[],
    # )

    nodeuuid2idx = {node.uuid: idx for idx, node in enumerate(board_config.points)}
    edges = get_edges(rng, board_config, nodeuuid2idx)
    
    kernel = init_state_kernel(
        rng=rng,
        game_config=game_config,
        edges=edges,
        nodes=nodes,
        decks=decks,
        piles=piles,
        players=[Player(idx=idx, pieces=[], cards=[], discard_tray=[]) for idx in range(game_config.num_players)],
        player_idxs=list(range(game_config.num_players)),
        history=[],
        player_scores=[PlayerScore2(public_items=[], private_items=[]) for _ in range(game_config.num_players)],
        starting_decks=[Deck.__fromdict__(x.__todict__()) for x in decks],
        starting_piles=[Pile.__fromdict__(x.__todict__()) for x in piles],
        goals=board_config.goals,
    )

    kernel = run_kernel_hooks(kernel, INITIALIZATION_HOOKS, True)

    return init_memoized_state(kernel)


@dispatch(StateKernel)
def init_memoized_state(kernel):
    state = State(
        kernel=kernel,
        legal_actions_3=calc_legal_actions3(kernel),
        bonus_statuses_3=calc_bonus_statuses3(kernel),
    )
    return memoize_state(state)


@dispatch(State)
def memoize_state(state):
    state = state.set(player_scores_3=calc_player_scores3(state))
    state = state.set(winners=calc_winners_3(state))
    return state


@dispatch(StateKernel)
def calc_bonus_statuses3(kernel):
    bonus_statuses = [
        calc_bonus_status3(kernel, bonus)
        for bonus in kernel.game_config.fig.board_config.bonuses
    ]
    bonus_statuses = [bs for bs in bonus_statuses if bs is not None]
    return bonus_statuses


@dispatch(State)
def calc_player_scores3(state):
    player_scores = [
        PlayerScore2(
            public_items=score_public_items3(state, player_idx), 
            private_items=score_private_items3(state.kernel, player_idx),
        ) for player_idx in range(len(state.kernel.players))
    ]
    return player_scores


def run_state_hooks(state, hooks, log=False):
    return reduce(
        lambda s, h: run_state_hook(s, h, log), 
        hooks, 
        state
    )


@dispatch(StateKernel, list, bool)
def run_kernel_hooks(kernel, hooks, log=False):
    return reduce(
        lambda k, h: run_kernel_hook(k, h, log), 
        hooks, 
        kernel
    )


def run_accept_action_hooks(state, action, hooks, log=False):
    # Just like "run_state_action_hooks", but returns immediately returns True if any hook returns True, otherwise returns False
    for hook in hooks:
        is_accepted, reason = run_state_action_hook(state, action, hook, log)
        if is_accepted is not None and is_accepted:
            return True, reason
        elif is_accepted is not None and not is_accepted:
            return False, reason
    return False, "No hook accepted the action"


def run_state_action_hooks(state, action, hooks, log=False):
    return reduce(
        lambda s, h: run_state_action_hook(s, action, h, log), 
        hooks, 
        state
    )


@dispatch(State, int)
def score_public_items3(state, player_idx):
    items = []
    for edge in state.kernel.edges:
        for path in edge.paths:
            if len(path.segments) > 0:
                first_segment = path.segments[0]
                if first_segment.pieces and len(first_segment.pieces) > 0:
                    first_piece = state.kernel.pieceuuid2piece[first_segment.pieces[0]]
                    if first_piece.player_idx == player_idx:
                        items.append(
                            ScoreItem2(
                                amount=edge.score,
                                owns_path=ScoreItemOwnsPath(
                                    path_idx=path.idx, 
                                    edge_uuid=edge.uuid,
                                    length=len(path.segments),
                                ),
                                description="Player {} owns edge {}".format(player_idx, edge.uuid),
                            )
                        )
    for bonus_status in state.bonus_statuses_3:
        bonus_idx = state.kernel.bonusuuid2bonusidx.get(bonus_status.bonus_uuid)
        bonus = state.kernel.game_config.fig.board_config.bonuses[bonus_idx] if bonus_idx is not None else None
        if bonus:
            if player_idx in bonus_status.winners:
                items.append(
                    ScoreItem2(
                        amount=bonus.score, 
                        description="Player {} wins bonus {}".format(player_idx, bonus.code),
                        bonus=ScoreItemBonus(bonus_uuid=bonus.uuid),
                    )
                )
    return items


@dispatch(State, int)
def score_public_items(state, player_idx):
    items = []
    for edge in state.edges:
        for path in edge.paths:
            if len(path.segments) > 0:
                first_segment = path.segments[0]
                if first_segment.pieces and len(first_segment.pieces) > 0:
                    first_piece = state.kernel.pieceuuid2piece[first_segment.pieces[0]]
                    if first_piece.player_idx == player_idx:
                        items.append(
                            ScoreItem2(
                                amount=edge.score,
                                owns_path=ScoreItemOwnsPath(
                                    path_idx=path.idx, 
                                    edge_uuid=edge.uuid,
                                    length=len(path.segments),
                                ),
                                description="Player {} owns edge {}".format(player_idx, edge.uuid),
                            )
                        )
    for bonus_status in state.bonus_statuses:
        bonus_idx = state.kernel.bonusuuid2bonusidx.get(bonus_status.bonus_uuid)
        bonus = state.kernel.game_config.fig.board_config.bonuses[bonus_idx] if bonus_idx is not None else None
        if bonus:
            if player_idx in bonus_status.winners:
                items.append(
                    ScoreItem2(
                        amount=bonus.score, 
                        description="Player {} wins bonus {}".format(player_idx, bonus.code),
                        bonus=ScoreItemBonus(bonus_uuid=bonus.uuid),
                    )
                )
    return items


@dispatch(State, int)
def score_private_items(state, player_idx):
    items = []
    goaluuid2goal = {goal.uuid: goal for goal in state.kernel.goals}
    goal_completions = get_goal_completions(state.kernel, player_idx)
    complete_goal_uuids = [gc.goal_uuid for gc in goal_completions if gc.complete]
    incomplete_goal_uuids = [gc.goal_uuid for gc in goal_completions if not gc.complete]
    for complete_goal_uuid in complete_goal_uuids:
        goal = goaluuid2goal[complete_goal_uuid]
        items.append(
            ScoreItem2(
                amount=goal.score, 
                description="Player {} completed goal {}".format(player_idx, complete_goal_uuid),
                goal=ScoreItemGoal(goal_uuid=complete_goal_uuid, complete=True)
            )
        )
    for incomplete_goal_uuid in incomplete_goal_uuids:
        goal = goaluuid2goal[incomplete_goal_uuid]
        items.append(
            ScoreItem2(
                amount=(-1*goal.score), 
                description="Player {} incomplete goal {}".format(player_idx, incomplete_goal_uuid),
                goal=ScoreItemGoal(goal_uuid=incomplete_goal_uuid, complete=False)
            )
        )
    return items


@dispatch(StateKernel, int)
def score_private_items3(kernel, player_idx):
    items = []
    goaluuid2goal = {goal.uuid: goal for goal in kernel.goals}
    goal_completions = get_goal_completions3(kernel, player_idx)
    complete_goal_uuids = [gc.goal_uuid for gc in goal_completions if gc.complete]
    incomplete_goal_uuids = [gc.goal_uuid for gc in goal_completions if not gc.complete]
    for complete_goal_uuid in complete_goal_uuids:
        goal = goaluuid2goal[complete_goal_uuid]
        items.append(
            ScoreItem2(
                amount=goal.score, 
                description="Player {} completed goal {}".format(player_idx, complete_goal_uuid),
                goal=ScoreItemGoal(goal_uuid=complete_goal_uuid, complete=True)
            )
        )
    for incomplete_goal_uuid in incomplete_goal_uuids:
        goal = goaluuid2goal[incomplete_goal_uuid]
        items.append(
            ScoreItem2(
                amount=(-1*goal.score), 
                description="Player {} incomplete goal {}".format(player_idx, incomplete_goal_uuid),
                goal=ScoreItemGoal(goal_uuid=incomplete_goal_uuid, complete=False)
            )
        )
    return items


def handle_last_to_play(game):
    if game.last_to_play is None:
        # If any player can less than 3 pieces, the game is terminal
        for player in game.players:
            if len(player.pieces) < 3:
                return game.set(last_to_play=player.idx)
    elif game.last_to_play == game.kernel.history[-1].legal_action.player_idx:
        if not game.legal_actions_3:
            return game.set(terminal=True)
    return game


@dispatch(State)
def getfinalscores(state):
    return [
        getpublicplayerscore(state, state.player_scores_3[player_idx]).total
        for player_idx in range(len(state.kernel.players))
    ]


@dispatch(State)
def getfinalscores3(state):
    return [
        getpublicplayerscore(state, state.player_scores_3[player_idx]).total
        for player_idx in range(len(state.kernel.players))
    ]


def handle_calc_winners(game):
    if isterminal(game):
        players_with_highest_score = []
        highest_score = -1000
        final_scores = getfinalscores(game)
        for player_idx in range(len(game.players)):
            final_score = final_scores[player_idx]
            if final_score > highest_score:
                highest_score = final_score
                players_with_highest_score = [player_idx]
            elif final_score == highest_score:
                players_with_highest_score.append(player_idx)
        return game.set(
            winners=players_with_highest_score,
        )

    return game


@dispatch(State)
def calc_winners_3(state):
    if isterminal(state):
        players_with_highest_score = []
        highest_score = -1000
        final_scores = getfinalscores3(state)
        for player_idx in range(len(state.kernel.players)):
            final_score = final_scores[player_idx]
            if final_score > highest_score:
                highest_score = final_score
                players_with_highest_score = [player_idx]
            elif final_score == highest_score:
                players_with_highest_score.append(player_idx)
        return players_with_highest_score

    return []


def default_handle_terminal(game):
    game = handle_last_to_play(game)
    game = handle_calc_winners(game)
    return game


def calc_bonus_status(game, bonus):
    if not bonus:
        return None
    if bonus.code == "longest-trail":
        return get_bonus_status_longest_trail(game, bonus)
    return None


@dispatch(StateKernel, FrozenBonus)
def calc_bonus_status3(kernel, bonus):
    if not bonus:
        return None
    if bonus.code == "longest-trail":
        return get_bonus_status_longest_trail3(kernel, bonus)
    return None


@dispatch(StateKernel, FrozenBonus)
def get_bonus_status_longest_trail3(kernel, bonus):
    longest_trail = 0
    winners = []
    player_longest_trail_lens = []

    for player_idx in range(kernel.game_config.num_players):
        trail_length = get_longest_path_length3(kernel, player_idx)
        player_longest_trail_lens.append(trail_length)
        if trail_length > longest_trail:
            longest_trail = trail_length
            winners = [player_idx]
        elif trail_length == longest_trail and trail_length > 0:
            winners.append(player_idx)

    player_statuses = [
        BonusPlayerStatus(
            player_idx=player_idx,
            score=bonus.score if player_idx in winners else 0,
            longest_trail=LongestTrailBonusPlayerStatus(
                length=player_longest_trail_len
            ),
        )
        for player_idx, player_longest_trail_len in enumerate(player_longest_trail_lens)
    ]

    return BonusStatus(
        bonus_uuid=bonus.uuid,
        winners=winners,
        player_statuses=player_statuses,
    )


def get_bonus_status_longest_trail(state, bonus):
    longest_trail = 0
    winners = []
    player_longest_trail_lens = []

    for player_idx in range(state.kernel.game_config.num_players):
        trail_length = get_longest_path_length(state, player_idx)
        player_longest_trail_lens.append(trail_length)
        if trail_length > longest_trail:
            longest_trail = trail_length
            winners = [player_idx]
        elif trail_length == longest_trail and trail_length > 0:
            winners.append(player_idx)

    player_statuses = [
        BonusPlayerStatus(
            player_idx=player_idx,
            score=bonus.score if player_idx in winners else 0,
            longest_trail=LongestTrailBonusPlayerStatus(
                length=player_longest_trail_len
            ),
        )
        for player_idx, player_longest_trail_len in enumerate(player_longest_trail_lens)
    ]

    return BonusStatus(
        bonus_uuid=bonus.uuid,
        winners=winners,
        player_statuses=player_statuses,
    )


def handle_bonus_statuses(state):
    bonus_statuses = [
        calc_bonus_status(state, bonus)
        for bonus in state.kernel.game_config.fig.board_config.bonuses
    ]
    # Remove all None bonus statuses
    bonus_statuses = [bs for bs in bonus_statuses if bs is not None]
    return state.set(bonus_statuses=bonus_statuses)


def default_handle_scoring(game):
    game = handle_bonus_statuses(game)
    player_scores = [
        PlayerScore2(
            public_items=score_public_items(game, player_idx), 
            private_items=score_private_items(game, player_idx),
        ) for player_idx in range(len(game.players))
    ]
    return game.set(player_scores=player_scores)


@dispatch(StateKernel, Action2)
def default_handle_action(kernel, action):
    if action.legal_action.discard:
        return handle_discard_action(kernel, action)
    if action.legal_action.keep:
        return handle_keep_action(kernel, action)
    if action.legal_action.move_pieces_to_path:
        kernel = handle_move_pieces_to_path_action(kernel, action)
        return handle_after_move_pieces_to_path_action(kernel, action)
    if action.legal_action.faceup_draw:
        return handle_faceup_draw_action(kernel, action)
    if action.legal_action.draw:
        return handle_draw_action(kernel, action)
    if action.legal_action.draw_discard:
        return handle_draw_discard_action(kernel, action)

    return kernel


@dispatch(StateKernel, Action2)
def default_after_accept_action(kernel, action):
    # Remove all actions for matching player of action
    if not kernel or not action or not action.legal_action:
        return kernel
    player_idx = action.legal_action.player_idx
    if player_idx < 0 or player_idx >= len(kernel.players):
        return kernel
    history = kernel.history + [action]
    return kernel.set(
        history=history,
    )


@dispatch(StateKernel)
def recycle_decks_if_needed(kernel):
    for deck_idx in range(len(kernel.decks)):
        print("recycle_decks_if_needed for deck_idx =", deck_idx)
        kernel = recycle_if_needed(kernel, deck_idx)
    return kernel


@dispatch(StateKernel)
def replenish_decks_if_needed(kernel):
    for deck_idx in range(len(kernel.decks)):
        kernel = replenish_faceup_if_needed(kernel, deck_idx)
    return kernel


@dispatch(StateKernel, int, int)
def replenish_faceup_spot_if_needed(kernel, deck_idx, spot_idx):
    deck = kernel.decks[deck_idx]

    if deck.faceup_spots[spot_idx] is not None:
        return kernel
    
    if len(deck.facedown_stack) == 0:
        return kernel
    
    deck.faceup_spots[spot_idx] = deck.facedown_stack.pop()

    kernel = ensure_faceup_spots_valid(kernel)

    return kernel.set(
        decks=kernel.decks,
    )


@dispatch(StateKernel, int)
def replenish_faceup_if_needed(kernel, deck_idx):
    deck = kernel.decks[deck_idx]
    for spot_idx in range(len(deck.faceup_spots)):
        kernel = replenish_faceup_spot_if_needed(kernel, deck_idx, spot_idx)
    return kernel


@dispatch(StateKernel, int)
def recycle_if_needed(kernel, deck_idx):
    deck = kernel.decks[deck_idx]
    if len(deck.facedown_stack) == 0:
        shuffled_discards = list(deck.discard)
        kernel.rng.shuffle(shuffled_discards)
        deck = deck.set(
            facedown_stack = shuffled_discards,
            discard = []
        )
        kernel = set_deck(kernel, deck.idx, deck)
    return kernel


@dispatch(StateKernel, Action2)
def handle_draw_action(kernel, action):
    if not kernel or not action or not action.legal_action or not action.legal_action.draw:
        return kernel
    legal_action = action.legal_action
    draw = legal_action.draw
    player = kernel.players[legal_action.player_idx]
    deck = kernel.decks[draw.deck_idx]
    
    if len(deck.facedown_stack) == 0:
        return kernel  # No cards to draw

    for _ in range(draw.quantity):
        drawn_card = deck.facedown_stack.pop()
        player.cards.append(drawn_card)
        kernel = recycle_if_needed(kernel, draw.deck_idx)

    kernel = kernel.set(
        players=kernel.players,
    )

    # TODO: extract this out to user-defined function/hook
    # if draw.quantity == 1:
    #     game = append_follow_up_draw_legal_actions(game, action)

    return kernel


@dispatch(StateKernel, Action2)
def handle_draw_discard_action(kernel, action):
    if not kernel or not action or not action.legal_action or not action.legal_action.draw_discard:
        return kernel
    legal_action = action.legal_action
    draw_discard = legal_action.draw_discard
    player = kernel.players[legal_action.player_idx]
    deck = kernel.decks[draw_discard.deck_idx]
    
    if len(deck.facedown_stack) == 0:
        return kernel  # No cards to draw

    for _ in range(draw_discard.quantity):
        drawn_card = deck.facedown_stack.pop()
        player.discard_tray.append(drawn_card)

    return kernel.set(
        players=kernel.players,
        decks=kernel.decks,
    )


@dispatch(StateKernel, Action2)
def get_follow_up_draw_legal_actions(kernel, action):
    to_return = []
    legal_action = action.legal_action
    if len(kernel.history) >= 2:
        last_action = kernel.history[-2]
        if (last_action.legal_action.player_idx != legal_action.player_idx) or last_action.legal_action.name == "INITIAL-GOAL-KEEP":
            
            if len(kernel.decks[0].facedown_stack) >= 1:
                to_return.append(
                    LegalAction(
                        auto_preferred=True,
                        player_idx=legal_action.player_idx,
                        name="DRAW",
                        instruction="draw a unit",
                        allotted_seconds=DEFAULT_ALLOTTED_SECONDS,
                        allotted_since_action_idx=(len(kernel.history) - 1),
                        draw=LegalActionDraw(
                            deck_idx=0,
                            quantity=1,
                        )
                    )
                )
            
            for card_uuid in kernel.decks[0].faceup_spots:
                if card_uuid:
                    if not kernel.carduuid2card[card_uuid].is_wild:
                        to_return.append(
                            LegalAction(
                                player_idx=legal_action.player_idx,
                                name="FACEUP-DRAW",
                                instruction="draw a faceup unit",
                                allotted_seconds=DEFAULT_ALLOTTED_SECONDS,
                                allotted_since_action_idx=(len(kernel.history) - 1),
                                faceup_draw=LegalActionFaceupDraw(
                                    deck_idx=0,
                                    card_uuid=card_uuid,
                                )
                            )
                        )
    
    return to_return


@dispatch(StateKernel, int)
def get_num_faceup_wilds(kernel, deck_idx):
    deck = kernel.decks[deck_idx]
    non_empty_spots = [spot for spot in deck.faceup_spots if spot]
    if not non_empty_spots:
        return 0
    return sum(1 for card_uuid in non_empty_spots if kernel.carduuid2card[card_uuid].is_wild)


@dispatch(StateKernel)
def ensure_faceup_spots_valid(kernel):
    for deck in kernel.decks:
        max_iters = 5
        i = 0
        while i < max_iters and get_num_faceup_wilds(kernel, deck.idx) >= 3:
            kernel = discardfaceup_shuffle_flip(kernel, deck.idx)
            i += 1
    return kernel


@dispatch(StateKernel, int)
def discardfaceup_shuffle_flip(kernel, deck_idx):
    deck = kernel.decks[deck_idx]
    num_faceup_spots = len(deck.faceup_spots)
    for faceup_spot in deck.faceup_spots:
        if faceup_spot:
            deck.discard.append(faceup_spot)
    deck = deck.set(faceup_spots=[])
    while len(deck.discard) > 0:
        card = deck.discard.pop()
        deck.facedown_stack.append(card)
    deck = shuffle(kernel.rng, deck)
    kernel = set_deck(kernel, deck.idx, deck)
    kernel = flip_cards(kernel, deck.idx, num_faceup_spots)
    return kernel


@dispatch(StateKernel, Action2)
def handle_faceup_draw_action(kernel, action):
    if not kernel or not action or not action.legal_action or not action.legal_action.faceup_draw:
        return kernel
    legal_action = action.legal_action
    faceup_draw = legal_action.faceup_draw
    player = kernel.players[legal_action.player_idx]
    deck = kernel.decks[faceup_draw.deck_idx]
    # find the faceup spot idx with uuid "faceup_draw.card_uuid"
    spot_idx = next((i for i, card_uuid in enumerate(deck.faceup_spots) if card_uuid == faceup_draw.card_uuid), None)
    drawn_card = deck.faceup_spots[spot_idx] if spot_idx is not None else None
    player.cards.append(drawn_card)
    
    deck.faceup_spots[spot_idx] = None
    kernel = kernel.set(decks=kernel.decks)
    kernel = replenish_faceup_spot_if_needed(kernel, faceup_draw.deck_idx, spot_idx)

    # Prevent an extra draw if last draw was a face-wild-draw
    # if not game.kernel.carduuid2card[drawn_card].is_wild:
    #     # TODO: extract this out to user-defined function/hook
    #     game = append_follow_up_draw_legal_actions(game, action)

    return kernel.set(
        players=kernel.players,
    )


@dispatch(StateKernel, Action2)
def handle_after_move_pieces_to_path_action(kernel, action):
    kernel = handle_move_bonus_cards(kernel, action)
    return kernel


@dispatch(StateKernel, Action2)
def handle_move_bonus_cards(kernel, action):
    return handle_move_longest_path_card(kernel, action)


# Take a random walk on the player's graph. A node can be visiting more than once, but an edge cannot be visited more than once.
# Example graph: PlayerGraph(player_idx=0, neighbors=[[], [], [], [], [], [], [], [], [], [], [30]
def random_player_graph_walk(game, player_idx):
    player_graph = game.player_graphs[player_idx]
    nodes_indices_with_neighbors = [i for i, neighbors in enumerate(player_graph.neighbors) if neighbors]
    
    if not nodes_indices_with_neighbors:
        return None
    
    rng = random.Random()
    random_start_node_idx = rng.choice(nodes_indices_with_neighbors)

    def choose_next_node(visited_nodes, visited_edges):
        current_node_idx = visited_nodes[-1]
        neighbors = player_graph.neighbors[current_node_idx]
        if not neighbors:
            return None
        
        shuffled_neighbors = neighbors.copy()
        rng.shuffle(shuffled_neighbors)
        
        for neighbor in shuffled_neighbors:
            edge = (min(current_node_idx, neighbor), max(current_node_idx, neighbor))
            if edge not in visited_edges:
                return neighbor
        
        return None

    def walk(visited_nodes, visited_edges):
        next_node = choose_next_node(visited_nodes, visited_edges)
        if next_node is None:
            return (visited_nodes, visited_edges)
        next_edge = (min(visited_nodes[-1], next_node), max(visited_nodes[-1], next_node))
        return walk(
            visited_nodes + [next_node], 
            set(list(visited_edges) + [next_edge])
        )

    return walk([random_start_node_idx], set([]))


@dispatch(StateKernel, int)
def random_player_graph_walk3(kernel, player_idx):
    player_graph = kernel.player_graphs_3[player_idx]
    nodes_indices_with_neighbors = [i for i, neighbors in enumerate(player_graph.neighbors) if neighbors]
    
    if not nodes_indices_with_neighbors:
        return None
    
    rng = random.Random()
    random_start_node_idx = rng.choice(nodes_indices_with_neighbors)

    def choose_next_node(visited_nodes, visited_edges):
        current_node_idx = visited_nodes[-1]
        neighbors = player_graph.neighbors[current_node_idx]
        if not neighbors:
            return None
        
        shuffled_neighbors = neighbors.copy()
        rng.shuffle(shuffled_neighbors)
        
        for neighbor in shuffled_neighbors:
            edge = (min(current_node_idx, neighbor), max(current_node_idx, neighbor))
            if edge not in visited_edges:
                return neighbor
        
        return None

    def walk(visited_nodes, visited_edges):
        next_node = choose_next_node(visited_nodes, visited_edges)
        if next_node is None:
            return (visited_nodes, visited_edges)
        next_edge = (min(visited_nodes[-1], next_node), max(visited_nodes[-1], next_node))
        return walk(
            visited_nodes + [next_node], 
            set(list(visited_edges) + [next_edge])
        )

    return walk([random_start_node_idx], set([]))


@dispatch(StateKernel)
def find_player_with_longest_path(kernel):
    longest_path_player_idx = None
    longest_path_length = 0

    for player_idx in range(kernel.game_config.num_players):
        path_length = get_longest_path_length(kernel, player_idx)
        if path_length > longest_path_length:
            longest_path_length = path_length
            longest_path_player_idx = player_idx

    if longest_path_player_idx is None:
        return None
    
    return kernel.players[longest_path_player_idx]


@dispatch(State, set)
def calc_path_len_from_edges(state, edge_tuples):
    if edge_tuples is None:
        return 0
    edge_lens = []
    for edge_tuple in edge_tuples:
        edge_uuid = state.kernel.edgetuple2uuid.get(edge_tuple)
        edge_idx = state.kernel.edgeuuid2idx.get(edge_uuid)
        if edge_idx is not None:
            edge = state.edges[edge_idx]
            if edge and edge.paths:
                first_path = edge.paths[0]
                edge_len = len(first_path.segments)
                edge_lens.append(edge_len)

    return sum(edge_lens)


@dispatch(StateKernel, set)
def calc_path_len_from_edges3(kernel, edge_tuples):
    if edge_tuples is None:
        return 0
    edge_lens = []
    for edge_tuple in edge_tuples:
        edge_uuid = kernel.edgetuple2uuid.get(edge_tuple)
        edge_idx = kernel.edgeuuid2idx.get(edge_uuid)
        if edge_idx is not None:
            edge = kernel.edges[edge_idx]
            if edge and edge.paths:
                first_path = edge.paths[0]
                edge_len = len(first_path.segments)
                edge_lens.append(edge_len)

    return sum(edge_lens)


@dispatch(StateKernel, int)
def get_longest_path_length3(kernel, player_idx):
    longest_path_length = 0
    num_iters_since_change = 0

    for _ in range(1000):
        walk = random_player_graph_walk3(kernel, player_idx)
        if not walk:
            return 0
        path_len = calc_path_len_from_edges3(kernel, walk[1])
        if path_len > longest_path_length:
            longest_path_length = path_len
            num_iters_since_change = 0
        else:
            num_iters_since_change += 1
        # If we haven't found a longer path in 500 iterations, return
        if num_iters_since_change > 500:
            return longest_path_length

    print("longest_path_length: ", longest_path_length)
    return longest_path_length


@dispatch(StateKernel, int)
def get_longest_path_length(kernel, player_idx):
    longest_path_length = 0
    num_iters_since_change = 0

    for _ in range(1000):
        walk = random_player_graph_walk(kernel, player_idx)
        if not walk:
            return 0
        path_len = calc_path_len_from_edges(kernel, walk[1])
        if path_len > longest_path_length:
            longest_path_length = path_len
            num_iters_since_change = 0
        else:
            num_iters_since_change += 1
        # If we haven't found a longer path in 500 iterations, return
        if num_iters_since_change > 500:
            return longest_path_length

    print("longest_path_length: ", longest_path_length)
    return longest_path_length


@dispatch(StateKernel, Action2)
def handle_move_longest_path_card(kernel, action):
    player = find_player_with_longest_path(kernel)

    if not kernel or not player:
        return kernel

    longest_path_card = None

    if len(kernel.decks) > 2:
        longest_path_deck = kernel.decks[2]
        if longest_path_deck.facedown_stack:
            # Move the longest path card to the player's hand
            longest_path_card = longest_path_deck.facedown_stack.pop()
        else:
            # Search for the longest path card in each player's cards
            player_with_card = find_player_with_longest_path_card(kernel)
            if player_with_card:
                # Find the index of the card from the player's cards, then pop it
                card_idx = next((i for i, card_uuid in enumerate(player_with_card.cards) if kernel.carduuid2card[card_uuid].deck_idx == 2), None)
                if card_idx is not None:
                    longest_path_card = player_with_card.cards.pop(card_idx)


    if longest_path_card:
        player.cards.append(longest_path_card)

    return kernel.set(
        players=kernel.players,
        decks=kernel.decks,
    )


def find_player_with_longest_path_card(game):
    for player in game.players:
        if any(game.kernel.carduuid2card[card_uuid].deck_idx == 2 for card_uuid in player.cards):
            return player
    return None


@dispatch(StateKernel, Action2)
def handle_move_pieces_to_path_action(kernel, action):
    if not kernel or not action or not action.legal_action or not action.legal_action.move_pieces_to_path:
        return kernel
    
    legal_action = action.legal_action
    move_pieces_to_path = legal_action.move_pieces_to_path
    default = move_pieces_to_path.default
    override = action.move_pieces_to_path
    if override:
        default = default.set(piece_uuids=override.piece_uuids)
        default = default.set(card_uuids=override.card_uuids)

    player = kernel.players[legal_action.player_idx]
    if not player or not player.pieces:
        return kernel

    path_idx = move_pieces_to_path.path_idx
    path = kernel.idx2path[path_idx]

    if path is None or not path.segments:
        return kernel

    for piece_uuid, segment in zip(default.piece_uuids, path.segments):
        # Find the piece in the player's pieces
        piece_idx = next((i for i, player_piece_uuid in enumerate(player.pieces) if player_piece_uuid == piece_uuid), None)
        if piece_idx is not None:
            # Remove the piece from player's pieces
            piece = player.pieces.pop(piece_idx)
            segment.pieces.append(piece)

    for card_uuid in default.card_uuids:
        # Find the card in the player's cards
        card_idx = next((i for i, player_card_uuid in enumerate(player.cards) if player_card_uuid == card_uuid), None)
        if card_idx is not None:
            # Remove the card from player's cards
            card_uuid = player.cards.pop(card_idx)
            # add to discard
            kernel.decks[kernel.carduuid2card[card_uuid].deck_idx].discard.append(card_uuid)

    kernel = recycle_decks_if_needed(kernel)
    kernel = replenish_decks_if_needed(kernel)
    kernel = kernel.set(players=kernel.players)
    kernel = kernel.set(idx2path=kernel.idx2path)

    return kernel


@dispatch(State, int)
def calc_player_graph(state, player_idx):
    nodes = state.nodes
    node2neighbors = {node.idx: set() for node in nodes}

    for edge in state.edges:
        for path in edge.paths:
            for segment in path.segments:
                if segment.pieces and segment.pieces[0] and state.kernel.pieceuuid2piece[segment.pieces[0]].player_idx == player_idx:
                    # print(f"[path_idx {path.idx}] edge.start_point_uuid {edge.start_point_uuid} ({edge.node_1_idx}) connected to edge.end_point_uuid {edge.end_point_uuid} ({edge.node_2_idx}) player_idx: {player_idx}")
                    node2neighbors[edge.node_1_idx].add(edge.node_2_idx)
                    node2neighbors[edge.node_2_idx].add(edge.node_1_idx)
    
    return PlayerGraph(
        player_idx=player_idx, 
        neighbors=[
            list(node2neighbors.get(node_idx, set())) 
            for node_idx in range(len(nodes))
        ]
    )


@dispatch(list, list, dict, int)
def calc_player_graph3(nodes, edges, pieceuuid2piece, player_idx):
    node2neighbors = {node.idx: set() for node in nodes}

    for edge in edges:
        for path in edge.paths:
            for segment in path.segments:
                if segment.pieces and segment.pieces[0] and pieceuuid2piece[segment.pieces[0]].player_idx == player_idx:
                    # print(f"[path_idx {path.idx}] edge.start_point_uuid {edge.start_point_uuid} ({edge.node_1_idx}) connected to edge.end_point_uuid {edge.end_point_uuid} ({edge.node_2_idx}) player_idx: {player_idx}")
                    node2neighbors[edge.node_1_idx].add(edge.node_2_idx)
                    node2neighbors[edge.node_2_idx].add(edge.node_1_idx)
    
    return PlayerGraph(
        player_idx=player_idx, 
        neighbors=[
            list(node2neighbors.get(node_idx, set())) 
            for node_idx in range(len(nodes))
        ]
    )


def calc_player_graphs(state):
    game_config = state.kernel.game_config
    return [
        calc_player_graph(state, player_idx) 
        for player_idx in range(game_config.num_players)
    ]


@dispatch(list, list, dict, GameConfig)
def calc_player_graphs3(nodes, edges, pieceuuid2piece, game_config):
    return [
        calc_player_graph3(nodes, edges, pieceuuid2piece, player_idx)
        for player_idx in range(game_config.num_players)
    ]


# Does the opposite of handle_discard_action, i.e., it keeps the cards in the discard tray (the other cards are discarded)
@dispatch(StateKernel, Action2)
def handle_keep_action(kernel, action):
    if not kernel or not action or not action.legal_action.keep:
        return kernel

    deck_idx = action.legal_action.keep.deck_idx
    if deck_idx < 0 or deck_idx >= len(kernel.decks):
        return kernel

    deck = kernel.decks[deck_idx]
    if not deck:
        return kernel

    player = kernel.players[action.legal_action.player_idx]
    if not player:
        return kernel

    # Keep the specified cards in the discard tray
    kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid in action.keep.card_uuids]
    non_kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid not in action.keep.card_uuids]


    # Discard the non-kept cards to the deck's discard pile
    deck.discard.extend(non_kept_cards)
    
    # Clear the discard tray and add the kept cards back
    player.cards.extend([c for c in kept_cards if c is not None])

    player.discard_tray.clear()
    return kernel.set(decks=kernel.decks, players=kernel.players)


@dispatch(StateKernel, Action2)
def handle_discard_action(kernel, action):
    print("****************************** handle_discard_action 1", action)
    if not kernel or not action or not action.legal_action.discard:
        return kernel

    print("****************************** handle_discard_action 2", action)

    deck_idx = action.legal_action.discard.deck_idx
    if deck_idx < 0 or deck_idx >= len(kernel.decks):
        return kernel

    print("****************************** handle_discard_action 3", deck_idx)

    deck = kernel.decks[deck_idx]
    print("****************************** handle_discard_action 3.5", deck)
    if not deck:
        return kernel

    print("****************************** handle_discard_action 4")

    player = kernel.players[action.legal_action.player_idx]
    if not player:
        return kernel

    # Keep the specified cards in the discard tray
    non_kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid in action.discard.card_uuids]
    kept_cards = [card_uuid for card_uuid in player.discard_tray if card_uuid not in action.discard.card_uuids]

    print("****************************** handle_discard_action 5", kept_cards)
    print("****************************** handle_discard_action 6", non_kept_cards)

    # Discard the non-kept cards to the deck's discard pile
    deck.discard.extend(non_kept_cards)
    
    # Clear the discard tray and add the kept cards back
    player.cards.extend([c for c in kept_cards if c is not None])

    player.discard_tray.clear()
    print("****************************** handle_discard_action 10 kept_cards: ", kept_cards)

    return kernel.set(decks=kernel.decks, players=kernel.players)


@dispatch(StateKernel)
def shuffle_all_decks(kernel):
    if not kernel or not kernel.decks:
        return kernel

    for i in range(len(kernel.decks)):
        kernel = shuffle_deck(kernel, i)

    return kernel


@dispatch(StateKernel, int, Deck)
def set_deck(kernel, deck_idx, deck):
    new_decks = kernel.decks[:deck_idx] + [deck] + kernel.decks[deck_idx + 1:]
    return kernel.set(decks=new_decks)


def shuffle(rng, deck):
    shuffled_cards = list(deck.facedown_stack)
    rng.shuffle(shuffled_cards)
    return deck.set(facedown_stack=shuffled_cards)


@dispatch(StateKernel, int)
def shuffle_deck(kernel, deck_idx):
    if not kernel or not kernel.decks or deck_idx < 0 or deck_idx >= len(kernel.decks):
        return kernel
    
    deck = kernel.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return kernel

    shuffled_deck = shuffle(kernel.rng, deck)
    kernel = set_deck(kernel, deck_idx, shuffled_deck)
    return kernel


@dispatch(StateKernel)
def shuffle_player_order(kernel):
    if not kernel or not kernel.player_idxs:
        return kernel
    
    rng = kernel.rng
    shuffled_idxs = list(kernel.player_idxs)
    rng.shuffle(shuffled_idxs)
    
    return kernel.set(player_idxs=shuffled_idxs)


@dispatch(StateKernel, int, int)
def flip_cards(kernel, deck_idx, num_cards):
    if not kernel or deck_idx < 0 or deck_idx >= len(kernel.decks):
        return kernel
    
    deck = kernel.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return kernel

    # Flip the top num_cards from the facedown_stack to the faceup_spots
    for _ in range(num_cards):
        if deck.facedown_stack:
            card = deck.facedown_stack.pop()
            deck.faceup_spots.append(card)

    return kernel.set(decks=kernel.decks)


@dispatch(StateKernel)
def distribute_all_piles(kernel):
    if not kernel or not kernel.piles:
        return kernel

    for pile in kernel.piles:
        player_idx = pile.player_idx
        if player_idx < 0 or player_idx >= len(kernel.players):
            continue
        
        player = kernel.players[player_idx]
        player.pieces.extend(pile.pieces)
        pile.pieces.clear()  # Clear the pile after distribution

    return kernel.set(players=kernel.players, piles=kernel.piles)


@dispatch(StateKernel, int, int)
def deal_cards_to_each_player_discard_tray(kernel, deck_idx, num_cards):
    if not kernel or deck_idx < 0 or deck_idx >= len(kernel.decks):
        return kernel

    deck = kernel.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return kernel

    for player in kernel.players:
        # Deal cards to the player's discard tray
        for _ in range(num_cards):
            if deck.facedown_stack:
                card = deck.facedown_stack.pop()
                player.discard_tray.append(card)

    return kernel.set(players=kernel.players, decks=kernel.decks)


@dispatch(StateKernel, int, int)
def deal_cards_to_each_player(kernel, deck_idx, num_cards):
    if not kernel or deck_idx < 0 or deck_idx >= len(kernel.decks):
        return kernel

    deck = kernel.decks[deck_idx]
    if not deck or not deck.facedown_stack:
        return kernel

    for player in kernel.players:
        player_hand = player.cards
        # Deal cards to the player's hand
        for _ in range(num_cards):
            if deck.facedown_stack:
                card = deck.facedown_stack.pop()
                player_hand.append(card)

    return kernel.set(players=kernel.players, decks=kernel.decks)


def default_accept_action(game, action):

    # Returns true if action.legal_action is found in game.legal_actions_3
    # The comparision is by value, not by reference
    if action.legal_action not in game.legal_actions_3:
        return False, "Action not found in legal actions"
    
    # Check if "action.move_pieces_to_path" is not None
    if action.move_pieces_to_path: 
        is_legal = is_move_pieces_to_path_action_legal(game, action)
        if not is_legal:
            return False, "Move pieces to path action is not legal"
    
    return True, "Action is legal"


@dispatch(State, Action2)
def is_move_pieces_to_path_action_legal(state, action):
    # print("******************************1234 is_move_pieces_to_path_action_legal 1")
    player_idx = action.legal_action.player_idx
    proposed_cards_uuids = action.move_pieces_to_path.card_uuids
    path_idx = action.legal_action.move_pieces_to_path.path_idx
    path = state.kernel.idx2path[path_idx]
    proposed_cards = [card_uuid for card_uuid in state.kernel.players[player_idx].cards if card_uuid in proposed_cards_uuids]
    proposed_pieces = [piece_uuid for piece_uuid in state.kernel.players[player_idx].pieces if piece_uuid in action.move_pieces_to_path.piece_uuids]
    remaining_segments = path.segments

    # print("******************************1234 is_move_pieces_to_path_action_legal 1b: ", proposed_cards)
    # print("******************************1234 is_move_pieces_to_path_action_legal 1c: ", proposed_pieces)
    # print("******************************1234 is_move_pieces_to_path_action_legal 1d: ", len(remaining_segments))
    
    card_fulfillment, piece_fulfillment = get_path_fulfillment_from_resources(
        state.kernel,
        proposed_cards,
        proposed_pieces,
        remaining_segments,
    )

    # print("******************************1234 is_move_pieces_to_path_action_legal 2a", card_fulfillment)
    # print("******************************1234 is_move_pieces_to_path_action_legal 2b", piece_fulfillment)

    if card_fulfillment is None or piece_fulfillment is None:
        return False

    # print("******************************1234 is_move_pieces_to_path_action_legal 3")
    # print("******************************1234 is_move_pieces_to_path_action_legal piece_fulfillment: ", piece_fulfillment)
    # print("******************************1234 is_move_pieces_to_path_action_legal proposed_pieces: ", proposed_pieces)

    return (
        len(card_fulfillment) == len(proposed_cards_uuids) and
        len(piece_fulfillment) == len(proposed_pieces)
    )


@dispatch(StateKernel)
def get_total_path_count(kernel):
    return len(kernel.idx2path)


@dispatch(StateKernel, int, int)
def get_legal_actions_for_path(state_kernel, player_idx, path_idx):
    if path_idx < 0 or get_total_path_count(state_kernel) <= path_idx:
        return []

    if not is_path_open_to_player(state_kernel, path_idx, player_idx):
        return []

    legal_actions = []
    default = get_sample_actionclaimpath(state_kernel, player_idx, path_idx)
    if default:
        legal_actions.append(
            LegalAction(
                player_idx=player_idx,
                name="CLAIM-PATH",
                title="Select resources to claim path",
                instruction="claim a path",
                allotted_seconds=DEFAULT_ALLOTTED_SECONDS,
                allotted_since_action_idx=(len(state_kernel.history) - 1),
                btn_text="Claim path",
                move_pieces_to_path=LegalActionMovePiecesToPath(
                    path_idx=int(path_idx),
                    default=default
                )
            )
        )
        return legal_actions
    return []


@dispatch(StateKernel, int)
def get_legal_actions_for_paths(kernel, player_idx):
    legal_actions = []
    
    for path_idx in range(get_total_path_count(kernel)):
        legal_actions_for_path = get_legal_actions_for_path(kernel, player_idx, path_idx)
        if legal_actions_for_path:
            legal_actions.extend(legal_actions_for_path)
        # else:
        #     print(f"Path {path_idx} is not claimable by player {player_idx}")
    
    return legal_actions


@dispatch(StateKernel, BiEdge)
def get_player_idxs_on_edge(kernel, edge):
    player_idxs = set()
    if not edge or not edge.paths:
        return list(player_idxs)
    
    for path in edge.paths:
        for segment in path.segments:
            if segment.pieces and segment.pieces[0]:
                piece = kernel.pieceuuid2piece.get(segment.pieces[0])
                if piece:
                    player_idxs.add(piece.player_idx)
    
    return list(player_idxs)

@dispatch(StateKernel, int, int)
def is_path_open_to_player(state_kernel, path_idx, player_idx):

    if not state_kernel or path_idx < 0 or get_total_path_count(state_kernel) <= path_idx:
        return False
    
    path = state_kernel.idx2path[path_idx]
    edge_idx = state_kernel.edgeuuid2idx[path.edge_uuid]
    edge = state_kernel.edges[edge_idx]

    player_idxs_on_edge = get_player_idxs_on_edge(state_kernel, edge)

    # Check if edge is too crowded for the number of players
    if state_kernel.game_config.num_players <= 3:
        if len(player_idxs_on_edge) > 0:
            return False
        
    if player_idx in player_idxs_on_edge:
        return False
    
    # Check if any segment of the path has pieces from any player
    if path.segments[0].pieces:
        return False

    # Check if the player has enough pieces to claim the path
    player_pieces = state_kernel.players[player_idx].pieces
    if len(player_pieces) < len(path.segments):
        return False
    
    return True


HOOK_NAMESPACE = {
    'INITIAL_ALLOTTED_SECONDS': INITIAL_ALLOTTED_SECONDS,
    'DEFAULT_ALLOTTED_SECONDS': DEFAULT_ALLOTTED_SECONDS,
    'shuffle_all_decks': shuffle_all_decks,
    'shuffle_player_order': shuffle_player_order,
    'deal_cards_to_each_player': deal_cards_to_each_player,
    'deal_cards_to_each_player_discard_tray': deal_cards_to_each_player_discard_tray,
    'distribute_all_piles': distribute_all_piles,
    'flip_cards': flip_cards,
    'LegalActionDiscard': LegalActionDiscard,
    'LegalActionKeep': LegalActionKeep,
    'score_public_items': score_public_items,
    'score_private_items': score_private_items,
    'default_handle_scoring': default_handle_scoring,
    'default_handle_terminal': default_handle_terminal,
    'default_handle_action': default_handle_action,
    'handle_discard_action': handle_discard_action,
    'handle_keep_action': handle_keep_action,
    'handle_move_pieces_to_path_action': handle_move_pieces_to_path_action,
    'handle_after_move_pieces_to_path_action': handle_after_move_pieces_to_path_action,
    'handle_move_bonus_cards': handle_move_bonus_cards,
    'handle_move_longest_path_card': handle_move_longest_path_card,
    'find_player_with_longest_path_card': find_player_with_longest_path_card,
    'default_after_accept_action': default_after_accept_action,
    'default_accept_action': default_accept_action,
    'LegalAction': LegalAction,
    'LegalActionDraw': LegalActionDraw,
    'LegalActionDrawDiscard': LegalActionDrawDiscard,
    'LegalActionFaceupDraw': LegalActionFaceupDraw,
    'LegalActionMovePiecesToPath': LegalActionMovePiecesToPath,
    'get_legal_actions_for_paths': get_legal_actions_for_paths,
    'get_legal_actions_for_path': get_legal_actions_for_path,
    'is_path_open_to_player': is_path_open_to_player,
    'ActionMovePiecesToPath': ActionMovePiecesToPathOptional,
}

@dispatch(StateKernel)
def get_wild_unit_uuids(state_kernel):
    wild_unit_uuids = []
    for card in state_kernel.carduuid2card.values():
        if card.is_wild:
            wild_unit_uuids.append(card.resource_uuid)
    return wild_unit_uuids


@dispatch(StateKernel, list, list, list)
def match_strict_wild(state_kernel, fulfillment, cards, segments):
    new_fulfillment = fulfillment.copy()
    new_cards = cards.copy()
    wild_unit_uuids = get_wild_unit_uuids(state_kernel)
    new_segments = []

    for segment in segments:
        if segment.unit_uuid and segment.unit_uuid in wild_unit_uuids:
            first_matching_idx = next((i for i, card_uuid in enumerate(new_cards) if state_kernel.carduuid2card[card_uuid].resource_uuid == segment.unit_uuid), None)
            if first_matching_idx is not None:
                new_fulfillment.append(new_cards.pop(first_matching_idx))
            else:
                new_segments.append(segment)
        else:
            new_segments.append(segment)

    return new_fulfillment, new_cards, new_segments

@dispatch(StateKernel, list, list, list)
def match_non_wild_non_empty(state_kernel, fulfillment, cards, segments):
    new_fulfillment = fulfillment.copy()
    new_cards = cards.copy()
    wild_unit_uuids = get_wild_unit_uuids(state_kernel)
    new_segments = []

    for segment in segments:
        first_strict_matching_idx = next((i for i, card_uuid in enumerate(new_cards) if state_kernel.carduuid2card[card_uuid].resource_uuid == segment.unit_uuid), None)
        first_wild_matching_idx = next((i for i, card_uuid in enumerate(new_cards) if state_kernel.carduuid2card[card_uuid].resource_uuid in wild_unit_uuids), None)
        first_matching_idx = first_strict_matching_idx if first_strict_matching_idx is not None else first_wild_matching_idx
        if first_matching_idx is not None:
            new_fulfillment.append(new_cards.pop(first_matching_idx))
        else:
            new_segments.append(segment)
    
    return new_fulfillment, new_cards, new_segments

    
@dispatch(StateKernel, list, list, list)
def match_empty(state_kernel, fulfillment, cards, segments):
    num_empty_segments = sum(1 for segment in segments if segment.unit_uuid is None)
    if num_empty_segments == 0:
        return fulfillment, cards, segments
    
    tuples = get_uniform_sets(state_kernel, cards, num_empty_segments)
    # print(f"****************************************** len(cards): {len(cards)}")
    # print(f"****************************************** num_empty_segments: {num_empty_segments}")
    # print(f"Found {len(tuples)} tuples for empty segments: {tuples}")
    if len(tuples) == 0:
        return fulfillment, cards, segments
    
    new_fulfillment = fulfillment.copy()

    new_segments = []
    for segment in segments:
        if segment.unit_uuid:
            new_segments.append(segment)

    first_tuple = tuples[0][:num_empty_segments]
    # print(f"Using first tuple for empty segments: {first_tuple}")
    new_cards = list(set(cards) - set(first_tuple))
    new_fulfillment.extend(first_tuple)
    return new_fulfillment, new_cards, new_segments


@dispatch(StateKernel, list, int)
def get_uniform_sets(state_kernel, cards, min_length):
    wilds = [card_uuid for card_uuid in cards if state_kernel.carduuid2card[card_uuid].is_wild]
    non_wilds = [card_uuid for card_uuid in cards if not state_kernel.carduuid2card[card_uuid].is_wild]
    # print("********************* cards: ", cards)
    # print("********************* wilds: ", wilds)
    # print("********************* non_wilds: ", non_wilds)
    unit_uuid_2_cards = {}
    for card_uuid in non_wilds:
        card = state_kernel.carduuid2card[card_uuid]
        if card.resource_uuid not in unit_uuid_2_cards:
            unit_uuid_2_cards[card.resource_uuid] = []
        unit_uuid_2_cards[card.resource_uuid].append(card_uuid)
    
    uniform_sets_no_wilds = [
        card_uuids for card_uuids in unit_uuid_2_cards.values() if len(card_uuids) >= min_length
    ]
    # print("********************* uniform_sets_no_wilds: ", uniform_sets_no_wilds)
    # print("********************* length: ", min_length)
    # print("********************* unit_uuid_2_cards.values(): ", unit_uuid_2_cards.values())

    uniform_sets_with_wilds = []
    for num_wilds in range(0, len(wilds)+1):
        uniform_set = wilds[:num_wilds]
        if len(uniform_set) >= min_length:
            uniform_sets_with_wilds.append(uniform_set)
        for unit_uuid, cards in unit_uuid_2_cards.items():
            uniform_set = cards + wilds[:num_wilds]
            if len(uniform_set) >= min_length:
                uniform_sets_with_wilds.append(uniform_set)

    # Sort the uniform sets by their length, smallest first
    uniform_sets_no_wilds.sort(key=len)
    uniform_sets_with_wilds.sort(key=len)
    # print("********************* uniform_sets_no_wilds 2: ", uniform_sets_no_wilds)
    sorted = uniform_sets_no_wilds + uniform_sets_with_wilds
    # print("********************* sorted : ", sorted)
    # Filter out sets that are smaller than the required length
    return sorted


def does_fulfill_path(game, player_idx, path_idx, fulfillment):
    return False


def get_sample_actionclaimpath(game, player_idx, path_idx):
    card_fulfillment, piece_fulfillment = get_sample_path_fulfillment(game, player_idx, path_idx)
    if not card_fulfillment or not piece_fulfillment:
        return None

    return ActionMovePiecesToPathOptional(
        piece_uuids=[piece_uuid for piece_uuid in piece_fulfillment],
        card_uuids=card_fulfillment,
    )

@dispatch(StateKernel, int, int)
def get_sample_path_fulfillment(kernel, player_idx, path_idx):
    path = kernel.idx2path[path_idx]
    remaining_card_uuids = [card_uuid for card_uuid in kernel.players[player_idx].cards if kernel.carduuid2card[card_uuid].deck_idx == 0]
    remaining_pieces = [
        piece_uuid 
        for piece_uuid in kernel.players[player_idx].pieces 
        if kernel.pieceuuid2piece[piece_uuid].piece_template_idx == 0
    ]
    remaining_segments = path.segments
    return get_path_fulfillment_from_resources(
        kernel,
        remaining_card_uuids,
        remaining_pieces,
        remaining_segments,
    )

@dispatch(StateKernel, list, list, list)
def get_path_fulfillment_from_resources(state_kernel, remaining_card_uuids, remaining_pieces, remaining_segments, log=False):

    if len(remaining_pieces) < len(remaining_segments):
        print("Not enough pieces to fulfill the path segments")
        return None, None
    
    piece_fulfillment = remaining_pieces[:len(remaining_segments)]

    card_fulfillment = []
    card_fulfillment, remaining_card_uuids, remaining_segments = match_strict_wild(state_kernel, card_fulfillment, remaining_card_uuids, remaining_segments)

    if len(remaining_segments) == 0:
        return card_fulfillment, piece_fulfillment
    # Probably don't need this check, but we should unit test
    # elif len(get_wild_segments(remaining_segments)) > 0:
    #     return None

    card_fulfillment, remaining_card_uuids, remaining_segments = match_non_wild_non_empty(state_kernel, card_fulfillment, remaining_card_uuids, remaining_segments)
    if len(remaining_segments) == 0:
        return card_fulfillment, piece_fulfillment
    # Probably don't need this check, but we should unit test
    # elif len(get_non_wild_non_empty_segments(remaining_segments)) > 0:
    #     return None

    card_fulfillment, remaining_card_uuids, remaining_segments = match_empty(state_kernel, card_fulfillment, remaining_card_uuids, remaining_segments)
    if len(remaining_segments) == 0:
        return card_fulfillment, piece_fulfillment

    # print("get_path_fulfillment_from_resources (None, None) because remaining_segments is not empty: ", remaining_segments)
    return None, None


def run_state_action_hook(state, action, hook, log=False):

    # Clone HOOK_NAMESPACE
    namespace = HOOK_NAMESPACE.copy()

    try:
        # Execute the code string
        exec(hook.code, namespace)

        # Retrieve the handler function
        handler_func = namespace.get('handler')
        
        if handler_func is None or not callable(handler_func):
            raise ValueError("No callable function named 'handler' found in the code")
        
        # Call the handler function
        result = handler_func(state, action)
        if log:
            pass
            # print(f"****************************** Running initialization hook 3: {hook.uuid} {result.player_idxs}")
            # print(f"****************************** Result of handler(5, 3): {result}")
        return result

    except SyntaxError as e:
        msg = f"Syntax error in initialization hook {hook.uuid}: {str(e)}"
        logging.error(msg, exc_info=True)
        raise SyntaxError(msg) from e
    except Exception as e:
        msg = f"Error in initialization hook {hook.uuid}: {str(e)}"
        logging.error(msg, exc_info=True)
        raise Exception(msg) from e


def run_state_hook(state, hook, log=False):

    namespace = HOOK_NAMESPACE.copy()

    try:
        # Execute the code string
        exec(hook.code, namespace)
        
        # Retrieve the handler function
        handler_func = namespace.get('handler')
        
        if handler_func is None or not callable(handler_func):
            raise ValueError("No callable function named 'handler' found in the code")
        
        # Call the handler function
        result = handler_func(state)
        # if log:
        #     print(f"****************************** Running initialization hook 3: {hook.uuid} {result.player_idxs}")
            # print(f"****************************** Result of handler(5, 3): {result}")
        return result

    except SyntaxError as e:
        msg = f"Syntax error in initialization hook {hook.uuid}: {str(e)}"
        logging.error(msg, exc_info=True)
        raise SyntaxError(msg) from e
    except Exception as e:
        msg = f"Error in initialization hook {hook.uuid}: {str(e)}"
        logging.error(msg, exc_info=True)
        raise Exception(msg) from e


def run_kernel_hook(kernel, hook, log=False):

    namespace = HOOK_NAMESPACE.copy()

    try:
        # Execute the code string
        exec(hook.code, namespace)
        
        # Retrieve the handler function
        handler_func = namespace.get('handler')
        
        if handler_func is None or not callable(handler_func):
            raise ValueError("No callable function named 'handler' found in the code")
        
        # Call the handler function
        result = handler_func(kernel)
        # if log:
        #     print(f"****************************** Running initialization hook 3: {hook.uuid} {result.player_idxs}")
            # print(f"****************************** Result of handler(5, 3): {result}")
        return result

    except SyntaxError as e:
        msg = f"Syntax error in initialization hook {hook.uuid}: {str(e)}"
        logging.error(msg, exc_info=True)
        raise SyntaxError(msg) from e
    except Exception as e:
        msg = f"Error in initialization hook {hook.uuid}: {str(e)}"
        logging.error(msg, exc_info=True)
        raise Exception(msg) from e


# Implementing the following Julia function:
# function getfaceupspots(f, unit_deck, unit_deck_idx)
#     num_faceup_spots = getsettingvalue(f, :num_faceup_spots)
#     unit_deck[unit_deck_idx:(unit_deck_idx+(num_faceup_spots - 1))]
# end
def getfaceupspots(f, unit_deck, unit_deck_idx):
    num_faceup_spots = getsettingvalue(f, 'num_faceup_spots')
    if num_faceup_spots is None:
        raise ValueError("Setting 'num_faceup_spots' not found in board config.")
    return unit_deck[unit_deck_idx:(unit_deck_idx + num_faceup_spots)] if unit_deck_idx < len(unit_deck) else []


# Implementing the following Julia function:
# getpath(f::Fig, num::Int) = f.board_config.board_paths[num]
def getpath(f, num):
    if f and f.board_config and num < len(f.board_config.board_paths):
        return f.board_config.board_paths[num]
    raise ValueError(f"Path number {num} not found in board config.")







def isactionlegal2(s, a):
    return run_accept_action_hooks(s, a, ACCEPT_ACTION_HOOKS, False)


def calc_legal_actions3(state_kernel):
    history = state_kernel.history
    last_action = history[-1] if len(history) > 0 else None

    if last_action is None or last_action.legal_action.name == "INITIAL-GOAL-KEEP":

        yet_to_make_initial_move = [
            player for player in state_kernel.players if len(player.discard_tray) > 0
        ]
        
        if len(yet_to_make_initial_move) == 0:
            # All players have made their initial move, proceed to the first player's turn
            return get_default_legal_actions(state_kernel, state_kernel.player_idxs[0])

        return [
            LegalAction(
                player_idx=player.idx,
                name="INITIAL-GOAL-KEEP",
                instruction="Your move. Please select the routes you want to keep.",
                allotted_seconds=INITIAL_ALLOTTED_SECONDS,
                allotted_since_action_idx=(len(history) - 1),
                keep=LegalActionKeep(
                    deck_idx=1,
                    min=2,
                )
            )
            for player in yet_to_make_initial_move
        ]
    
    elif last_action.legal_action.faceup_draw:
        faceup_draw = last_action.legal_action.faceup_draw
        if not state_kernel.carduuid2card[faceup_draw.card_uuid].is_wild:
            legal_actions = get_follow_up_draw_legal_actions(state_kernel, last_action)
            if legal_actions:
                return legal_actions
    
    elif last_action.legal_action.draw:
        if last_action.legal_action.draw.quantity == 1:
            legal_actions = get_follow_up_draw_legal_actions(state_kernel, last_action)
            if legal_actions:
                return legal_actions
    
    elif last_action.legal_action.draw_discard:
        draw_discard = last_action.legal_action.draw_discard
        player = state_kernel.players[last_action.legal_action.player_idx]
        return [
            LegalAction(
                player_idx=player.idx,
                name="GOAL-KEEP",
                instruction="Your move. Please select the routes you want to keep.",
                allotted_seconds=INITIAL_ALLOTTED_SECONDS,
                allotted_since_action_idx=(len(state_kernel.history) - 1),
                keep=LegalActionKeep(
                    deck_idx=draw_discard.deck_idx,
                    min=draw_discard.min,
                    max=draw_discard.max,
                )
            )
        ]
    
    next_player_idx = get_next_player_shuffled_idx(state_kernel, last_action)
    return get_default_legal_actions(state_kernel, state_kernel.player_idxs[next_player_idx])


def get_next_player_shuffled_idx(state_kernel, last_action):
    last_player_idx = last_action.legal_action.player_idx
    last_player_shuffled_idx = state_kernel.player_idxs.index(last_player_idx)
    next_player_shuffled_idx = (last_player_shuffled_idx + 1) % len(state_kernel.player_idxs)
    return next_player_shuffled_idx


def getnextstate2(s, a, log=False):
    is_legal, reason = isactionlegal2(s, a)
    if not is_legal:
        raise ValueError(f"Action is not legal: {a}. Reason: {reason}")
    kernel = s.kernel
    kernel = run_state_action_hooks(kernel, a, AFTER_ACCEPT_ACTION_HOOKS, log)
    kernel = run_state_action_hooks(kernel, a, HANDLE_ACTION_HOOKS, log)
    return init_memoized_state(kernel)


def getpublicplayerscore(s, player_score):
    if isterminal(s):
        # Join the arrays of public and private items
        items = player_score.public_items + player_score.private_items
    else:
        # Just public items
        items = player_score.public_items
    total = sum(item.amount for item in items)
    return PublicPlayerScore(
        items=items,
        total=total,
    )


def getprivateplayerscore(s, player_score):
    items = player_score.private_items
    total = sum(item.amount for item in items)
    return PrivatePlayerScore(
        items=items,
        total=total,
    )


def getpublictoplay(s):
    player_idxs = [legal_action.player_idx for legal_action in s.legal_actions_3]
    # filter out duplicates
    return list(set(player_idxs))


def get_max_allotted_times(s):
    return [
        get_player_max_allotted_time(s, player_idx) 
        for player_idx in range(s.kernel.game_config.num_players)
    ]


def get_player_max_allotted_time(s, player_idx):
    max_allotted_seconds = 0
    since_action_idx_of_max = -1
    for legal_action in s.legal_actions_3:
        if legal_action.player_idx == player_idx:
            if legal_action.allotted_seconds > max_allotted_seconds:
                max_allotted_seconds = legal_action.allotted_seconds
                since_action_idx_of_max = legal_action.allotted_since_action_idx
    if max_allotted_seconds:
        return AllottedTime(
            seconds=max_allotted_seconds,
            since_action_idx=since_action_idx_of_max,
        )
    return None


def get_deadline(s, max_allotted_time):
    if not max_allotted_time:
        return None
    since_action_idx = max_allotted_time.since_action_idx
    if since_action_idx == -1:
        allotted_since = datetime.strptime(
            s.kernel.game_config.started_at, 
            "%Y-%m-%d %H:%M:%S"
        )
    else:
        since_action = s.kernel.history[since_action_idx]
        submitted_at = since_action.submitted_at
        allotted_since = datetime.strptime(submitted_at, "%Y-%m-%d %H:%M:%S")
    deadline = allotted_since + timedelta(seconds=max_allotted_time.seconds)
    remaining_seconds = int((deadline - datetime.now()).total_seconds())
    return RemainingAllottedTime(
        seconds=max_allotted_time.seconds,
        remaining_seconds=remaining_seconds,
        since_action_idx=since_action_idx,
    )


@dispatch(State)
def get_deadlines(s):
    if isterminal(s):
        return [None for _ in range(s.kernel.game_config.num_players)]
    return [
        get_deadline(s, max_allotted_time)
        for max_allotted_time in get_max_allotted_times(s)
    ]


def get_public_player_scores(s):
    return [getpublicplayerscore(s, player_score) for player_score in s.player_scores_3]


# deadlines = field(type=list)  # List[RemainingAllottedTime|None]
# game_started_at = field(type=str)
# allotted_times = field(type=list)
# all_pieces = field(type=list)  # List[Piece]
# to_play_2 = field(type=list)  # List[int]
# bonus_statuses = field(type=list)  # List[BonusStatus]
# starting_decks = field(type=list)  # List[Deck]
# starting_piles = field(type=list)  # List[Pile]
# history = field(type=list)  # List[PublicAction]
# player_scores = field(type=list)  # List[PublicPlayerScore]
# player_graphs = field(type=list)  # List[PlayerGraph]
# goals = field(type=list)  # List[Goal]
# nodes = field(type=list)  # List[Node]
# edges = field(type=list)  # List[BiEdge]
# regions = field(type=list)
# decks = field(type=list)  # List[PublicDeck]
# piles = field(type=list)  # List[Pile]
# player_idxs = field(type=list)  # List[int]
# players = field(type=list)  # List[PublicPlayer]
# last_to_play = field(type=(int, type(None)), initial=None)
# winners = field(type=list)
#  = field(type=bool)


# player_score = field(type=PrivatePlayerScore)
# player = field(type=Player)
# goal_completions = field(type=list, initial=[])  # List[GoalCompletion]


@dispatch(State)
def get_public_history(s):
    return [action.get_public(s) for action in s.kernel.history]


def imagine_history(public_state, private_state):
    pass

def imagine_player_scores(public_state, private_state):
    pass

def imagine_legal_actions(public_state, private_state):
    pass

def imagine_players(public_state, private_state):
    pass

def imagine_decks(public_state, private_state):
    pass


def imagine_state(public_state, private_state):
    game_config = public_state.game_config
    imagined_kernel = init_state_kernel(
        rng=random.Random(),
        game_config=game_config,
        edges=public_state.edges,
        nodes=public_state.nodes,
        piles=public_state.piles,
        decks=imagine_decks(public_state, private_state),
        players=imagine_players(public_state, private_state),
        player_idxs=public_state.player_idxs,
        history=imagine_history(public_state, private_state),
        player_scores=imagine_player_scores(public_state, private_state),
        starting_decks=[Deck.__fromdict__(x.__todict__()) for x in decks],
        starting_piles=[Pile.__fromdict__(x.__todict__()) for x in public_state.piles],
        goals=game_config.fig.board_config.goals,
    )
    return init_memoized_state(imagined_kernel)


@dispatch(State)
def isterminal(s):
    return len(s.legal_actions_3) == 0


@dispatch(State)
def getpublicstate(s):
    return PublicState(
        deadlines=get_deadlines(s),
        game_started_at=s.kernel.game_config.started_at,
        allotted_times=get_max_allotted_times(s),
        all_pieces=list(s.kernel.pieceuuid2piece.values()),
        to_play_2=getpublictoplay(s),
        bonus_statuses=s.bonus_statuses_3,
        starting_decks=s.kernel.starting_decks,
        starting_piles=s.kernel.starting_piles,
        history=get_public_history(s),
        player_scores=get_public_player_scores(s),
        player_graphs=s.kernel.player_graphs_3,
        goals=s.kernel.goals,
        nodes=s.kernel.nodes,
        edges=s.kernel.edges,
        regions=s.kernel.regions,
        decks=[getpublicdeck(s, deck) for deck in s.kernel.decks],
        piles=s.kernel.piles,
        player_idxs=s.kernel.player_idxs,
        players=[getpublicplayer(s, p) for p in s.kernel.players],
        last_to_play=s.kernel.last_to_play,
        winners=s.winners,
        terminal=isterminal(s),
    )


@dispatch(State, Deck)
def getpublicdeck(s, d):
    return PublicDeck(
        idx=d.idx,
        uuid=d.uuid,
        units=d.units,
        facedown_stack_len=len(d.facedown_stack),
        discard_len=len(d.discard),
        faceup_spots=d.faceup_spots,
    )


@dispatch(State, Player)
def getpublicplayer(s, p):
    deck_counts = [0 for _ in s.kernel.game_config.fig.board_config.deks]
    for card in p.cards:
        deck_counts[s.kernel.carduuid2card[card].deck_idx] += 1
    piece_template_counts = [0 for _ in s.kernel.game_config.fig.board_config.piece_templates]
    for piece_uuid in p.pieces:
        piece_template_counts[s.kernel.pieceuuid2piece[piece_uuid].piece_template_idx] += 1
    return PublicPlayer(
        idx=p.idx,
        pieces=p.pieces,
        deck_counts=deck_counts,
        piece_template_counts=piece_template_counts,
    )


# Implementing the following Julia function:
# function getpublicscore(s::State, player_idx::Int)
#     addends = Int[]
    
#     if getsettingvalue(s, :path_scoring)
#         (; path_scores) = s.fig
#         path_lens = getplayerpathlens(s, player_idx)
#         if isempty(path_lens)
#             return 0
#         end
#         push!(addends, sum(map(len -> path_scores[len], path_lens)))
#     end

#     if getsettingvalue(s, :cluster_scoring)
#         (; clusters) = s.fig.board_config
#         uuid2cluster = Dict((x.uuid, x) for x in clusters)
#         (; completed_clusters) = s.player_hands[player_idx]
#         cluster_scores = map(completed_clusters) do cluster_uuid
#             uuid2cluster[cluster_uuid].score
#         end
#         if !isempty(cluster_scores)
#             push!(addends, sum(cluster_scores))
#         end
#     end

#     sum(addends)
# end
def getpublicscore(s, player_idx):
    addends = []
    if getsettingvalue(s, 'path_scoring'):
        path_lens = getplayerpathlens(s, player_idx)
        if not path_lens:
            return 0
        addends.append(sum(s.kernel.game_config.fig.path_scores[len] for len in path_lens))
    
    if getsettingvalue(s, 'cluster_scoring'):
        clusters = s.kernel.game_config.fig.board_config.clusters
        uuid2cluster = {x.uuid: x for x in clusters}
        completed_clusters = s.player_hands[player_idx].completed_clusters
        cluster_scores = [uuid2cluster[cluster_uuid].score for cluster_uuid in completed_clusters]
        if cluster_scores:
            addends.append(sum(cluster_scores))
    
    return sum(addends)


# Implementing the following Julia function:
# function getplayerpathlens(s::State, player_idx::Int)
#     getpathlens(s)[getplayerpathidxs(s, player_idx)]
# end
def getplayerpathlens(s, player_idx):
    path_lens = getpathlens(s)
    player_path_idxs = getplayerpathidxs(s, player_idx)
    return [path_lens[idx] for idx in player_path_idxs]


# Implementing the following Julia function:
# getpathlens(s::State) = length.(getfield.(getfield.(s.fig.board_config.board_paths, :path), :segments))
def getpathlens(s):
    return [len(p.path.segments) for p in s.kernel.game_config.fig.board_config.board_paths]

# Implementing the following Julia function:
# function getplayerpathidxs(s::State, player_idx::Int)
#     s.player_hands[player_idx].paths
# end
def getplayerpathidxs(s, player_idx):
    return s.player_hands[player_idx].paths


# Function implements the following Julia function:
# function getlastactionkey(s)
#     last_action = getlastaction(s)
#     if isnothing(last_action)
#         return nothing
#     end
#     Val(Symbol(last_action.action_name))
# end
@dispatch(State)
def getlastactiontype(s):
    pass


def getactiontype(action_name):
    match action_name:
        case "ROUTE_DISCARD":
            return RouteDiscardAction()
        case "DRAW_UNIT_DECK":
            return DrawUnitDeckAction()
        case "DRAW_UNIT_FACEUP":
            return DrawUnitFaceupAction()
        case "CLAIM_POINT":
            return ClaimPointAction()
        case "CLAIM_PATH":
            return MovePiecesToPathAction()
    
    return NoAction()


# Function implements the following Julia function:
# getlastplayeridxplus1(s) = mod1(getlastaction(s).player_idx + 1, s.kernel.game_config.num_players)
def getlastplayeridxplus1(s):
    pass


@dispatch(State)
def gettoplay(s):
    return gettoplay(s, getlastactiontype(s))


@dispatch(State, object)
def gettoplay(s, last_action_type):
    return [getlastplayeridxplus1(s)]


def getrng(seed):
    rng = random.Random()
    rng.seed(seed)
    return rng


# Implementing the following Julia function:
# getfirstplayeridx(g::Game) = rand(getrng(g), 1:g.num_players)
def getfirstplayeridx(rng, num_players):
    return rng.randint(0, num_players-1)


@dispatch(State, int)
def get_legal_actions3(s, player_idx):
    return [a for a in s.legal_actions_3 if a.player_idx == player_idx]


@dispatch(State, int)
def get_legal_actions(s, player_idx):
    return [a for a in s.legal_actions_3 if a.player_idx == player_idx]


@dispatch(StateKernel, int)
def get_goal_completions(kernel, player_idx):
    # print("len(get_goals(s, player_idx)): ", len(get_goals(s, player_idx)))
    # print("len(s.history): ", len(s.history))
    # print("player.cards: ", len(s.players[player_idx].cards))
    return [
        GoalCompletion(
            goal_uuid=goal.uuid,
            complete=is_goal_complete(kernel, goal, player_idx),
        )
        for goal in get_goals(kernel, player_idx)
    ]


@dispatch(StateKernel, int)
def get_goal_completions3(kernel, player_idx):
    # print("len(get_goals(s, player_idx)): ", len(get_goals(s, player_idx)))
    # print("len(s.history): ", len(s.history))
    # print("player.cards: ", len(s.players[player_idx].cards))
    return [
        GoalCompletion(
            goal_uuid=goal.uuid,
            complete=is_goal_complete(kernel, goal, player_idx),
        )
        for goal in get_goals3(kernel, player_idx)
    ]


@dispatch(StateKernel, FrozenGoal, int)
def is_goal_complete(kernel, goal, player_idx):
    graph = kernel.player_graphs_3[player_idx].neighbors
    node_idxs = [kernel.nodeuuid2idx[node_uuid] for node_uuid in goal.node_uuids]
    return are_nodes_connected(
        graph,
        node_idxs,
    )


def are_nodes_connected(graph, node_set):
    if len(node_set) == 0:
        raise ValueError("Node set cannot be empty")
    if len(node_set) <= 1:
        return True  # Trivial cases
    
    node_set = set(node_set)  # For faster lookups
    start = next(iter(node_set))  # Pick any starting node
    
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    # Check if all nodes in the set were visited
    return all(node in visited for node in node_set)


def get_player_graph(s, player_idx):
    nodes = {node.idx: [] for node in s.nodes}
    return nodes


@dispatch(StateKernel, int)
def get_goals(kernel, player_idx):
    player = kernel.players[player_idx]
    goaluuid2goal = {goal.uuid: goal for goal in kernel.goals}
    goal_uuids = [kernel.carduuid2card[card_uuid].goal_uuid for card_uuid in player.cards if kernel.carduuid2card[card_uuid].goal_uuid]
    return [
        goaluuid2goal[goal_uuid] for goal_uuid in goal_uuids if goal_uuid in goaluuid2goal
    ]


@dispatch(StateKernel, int)
def get_goals3(kernel, player_idx):
    player = kernel.players[player_idx]
    goaluuid2goal = {goal.uuid: goal for goal in kernel.goals}
    goal_uuids = [kernel.carduuid2card[card_uuid].goal_uuid for card_uuid in player.cards if kernel.carduuid2card[card_uuid].goal_uuid]
    return [
        goaluuid2goal[goal_uuid] for goal_uuid in goal_uuids if goal_uuid in goaluuid2goal
    ]


def getrepeatplayerbooltype(s, player_idx):
    pass


def combinations(a, n=None):
    if n is None:
        return chain.from_iterable(itertools_combinations(a, r) for r in range(len(a) + 1))
    return itertools_combinations(a, n)


# def combinations(a, n=None):
#     """
#     Generate combinations from a sequence a.

#     If n is specified, generate all combinations of n elements from a.
#     If n is not specified, generate combinations of all sizes, from 0 to len(a).

#     The function returns an iterator. To collect all combinations into a list,
#     use list(combinations(a, n)).

#     Note: a should be a sequence with a defined length, such as a list or tuple.
#     """
#     if n is None:
#         return itertools.chain.from_iterable(itertools.combinations(a, k) for k in range(len(a)+1))
#     else:
#         return itertools.combinations(a, n)


###
# Causal function chain is:
# gettoplay => getlegalactions => isterminal
#
# So, gettoplay() determines getlegalactions().
# Moreover, if there are no "legal_actions" for "to_play",
# then the state is "terminal".
###


# Implementing the following Julia function:
# function getpotentialpathnums(s::State, player_num::Int)
#     num_pieces = s.player_hands[player_num].num_pieces
#     setdiff(
#         Set(getpathidxs(s.fig, num_pieces)),
#         Set(getunavailablepaths(s, player_num)),
#     ) |> collect
# end
def getpotentialpathidxs(s, player_num):
    num_pieces = s.player_hands[player_num-1].num_pieces
    return list(
        set(getpathidxs(s.kernel.game_config.fig, num_pieces)) - set(getunavailablepathidxs(s, player_num))
    )
    # return list(set(getpathidxs(s.fig, num_pieces)) - set(getunavailablepaths(s, player_num)))


# Implementing the following Julia function:
# function getpathidxs(f::Fig, max_pieces::Int)
#     [p.num for p in f.board_config.board_paths if length(p.path.segments) <= max_pieces]
# end
def getpathidxs(fig, max_pieces):
    return [
        (p.num - 1)
        for p in fig.board_config.board_paths
        if len(p.path.segments) <= max_pieces
    ]


# Implementing the following Julia function:
# function getunavailablepaths(s::State, player_idx::Int)
#     link2paths = Dict()
#     path2link = Dict()

#     for board_path in s.fig.board_config.board_paths
#         (; link_num) = board_path
#         if !haskey(link2paths, link_num)
#             link2paths[link_num] = []
#         end
#         push!(link2paths[link_num], board_path.num)
#         path2link[board_path.num] = link_num
#     end

#     multipath_links = [board_link.num for board_link in getmultipathlinks(s.fig)]

#     # TODO: this is fig-specific game logic 
#     # and should be factored out.
#     if s.game.num_players < 4
#         blocking_hands = s.player_hands
#     else
#         blocking_hands = [s.player_hands[player_idx]]
#     end

#     unavailable_links = []
#     for hand in blocking_hands
#         for path_idx in hand.paths
#             link_idx = path2link[path_idx]
#             if in(link_idx, multipath_links)
#                 push!(unavailable_links, link_idx)
#             end
#         end
#     end

#     unavailable_paths = getclaimedpathidxs(s)
#     for link_idx in unavailable_links
#         for peer in link2paths[link_idx]
#             push!(unavailable_paths, peer)
#         end
#     end

#     unavailable_paths |> unique
# end
def getunavailablepathidxs(s, player_idx):
    link2paths = {}
    path2link = {}

    for board_path in s.kernel.game_config.fig.board_config.board_paths:
        link_idx = board_path.link_num - 1
        if link_idx not in link2paths:
            link2paths[link_idx] = []
        link2paths[link_idx].append(board_path.num-1)
        path2link[board_path.num-1] = link_idx

    multipath_links = [(board_link.num-1) for board_link in getmultipathlinks(s.kernel.game_config.fig)]

    if s.kernel.game_config.num_players < 4:
        blocking_hands = s.player_hands
    else:
        blocking_hands = [s.player_hands[player_idx]]

    unavailable_links = []
    for hand in blocking_hands:
        for path_idx in hand.paths:
            link_idx = path2link[path_idx]
            if link_idx in multipath_links:
                unavailable_links.append(link_idx)

    unavailable_paths = getclaimedpathidxs(s)
    for link_idx in unavailable_links:
        unavailable_paths.extend(link2paths[link_idx])

    return list(set(unavailable_paths))


# Implementing the following Julia function:
# function getmultipathlinks(f::Fig)
#     filter(
#         frozen_link->frozen_link.width > 1,
#         f.board_config.links,
#     )
# end
def getmultipathlinks(fig):
    return [
        frozen_link
        for frozen_link in fig.board_config.links
        if frozen_link.width > 1
    ]


# Implementing the following Julia function:
# function prioritysort(fig::Fig, segments::Vector)
#     (; board_config) = fig
#     (; deck_units) = board_config
#     unituuid2deckunit = Dict(x.unit_uuid => x for x in deck_units)
#     to_sort = [OrderedSegment(n, segment) for (n, segment) in enumerate(segments)]
#     function lt(a, b)
#         segment_a = a.segment
#         segment_b = b.segment
#         deck_unit_a = isnothing(segment_a.unit_uuid) ? nothing : unituuid2deckunit[segment_a.unit_uuid]
#         deck_unit_b = isnothing(segment_b.unit_uuid) ? nothing : unituuid2deckunit[segment_b.unit_uuid]
#         if isnothing(deck_unit_a) && isnothing(deck_unit_b)
#             return a.path_segment_num < b.path_segment_num
#         elseif isnothing(deck_unit_a) && !isnothing(deck_unit_b)
#             return true
#         elseif !isnothing(deck_unit_a) && isnothing(deck_unit_b)
#             return false
#         elseif deck_unit_a.is_wild && deck_unit_b.is_wild
#             return a.path_segment_num < b.path_segment_num
#         elseif deck_unit_a.is_wild && !deck_unit_b.is_wild
#             return false
#         elseif !deck_unit_a.is_wild && deck_unit_b.is_wild
#             return true
#         end
#         a.path_segment_num < b.path_segment_num
#     end
#     Base.sort(to_sort; lt=lt, rev=true)
# end
def prioritysort(fig, segments):
    board_config = fig.board_config
    deck_units = board_config.deck_units
    unituuid2deckunit = {x.unit_uuid: x for x in deck_units}
    to_sort = [OrderedSegment(path_segment_num=n, segment=segment) for n, segment in enumerate(segments)]
    
    def lt(a, b):
        segment_a = a.segment
        segment_b = b.segment
        deck_unit_a = unituuid2deckunit.get(segment_a.unit_uuid) if segment_a.unit_uuid else None
        deck_unit_b = unituuid2deckunit.get(segment_b.unit_uuid) if segment_b.unit_uuid else None
        
        if deck_unit_a is None and deck_unit_b is None:
            return a.path_segment_num < b.path_segment_num
        elif deck_unit_a is None and deck_unit_b is not None:
            return True
        elif deck_unit_a is not None and deck_unit_b is None:
            return False
        elif deck_unit_a.is_wild and deck_unit_b.is_wild:
            return a.path_segment_num < b.path_segment_num
        elif deck_unit_a.is_wild and not deck_unit_b.is_wild:
            return False
        elif not deck_unit_a.is_wild and deck_unit_b.is_wild:
            return True
        
        return a.path_segment_num < b.path_segment_num
    
    return sorted(to_sort, key=cmp_to_key(lt), reverse=True)


# Implementing the following Julia function:
# getwildunituuids(f::Fig) = [x.unit_uuid for x in f.board_config.deck_units if x.is_wild]
def getwildunituuids(fig):
    return [x.unit_uuid for x in fig.board_config.deck_units if x.is_wild]

# Implementing the following Julia function:
# getnonwildunituuids(f::Fig) = [x.unit_uuid for x in f.board_config.deck_units if !x.is_wild]
def getnonwildunituuids(fig):
    return [x.unit_uuid for x in fig.board_config.deck_units if not x.is_wild]


# Implementing the following Julia function:
# function getunituuid(f::Fig, card_num::Int)
#     from = 1
#     for deck_unit in f.board_config.deck_units
#         (; quantity, unit_uuid) = deck_unit
#         to = from + quantity - 1
#         if from <= card_num <= to
#             return unit_uuid
#         end
#         from += quantity
#     end
#     throw(ErrorException("unit_uuid not found for card_num $card_num"))
# end
def getunituuid(fig, card_num):
    from_idx = 1
    for deck_unit in fig.board_config.deck_units:
        quantity = deck_unit.quantity
        unit_uuid = deck_unit.unit_uuid
        to = from_idx + quantity - 1
        if from_idx <= card_num <= to:
            return unit_uuid
        from_idx += quantity
    raise ValueError(f"unit_uuid not found for card_num {card_num}")


# Implementing the following Julia function:
# function getclaimedpathidxs(s::State)
#     claimed = []
#     for player_hand in s.player_hands
#         append!(claimed, player_hand.paths)
#     end
#     claimed
# end
def getclaimedpathidxs(s):
    claimed = []
    for player_hand in s.player_hands:
        claimed.extend(player_hand.paths)
    return claimed






# Implementing the following Julia function:
# function getnodeuuids(f::Fig, remaining_pieces::Int)
#     point_capture_unit_count = getsettingvalue(f, :point_capture_unit_count)
#     if point_capture_unit_count <= remaining_pieces
#         return [p.uuid for p in f.board_config.points]
#     end
#     []
# end
def getnodeuuids(f, remaining_pieces):
    point_capture_unit_count = getsettingvalue(f, 'point_capture_unit_count')
    # print(f"f.board_config: ", f.board_config)
    # print(f"f.board_config: ", f.board_config.points)
    if point_capture_unit_count <= remaining_pieces:
        return [p.uuid for p in f.board_config.points]
    return []


# Implementing the following Julia function:
# function getunavailablepoints(s::State)
#     unavailable_points = []
#     for hand in s.player_hands
#         for point_uuid in hand.points
#             push!(unavailable_points, point_uuid)
#         end
#     end
#     unavailable_points
# end
def getunavailablepoints(s):
    unavailable_points = []
    for hand in s.player_hands:
        for point_uuid in hand.points:
            unavailable_points.append(point_uuid)
    return unavailable_points


def printplayer(s, player_idx):
    pass


def printstate(s):
    pass


def printaction(a, i):
    pass


# Implementing the following Julia function:
# getprivatescore(s::State, player_idx::Int; bonus=true) = getprivatescore(s, s.player_hands[player_idx]; bonus=bonus)
@dispatch(State, int)
def getprivatescore(s, player_idx):
    return getprivatescore(s, s.player_hands[player_idx])


# Implementing the following Julia function:
# function getscorecodeidx(f::Fig, score_code::Symbol)
#     findfirst(
#         isequal(string(score_code)),
#         getscorecodes(f),
#     )
# end
def getscorecodeidx(f, score_code):
    return getscorecodes(f).index(score_code)


# Implementing the following Julia function:
# function getscorecodes(f::Fig)
#     score_codes = ["PATH", "ROUTE", "CLUSTER"]
#     disable_longest_path_bonus = getsettingvalue(f, :disable_longest_path_bonus)
#     if !disable_longest_path_bonus
#         push!(score_codes, "LONGEST_ROAD", "MOST_CLUSTERS")
#     end
#     score_codes
# end
# # TODO: this list needs to be remove, totally unnecessary.
def getscorecodes(f):
    score_codes = ["PATH", "ROUTE", "CLUSTER"]
    disable_longest_path_bonus = getsettingvalue(f, 'disable_longest_path_bonus')
    if not disable_longest_path_bonus:
        score_codes.extend(["LONGEST_ROAD", "MOST_CLUSTERS"])
    return score_codes


# Implementing the following Julia function:
# function getvalidspotnums(s::State)
#     filter(n -> !isnothing(s.faceup_spots[n]), 1:length(s.faceup_spots))
# end
def getvalidspotnums(s):
    return [n for n in range(1, len(s.faceup_spots) + 1) if s.faceup_spots[n-1] is not None]


def json_serializer(obj):
    if isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, '__todict__'):
        return obj.__todict__()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


@dispatch(str, str, Fig, int, int)
def initgameconfig(uuid, started_at, fig, num_players, seed):
    return GameConfig(
        uuid=uuid,
        started_at=started_at,
        fig=fig, 
        num_players=num_players, 
        seed=seed,
    )


def rng2json(rng):
    """Convert a random.Random instance to a JSON string."""
    rng_state = rng.getstate()
    return json.dumps({"state": [rng_state[0], list(rng_state[1]), rng_state[2]]})


def json2rng(json_str):
    """Reconstruct a random.Random instance from a JSON string."""
    data = json.loads(json_str)
    state_data = data["state"]
    
    # Create a new Random instance
    rng = random.Random()
    
    # Convert the middle part back to tuple of integers
    state = (state_data[0], tuple(state_data[1]), state_data[2])
    
    # Set the state
    rng.setstate(state)
    
    return rng


# Implementing the following Julia function:
# function getprivatestate(s::State, player_idx::Int)
#     legal_actions = getlegalactions(s, player_idx)
#     PrivateState(
#         getpublicstate(s),
#         legal_actions,
#         getsegmentstatuses(s, player_idx),
#         s.player_hands[player_idx],
#     )
# end
@dispatch(State, int)
def getprivatestate(s, player_idx):
    return PrivateState(
        my_history=[a for a in s.kernel.history if a.legal_action.player_idx == player_idx],
        player_score=getprivateplayerscore(s, s.player_scores_3[player_idx]),
        player=s.kernel.players[player_idx],
        legal_actions_3 = get_legal_actions3(s, player_idx),
        goal_completions=get_goal_completions(s.kernel, player_idx),
    )


# Implement the following Julia function
# function getqvaluetrajectories(g::Game)
#     curr_state = getinitialstate(g)
#     states = State[]
#     scores = [Int[] for _ in 1:(length(g.actions)+1)]
#     action_player_nums = Vector{Int}(undef, length(g.actions)) 
#     q_values = Vector{Int}(undef, length(g.actions))
#     formula_q_idxs = Vector{Union{Nothing,Int}}(nothing, length(g.actions))
#     formula_score_diffs = Vector{Tuple{Int,Int}}(undef, length(g.actions))
#     for (i,action) in enumerate(g.actions)
#         push!(states, curr_state)
#         scores[i] = map(1:g.num_players) do player_num
#             getprivatescore(curr_state, player_num; bonus=true).total
#         end
#         action_player_nums[i] = action.player_idx
#         curr_state = getnextstate(curr_state, action)
#     end
#     scores[end] = map(1:g.num_players) do player_num
#         getprivatescore(curr_state, player_num; bonus=true).total
#     end
#     for player_num in 1:g.num_players
#         player_action_idxs = findall(isequal(player_num), action_player_nums)
#         player_action_idxs_plus_terminal_idx = [player_action_idxs..., length(scores)]
#         scores_at_player_action_idxs = [x[player_num] for x in scores[player_action_idxs_plus_terminal_idx]]
#         q_values_at_player_action_idxs = reverse(cumsum(-diff(reverse(scores_at_player_action_idxs))))
#         q_values[player_action_idxs] = q_values_at_player_action_idxs
#         formula_q_idxs[player_action_idxs[1:end-1]] .= player_action_idxs[2:end]
#         formula_score_diffs[player_action_idxs] .= map(enumerate(player_action_idxs_plus_terminal_idx[1:end-1])) do (i,idx)
#             (player_action_idxs_plus_terminal_idx[i+1], idx)
#         end
#     end
#     formulas = map(zip(formula_q_idxs, formula_score_diffs)) do (formula_q_idx, formula_score_diff)
#         QValueFormula((q_num=formula_q_idx, score_diff=formula_score_diff))
#     end
#     QValueTrajectories(scores, q_values, formulas, states, g.actions)
#     # for player_idx in 1:g.num_players
#     # end
#     # -diff([110,10,0,0])
#     # cumsum([100,10,0])
# end
@dispatch(GameConfig, list)
def get_qvalue_trajectories(game_config, actions):
    curr_state = getinitialstate(game_config)
    states = []
    scores = np.array([list([0] * game_config.num_players) for _ in range(len(actions) + 1)])
    action_player_idxs = [None] * len(actions)
    q_values = [None] * len(actions)
    formula_q_idxs = np.array([None] * len(actions))
    formula_score_diffs = np.array([None] * len(actions))

    for i, action in enumerate(actions):
        states.append(curr_state)
        scores[i] = list([getprivatescore(curr_state, player_idx)[0] for player_idx in range(game_config.num_players)])
        action_player_idxs[i] = action.player_idx
        curr_state = getnextstate(curr_state, action)

    scores[-1] = np.array([getprivatescore(curr_state, player_idx)[0] for player_idx in range(game_config.num_players)])

    for player_idx in range(game_config.num_players):
        player_action_idxs = [i for i, x in enumerate(action_player_idxs) if x == player_idx]

        player_action_idxs_plus_terminal_idx = player_action_idxs + [len(scores) - 1]
        scores_at_player_action_idxs = [x[player_idx] for x in scores[player_action_idxs_plus_terminal_idx]]
        q_values_at_player_action_idxs = np.flip(
            np.cumsum((-1 * np.diff(np.flip(np.array(scores_at_player_action_idxs)))))
        )

        for idx, action_idx in enumerate(player_action_idxs):
            q_values[action_idx] = q_values_at_player_action_idxs[idx].item()

        formula_q_idxs[player_action_idxs[:-1]] = player_action_idxs[1:]

        formula_score_diffs[player_action_idxs] = [
            (player_action_idxs_plus_terminal_idx[i+1], idx)
            for i, idx in enumerate(player_action_idxs_plus_terminal_idx[:-1])
        ]

    formulas = [
        QValueFormula(q_num=formula_q_idx, score_diff=ScoreDiff(a=formula_score_diff[0], b=formula_score_diff[1]))
        for formula_q_idx, formula_score_diff in zip(formula_q_idxs, formula_score_diffs)
    ]

    return QValueTrajectories(scores=scores.tolist(), q_values=q_values, formulas=formulas, states_no_terminal=states, actions=actions)


@dispatch(str, str, str, int, int, list)
def get_qvalue_trajectories(logged_game_uuid, started_at, static_board_config_uuid, board_config_json, num_players, seed, actions):
    game_config = initgameconfig(logged_game_uuid, started_at, static_board_config_uuid, board_config_json, num_players, seed)
    return get_qvalue_trajectories(game_config, actions)


@dispatch(str, str, str, int, int)
def initgameconfig(logged_game_uuid, started_at, static_board_config_uuid, board_config_json, num_players, seed):
    board_config = FrozenBoardConfig.__fromdict__(json.loads(board_config_json))
    return initgameconfig(
        logged_game_uuid, 
        started_at,
        initfig(static_board_config_uuid, board_config),
        num_players, 
        seed,
    )


# Implementing the following Julia function:
# diff(A::AbstractVector)
# diff(A::AbstractArray; dims::Integer)

#   Finite difference operator on a vector or a multidimensional array A. In the latter case the dimension to operate on needs to be specified with the dims keyword argument.

#   │ Julia 1.1
#   │
#   │  diff for arrays with dimension higher than 2 requires at least Julia 1.1.

#   Examples
#   ≡≡≡≡≡≡≡≡

#   julia> a = [2 4; 6 16]
#   2×2 Matrix{Int64}:
#    2   4
#    6  16
  
#   julia> diff(a, dims=2)
#   2×1 Matrix{Int64}:
#     2
#    10
  
#   julia> diff(vec(a))
#   3-element Vector{Int64}:
#     4
#    -2
#    12
def diff(A, dims=None):
    if dims is None:
        # For 1D arrays, return the difference between consecutive elements
        return [A[i] - A[i - 1] for i in range(1, len(A))]
    else:
        # For 2D arrays, compute the difference along the specified dimension
        if dims == 1:
            return [[A[i][j] - A[i - 1][j] for j in range(len(A[0]))] for i in range(1, len(A))]
        elif dims == 2:
            return [[A[i][j] - A[i][j - 1] for j in range(1, len(A[0]))] for i in range(len(A))]
        else:
            raise ValueError("dims must be either 1 or 2")


def get_default_toplay(s):
    if s.legal_actions_3:
        return s.legal_actions_3[0].player_idx
    return None


def get_intuited_best_actions(ps):
    if not ps.legal_actions_3:
        return None
    return ps.legal_actions_3[:8]


def get_spread(q_values, p_idx):
    my_q = q_values[p_idx]
    other_qs = [q for i, q in enumerate(q_values) if i != p_idx]
    spread = my_q - max(other_qs)
    return spread


def getvproxy0(ps):
    return 0


def imagine_dynamics(ps, a):
    return dynamics(imagine_state(ps), a)


def dynamics(s, a):
    scores = get_public_player_scores(s)
    next_s = getnextstate2(s, a)
    next_scores = get_public_player_scores(next_s)
    rewards = [next_scores[i] - scores[i] for i in range(len(scores))]
    return next_s, rewards


def alpha0(ps):
    td = 3
    legal_actions = ps.legal_actions_3
    if not legal_actions:
        return None
    intuited = get_intuited_best_actions(ps)
    q_proxies = [getqproxy0(ps, a, td) for a in intuited]
    max_spread_idx = get_max_spread_idx(q_proxies, ps.player.player_idx)
    return intuited[max_spread_idx]


def get_max_spread_idx(q_proxies, p_idx):
    spreads = [get_spread(q_proxy, p_idx) for q_proxy in q_proxies]
    max_spread_idx = np.argmax(spreads)
    return max_spread_idx


def getqproxy0(ps, a, td):

    def qproxybase():
        next_s, rewards = imagine_dynamics(ps, a)
        if isterminal(next_s):
            return rewards
        v_proxies = [
            getvproxy0(getprivatestate(next_s, i))
            for i in range(next_s.kernel.game_config.num_players)
        ]
        q_proxies = [
            r + v_proxies[i]
            for i, r in enumerate(rewards)
        ]
        return q_proxies

    def qproxyrecurse():
        next_s, rewards = imagine_dynamics(ps, a)
        if isterminal(next_s):
            return rewards
        next_p_idx = get_default_toplay(next_s)
        next_ps = getprivatestate(next_s, next_p_idx)
        next_p_idx = next_ps.player.player_idx
        next_intuited = get_intuited_best_actions(next_ps)
        competing_next_q_values = [getqproxy0(next_ps, a, td-1) for a in next_intuited]
        max_next_spread_idx = get_max_spread_idx(competing_next_q_values, next_p_idx)
        next_q_values = competing_next_q_values[max_next_spread_idx]
        q_values = [r + next_q_values[i] for i, r in enumerate(rewards)]
        return q_values

    return qproxyrecurse() if td > 0 else qproxybase()


INIT_HOOK_1 = """def handler(kernel):
    return shuffle_all_decks(kernel)  
"""
INIT_HOOK_2 = """def handler(kernel):
    return deal_cards_to_each_player(kernel, 0, 4)
"""
INIT_HOOK_3 = """def handler(kernel):
    return deal_cards_to_each_player_discard_tray(kernel, 1, 3)
"""
INIT_HOOK_4 = """def handler(kernel):
    return distribute_all_piles(kernel)
"""
INIT_HOOK_5 = """def handler(kernel):
    return flip_cards(kernel, 0, 5)
"""
INIT_HOOK_7 = """def handler(kernel):
    return shuffle_player_order(kernel)
"""

INITIALIZATION_HOOKS = [
    Hook(
        name="SampleHook1",
        uuid="81248263-5cb4-4439-afea-78c01aba3de3",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_1,
    ),
    Hook(
        name="SampleHook2",
        uuid="d654d7f6-c2f4-443d-b603-8fa034717830",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_2,
    ),
    Hook(
        name="SampleHook3",
        uuid="ffbc3d4a-85c6-461d-9272-0ddeb873f216",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_3,
    ),
    Hook(
        name="SampleHook4",
        uuid="e3a9161b-ad27-4166-a013-77ebcd2f75b7",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_4,
    ),
    Hook(
        name="SampleHook5",
        uuid="bff1a9e9-90a5-4431-9d41-2b68c5eff55e",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_5,
    ),
    Hook(
        name="SampleHook7",
        uuid="240b8706-7fcf-4d35-9894-276aa10f799f",
        when="AFTER_GAME_STARTS",
        code=INIT_HOOK_7,
    ),
]


HANDLE_ACTION_HOOK_1 = """
def handler(kernel, action):
    return default_handle_action(kernel, action)
"""

HANDLE_ACTION_HOOKS = [
    Hook(
        name="SampleHookHandleAction1",
        uuid="11e83980-5a10-43f0-9504-66fe66eebb11",
        when="HANDLE_ACTION",
        code=HANDLE_ACTION_HOOK_1,
    ),
]

AFTER_ACCEPT_ACTION_HOOK_1 = """
def handler(kernel, action):
    return default_after_accept_action(kernel, action)
"""

AFTER_ACCEPT_ACTION_HOOKS = [
    Hook(
        name="SampleHookAfterAcceptAction1",
        uuid="3467e35e-f6b6-4b75-aeff-97e4bab47c75",
        when="AFTER_ACCEPT_ACTION",
        code=AFTER_ACCEPT_ACTION_HOOK_1,
    )
]

ACCEPT_ACTION_HOOK_1 = """
def handler(game, action):
    return default_accept_action(game, action)
"""

ACCEPT_ACTION_HOOKS = [
    Hook(
        name="SampleHookAcceptAction1",
        uuid="01b8ce2c-9aa5-44f5-b82f-bc22afeb49ef",
        when="ACCEPT_ACTION",
        code=ACCEPT_ACTION_HOOK_1,
    )
]

HANDLE_SCORING_HOOK_1 = """
def handler(game):
    return default_handle_scoring(game)
"""

HANDLE_SCORING_HOOKS = [
    Hook(
        name="SampleHookHandleScoring1",
        uuid="11e83980-5a10-43f0-9504-66fe66eebb11",
        when="HANDLE_SCORING",
        code=HANDLE_SCORING_HOOK_1,
    ),
]

HANDLE_TERMINAL_HOOK_1 = """
def handler(game):
    return default_handle_terminal(game)
"""

HANDLE_TERMINAL_HOOKS = [
    Hook(
        name="SampleHookHandleTerminal1",
        uuid="11e83980-5a10-43f0-9504-66fe66eebb11",
        when="HANDLE_TERMINAL",
        code=HANDLE_TERMINAL_HOOK_1,
    ),
]

@dispatch(StateKernel, int)
def get_default_legal_actions(state_kernel, player_idx):
    allotted_seconds = DEFAULT_ALLOTTED_SECONDS
    allotted_since_action_idx = len(state_kernel.history) - 1
    legal_actions = []

    if len(state_kernel.decks[1].facedown_stack) >= 1:
        legal_actions.append(
            LegalAction(
                player_idx=player_idx,
                name="DRAW-GOAL",
                instruction="draw a route",
                allotted_seconds=allotted_seconds,
                allotted_since_action_idx=allotted_since_action_idx,
                draw_discard=LegalActionDrawDiscard(
                    deck_idx=1,
                    quantity=3,
                    min=1,
                )
            )
        )

    if len(state_kernel.decks[0].facedown_stack) >= 1:
        legal_actions.append(
            LegalAction(
                auto_preferred=True,
                player_idx=player_idx,
                name="DRAW",
                instruction="draw a unit",
                allotted_seconds=allotted_seconds,
                allotted_since_action_idx=allotted_since_action_idx,
                draw=LegalActionDraw(
                    deck_idx=0,
                    quantity=1,
                )
            )
        )

    if len(state_kernel.decks[0].facedown_stack) >= 2:
        legal_actions.append(
            LegalAction(
                player_idx=player_idx,
                name="DRAW-DOUBLE",
                instruction="draw 2 units",
                allotted_seconds=allotted_seconds,
                allotted_since_action_idx=allotted_since_action_idx,
                draw=LegalActionDraw(
                    deck_idx=0,
                    quantity=2,
                )
            )
        )

    for card_uuid in state_kernel.decks[0].faceup_spots:
        if card_uuid:
            legal_actions.append(
                LegalAction(
                    player_idx=player_idx,
                    name="FACEUP-DRAW",
                    instruction="draw a faceup unit",
                    allotted_seconds=allotted_seconds,
                    allotted_since_action_idx=allotted_since_action_idx,
                    faceup_draw=LegalActionFaceupDraw(
                        deck_idx=0,
                        card_uuid=card_uuid,
                    )
                )
            )

    for legal_action in get_legal_actions_for_paths(state_kernel, player_idx):
        legal_actions.append(legal_action)
    
    return legal_actions