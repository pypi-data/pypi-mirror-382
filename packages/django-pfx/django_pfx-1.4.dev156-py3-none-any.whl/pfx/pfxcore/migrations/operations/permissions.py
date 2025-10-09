from django.db.migrations.operations.base import Operation


class GroupPermsOperation(Operation):
    def state_forwards(self, app_label, state):
        pass


class CreateGroup(GroupPermsOperation):
    """Create a group."""

    def __init__(self, name):
        self.group_name = name

    def deconstruct(self):
        return (self.__class__.__qualname__, [self.group_name], {})

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state):
        Group = to_state.apps.get_model('auth', 'Group')
        if self.allow_migrate_model(schema_editor.connection.alias, Group):
            Group.objects.create(name=self.group_name)

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state):
        Group = to_state.apps.get_model('auth', 'Group')
        if self.allow_migrate_model(schema_editor.connection.alias, Group):
            Group.objects.get(name=self.group_name).delete()

    def describe(self):
        return (f"Create group {self.group_name}")


class DeleteGroup(GroupPermsOperation):
    """Delete a group."""

    def __init__(self, name):
        self.group_name = name

    def deconstruct(self):
        return (self.__class__.__qualname__, [self.group_name], {})

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state):
        Group = to_state.apps.get_model('auth', 'Group')
        if self.allow_migrate_model(schema_editor.connection.alias, Group):
            Group.objects.get(name=self.group_name).delete()

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state):
        Group = to_state.apps.get_model('auth', 'Group')
        if self.allow_migrate_model(schema_editor.connection.alias, Group):
            Group.objects.create(name=self.group_name)

    def describe(self):
        return (f"Create group {self.group_name}")


class RenameGroup(GroupPermsOperation):
    """Rename a group."""

    def __init__(self, old_name, new_name):
        self.group_old_name = old_name
        self.group_new_name = new_name

    def deconstruct(self):
        return (self.__class__.__qualname__, [
            self.group_old_name, self.group_new_name], {})

    def database_forwards(
            self, app_label, schema_editor, from_state, to_state):
        Group = to_state.apps.get_model('auth', 'Group')
        if self.allow_migrate_model(schema_editor.connection.alias, Group):
            group = Group.objects.get(name=self.group_old_name)
            group.name = self.group_new_name
            group.save()

    def database_backwards(
            self, app_label, schema_editor, from_state, to_state):
        Group = to_state.apps.get_model('auth', 'Group')
        if self.allow_migrate_model(schema_editor.connection.alias, Group):
            group = Group.objects.get(name=self.group_new_name)
            group.name = self.group_old_name
            group.save()

    def describe(self):
        return (f"Rename group {self.group_old_name} to {self.group_new_name}")
