# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import codecs
import os
import tempfile

from ctypes_unicode_proclaunch import launch, wait
from get_unicode_arguments_to_launch_editor import get_unicode_arguments_to_launch_editor
from typing import List, Optional, Sequence, Text


def get_unicode_multiline_input_with_editor(
        unicode_initial_input_lines,
        unicode_line_comments_start_with=None,
        editor=None
):
    # type: (Sequence[Text], Optional[Text], Optional[Text]) -> List[Text]
    unicode_arguments_to_launch_editor = get_unicode_arguments_to_launch_editor(editor)

    # Create temporary file context and close the temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='wb+', delete=False) as named_temporary_file:
        filename = named_temporary_file.name

        for unicode_initial_input_line in unicode_initial_input_lines:
            named_temporary_file.write(unicode_initial_input_line.encode('utf-8'))
            named_temporary_file.write(b'\n')

        named_temporary_file.flush()

    try:
        unicode_arguments_to_launch_editor.append(filename)

        # Launch the editor and wait for it to close
        wait(launch(unicode_arguments_to_launch_editor))

        # Read the content after editing
        lines = []
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            if unicode_line_comments_start_with is not None:
                for line in f:
                    comment_start_at = line.find(unicode_line_comments_start_with)
                    if comment_start_at >= 0:
                        lines.append(line[:comment_start_at])
                    else:
                        lines.append(line)
            else:
                lines.extend(f)

        return lines
    finally:
        os.unlink(filename)
