import pluggy

plugin_manager = pluggy.PluginManager("pyroll_report")
hookspec = pluggy.HookspecMarker("pyroll_report")
hookimpl = pluggy.HookimplMarker("pyroll_report")
