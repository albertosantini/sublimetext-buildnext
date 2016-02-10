"""This package augments the default build system."""

import sublime
import sublime_plugin
import re

import importlib
defaultExec = importlib.import_module("Default.exec")

output_errors = {}


class ExecCommand(defaultExec.ExecCommand):

    """This class extends the default build system."""

    def run(self, cmd=None, shell_cmd=None,
            file_regex="", line_regex="", working_dir="",
            encoding="utf-8", env={}, quiet=False, kill=False,
            word_wrap=True, syntax="Packages/Text/Plain text.tmLanguage",
            # Catches "path" and "shell"
            **kwargs):
        """Run the text command."""

        self.env = {}
        self.env["ST_BUILD_SHOW_OUTPUTVIEW"] = "false"
        self.env["ST_BUILD_ADJUST_COLUMNERROR"] = "0"
        self.env["ST_BUILD_PUT_PRIORITY"] = ""
        self.env.update(env)

        super(ExecCommand, self).run(cmd, shell_cmd,
                                     file_regex, line_regex,
                                     working_dir, encoding, env,
                                     quiet, kill, word_wrap, syntax,
                                     **kwargs)

    def on_finished(self, proc):
        """It is the entry point after the process is finished."""

        global output_errors

        super(ExecCommand, self).on_finished(proc)

        view = self.window.active_view()
        output_view = self.output_view

        if hasattr(view, "file_name"):
            key = view.file_name()
        else:
            return

        exit_code = proc.exit_code()
        errors_len = len(output_view.find_all_results())

        if (exit_code is None or exit_code == 0 and errors_len == 0):
            if (self.env["ST_BUILD_SHOW_OUTPUTVIEW"] == "false"):
                self.window.run_command("hide_panel", {"panel": "output.exec"})

            view.erase_regions("exec_errors")
            if (key in output_errors):
                del output_errors[key]

        else:
            output_errors[key] = self.getErrors(output_view)

            error_files = output_errors[key]["error_files"]
            indexes = [i for i, x in enumerate(error_files) if key.find(x) >= 0]

            regions = [output_errors[key]["error_regions"][i] for i in indexes]
            view.add_regions(
                "exec_errors",
                regions,
                "keyword",
                "dot",
                sublime.DRAW_EMPTY_AS_OVERWRITE |
                sublime.DRAW_NO_FILL |
                sublime.DRAW_NO_OUTLINE |
                sublime.HIDE_ON_MINIMAP
            )

    def getAdjustedRegion(self, line, col):
        """It adjusts the line and column values if the view contains tabs."""

        line = int(line) - 1
        view = self.window.active_view()
        settings = view.settings()
        line_begin = view.text_point(line, 0)
        line_region = view.full_line(line_begin)
        buf = view.substr(line_region)
        tab_length = len(re.findall("\t", buf))
        isSpacesIndentation = settings.get("translate_tabs_to_spaces")
        tab_size = 1
        if (not isSpacesIndentation):
            tab_size = settings.get("tab_size")
        col = int(col) - 1 - (tab_size * tab_length) + tab_length
        text_point = view.text_point(line, col)

        return sublime.Region(text_point, text_point)

    def putPriority(self, errors):
        """It puts priority on line errors containing a token."""

        priority = self.env["ST_BUILD_PUT_PRIORITY"]
        if priority == "":
            return sorted(errors)
        else:
            errors_with_priority = sorted(list(filter(
                lambda error: error[1].lower().find(priority) != -1, errors)))
            errors_other = sorted(list(filter(
                lambda error: error[1].lower().find(priority) == -1, errors)))

            return errors_with_priority + errors_other

    def getErrors(self, view):
        """It parses the output of the build system to get the errors."""

        view_errors = {
            "view": view,
            "view_text": view.substr(sublime.Region(0, view.size())),
            "error_regions": [],
            "error_messages": [],
            "output_regions": [],
            "error_files": []
        }

        file_regex = str(view.settings().get("result_file_regex"))
        if (file_regex == ""):
            return view_errors

        adjust_column = int(self.env["ST_BUILD_ADJUST_COLUMNERROR"])

        errors = []
        output_regions = view.find_all(file_regex)
        for output_region in output_regions:
            buf = str(view.substr(output_region))
            error = re.findall(file_regex, buf)[0]
            filename = error[0]
            line = error[1]
            column = int(error[2]) + int(adjust_column)
            error_message = error[3]
            error_region = self.getAdjustedRegion(line, column)
            errors.append((error_region, error_message, output_region,
                           filename))

        errors = self.putPriority(errors)
        for i, error in enumerate(errors):
            view_errors["error_regions"].append(errors[i][0])
            view_errors["error_messages"].append(errors[i][1])
            view_errors["output_regions"].append(errors[i][2])
            view_errors["error_files"].append(errors[i][3])

        return view_errors


