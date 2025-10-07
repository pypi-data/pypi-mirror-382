import logging
import shutil
import textwrap


class AlignedFormatter(logging.Formatter):
    """A logging formatter that aligns log messages for better readability."""

    def format(self, record):  # noqa: D102, manually set below
        if not hasattr(self, "_max_record_name_length"):
            self._max_record_name_length = 8

        if len(record.name) > self._max_record_name_length:
            self._max_record_name_length = min(35, len(record.name))

        # Get the base message
        message = record.getMessage()
        separator_1 = "├"
        separator_2 = "│"

        # Compute available width for message text
        terminal_width = shutil.get_terminal_size((80, 20)).columns

        right_padded_record_name = f"{record.name:>{self._max_record_name_length}.{self._max_record_name_length}}"
        prefix = (
            " ".join(
                (
                    f"{record.relativeCreated:13.2f}",
                    f"{record.levelname:>8}",
                    f"{right_padded_record_name}:{record.lineno:4d}",
                ),
            )
            + f" {separator_1} "
        )
        text_width = max(10, terminal_width - len(prefix))

        # Wrap the message text
        wrapped_lines = textwrap.wrap(message, width=text_width)

        # Assemble aligned output
        if wrapped_lines:
            lines = [prefix + wrapped_lines[0]]
            continuation_prefix = " " * (len(prefix) - 2) + separator_2 + " "
            for line in wrapped_lines[1:]:
                lines.append(continuation_prefix + line)
            formatted = "\n".join(lines)
        else:
            formatted = prefix

        return formatted

    format.__doc__ = logging.Formatter.format.__doc__
