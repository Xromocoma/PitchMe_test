import pytest
from profile_schema import Profile, Location, Experience, LocationFilter
from profile_seeker import ProfileSeeker


@pytest.fixture
def source_file_path() -> str:
    return 'tests/test_profiles.json'


@pytest.fixture
def valid_profile() -> Profile:
    return Profile(
        first_name="Bill",
        last_name="Murray",
        skills=["Docker", "PostgreSQL", "MongoDB", "Redis", "Kafka", "Asyncio"],
        description="True - candidate OK",
        location=Location(
            city="London",
            country="England",
        ),
        experiences=[
            Experience(
                company_name="FAANG",
                job_title="Backend Developer",
                description="",
                skills=["python", "c++"],
                starts_at="2010-03-15",
                location=Location(
                    city="London",
                    country="",
                ),
            )
        ]
    )


@pytest.fixture
def seeker() -> ProfileSeeker:
    return ProfileSeeker(
        location=LocationFilter(city="London"),
        experience=8,
        last_job_title=[("backend", "developer"), "software engineer"],
        last_job_title_count=3,
        last_job_skills=["python", "c++"],
        last_job_company_name="FAANG",
        last_job_company_name_count=2,
    )