class ReplaceTextOutputView(sublime_plugin.TextCommand):

    """It replaces the text in the output view."""

    def run(self, edit, args):
        """Run the text command."""

        self.view.replace(
            edit,
            sublime.Region(0, self.view.size()),
            args["text"]
        )


class GotoError(sublime_plugin.TextCommand):

    """It is the helper class to go to the error."""

    def run(self, edit, direction):
        """Run the text command."""

        global output_errors

        key = sublime.active_window().active_view().file_name()
        if (not key):
            return

        indexes = [i for i, x in enumerate(output_errors[key]["error_files"])
                   if x == key]
        if (len(indexes) == 0):
            return

        output_view = output_errors[key]["view"]
        output_text = output_errors[key]["view_text"]
        error_regions = [output_errors[key]["error_regions"][i]
                         for i in indexes]
        error_messages = [output_errors[key]["error_messages"][i]
                          for i in indexes]
        output_regions = [output_errors[key]["output_regions"][i]
                          for i in indexes]

        output_view.run_command(
            "replace_text_output_view",
            {
                "args": {
                    "text": output_text
                }
            }
        )

        caret = self.view.sel()[0].begin()
        distances = []
        for i, region in enumerate(error_regions):
            distance = region.end() - caret
            distances.append((distance, i))

        if direction == "next":
            results = sorted(list(filter(
                lambda x: x[0] > 0, distances)), key=lambda x: x[1])
            if results:
                distance, index = results[0]
            else:
                index = 0

        if direction == "prev":
            results = sorted(list(filter(
                lambda x: x[0] < 0, distances)), key=lambda x: x[1],
                reverse=True)
            if results:
                distance, index = results[0]
            else:
                index = len(error_messages) - 1

        self.updateEditAndOutputView(
            output_view,
            error_regions[index],
            error_messages[index],
            output_regions[index]
        )

    def updateEditAndOutputView(self, view, region, message, output):
        """It updates the edit and output view."""

        self.highlightBuildError(view, output)
        sublime.status_message(message)
        self.setCaret(self.view, region)

    def setCaret(self, view, position):
        """It sets the caret."""

        view.sel().clear()
        view.sel().add(sublime.Region(position.begin(), position.end()))
        view.show_at_center(position.end())

    def highlightBuildError(self, view, position):
        """It highlights the line error in the output view."""

        self.setCaret(view, position)

        window = sublime.active_window()
        window.run_command("hide_panel", {"panel": "output.exec"})
        window.run_command("show_panel", {"panel": "output.exec"})


class GotoNextError(GotoError):

    """It maps the key binding to go to the next error."""

    def run(self, edit):
        """Run the text command."""

        super(GotoNextError, self).run(edit, "next")


class GotoPrevError(GotoError):

    """It maps the key binding to go to the previous error."""

    def run(self, edit):
        """Run the text command."""

        super(GotoPrevError, self).run(edit, "prev")
