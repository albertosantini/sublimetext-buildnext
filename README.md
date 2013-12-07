sublimetext-buildnext
=====================

Build Next is a Sublime Text plugin to improve the default build system.

Features
--------

- Extend Default.exec plugin.
- Close build results view if there are not errors.
- Show a dot icon in the gutter area close to the error.
- Draw an horizontal region close to the column (tabs-aware) of the error.
- Open finally the output panel.
- Go to the results following a line number order.
- Wrap around the end of the document for the next (previous) result.
- The output panel content is refreshed on the next (previous) result command.

Notes
-----

If you need to execute the build when you save the file I recommend
[SublimeOnSaveBuild](https://github.com/alexnj/SublimeOnSaveBuild) plugin.


The build system should contain a regex for filename, line, column and message
error.

For instance, a JSHint build setting
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

You need to add the following user key bindings to engage the plugin:
```
...
    { "keys": ["f4"], "command": "goto_next_error" },
    { "keys": ["shift+f4"], "command": "goto_prev_error" },
...
```

