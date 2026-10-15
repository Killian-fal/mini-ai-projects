import subprocess
import sys

from interactive_support_core.registry import check_flows

CHECK_TRANSLATIONS = """
import interactive_support_core.registry
from interactive_support_core.translation import check_translations

check_translations()
"""


def test_every_issue_has_its_flow():
    check_flows()


def test_every_text_code_is_translated():
    result = subprocess.run(
        [sys.executable, "-c", CHECK_TRANSLATIONS], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
