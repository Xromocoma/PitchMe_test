from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class Location(BaseModel):
    city: str
    country: str


class LocationFilter(Location):
    city: Optional[str]
    country: Optional[str]


class Experience(BaseModel):
    company_name: str
    job_title: str
    description: str
    skills: List[str]
    starts_at: date
    ends_at: Optional[date]
    location: Location

    @staticmethod
    def sort_by_starts_at(experiences: List['Experience'], reverse: bool = False) -> List['Experience']:
        return sorted(experiences, key=lambda x: x.starts_at, reverse=reverse)


class Profile(BaseModel):
    first_name: str
    last_name: str
    skills: List[str]
    description: str
    location: Location
    experiences: List[Experience]
