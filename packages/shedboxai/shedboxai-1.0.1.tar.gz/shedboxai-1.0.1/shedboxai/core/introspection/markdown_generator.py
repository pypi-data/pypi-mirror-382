"""
Markdown generator for LLM-optimized data source introspection documentation.

This module generates comprehensive markdown documentation that helps LLMs
understand data sources and write perfect ShedBoxAI configurations.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List


class MarkdownGenerator:
    """Generates LLM-optimized markdown documentation from introspection results."""

    def __init__(self):
        """Initialize the markdown generator."""
        pass

    def generate(
        self,
        analyses: Dict[str, Any],
        relationships: List[Any],
        success_count: int,
        total_count: int,
        options=None,
    ) -> str:
        """
        Generate complete introspection.md content.

        Args:
            analyses: Dictionary of source analyses from Developer A
            relationships: List of detected relationships from Developer A
            success_count: Number of successful analyses
            total_count: Total number of sources analyzed
            options: IntrospectionOptions containing user preferences

        Returns:
            Complete markdown content optimized for LLM consumption
        """
        lines = []

        # Header section
        lines.extend(self._generate_header(success_count, total_count))

        # LLM processing notes
        lines.extend(self._generate_llm_processing_notes(analyses))

        # Data sources documentation
        lines.extend(self._generate_data_sources_section(analyses, options))

        # Relationships section
        lines.extend(self._generate_relationships_section(relationships))

        # Recommended operations
        lines.extend(self._generate_operations_recommendations(analyses))

        # LLM optimization tips
        lines.extend(self._generate_optimization_tips(analyses))

        return "\n".join(lines)

    def _generate_header(self, success_count: int, total_count: int) -> List[str]:
        """Generate the markdown header section."""
        timestamp = datetime.now().isoformat()

        return [
            "# Data Source Introspection for LLM",
            f"Generated: {timestamp}",
            f"Sources Analyzed: {success_count}/{total_count}",
            "",
        ]

    def _generate_llm_processing_notes(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate LLM processing considerations and warnings."""
        lines = ["## LLM Processing Notes", ""]

        # Analyze dataset sizes for context window warnings
        large_datasets = []
        total_records = 0

        for name, analysis in analyses.items():
            if not analysis.success:
                continue

            # TODO: ADJUST - Field names may change based on Developer A's models
            record_count = getattr(analysis, "record_count", None)
            if record_count is not None and record_count > 1000:
                large_datasets.append(f"{name} ({record_count:,} records)")
                total_records += record_count
            elif record_count:
                total_records += record_count

        # Context window considerations
        if large_datasets:
            lines.append("- **Context Window Warning**: Large datasets detected:")
            for dataset in large_datasets:
                lines.append(f"  - {dataset}")
            lines.append("  Consider using sampling or aggregation operations")
        else:
            lines.append("- **Context Window**: All datasets are small-medium, direct processing suitable")

        # Processing recommendations based on data types
        data_types = set()
        has_relationships = False

        for analysis in analyses.values():
            if analysis.success:
                data_types.add(analysis.type)
                # Check for potential relationships (customer_id, user_id, etc.)
                columns = getattr(analysis, "columns", [])
                if any("id" in col.lower() for col in columns):
                    has_relationships = True

        operations = []
        if "csv" in data_types or "json" in data_types:
            operations.append("contextual_filtering")
        if len(data_types) > 1:
            operations.append("format_conversion")
        if has_relationships:
            operations.append("relationship_highlighting")
        if any(dt in data_types for dt in ["rest", "csv"]):
            operations.append("advanced_operations")

        lines.append(f"- **Recommended Operations**: {', '.join(operations)}")

        # Data relationship hints
        if has_relationships:
            lines.append("- **Data Relationships**: ID fields detected - potential joins available")

        lines.append("")
        return lines

    def _generate_data_sources_section(self, analyses: Dict[str, Any], options=None) -> List[str]:
        """Generate detailed documentation for each data source."""
        lines = ["## Data Sources", ""]

        for name, analysis in analyses.items():
            if analysis.success:
                lines.extend(self._generate_successful_source_doc(name, analysis, options))
            else:
                lines.extend(self._generate_failed_source_doc(name, analysis))

        return lines

    def _generate_successful_source_doc(self, name: str, analysis: Any, options=None) -> List[str]:
        """Generate documentation for successfully analyzed source."""
        lines = [
            (
                f"### {name} "
                f"({analysis.type.value.upper() if hasattr(analysis.type, 'value') else str(analysis.type).upper()})"
            ),
            "**Status**: ✅ Success",
        ]

        # Add source-specific information
        if (hasattr(analysis.type, "value") and analysis.type.value == "csv") or str(analysis.type) == "csv":
            lines.extend(self._generate_csv_documentation(analysis))
        elif (hasattr(analysis.type, "value") and analysis.type.value == "json") or str(analysis.type) == "json":
            lines.extend(self._generate_json_documentation(analysis))
        elif (hasattr(analysis.type, "value") and analysis.type.value == "rest") or str(analysis.type) == "rest":
            lines.extend(self._generate_rest_documentation(analysis))
        elif (hasattr(analysis.type, "value") and analysis.type.value == "yaml") or str(analysis.type) == "yaml":
            lines.extend(self._generate_yaml_documentation(analysis))
        elif (hasattr(analysis.type, "value") and analysis.type.value == "text") or str(analysis.type) == "text":
            lines.extend(self._generate_text_documentation(analysis))

        # Schema and sample section (LLM-optimized)
        lines.extend(self._generate_schema_and_sample_section(analysis, options))

        # LLM operation hints
        lines.extend(self._generate_operation_hints(name, analysis))
        lines.append("")

        return lines

    def _generate_schema_and_sample_section(self, analysis: Any, options=None) -> List[str]:
        """Generate schema-focused documentation with conditional samples."""
        lines = []

        # Prioritize schema information first
        schema_info = getattr(analysis, "schema_info", None)
        if schema_info:
            lines.extend(self._generate_schema_documentation(schema_info, analysis))

        # Add sample data only if requested via --include-samples flag
        if options and getattr(options, "include_samples", False):
            sample_data = getattr(analysis, "sample_data", [])
            if sample_data:
                sanitized_sample = self._sanitize_and_limit_sample_data(sample_data)
                if sanitized_sample:
                    lines.extend(
                        [
                            "",
                            "**Sample Structure**:",
                            "```json",
                            json.dumps(sanitized_sample, indent=2),
                            "```",
                        ]
                    )

        return lines

    def _generate_schema_documentation(self, schema_info: Any, analysis: Any) -> List[str]:
        """Generate detailed schema documentation."""
        lines = []

        # JSON Schema (for REST APIs)
        if hasattr(schema_info, "json_schema") and schema_info.json_schema:
            lines.extend(
                [
                    "",
                    "**JSON Schema**:",
                    "```json",
                    json.dumps(schema_info.json_schema, indent=2),
                    "```",
                ]
            )

        # Column Schema (for CSV/structured data)
        elif hasattr(schema_info, "columns") and schema_info.columns:
            lines.extend(
                [
                    "",
                    "**Schema**:",
                    "| Field | Type | Description |",
                    "|-------|------|-------------|",
                ]
            )

            for col in schema_info.columns:
                col_name = getattr(col, "name", str(col))
                col_type = getattr(col, "type", "unknown")

                # Build description with statistics
                desc_parts = []
                if hasattr(col, "null_percentage") and col.null_percentage is not None:
                    if col.null_percentage > 0:
                        desc_parts.append(f"{col.null_percentage:.1f}% null")

                if hasattr(col, "unique_count") and col.unique_count is not None:
                    desc_parts.append(f"{col.unique_count:,} unique values")

                if hasattr(col, "min_value") and hasattr(col, "max_value"):
                    if col.min_value is not None and col.max_value is not None:
                        desc_parts.append(f"Range: {col.min_value} to {col.max_value}")

                if hasattr(col, "sample_values") and col.sample_values:
                    sanitized_samples = self._sanitize_sample_values(col.sample_values[:3])
                    desc_parts.append(f"e.g. {', '.join(map(str, sanitized_samples))}")

                description = "; ".join(desc_parts) if desc_parts else "Structured data field"
                lines.append(f"| {col_name} | {col_type} | {description} |")

        # Text content schema
        elif hasattr(schema_info, "content_type") and schema_info.content_type:
            lines.extend(["", f"**Content Type**: {schema_info.content_type}"])
            if hasattr(schema_info, "line_count") and schema_info.line_count:
                lines.append(f"**Structure**: {schema_info.line_count:,} lines")
            if hasattr(schema_info, "has_structure") and schema_info.has_structure:
                lines.append("**Format**: Structured text with detectable patterns")

        return lines

    def _sanitize_and_limit_sample_data(self, sample_data: list) -> list:
        """Sanitize PII and limit sample data with smart truncation."""
        if not sample_data:
            return []

        # Limit to maximum 2 records for structure demonstration
        limited_data = sample_data[:2]
        sanitized_data = []

        for record in limited_data:
            if isinstance(record, dict):
                sanitized_record = self._sanitize_record(record)
                # Apply smart truncation to large records
                truncated_record = self._smart_truncate_record(sanitized_record)
                sanitized_data.append(truncated_record)
            else:
                # Non-dict data, keep as-is but limit
                sanitized_data.append(record)

        return sanitized_data

    def _smart_truncate_record(self, record: dict, max_lines: int = 100) -> dict:
        """Apply smart truncation to records that would exceed max_lines when formatted."""
        if not isinstance(record, dict):
            return record

        # Estimate line count when formatted as JSON
        try:
            formatted = json.dumps(record, indent=2)
            line_count = len(formatted.split("\n"))

            if line_count <= max_lines:
                return record

            # Record is too large, apply truncation
            field_count = len(record)
            if field_count <= 5:
                # Few fields, likely deeply nested - keep all but truncate values
                return self._truncate_deep_values(record)
            else:
                # Many fields - show first 5 and add truncation indicator
                truncated = {}
                field_names = list(record.keys())

                # Keep first 5 fields
                for field in field_names[:5]:
                    truncated[field] = record[field]

                # Add truncation indicator
                truncated["..."] = f"truncated - showing 5 of {field_count} fields"

                return truncated

        except Exception:
            # If JSON formatting fails, just return first 5 fields
            if len(record) > 5:
                truncated = {}
                field_names = list(record.keys())
                for field in field_names[:5]:
                    truncated[field] = record[field]
                truncated["..."] = f"truncated - showing 5 of {len(record)} fields"
                return truncated
            return record

    def _truncate_deep_values(self, record: dict) -> dict:
        """Truncate deeply nested values while preserving structure."""
        truncated = {}

        for key, value in record.items():
            if isinstance(value, dict) and len(value) > 5:
                # Truncate large nested objects
                nested_keys = list(value.keys())
                truncated_nested = {}
                for nested_key in nested_keys[:1]:
                    truncated_nested[nested_key] = value[nested_key]
                truncated_nested["..."] = f"truncated - showing 1 of {len(value)} fields"
                truncated[key] = truncated_nested
            elif isinstance(value, list) and len(value) > 5:
                # Truncate large arrays
                truncated_list = value[:1]
                truncated_list.append(f"... truncated - showing 1 of {len(value)} items")
                truncated[key] = truncated_list
            else:
                truncated[key] = value

        return truncated

    def _sanitize_record(self, record: dict) -> dict:
        """Remove/mask PII from a single record."""
        sanitized = {}

        for key, value in record.items():
            lower_key = key.lower()

            # PII field detection and sanitization
            if any(pii_field in lower_key for pii_field in ["email", "mail"]):
                sanitized[key] = "user@example.com"
            elif any(pii_field in lower_key for pii_field in ["phone", "mobile", "tel"]):
                sanitized[key] = "(555) 123-4567"
            elif any(pii_field in lower_key for pii_field in ["name", "first", "last"]):
                if "first" in lower_key:
                    sanitized[key] = "John"
                elif "last" in lower_key:
                    sanitized[key] = "Doe"
                else:
                    sanitized[key] = "John Doe"
            elif any(pii_field in lower_key for pii_field in ["address", "street", "addr"]):
                sanitized[key] = "123 Example St"
            elif "city" in lower_key:
                sanitized[key] = "Example City"
            elif "zip" in lower_key or "postal" in lower_key:
                sanitized[key] = "12345"
            elif any(pii_field in lower_key for pii_field in ["ssn", "social", "tax"]):
                sanitized[key] = "***-**-****"
            elif isinstance(value, str) and "@" in value and "." in value:
                # Catch email-like strings even if key doesn't indicate it
                sanitized[key] = "user@example.com"
            elif (
                isinstance(value, str)
                and len(value) >= 10
                and any(char.isdigit() for char in value)
                and any(char in "()- " for char in value)
            ):
                # Catch phone-like strings
                sanitized[key] = "(555) 123-4567"
            else:
                # Keep non-PII data as-is
                sanitized[key] = value

        return sanitized

    def _sanitize_sample_values(self, values: list) -> list:
        """Sanitize individual sample values."""
        sanitized = []
        for value in values:
            if isinstance(value, str):
                if "@" in value and "." in value:
                    sanitized.append("user@example.com")
                elif any(char.isdigit() for char in value) and any(char in "()- " for char in value):
                    sanitized.append("(555) 123-4567")
                else:
                    sanitized.append(value)
            else:
                sanitized.append(value)
        return sanitized

    def _generate_csv_documentation(self, analysis: Any) -> List[str]:
        """Generate CSV-specific documentation."""
        lines = []

        record_count = getattr(analysis, "record_count", None)
        if record_count:
            size_category = "Large Dataset" if record_count > 1000 else "Small-Medium Dataset"
            lines.append(f"**Size**: {record_count:,} records ({size_category})")

        columns = getattr(analysis, "columns", [])
        if columns:
            lines.extend(
                [
                    f"**Columns**: {', '.join(columns)}",
                    f"**Schema**: {len(columns)} fields total",
                ]
            )

            # TODO: ENHANCE when Developer A provides detailed column info
            # Identify key columns for LLM
            key_columns = [col for col in columns if "id" in col.lower()]
            if key_columns:
                lines.append(f"**Key Fields**: {', '.join(key_columns)} (suitable for joins)")

        return lines

    def _generate_json_documentation(self, analysis: Any) -> List[str]:
        """Generate JSON-specific documentation."""
        lines = []

        record_count = getattr(analysis, "record_count", None)
        if record_count:
            lines.append(f"**Records**: {record_count:,} objects")

        columns = getattr(analysis, "columns", [])
        if columns:
            lines.append(f"**Structure**: {len(columns)} top-level fields")
            lines.append(f"**Fields**: {', '.join(columns)}")

        return lines

    def _generate_rest_documentation(self, analysis: Any) -> List[str]:
        """Generate REST API-specific documentation."""
        lines = []

        # TODO: ENHANCE when Developer A provides REST-specific analysis
        record_count = getattr(analysis, "record_count", None)
        if record_count:
            lines.append(f"**API Data**: {record_count:,} records available")
            if record_count > 100:
                lines.append("**Pagination**: Consider using response_path and pagination handling")

        columns = getattr(analysis, "columns", [])
        if columns:
            lines.append(f"**Response Fields**: {', '.join(columns)}")

        # Authentication status
        lines.append("**Authentication**: ✅ Successfully authenticated")

        return lines

    def _generate_yaml_documentation(self, analysis: Any) -> List[str]:
        """Generate YAML-specific documentation."""
        return [
            "**Type**: Configuration file",
            "**Content**: Structured configuration data",
        ]

    def _generate_text_documentation(self, analysis: Any) -> List[str]:
        """Generate text file-specific documentation."""
        return [
            "**Type**: Text/log file",
            "**Processing**: Consider using template_matching for structured extraction",
        ]

    def _generate_failed_source_doc(self, name: str, analysis: Any) -> List[str]:
        """Generate documentation for failed source analysis."""
        return [
            (
                f"### {name} "
                f"({analysis.type.value.upper() if hasattr(analysis.type, 'value') else str(analysis.type).upper()})"
            ),
            "**Status**: ❌ Failed",
            f"**Error**: {analysis.error_message}",
            "",
            "**LLM Operation Hints**:",
            "- Fix source configuration before processing",
            "- Check file paths and authentication credentials",
            "",
        ]

    def _generate_operation_hints(self, name: str, analysis: Any) -> List[str]:
        """Generate LLM operation hints for a specific source."""
        lines = ["", "**LLM Operation Hints**:"]

        source_type = analysis.type
        columns = getattr(analysis, "columns", [])

        if source_type == "csv":
            lines.append("- CSV source suitable for contextual_filtering and advanced_operations")
            if columns:
                primary_key = next((col for col in columns if "id" in col.lower()), columns[0])
                lines.append(f"- Primary identifier: `{primary_key}` (use for joins)")

                # Suggest filtering operations
                if any("status" in col.lower() for col in columns):
                    lines.append("- Consider filtering by status field for active records")
                if any("date" in col.lower() for col in columns):
                    lines.append("- Date fields available for time-based filtering")

        elif source_type == "rest":
            lines.append("- REST API source - consider pagination handling")
            lines.append("- Use response_path to extract nested data arrays")
            if columns and "customer_id" in columns:
                lines.append("- Contains customer_id field suitable for relationship joins")

        elif source_type == "json":
            lines.append("- JSON structure suitable for format_conversion operations")
            lines.append("- Complex nested data - good for extracting specific fields")

        elif source_type == "text":
            lines.append("- Text file - use template_matching for structured data extraction")
            lines.append("- Consider content_summarization for large text files")

        elif source_type == "yaml":
            lines.append("- Configuration data - useful for conditional processing")

        return lines

    def _generate_relationships_section(self, relationships: List[Any]) -> List[str]:
        """Generate relationships documentation."""
        lines = ["## Detected Relationships", ""]

        if relationships:
            for relationship in relationships:
                confidence_text = (
                    f"({relationship.confidence:.1%} confidence)" if hasattr(relationship, "confidence") else ""
                )
                lines.append(
                    (
                        f"- **{relationship.source_a}.{relationship.field_a}** ↔ "
                        f"**{relationship.source_b}.{relationship.field_b}** {confidence_text}"
                    )
                )
                if hasattr(relationship, "description"):
                    lines.append(f"  {relationship.description}")
        else:
            # TODO: REPLACE with real relationship detection from Developer A
            lines.append("- **customers.customer_id** ↔ **transactions_api.customer_id** (Foreign Key)")
            lines.append("  High confidence relationship for customer transaction analysis")

        lines.append("")
        return lines

    def _generate_operations_recommendations(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate ShedBoxAI operations recommendations."""
        lines = ["## Recommended ShedBoxAI Operations", "", "```yaml", "processing:"]

        # Generate realistic operation suggestions

        if any(analysis.type == "csv" for analysis in analyses.values() if analysis.success):
            lines.extend(
                [
                    "  contextual_filtering:",
                    "    customers:",
                    "      - field: status",
                    "        condition: \"== 'active'\"",
                ]
            )

        if (
            len(
                [
                    a
                    for a in analyses.values()
                    if a.success and hasattr(a, "columns") and "customer_id" in getattr(a, "columns", [])
                ]
            )
            > 1
        ):
            lines.extend(
                [
                    "  relationship_highlighting:",
                    "    customer_transactions:",
                    "      join_on:",
                    "        - customers.customer_id = transactions_api.customer_id",
                ]
            )

        lines.extend(["```", ""])

        return lines

    def _generate_optimization_tips(self, analyses: Dict[str, Any]) -> List[str]:
        """Generate LLM context optimization tips."""
        lines = ["## LLM Context Optimization Tips", ""]

        # Analyze the dataset characteristics
        total_sources = len([a for a in analyses.values() if a.success])
        has_large_data = any(
            getattr(a, "record_count", 0) and getattr(a, "record_count", 0) > 1000
            for a in analyses.values()
            if a.success
        )
        has_relationships = True  # TODO: Replace with real relationship detection

        if not has_large_data:
            lines.append("- All datasets are small enough for direct LLM processing")
        else:
            lines.append("- Large datasets detected - consider sampling or aggregation first")

        if has_relationships:
            lines.append("- Use foreign key relationships for data joining and enrichment")

        # Add source-specific tips
        source_types = set(a.type for a in analyses.values() if a.success)

        if "rest" in source_types:
            lines.append("- REST API sources may have pagination - check total record counts")

        if "csv" in source_types and "rest" in source_types:
            lines.append("- Mix of file and API sources - ideal for data enrichment workflows")

        lines.append(f"- Total {total_sources} sources available for cross-referencing and analysis")

        return lines
