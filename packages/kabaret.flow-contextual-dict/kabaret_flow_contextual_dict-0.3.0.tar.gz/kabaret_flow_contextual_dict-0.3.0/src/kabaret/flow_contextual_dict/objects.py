from __future__ import print_function

import getpass
import time
import datetime
import logging

import traceback
from kabaret import flow


#
#   EDIT
#


class ContextualEditsValue(flow.values.Value):

    _item = flow.Parent()

    def set(self, value):
        super(ContextualEditsValue, self).set(value)
        self._item.log.add_changed_event(value)


class ContextualEditsValueEnabledValue(flow.values.BoolValue):

    _item = flow.Parent()

    def set(self, value):
        if self.get() != value:
            super(ContextualEditsValueEnabledValue, self).set(value)
            self._item.log.add_toggled_event(value)


class ValueLogItem(flow.Object):

    event_type = flow.Param().ui(editable=False)
    by = flow.Param().ui(editable=False)
    on = flow.Param().ui(editable=False, editor="datetime")
    value = flow.Param().ui(editable=False)


class ValueLog(flow.Map):
    @classmethod
    def mapped_type(cls):
        return ValueLogItem

    def columns(self):
        return ["#", "Event Type", "Value", "By", "On"]

    def _fill_row_cells(self, row, item):
        row.update(
            {
                "#": item.name()[6:].zfill(5),
                "Event Type": item.event_type.get(),
                "Value": item.value.get(),
                "By": item.by.get(),
                "On": datetime.datetime.fromtimestamp(item.on.get()).ctime(),
            }
        )

    def add_changed_event(self, value):
        item = self.add("Event_{}".format(len(self) + 1))
        item.event_type.set("Changed")
        item.by.set(getpass.getuser())
        item.on.set(time.time())
        item.value.set(value)
        self.touch()

    def add_toggled_event(self, enabled):
        item = self.add("Event_{}".format(len(self) + 1))
        item.event_type.set("Toggled")
        item.by.set(getpass.getuser())
        item.on.set(time.time())
        item.value.set(enabled and "Enabled" or "Disabled")
        self.touch()


class ContextualEditsItem(flow.Object):

    _edit_map = flow.Parent()

    value_name = flow.Param("???").ui(editable=False)
    value = flow.Param(None, ContextualEditsValue).watched()
    enabled = flow.Param(True, ContextualEditsValueEnabledValue).watched()

    log = flow.Child(ValueLog)

    def child_value_changed(self, value):
        self._edit_map.touch()


class ContextualEdits(flow.Map):

    MAX_EDIT_COUNT = 500

    @classmethod
    def mapped_type(cls):
        return ContextualEditsItem

    def columns(self):
        return ["Name", "Value"]

    def _fill_row_cells(self, row, item):
        row["Name"] = item.value_name.get()
        row["Value"] = item.value.get()

    def to_dict(self, keys=None):
        """
        If keys is not None, it must be a list of
        value names to return
        """
        edits = {}
        for item in self.mapped_items():
            if not item.enabled.get():
                continue
            value_name = item.value_name.get()
            if keys is None or value_name in keys:
                edits[value_name] = item.value.get()
        return edits

    def has_edit(self, name):
        for item in self.mapped_items():
            if item.value_name.get() == name:
                return item.enabled.get()
        return False

    def set_edit(self, name, value):
        for item in self.mapped_items():
            if item.value_name.get() == name:
                if not item.enabled.get():
                    item.enabled.set(True)
                item.value.set(value)
                return

        # item not found, create a new one:

        item_name = None
        names = self.mapped_names()
        for i in range(self.MAX_EDIT_COUNT):
            test_name = "Item{}".format(i)
            if test_name not in names:
                item_name = test_name
                break
        if item_name is None:
            raise Exception("Too many edits here, I wont allow more.")
        item = self.add(item_name)
        item.value_name.set(name)
        item.value.set(value)

    def remove_edit(self, name):
        for item in self.mapped_items():
            if item.value_name.get() == name:
                item.enabled.set(False)
                return
        raise ValueError('Edit for "{}" not found.'.format(name))


class EditGroup(flow.Object):

    edit_map = flow.Child(ContextualEdits)


#
#   VIEW
#


