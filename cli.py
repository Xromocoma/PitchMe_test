import argparse
from pathlib import Path

from profile_seeker import ProfileSeeker, LocationFilter


def find_python_developer(source_file_path: Path):
    seeker = ProfileSeeker(
        location=LocationFilter(city="London"),
        experience=8,
        last_job_title=[("backend", "developer"), "software engineer"],
        last_job_title_count=3,
        last_job_skills=["python", "c++"],
        last_job_company_name="FAANG",
        last_job_company_name_count=2,
    )
    seeker.process_profiles_from_file(file_path=source_file_path)


def find_ux_designer(source_file_path: Path):
    print("Not implemented yet")
    return


FILTER_FUNCTION_BY_NAME = {
    "python-developer": find_python_developer,
    "ux-designer": find_ux_designer,
}

if __name__ == '__main__':

    # Define the command-line arguments
    parser = argparse.ArgumentParser(description='Profile filter CLI')
    parser.add_argument(
        '--filter',
        type=str,
        help='Type of filtering',
        choices=["python-developer", "ux-designer"],
        required=True
    )
    parser.add_argument(
        '--input',
        type=Path,
        help='Path to .json file with candidates data',
        required=True
    )

    # Parse the arguments
    args = parser.parse_args()

    func = FILTER_FUNCTION_BY_NAME.get(args.filter)
    func(args.input)
