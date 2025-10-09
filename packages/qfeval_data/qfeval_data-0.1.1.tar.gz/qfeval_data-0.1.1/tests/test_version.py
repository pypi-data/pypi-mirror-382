import configparser
import os.path

import qfeval_data


def test_version() -> None:
    parser = configparser.ConfigParser()
    with open(
        os.path.join(os.path.dirname(__file__), "..", "pyproject.toml"), "r"
    ) as f:
        lines = f.readlines()[:5]
    parser.read_string("\n".join(lines))
    assert qfeval_data.__version__ == parser["project"]["version"].replace(
        '"', ""
    )
