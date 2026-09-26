import tempfile
import unittest
from pathlib import Path

from agent_utils import (
    InputError,
    MAX_SOURCE_BYTES,
    OutputValidationError,
    read_source,
    split_sentences,
    validate_generated_output,
)


class AgentUtilsTests(unittest.TestCase):
    def test_validate_generated_output_rejects_unsupported_content(self) -> None:
        output = (
            "Headline\nMars colony discovers aliens\n\n"
            "Summary\nColonists made a historic discovery on Mars.\n\n"
            "Key Points\n- Scientists confirmed extraterrestrial life."
        )
        with self.assertRaisesRegex(OutputValidationError, "not sufficiently grounded"):
            validate_generated_output(
                output,
                "Riverdale opened a community library with 5,000 books.",
                ("Headline", "Summary", "Key Points"),
                frozenset({"Key Points"}),
            )

    def test_validate_generated_output_rejects_punctuation_only_content(self) -> None:
        output = (
            "Headline\nRiverdale opened a community library.\n\n"
            "Summary\nRiverdale opened a community library.\n\n"
            "Key Points\n- !!! 🚀"
        )
        with self.assertRaisesRegex(OutputValidationError, "not sufficiently grounded"):
            validate_generated_output(
                output,
                "Riverdale opened a community library.",
                ("Headline", "Summary", "Key Points"),
                frozenset({"Key Points"}),
            )

    def test_validate_generated_output_rejects_short_token_command(self) -> None:
        output = (
            "Headline\nRiverdale opened a community library.\n\n"
            "Summary\nDo it now\n\n"
            "Key Points\n- Riverdale opened a community library."
        )
        with self.assertRaisesRegex(OutputValidationError, "not sufficiently grounded"):
            validate_generated_output(
                output,
                "Riverdale opened a community library.",
                ("Headline", "Summary", "Key Points"),
                frozenset({"Key Points"}),
            )

    def test_validate_generated_output_rejects_negation_flip(self) -> None:
        output = (
            "Headline\nThe council did approve the plan.\n\n"
            "Summary\nThe council did not approve the plan.\n\n"
            "Key Points\n- The council did approve the plan."
        )
        with self.assertRaisesRegex(OutputValidationError, "not sufficiently grounded"):
            validate_generated_output(
                output,
                "The council did approve the plan.",
                ("Headline", "Summary", "Key Points"),
                frozenset({"Key Points"}),
            )

    def test_validate_generated_output_rejects_sentence_substrings(self) -> None:
        cases = (
            (".", "Riverdale opened a community library."),
            ("Do", "Donors opened a community library."),
            ("approve the plan.", "The council did not approve the plan."),
        )
        for injected_content, source in cases:
            with self.subTest(injected_content=injected_content):
                output = (
                    f"Headline\n{source}\n\n"
                    f"Summary\n{injected_content}\n\n"
                    f"Key Points\n- {source}"
                )
                with self.assertRaisesRegex(OutputValidationError, "not sufficiently grounded"):
                    validate_generated_output(
                        output,
                        source,
                        ("Headline", "Summary", "Key Points"),
                        frozenset({"Key Points"}),
                    )

    def test_validate_generated_output_accepts_exact_source_entity(self) -> None:
        source = "Mayor Lina Ahmed opened a community library."
        output = (
            "Headline\nMayor Lina Ahmed opened a community library.\n\n"
            "Summary\nMayor Lina Ahmed opened a community library.\n\n"
            "Important Entities\n- Mayor Lina Ahmed"
        )

        validate_generated_output(
            output,
            source,
            ("Headline", "Summary", "Important Entities"),
            frozenset({"Important Entities"}),
        )

    def test_validate_generated_output_does_not_exempt_factual_sections(self) -> None:
        output = (
            "Headline\nRiverdale opened a community library.\n\n"
            "Summary\nDo it now\n\n"
            "Key Points\n- Riverdale opened a community library."
        )
        with self.assertRaisesRegex(OutputValidationError, "not sufficiently grounded"):
            validate_generated_output(
                output,
                "Riverdale opened a community library.",
                ("Headline", "Summary", "Key Points"),
                frozenset({"Key Points"}),
                frozenset({"Summary"}),
            )

    def test_validate_generated_output_accepts_exact_source_wording(self) -> None:
        source = (
            "Riverdale opened a community library. "
            "The library contains 5,000 books."
        )
        output = (
            "Headline\nRiverdale opened a community library.\n\n"
            "Summary\nRiverdale opened a community library. "
            "The library contains 5,000 books.\n\n"
            "Key Points\n- The library contains 5,000 books.\n\n"
            "Questions for Further Research\n- What should researchers examine next?"
        )

        validate_generated_output(
            output,
            source,
            ("Headline", "Summary", "Key Points", "Questions for Further Research"),
            frozenset({"Key Points", "Questions for Further Research"}),
            frozenset({"Questions for Further Research"}),
        )

    def test_validate_generated_output_rejects_missing_required_structure(self) -> None:
        with self.assertRaisesRegex(OutputValidationError, "required section structure"):
            validate_generated_output(
                "Headline\nRiverdale opens library",
                "Riverdale opened a community library.",
                ("Headline", "Summary", "Key Points"),
                frozenset({"Key Points"}),
            )

    def test_read_source_rejects_input_over_utf8_byte_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "oversized.txt"
            input_path.write_bytes(b"a" * (MAX_SOURCE_BYTES + 1))

            with self.assertRaisesRegex(
                InputError,
                rf"exceeds the {MAX_SOURCE_BYTES:,}-byte UTF-8 input limit",
            ):
                read_source(str(input_path))

    def test_time_abbreviations_do_not_split_sentences(self) -> None:
        text = "Buses run from 6 a.m. to 10 p.m. Officials will review the schedule."
        self.assertEqual(
            split_sentences(text),
            [
                "Buses run from 6 a.m. to 10 p.m.",
                "Officials will review the schedule.",
            ],
        )


if __name__ == "__main__":
    unittest.main()
