"""
In this example we define a 'settings' contextual dict by declaring some
Child relations to a `ContextualView` with the name 'settings'.

At several levels of the (infinite) flow tree, the user can see,
override and add values in the `settings` context.
Those objects (Branch1 and Branch2) have a `settings` relation
to a `ContextualView` which provide those functionnalyties.

Edits can also be provided programatically by defining the
`get_extra_contextual_edits()` method, as seen in `Branch2`.

At other levels of the tree, we use values from this 'settings'
context to demonstrate how to retreive a sub set of the dict
 (please note that this is not a speed optimisation).

Sometimes you want to confine the settings inside an child objet instead
of having them directly inside objects in the branch path.
The `DemoFlow` object does this by defining the `get_contextual_view()`
method returning the view to use (`self.admin.settings` in
this case).

"""
import pprint

from kabaret import flow

from . import ContextualView, get_contextual_dict


class SettingsReaderAction(flow.Action):

    settings = flow.Child(ContextualView)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        return ["Print it!"]

    def run(self, button):
        context = get_contextual_dict(self, "settings")
        pprint.pprint(context)
        return self.get_result(close=False)


class SettingsReader(flow.Object):
    def compute_child_value(self, child_value):
        key = child_value.name()

        context = get_contextual_dict(leaf=self, context_name="settings", keys=[key])

        child_value.set(
            'The current {} is "{}"'.format(key, context.get(key, "! NOT FOUND !"))
        )


class SettingsReader1(SettingsReader):

    fps = flow.Computed()
    path = flow.Computed()
    test_action = flow.Child(SettingsReaderAction)


class SettingsReader2(SettingsReader):

    fps = flow.Computed()
    pool = flow.Computed()


class Branch1(flow.Object):

    # This will relate to a Group
    # when the class is defined
    sub_tree = flow.Child(None)

    # The name of this relation must match the context_name:
    settings = flow.Child(ContextualView)

    settings_usage = flow.Child(SettingsReader1)


class Branch2(flow.Object):

    # This will relate to a Group
    # when the class is defined
    sub_tree = flow.Child(None)

    # The name of this relation must match the context_name:
    settings = flow.Child(ContextualView)

    settings_usage = flow.Child(SettingsReader2)

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(oid=self.oid())


class Group(flow.Object):

    branch1 = flow.Child(Branch1)
    branch2 = flow.Child(Branch2)


# Configure Circular Relations
Branch1.sub_tree.set_related_type(Group)
Branch2.sub_tree.set_related_type(Group)


class ProjectAdmin(flow.Object):

    # the name of this relation drives the `context_name`
    # arg of `self.get_contextual_edits()`
    settings = flow.Child(ContextualView)


class DemoFlow(flow.Object):

    tree = flow.Child(Group)
    admin = flow.Child(ProjectAdmin)

    def get_contextual_view(self, context_name):
        if context_name == "settings":
            return self.admin.settings

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(fps=30, path="/DEFAULT/PATH/TO/STUFF", pool="render_nodes")

    def get_context_names(self):
        return ["settings"]
