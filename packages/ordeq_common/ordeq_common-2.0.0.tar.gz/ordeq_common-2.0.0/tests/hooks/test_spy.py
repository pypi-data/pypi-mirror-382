from ordeq_common import SpyHook


def test_it_spies():
    spy = SpyHook()
    spy.before_node_run("a", 1)
    spy.before_input_load("b")
    spy.after_input_load("c")
    spy.on_node_call_error("d", "error details")
    spy.before_output_save("e")
    spy.after_output_save()
    spy.after_node_run(None)
    assert spy.called_with == [
        ("before_node_run", "a", 1),
        ("before_input_load", "b"),
        ("after_input_load", "c"),
        ("on_node_call_error", "d", "error details"),
        ("before_output_save", "e"),
        ("after_output_save",),
        ("after_node_run", None),
    ]
