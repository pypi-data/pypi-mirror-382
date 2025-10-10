# kabaret.flow_contextual_dict

This package provide the `ContextualView` class, the `get_contextual_dict` function and the `ContextualDictFlowView` session view type.

Together, they give your flow users the ability to use defined value
anywhere in the branch underneeth and override those values where you 
see fit in the branches.

Everything is explained here, but if your of the kind that prefers to read and execute code, there is a demo flow in the package for that. Install the package an create a new project with the type `kabaret.flow_contextual_dict.demo_flow.DemoFlow`.

## Concept

Here is a quick example with this classic structure where `settings` are `ContextualView` Objects:
```
Project
    settings
    episodes
        ep001
            settings
            sequences
                seq001
                    settings
                    shots
                        shot001
                            settings
                            anim
                                settings
                                init_action
                                bake_action
                            lighting
                                settings
                                init_action
                                render_action
                            comp
                                settings
                                init_action
                                render_action
                        shot002
                seq002
                    ...
        ep002
            ...
```
Let's say in the `Project.settings` defines `fps=24` and a `pool="ANY"`.
Every object in the episodes branch can call `get_contextual_dict()` to receive a dict like `{fps:24, pool:"ANY"}`.
Most likely, action of every step/department of every shot will use this.

Now let's say the sequence `seq002` is in a hurry and you want to dispatch all actions on your farm's "SUPER_COMPUTERS" pool. All you need is to "override" with `pool="SUPER_COMPUTERS"` in `ep002.settings`.

You can do this in each `settings` in the flow, and you can also "add" values in each of them (those "overrides" and "adds" are called "edits").

In a nutshell, it's a cascading dict, or as some call it: a **contextual dict**.

## Install

`pip install kabaret.flow_contextual_dict`

Please use a virtual env, it is good for you and your karma ^^

## Usage

### Defining Contexts

In order to add a contextual dict in your flow, you just need to add
a Child relation to a `ContextualView`:
```
class Shot(flow.Object):

    settings = flow.Child(contextualView)
    ...

```

The name of the relation is very important:
- Overrides stacking is based on this name so you need to use the same
name along your branch in order for overrides to work as expected.
- It defines the "context_name" argument to use for `get_contextual_dict()` calls.

So this will not work:
```
Project
    settings
    episodes
        ep001
            episode_settings
```
But this will:
```
Project 
    settings
    episodes
        ep001
            settings
```
Note that you can use `Child().ui(label="Episode Settings")` if you *really* want to display a different name in the GUI.

This gives the ability to use several contexts in the same flow.
In this structure, all * marked item are `ContextualView`. There is two
context defined: `settings` and `config`. The first one drives values by `sequences` and `shots`, the second one only affects `episodes`.
```
Project
    settings *
    config *
    episodes
        ep001
        config *
        sequences
            seq001
                settings *
                shots
                    shot001
                        settings *
```

### Editing Context Values

Once your flow is salted with `ContextualView`, the user will be able to
add value using the *"Add"* action and to edit values by double clicking on them.

If you want, for debug or inquiry, you can inspect the edits done thru a `ContectualView` by using its "Show Edits" actions. It will bring you to
a page showing only values defined here. Double-clicking one of those items
will show you more information, especially **the history of modification** for this value (what changed, who did it, and when).
You will also be able to change the override value, as well as disable/enable it.

You can also programatically edit the context by defining `get_default_contextual_edits(context_name)` methods returning a dict of value to use if no override exists for them.

In other words: user edits made with `ContextualView` actions will override values returned by a local or upstream `get_default_contextual_edits()` method.

### Using Context Values

In order to get a context dict, you just need to call `get_contextual_dict(leaf, context_name)`. The `leaf` is the point in the branch where you want the value to be evaluated. It will most of the time be `self`. 

Here is an example in an Action.run():
```
class SubmitRender(flow.Action):

    render_settings = flow.Child(ContextualView)

    def run(self, button):
        if button == 'Confirm':
            context = get_contextual_dict(
                self, 'render_settings'
            )
            my_dispatcher.submit(
                scene=self.get_scene_path(),
                fps=context.get('fps', 24),
                pool=context.get('pool', 'ANY'),
            )
```
Note that the second arg of the `get_contextual_dict()` call must match
the name of each `ContextualView` to evaluate in the upstream branch.

Also note that using a `ContextualView` as the Action Child has drawbacks in term of UX. We're waiting for a update of `kabaret` to fix this.

### Default Value

At the base of your context, you will probably want to have a set of default values.

You will do this by adding a 'get_default_contextual_edits()` method returning the default value.

Let's say your `Project` is the first level for you settings. You would
do something like:
```
class Project(flow.Object):

    settings = flow.Child(ContextualView)
    episodes = flow.Child(Episodes)

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                fps=30,
                pool="ANY"
            )
```

## Special Case

Sometimes, you will want to put the visualisation/edition of the contextual values aside from the branch it affect.

An example would be the settings of a project. They affect the **WHOLE UNIVERSE** so maybe you wouldn't want them to show on the first page all users land to...

A classic aproach is to use an `admin` group and shove all geeky stuff in it:
```
Project
    word_of_the_day
    episodes
        ...
    admin
        settings
        config
        preferences
```

In this case, the `settings` object is not inside the `episodes` branch so it does not affect it. This is a fail at being usefull :/

To fix this, you can define inside `Project` a `get_contextual_view` method that returns a `ContextView` to consider as if it was its Child:
```
class Project(flow.Object):
    
    word_of_the_day = flow.Chid(WOTD)
    episodes = flow.Child(Episodes)
    admin = flow.Child(ProjectAdmin)

    def get_contextual_view(self, context_name):
        if context_name == 'settings':
            return self.admin.settings
        elif context_name == 'config'
            return self.admin.config

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                fps=30,
                pool="ANY"
            )
```

**Note** that the default value must still be provided by the `Project` class !

## Contextual Dict Flow View

The `ContextualDictFlowView` allows to visualize the contextual dict of any flow object, and edit the dict entries whenever the object defines a relation to a `ContextualView`.

This view displays the contextual dict as follow:
- default entries (defined by a `get_default_contextual_edits()` method) which have not been redefined appear in *italic*
- local edits appear in **bold**
- new values added at the current level appear with a brighter background color

This view relies on a list of context names which must be provided by the project with the `get_context_names()` method. Contexts available in a project automatically appear above the table of contextual entries in the view.

```python
class Project(flow.Object):

    def get_context_names(self):
        return ['settings'] # or any other context name(s)
```

As any session view in Kabaret, the `ContextualDictFlowView` class must be registered in the view types of the session to be available in its GUI:

```python
from kabaret.flow_contextual_dict import ContextualDictView

class MyStudioGUISession(gui.KabaretStandaloneGUISession):
    ...
    def register_view_types(self):
        super(MyStudioGUISession, self).register_view_types()
        ...
        type_name = self.register_view_type(ContextualDictView)
        self.add_view(type_name)
```