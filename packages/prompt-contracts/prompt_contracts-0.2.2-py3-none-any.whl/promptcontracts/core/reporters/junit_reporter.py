"""JUnit XML reporter for CI integration."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from xml.dom import minidom


class JUnitReporter:
    """JUnit XML reporter."""

    def report(self, results: dict[str, Any], output_path: str = "junit.xml"):
        """
        Write results as JUnit XML.

        Args:
            results: Results from ContractRunner
            output_path: Path to write XML
        """
        testsuites = ET.Element("testsuites")

        for target_result in results.get("targets", []):
            target = target_result["target"]
            target_name = f"{target.get('type')}:{target.get('model')}"

            summary = target_result.get("summary", {})
            total_checks = summary.get("total_checks", 0)
            passed_checks = summary.get("passed_checks", 0)
            failures = total_checks - passed_checks

            testsuite = ET.SubElement(testsuites, "testsuite")
            testsuite.set("name", target_name)
            testsuite.set("tests", str(total_checks))
            testsuite.set("failures", str(failures))
            testsuite.set("errors", "0")

            # Add test cases for each check
            for fixture_result in target_result.get("fixtures", []):
                fixture_id = fixture_result.get("fixture_id")

                for check in fixture_result.get("checks", []):
                    testcase = ET.SubElement(testsuite, "testcase")
                    testcase.set("name", f"{fixture_id}.{check.get('type')}")
                    testcase.set("classname", target_name)

                    if not check.get("passed"):
                        failure = ET.SubElement(testcase, "failure")
                        failure.set("message", check.get("message", "Check failed"))
                        failure.text = check.get("message", "Check failed")

        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(testsuites)).toprettyxml(indent="  ")

        Path(output_path).write_text(xml_str)
        print(f"JUnit XML written to {output_path}")
