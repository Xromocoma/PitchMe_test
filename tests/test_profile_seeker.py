import datetime
import json
from pathlib import Path

import pytest

from profile_schema import Profile, LocationFilter
from profile_seeker import (
    ProfileSeeker, LocationException, ExperienceException,
    JobTitleException, JobSkillsException, JobCompanyNameException
)


@pytest.mark.parametrize(
    "location, raise_exception",
    [
        (LocationFilter(city="Moscow"), True),
        (LocationFilter(city="Rome"), True),
        (LocationFilter(city="London"), False),
        (LocationFilter(city="LonDoN"), False),
        (LocationFilter(country="England"), False),
        (LocationFilter(country="Italy"), True)
    ])
def test_check_location(seeker: ProfileSeeker, valid_profile: Profile, location: LocationFilter, raise_exception: bool):
    try:
        seeker.filter_location = location
        seeker.current_profile = valid_profile
        seeker._check_location()
        if raise_exception is True:
            pytest.fail("exception not called", pytrace=True)
    except LocationException as exc:
        if raise_exception is False:
            pytest.fail(str(exc), pytrace=True)
    except Exception as exc:
        pytest.fail(str(exc), pytrace=True)


@pytest.mark.parametrize(
    "starts_at, result",
    [
        ("2006-10-12", 16),
        ("2018-05-12", 4),
    ])
def test_check_calculate_experience(seeker: ProfileSeeker, valid_profile: Profile, starts_at: str, result: bool):
    valid_profile.experiences[0].starts_at = datetime.datetime.strptime(starts_at, "%Y-%m-%d").date()
    seeker.current_profile = valid_profile

    assert int(seeker._get_calculated_experience()) == result


@pytest.mark.parametrize(
    "starts_at, raise_exception",
    [
        ("2006-10-12", False),
        ("2018-05-12", True),
    ])
def test_check_experience(seeker: ProfileSeeker, valid_profile: Profile, starts_at: str, raise_exception: bool):
    try:
        valid_profile.experiences[0].starts_at = datetime.datetime.strptime(starts_at, "%Y-%m-%d").date()

        seeker.current_profile = valid_profile
        seeker._check_experience()

        if raise_exception is True:
            pytest.fail("exception not called", pytrace=True)
    except ExperienceException as exc:
        if raise_exception is False:
            pytest.fail(str(exc), pytrace=True)
    except Exception as exc:
        pytest.fail(str(exc), pytrace=True)


@pytest.mark.parametrize(
    "job_title, raise_exception",
    [
        ("SofTware EnginEEr (python)", False),
        ("python developer backend", False),
        ("python Backend developer", False),
        ("python Frontend developer", True),
        ("python backend", True),
        ("engineer software", True),
    ])
def test_check_job_title(seeker: ProfileSeeker, valid_profile: Profile, job_title: str, raise_exception: bool):
    try:
        valid_profile.experiences[0].job_title = job_title

        seeker.current_profile = valid_profile
        seeker._check_job_title()

        if raise_exception is True:
            pytest.fail("exception not called", pytrace=True)
    except JobTitleException as exc:
        if raise_exception is False:
            pytest.fail(str(exc), pytrace=True)
    except Exception as exc:
        pytest.fail(str(exc), pytrace=True)


@pytest.mark.parametrize(
    "company_name, raise_exception",
    [
        ("feeng", True),
        ("FAANG limited", False),
        ("sub FAANG", True),
        ("FAANG", False),
        ("SUperFAANG", True),
        ("FAANGON", True),
    ])
def test_check_job_company_name(seeker: ProfileSeeker, valid_profile: Profile, company_name, raise_exception):
    try:
        valid_profile.experiences[0].company_name = company_name

        seeker.current_profile = valid_profile
        seeker._check_job_company_name()

        if raise_exception is True:
            pytest.fail("exception not called", pytrace=True)
    except JobCompanyNameException as exc:
        if raise_exception is False:
            pytest.fail(str(exc), pytrace=True)
    except Exception as exc:
        pytest.fail(str(exc), pytrace=True)


@pytest.mark.parametrize(
    "job_skills, raise_exception",
    [
        (["c++"], True),
        (["python"], True),
        (["c++", "react", "python"], False)
    ])
def test_check_job_skills(seeker: ProfileSeeker, valid_profile: Profile, job_skills: str, raise_exception: bool):
    try:
        valid_profile.experiences[0].skills = job_skills

        seeker.current_profile = valid_profile
        seeker._check_job_skills()

        if raise_exception is True:
            pytest.fail("exception not called", pytrace=True)
    except JobSkillsException as exc:
        if raise_exception is False:
            pytest.fail(str(exc), pytrace=True)
    except Exception as exc:
        pytest.fail(str(exc), pytrace=True)


def test_full_process(seeker: ProfileSeeker):
    try:
        seeker.process_profiles_from_file('tests/test_profiles.json')
    except Exception as exc:
        pytest.fail(str(exc), pytrace=True)


def test_each_profile(seeker: ProfileSeeker, source_file_path: Path):

    with open(source_file_path) as f:
        seeker.profiles = [Profile(**x) for x in json.load(f)]

    result = []
    for profile in seeker.profiles:
        status, _ = seeker.process_profile(profile=profile)
        result.append(
            f"{seeker.current_profile.first_name} {seeker.current_profile.last_name} - {status}"
        )

    assert result == [
        "Jhon Smith - False",
        "Garry Fisher - False",
        "Test False - False",
        "Doctor Who - True",
        "Clark Kent - True",
    ]

