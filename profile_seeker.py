import datetime
import itertools
import json
import re
from pathlib import Path
from typing import List, Union, Optional, Set, Tuple

from profile_schema import Profile, Experience, LocationFilter


class LocationException(Exception):
    pass


class EmtpyProfileException(Exception):
    pass


class ExperienceException(Exception):
    pass


class JobTitleException(Exception):
    pass


class JobTitleLimitCombinationsException(Exception):
    pass


class JobSkillsException(Exception):
    pass


class JobCompanyNameException(Exception):
    pass


class ProfileSeeker:
    def __init__(self, **kwargs):
        self.filter_location: Optional[LocationFilter] = kwargs.get("location")
        self.filter_experience: int = kwargs.get("experience", None)

        self.filter_last_job_title: List[Union[str, tuple]] = kwargs.get("last_job_title", [])
        self.filter_last_job_title_count: int = kwargs.get("last_job_title_count", None)

        self.filter_last_job_company_name: str = kwargs.get("last_job_company_name", "")
        self.filter_last_job_company_name_count: int = kwargs.get("last_job_company_name_count", None)

        self.filter_last_job_skills: Set[str] = {skill.lower() for skill in kwargs.get("last_job_skills", [])}

        self.profiles: List[Profile] = []
        self.current_profile: Optional[Profile] = None

        for item in self.filter_last_job_company_name:
            if isinstance(item, tuple) and len(item) > 4:
                raise JobTitleLimitCombinationsException(
                    "Forbidden use more than 4 lexeme in tuple Jobs title combination"
                )

    def _check_location(self):
        if not self.filter_location:
            return

        for key, value in self.filter_location.dict(exclude_unset=True, exclude_none=True).items():

            if not getattr(self.current_profile.location, key, "").lower() == value.lower():
                raise LocationException(
                    f"Not pass by location filter, current_location='{self.current_profile.location}',"
                    f" filter='{self.filter_location}'"
                )

    def _get_calculated_experience(self) -> float:
        current_date = datetime.date.today()
        _days = 0
        start_date = None
        end_date = None
        for job in self.current_profile.experiences[::-1]:
            if not job.ends_at:
                job.ends_at = current_date

            if not start_date and not end_date:
                start_date, end_date = job.starts_at, job.ends_at
                _days += abs((end_date - start_date).days)

            elif (
                    not (start_date <= job.starts_at <= end_date)
                    and not (start_date <= job.ends_at <= end_date)
            ):
                _days += abs((job.ends_at - job.starts_at).days)

            elif start_date <= job.starts_at <= end_date:
                _days += abs((job.ends_at - end_date).days)

        _month = _days * 0.032855
        return _month / 12

    def _check_experience(self):
        if not self.filter_experience:
            return

        current_experience = self._get_calculated_experience()
        if current_experience < self.filter_experience:
            raise ExperienceException(
                f"Not enough experience, current={int(current_experience)}, filter={self.filter_experience}"
            )

    def _get_job_title_pattern(self) -> str:
        re_filters = []
        for title in self.filter_last_job_title:
            if isinstance(title, str):
                re_filters.append(title)
                continue

            if len(title) == 1:
                re_filters.append(title[0])
                continue

            filter_str = []
            for x in range(len(title)):
                _title = list(title)
                first_word = _title.pop(x)

                # made limit in init for good performance of permutations
                for combinations in itertools.permutations(_title):
                    filter_str.append(fr"\b{first_word}.*{'.*'.join(combinations)}")

            re_filters.append(f"({'|'.join(filter_str)})")
        return "|".join(re_filters)

    def _check_job_title(self):
        if not self.filter_last_job_title:
            return

        if self.filter_last_job_title_count:
            experience = self.current_profile.experiences[:self.filter_last_job_title_count]
        else:
            experience = self.current_profile.experiences

        if not any(
                [
                    re.search(self._get_job_title_pattern(), job.job_title, flags=re.IGNORECASE)
                    for job in experience
                ]
        ):
            raise JobTitleException(
                f"Last {self.filter_last_job_title_count} jobs not include {self.filter_last_job_title}"
            )

    def _check_job_company_name(self):
        if not self.filter_last_job_title:
            return

        if self.filter_last_job_company_name_count:
            experience = self.current_profile.experiences[:self.filter_last_job_company_name_count]
        else:
            experience = self.current_profile.experiences

        if not any(
                [
                    re.match(fr"^{self.filter_last_job_company_name}($|\s+)", job.company_name, flags=re.IGNORECASE)
                    for job in experience
                ]
        ):
            raise JobCompanyNameException(
                f"Last {self.filter_last_job_company_name_count} jobs "
                f"not include company_name='{self.filter_last_job_company_name}'"
            )

    def _check_job_skills(self):
        skills: Set = {skill.lower() for skill in self.current_profile.experiences[0].skills}

        if not self.filter_last_job_skills.issubset(skills):
            raise JobSkillsException(f"Past job not include skills:{self.filter_last_job_skills}")

    def _check_conditions(self):
        self._check_location()
        self._check_experience()
        self._check_job_company_name()
        self._check_job_skills()
        self._check_job_title()

    def process_profile(self, profile: Optional[Profile] = None) -> Tuple[bool, Optional[str]]:
        if not (profile or self.current_profile):
            raise EmtpyProfileException("Profile not provided")

        if profile:
            self.current_profile = profile

        try:
            self.current_profile.experiences = Experience.sort_by_starts_at(
                experiences=self.current_profile.experiences,
                reverse=True,
            )

            self._check_conditions()
        except (
                ExperienceException,
                JobCompanyNameException,
                JobSkillsException,
                JobTitleException,
                JobTitleLimitCombinationsException,
                LocationException,
        ) as exc:
            return False, str(exc)

        return True, None

    def process_profiles_from_file(self, file_path: Path):
        # open file & serialize data
        # suppose that raise better in this case, removed all try\except for this block of code
        with open(file_path) as f:
            self.profiles = [Profile(**x) for x in json.load(f)]

        for profile in self.profiles:
            self.current_profile = profile
            _name = f"{self.current_profile.first_name} {self.current_profile.last_name}"
            status, err = self.process_profile()
            if status is True:
                print(f"{_name} - True")
            else:
                print(f"{_name} - False: {err}")
