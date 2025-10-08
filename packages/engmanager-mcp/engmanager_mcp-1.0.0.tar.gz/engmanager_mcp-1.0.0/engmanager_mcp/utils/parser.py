"""Template parser for procedure files with variable substitution"""

import re
from typing import Dict, List, Optional, Tuple

from ..utils.errors import TemplateParsingError


class ProcedureParser:
    """Parser for procedure markdown files with template variables"""

    def __init__(self, content: str, variables: Optional[Dict[str, str]] = None):
        """Initialize parser

        Args:
            content: Raw procedure file content
            variables: Dictionary of variables for substitution
        """
        self.content = content
        self.variables = variables or {}

    def substitute_variables(self) -> str:
        """Substitute template variables in content

        Supports variable syntax: {VAR_NAME}

        Returns:
            Content with variables substituted

        Raises:
            TemplateParsingError: If required variables are missing
        """
        # Find all variables in template
        variable_pattern = r'\{([A-Z_][A-Z0-9_]*)\}'
        found_variables = set(re.findall(variable_pattern, self.content))

        # Check for missing variables
        missing = found_variables - set(self.variables.keys())
        if missing:
            raise TemplateParsingError(
                f"Missing required template variables: {', '.join(sorted(missing))}"
            )

        # Perform substitution
        result = self.content
        for var_name, var_value in self.variables.items():
            result = result.replace(f"{{{var_name}}}", str(var_value))

        return result

    def extract_sections(self) -> Dict[str, str]:
        """Extract sections from markdown based on headings

        Returns:
            Dictionary mapping section titles to content
        """
        sections = {}
        current_section = None
        current_content = []

        for line in self.content.split('\n'):
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                # Save previous section if exists
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = heading_match.group(2).strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def get_section(self, section_title: str) -> Optional[str]:
        """Get content of a specific section

        Args:
            section_title: Title of the section to retrieve

        Returns:
            Section content or None if not found
        """
        sections = self.extract_sections()
        return sections.get(section_title)

    def find_section_by_keyword(self, keyword: str) -> List[Tuple[str, str]]:
        """Find sections containing a keyword

        Args:
            keyword: Keyword to search for (case-insensitive)

        Returns:
            List of (section_title, content) tuples
        """
        sections = self.extract_sections()
        keyword_lower = keyword.lower()

        matches = []
        for title, content in sections.items():
            if keyword_lower in title.lower() or keyword_lower in content.lower():
                matches.append((title, content))

        return matches

    def extract_steps(self) -> List[Tuple[int, str, str]]:
        """Extract numbered workflow steps

        Looks for sections starting with numbers (e.g., "1. Issue Selection")

        Returns:
            List of (step_number, step_title, content) tuples
        """
        sections = self.extract_sections()
        steps = []

        step_pattern = r'^(\d+)\.\s+(.+)$'

        for title, content in sections.items():
            match = re.match(step_pattern, title)
            if match:
                step_number = int(match.group(1))
                step_title = match.group(2).strip()
                steps.append((step_number, step_title, content))

        # Sort by step number
        steps.sort(key=lambda x: x[0])
        return steps

    def get_step(self, step_number: int) -> Optional[Tuple[str, str]]:
        """Get a specific numbered step

        Args:
            step_number: Number of the step to retrieve

        Returns:
            Tuple of (step_title, content) or None if not found
        """
        steps = self.extract_steps()
        for num, title, content in steps:
            if num == step_number:
                return (title, content)
        return None

    def get_next_step(self, current_step: int) -> Optional[Tuple[int, str, str]]:
        """Get the next step after the current one

        Args:
            current_step: Current step number

        Returns:
            Tuple of (step_number, step_title, content) or None if no next step
        """
        steps = self.extract_steps()
        for num, title, content in steps:
            if num == current_step + 1:
                return (num, title, content)
        return None

    def format_step(self, step_number: int, step_title: str, content: str) -> str:
        """Format a step for display

        Args:
            step_number: Step number
            step_title: Step title
            content: Step content

        Returns:
            Formatted step as markdown
        """
        return f"""## Step {step_number}: {step_title}

{content}
"""

    def get_all_steps_summary(self) -> str:
        """Get a summary of all steps

        Returns:
            Formatted list of all steps
        """
        steps = self.extract_steps()
        if not steps:
            return "No numbered steps found in procedure."

        lines = ["# Workflow Steps\n"]
        for num, title, _ in steps:
            lines.append(f"{num}. {title}")

        return '\n'.join(lines)


def parse_procedure(
    content: str,
    variables: Optional[Dict[str, str]] = None
) -> ProcedureParser:
    """Convenience function to create a parser

    Args:
        content: Procedure file content
        variables: Template variables

    Returns:
        Configured ProcedureParser instance
    """
    return ProcedureParser(content, variables)
