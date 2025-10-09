# ruff: noqa -- DO NOT UPDATE this @generated file

from __future__ import annotations

from typing import Any, Literal, Mapping, Sequence, TypedDict, Union


class CarResource(TypedDict):
    name: Literal['car']
    data: Sequence[Mapping[str, Any]]
    """
    Data items have to conform to the Car table schema
    """
    schema: Literal[
        'https://github.com/datisthq/cardealerdp/releases/download/v0.0.0-dev/car.json'
    ]


class DealerResource(TypedDict):
    name: Literal['dealer']
    data: Sequence[Mapping[str, Any]]
    """
    Data items have to conform to the Dealer table schema
    """
    schema: Literal[
        'https://github.com/datisthq/cardealerdp/releases/download/v0.0.0-dev/dealer.json'
    ]


class ShowroomResource(TypedDict):
    name: Literal['showroom']
    data: Sequence[Mapping[str, Any]]
    """
    Data items have to conform to the Showroom table schema
    """
    schema: Literal[
        'https://github.com/datisthq/cardealerdp/releases/download/v0.0.0-dev/showroom.json'
    ]


Resource = Union[CarResource, DealerResource, ShowroomResource]


Package = TypedDict(
    'Package',
    {
        '$schema': Literal[
            'https://github.com/datisthq/cardealerdp/releases/download/v0.3.0/profile.json'
        ],
        'resources': Sequence[Resource],
    },
)


class CarDealerDataPackageProfile(Package):
    pass