class EditValueAction(flow.Action):

    _view_map = flow.Parent(2)
    _view_item = flow.Parent()
    value = flow.Param()

    def allow_context(self, context):
        return context == "Flow.map" and self._view_map.allow_editing()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        value_name = self._view_item.value_name.get()
        self.message.set("<h2>Edit value for <b>{}</b></h2>".format(value_name))
        self.value.set(self._view_item.value.get())
        buttons = ["Save"]
        if self._view_map.get_edit_map().has_edit(value_name):
            buttons.append("Restore Default")
        return buttons

    def run(self, button):
        edit_map = self._view_map.get_edit_map()

        if button == "Restore Default":
            # ! beware, do not edit the view item,
            # the one to modify is in the edit map !
            edit_map.remove_edit(self._view_item.value_name.get())
            edit_map.touch()
            self._view_map.touch()

        elif button == "Save":
            # ! beware, do not edit the view item,
            # the one to modify is in the edit map !
            edit_map.set_edit(
                self._view_item.value_name.get(), self.value.get(),
            )
            edit_map.touch()
            self._view_map.touch()

        return self.get_result(goto=self._view_map._mng.parent.oid())


class AddEditAction(flow.Action):

    _view_map = flow.Parent()

    value_name = flow.Param().ui(label="Name")
    value = flow.Param()

    def allow_context(self, context):
        return self._view_map.allow_editing()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set("Enter the name and the value.")
        return [
            "Add Edit",
        ]

    def run(self, button):
        if not button == "Add Edit":
            return

        edit_map = self._view_map.get_edit_map()
        edit_map.set_edit(self.value_name.get(), self.value.get())
        edit_map.touch()
        self._view_map.touch()


class GotoEditsAction(flow.Action):

    _view_map = flow.Parent()

    def allow_context(self, context):
        return self._view_map.allow_editing()

    def needs_dialog(self):
        return False

    def run(self, button):
        edit_map = self._view_map.get_edit_map()
        return self.get_result(goto=edit_map._mng.parent.oid())


class ContextualViewItem(flow.SessionObject):

    edit = flow.Child(EditValueAction)

    value_name = flow.Computed(cached=True).ui(label="name")
    value = flow.Param(None)

    def compute_child_value(self, child_value):
        if child_value is self.value_name:
            child_value.set(self.name())


class ContextualView(flow.DynamicMap):

    ALLOW_EDIT = True

    add_value = flow.Child(AddEditAction)
    show_edits = flow.Child(GotoEditsAction)

    edits = flow.Child(EditGroup).ui(hidden=True)

    @classmethod
    def mapped_type(cls):
        return ContextualViewItem

    def allow_editing(self):
        return self.ALLOW_EDIT

    def get_edit_map(self):
        return self.edits.edit_map

    def get_edits(self, keys=None):
        if not self.ALLOW_EDIT:
            return None
        return self.get_edit_map().to_dict(keys)

    def mapped_names(self, page_num=0, page_size=None):
        # print('CALLING MAPPED NAME', self.oid)
        context = get_contextual_dict(
            self,
            self.name(),  # The view name drives the context name
            keys=None,  # None => fetch all keys
        )
        edits = self.get_edit_map().to_dict()
        context.update(edits)

        self._mng.children.clear()  # rebuild all to ensure item are updated
        self._cache = {}
        item_prefix = self.name() + "_"
        for i, (k, v) in enumerate(context.items()):
            attr_name = "{}{}".format(item_prefix, i)
            self._cache[attr_name] = dict(name=k, value=v)

        names = sorted(self._cache.keys())
        return names

    def _configure_child(self, child):
        child.value_name.set(self._cache[child.name()]["name"])
        child.value.set(self._cache[child.name()]["value"])

    def columns(self):
        return ["Name", "Value"]

    def _fill_row_cells(self, row, item):
        row["Name"] = item.value_name.get()
        row["Value"] = item.value.get()

    def _fill_row_style(self, style, item, row):
        pass

    def row(self, item):
        """
        Configure the double-click to edit the item instead of goto it
        """
        oid, row = super(ContextualView, self).row(item)
        return item.edit.oid(), row


#
#   FUNCTIONS
#


