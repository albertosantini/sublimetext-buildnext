Build Next
==========
![](https://github.com/albertosantini/sublimetext-buildnext/workflows/CI/badge.svg)

**Build Next** is a [Sublime Text](http://www.sublimetext.com/) plugin to improve the default build system.

Features
--------

- Extend Default.exec plugin and no external dependencies.
- Zero user preferences and preferences per build system.
- Close build results view if there are not errors.
- Show a dot icon in the gutter area close to the error.
- Draw an horizontal region close to the column (tabs-aware) of the error.
- Open finally the output panel.
- Go to the results following a line number order.
- Wrap around the end of the document for the next (previous) result.
- The output panel content is refreshed on the next (previous) result command.

Requirements
------------

At least Sublime Text 3 Build 3124.

Installation
------------

After installing the plugin with [Sublime Package Manager](http://wbond.net/sublime_packages/package_control),
you should add the following user key bindings (`Preferences / Key Bindings - User`)
to engage it:

```
[
...
    { "keys": ["f4"], "command": "goto_next_error" },
    { "keys": ["shift+f4"], "command": "goto_prev_error" },
...
]
```

This configuration overrides the default key bindings `next_result` and
`prev_result`.

Preferences
-----------

There are not user preferences, but there are preferences per build system file.
The preferences are embedded in the build file, contained in the `env` property.

There are use cases where the following preferences are useful, like displaying
the output after the unit test command or adjusting the error column, because
the build command is zero based column.


- `ST_BUILD_SHOW_OUTPUTVIEW` (default false): to display always the Build
Results panel, even if there are not error and the build command exit code is
zero.

- `ST_BUILD_ADJUST_COLUMNERROR` (default 0): to adjust the column of the error
adding a value.

For instance,

```
...
    "env":
    {
        "ST_BUILD_SHOW_OUTPUTVIEW": "true"
    }
...
```

- `ST_BUILD_PUT_PRIORITY` (default ""): to put priority on errors containing a
token.

Notes
-----

The build system should contain the `file_regex` property for the filename,
line, column and message field. For instance, a JSHint build setting
(`JSHint.sublime-build`):

```
{
    "selector": "source.js, source.json",

    "cmd": ["jshint", "$file"],
    "shell": true,

    "file_regex": "^(.*): line (\\d+), col (\\d+), (.+)$",

    "windows":
    {
        "cmd": ["jshint.cmd", "$file"]
    }
}
```

I recommend [SublimeOnSaveBuild](https://github.com/alexnj/SublimeOnSaveBuild)
plugin, if you need to execute the build when you save the file.
