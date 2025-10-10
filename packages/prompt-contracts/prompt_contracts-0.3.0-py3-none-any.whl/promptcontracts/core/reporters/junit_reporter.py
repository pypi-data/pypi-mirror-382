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
                fixture_status = fixture_result.get("status", "UNKNOWN")
                sampling_meta = fixture_result.get("sampling_metadata", {})
                repair_ledger = fixture_result.get("repair_ledger", [])

                for check in fixture_result.get("checks", []):
                    testcase = ET.SubElement(testsuite, "testcase")
                    testcase.set("name", f"{fixture_id}.{check.get('type')}")
                    testcase.set("classname", target_name)

                    # Add latency and sampling metadata as properties
                    properties = ET.SubElement(testcase, "properties")
                    if sampling_meta:
                        prop = ET.SubElement(properties, "property")
                        prop.set("name", "n_samples")
                        prop.set("value", str(sampling_meta.get("n_samples", 1)))

                        if "pass_rate" in sampling_meta:
                            prop = ET.SubElement(properties, "property")
                            prop.set("name", "pass_rate")
                            prop.set("value", f"{sampling_meta['pass_rate']:.2f}")

                        if "confidence_interval" in sampling_meta:
                            ci = sampling_meta["confidence_interval"]
                            if ci:
                                prop = ET.SubElement(properties, "property")
                                prop.set("name", "confidence_interval")
                                prop.set("value", f"[{ci[0]:.2f}, {ci[1]:.2f}]")

                    # FAIL and NONENFORCEABLE map to <failure/>
                    if not check.get("passed") or fixture_status in ["FAIL", "NONENFORCEABLE"]:
                        failure = ET.SubElement(testcase, "failure")
                        failure_msg = check.get("message", "Check failed")
                        if fixture_status == "NONENFORCEABLE":
                            failure_msg = f"NONENFORCEABLE: {failure_msg}"
                        failure.set("message", failure_msg)
                        failure.text = failure_msg

                    # Add repair ledger to system-out if available
                    elif repair_ledger and check.get("passed"):
                        system_out = ET.SubElement(testcase, "system-out")
                        repairs_applied = [r.get("steps_applied", []) for r in repair_ledger]
                        all_steps = [step for steps in repairs_applied for step in steps]
                        if all_steps:
                            system_out.text = f"Repairs applied: {', '.join(set(all_steps))}"

        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(testsuites)).toprettyxml(indent="  ")

        Path(output_path).write_text(xml_str)
        print(f"JUnit XML written to {output_path}")