def XX_get_contextual_dict(leaf, context_name, keys=None):
    parent = leaf._mng.parent
    if parent is None:
        context = dict()
    else:
        context = get_contextual_dict(parent, context_name, keys)

    try:
        get_edits = getattr(leaf, "get_contextual_edits")
    except AttributeError:
        pass
    else:
        try:
            edits = get_edits(context_name, keys)
        except Exception:
            context["ERROR at " + leaf.oid()] = traceback.format_exc()
        else:
            # get_contextual_edits is allowed to return None:
            if edits:
                context.update(edits)

    return context


def _get_logger(debug, name):
    def log(*a):
        print("[DEBUG en carton] {}:".format(name), *a)

    if debug:
        return log

    def no_log(*a):
        pass

    return no_log


def get_contextual_dict(leaf, context_name, keys=None):
    parent = leaf._mng.parent
    if parent is None:
        context = dict()
    else:
        context = get_contextual_dict(parent, context_name, keys)

    DEBUG = False
    log = _get_logger(DEBUG, "get_contextual_dict")

    log("  looking for default edit in", repr(leaf.oid()))
    try:
        default_edits_getter = getattr(leaf, "get_default_contextual_edits")
    except AttributeError:
        log("  no get_default_contextual_edits() found here.")
    else:
        default_edits = default_edits_getter(context_name)
        log("  found default edits", default_edits)
        if default_edits is not None:
            context.update(default_edits)

    log("Get contextual dict at", leaf.oid())
    contextual_view = None
    try:
        edit_view_getter = getattr(leaf, "get_contextual_view")
    except AttributeError:
        log("  no get_contextual_view() found, trying default.")
    else:
        log("  get_contextual_view() found, running it.")
        contextual_view = edit_view_getter(context_name)

    if contextual_view is None:
        try:
            contextual_view = getattr(leaf, context_name)
        except AttributeError:
            log("  no {} relation found here.")
            # No contextual view in this object.
            pass

    if contextual_view is not None and contextual_view.allow_editing():
        log("  found editable contextual view", contextual_view.oid())
        try:
            edits = contextual_view.get_edits(keys)
        except Exception:
            context["ERROR getting edits at " + leaf.oid()] = traceback.format_exc()
            log("    Error getting edits")
        else:
            log("    edits:", edits)
            context.update(edits)

    return context


def get_extended_contextual_dict(leaf, context_name, keys=None):
    parent = leaf._mng.parent
    if parent is None:
        context = dict()
    else:
        context = get_extended_contextual_dict(parent, context_name, keys)
        for key in context:
            # Inherited values are not new and not local edits by default
            context[key]['is_local_edit'] = False
            context[key]['is_new'] = False

    DEBUG = False
    log = _get_logger(DEBUG, "get_extended_contextual_dict")

    log("  looking for default edit in", repr(leaf.oid()))
    try:
        default_edits_getter = getattr(leaf, "get_default_contextual_edits")
    except AttributeError:
        log("  no get_default_contextual_edits() found here.")
    else:
        default_edits = default_edits_getter(context_name)
        log("  found default edits", default_edits)
        if default_edits is not None:
            # Search for new keys
            default_edits = {
                key: {
                    'value': value,
                    'default_value': value,
                    'is_edit': False,
                    'is_local_edit': False,
                    'is_flow_key': True,
                    'is_new': key not in context
                }
                for key, value in default_edits.items()
            }
            context.update(default_edits)

    log("Get contextual dict at", leaf.oid())
    contextual_view = None
    try:
        edit_view_getter = getattr(leaf, "get_contextual_view")
    except AttributeError:
        log("  no get_contextual_view() found, trying default.")
    else:
        log("  get_contextual_view() found, running it.")
        contextual_view = edit_view_getter(context_name)

    if contextual_view is None:
        try:
            contextual_view = getattr(leaf, context_name)
        except AttributeError:
            log("  no {} relation found here.")
            # No contextual view in this object.
            pass

    if contextual_view is not None and contextual_view.allow_editing():
        log("  found editable contextual view", contextual_view.oid())
        try:
            edits = contextual_view.get_edits(keys)
        except Exception:
            context["ERROR getting edits at " + leaf.oid()] = traceback.format_exc()
            log("    Error getting edits")
        else:
            log("    edits:", edits)
            for key, value in edits.items():
                edit = context.get(key, {
                    'default_value': value,
                    'is_flow_key': False,
                    'is_new': True
                })
                edit['value'] = value
                edit['is_edit'] = True
                edit['is_local_edit'] = True
                context[key] = edit

    return context
