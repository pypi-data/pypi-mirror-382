from kabaret import flow


#
#--- Lib Code
#
# Let's pretend this code is in a pip install package we can't 
# modify.
# 

class DeptChoiceValue(flow.values.MultiChoiceValue):

    CHOICES = ('Preprod', 'Prod', 'Edit')


class User(flow.Object):
    '''
    Base class for User in the Lib.
    Use the slot name <libmodule>.User to inject
    a custom User subclass.

    This User has a dept Param with a default 
    choice list.
    Use the slot name <libmodule>.DeptChoiceValue to
    inject a custom flow.values.ChoiceValue.
    '''
    @classmethod
    def get_source_display(cls, oid):
        return oid.rsplit('/', 1)[-1]
    
    # By default, the injection must be a subclass of the 
    # original. With inherit_default=False this restriction
    # is disabled:
    depts = flow.Param([], DeptChoiceValue).injectable(inherit_default=False)
    email = flow.Param('')

class AddUserAction(flow.Action):

    _users = flow.Parent()

    def needs_dialog(self): return False
    def run(self, button):
        user = self._users.add('User%03d'%len(self._users))
        self._users.touch()

class ClearUsersAction(flow.Action):

    _users = flow.Parent()

    def needs_dialog(self): return False
    def run(self, button):
        self._users.clear()
        self._users.touch()

class Users(flow.Map):
    '''
    A collection of Users.

    You can inject your custom User type using the slot
    <libmodule>.User

    You can inject you add_user and clear_users Action using
    the slot names:
    - <libmodule>.AddUserAction
    - <libmodule>.ClearUsersAction
    '''
    add_user = flow.Child(AddUserAction).injectable(inherit_default=False)
    clear_users = flow.Child(ClearUsersAction).injectable(inherit_default=False)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(User)
    
    def columns(self):
        return ['Name', 'User Type', 'Department(s)']
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['User Type'] = item.__class__.__name__
        row['Department(s)'] = ', '.join(item.depts.get())
        
class Task(flow.Object):

    start_date = flow.Param(0).ui(editor='date')
    nb_days = flow.IntParam(2)
    assigned = flow.Connection(User)


#
#--- Customization code
#

class MyDepts(flow.values.MultiChoiceValue):
    '''
    This will be injected in the lib to customize the
    list of departments.
    '''
    CHOICES = ('Mod', 'Rig', 'Surf', 'Anim', 'Lighting', 'Comp')

class MyUser(User):
    '''
    Our user has a squad param and a chapter_head boolean param.
    We will inject this User subclass in the lib code.
    '''
    squad = flow.Param('')
    chapter_head = flow.BoolParam(False)

class Demo(flow.Object, flow.InjectionProvider):
    '''
    This would be the Projet class.
    It uses the public Object from the lib (Task and Users),
    but it injects a couple type that the lib will use
    instead of the default ones.

    Note that this Object inherits flow.InjectionProvider
    This is not mandatory, you just need to implement
    the _injection_provider() class method. But the
    default implementation in flow.InjectionProvider
    will print injection request which is usefull
    to see all slot_names before starting to implement
    your provider...
    '''
    task1 = flow.Child(Task)
    task2 = flow.Child(Task)

    users = flow.Child(Users).ui(expanded=True)

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        # In this demo, the lib module name is the current 
        # one because it's not really a lib.
        # We're using __name__ but in real cases you'll
        # need to write the full qualified name like:
        # 'awesome_flow_users_lib.users.DeptChoiceValue'
        if slot_name == __name__+'.DeptChoiceValue':
            return MyDepts

        elif slot_name == __name__+'.User':
            return MyUser

#
#--- Simple Demo
#
class LibChild(flow.Object):
    lib_param = flow.Param('This is a lib Param').ui(editable=False)

class LibObject(flow.Object):
    child = flow.Child(LibChild).injectable()

class MyChild(LibChild):
    my_param = flow.Param('This is my additionnal Param').ui(editable=False)

class SimpleDemo(flow.Object, flow.InjectionProvider):
    doc = flow.Label(
        'This is a simple demonstration of Child and Map injection.\n'
        'The "some_lib_object" here contain a "child" object with 2 Params. '
        'One of those param was defined outside the lib.\n'
        '(Read the code as a reference.)'
    )
    some_lib_object = flow.Child(LibObject)

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if default_type is LibChild:
            return MyChild

class InjectionGroup(flow.Object):

    demo = flow.Child(Demo).ui(extended=True)
    simple_demo = flow.Child(SimpleDemo)

    intro = flow.Label(
        '''
        <html><body>
        <font size=+2>

        <H1>Dependency Injection / Inversion of Control</H1>
        <H2>Why ?</H2>
        <p>
        Hi-level Objects often need to relate each others.
        </p>
        <p>
        When building a self contained flow, this is not an issue.
        But while building flow libraries, you face a situation where
        you have to deliver Objects for every related high level 
        concepts so that they can interact thru their relations.
        </p>
        <p>
        The situation is also bad for the library users who will need
        to adopt all the concepts of the library because they can't
        change the relation between them.
        </p>
        <p>
        As an example, let's consider you want to build a Task 
        system:<br>
        You use a `Map` to manage a list of `Task`.<br>
        A `Task` has `start_date` and `duration`, as well as a 
        `assigned_user` which is a `Connection` to a `User`.<br>
        At this point you need to define what is a `User` and the 
        interface it needs to interact with your `Task`. So you had 
        a `Team` map containing `User` items...<br>
        You Task system now contains Tasks and Users and in order to
        use it in a pipeline flow one needs to adopt your Task system
        as well as your User system. <b>This sucks !!!</b>
        </p>
        <p>
        On this example, an <b>Inversion of Control</b> is to give
        the pipeline flow the control over the relation used by the Task
        lib flow.<br>
        A common way to achieve this is to <b>inject</b> the 
        <b>dependencies</b> inside the Task flow lib from the pipeline flow
        instead of letting the Task flow lib define them.
        </p>
        <H3>Why is it a problem ?</H3>
        <p>
        A flow Object dependencies are defined by the `Child` and `Map`
        contained in all its children. (`Param` are `Child`, but `Parent` 
        and `Relative` are special and dont apply here).<br>
        More precisely, they are defined by the type of Objects
        each `Relation` relate to and the type of item mapped to each `Map`.<br>
        The classic way to change those (in order to change the dependencies) is
        by inheritance: you inherit the relation owner and override the relation 
        by defining a new one with the same name.<br>
        The probleme is that you now need to use this new class instead of the one 
        containing the Relation you altered. So you also need to inherit its
        parent's class. And this goes up to your Project class !<br>
        <b>This sucks !!!</b><br>
        But keep your pants on and read on, we have a
        solution for this situation: <b>Dependency Injection</b>
        </p>
        <p>
        Also, it's worth specifying that dependency injection also makes writing 
        test code extremely easier as it lets you replace/mock-up part of the
        system to isolate the component you want to test.
        </p>
        <H2>How ?</H2>
        <p>
        So we want to "override" the <b>related type</b> of some Relations, and
        the <b>mapped type</b> of some Maps.<br>
        We want to do it with different types on different flow, be them pipeline
        flows or lib flows.<br>
        And as alwawy, we want to do from within the flow itsef so that everything
        is well tight together.<br>
        Also, as a lib flow developer, we want to specify which types can be 
        <b>injected</b> ("overidden") in my lib Objects.
        </p>
        <p>
        The first step is specifying that a Relation supports injection. This is 
        done by calling `injectable()` on it.<br>
        In this example, the `my_studio.flow.lib.foo` lib flow defines a `Foo` 
        Object that contains a `FooChild` Object. Let's say you want your lib users
        to be able to inject their Object intead of using your 'FooChild':
        <pre>
            # my_studio/flow/lib/foo.py`

            class Foo(flow.Object):    
                my_child = flow.Child(FooChild).injectable()

        </pre>
        The second step is to use the foo lib and inject a new type instead of
        `FooChild`.<br>
        This is done by defining an `_injection_provider()` method in any parent
        of the `Foo` Object.<br>
        In this example, we inject a `FooChild` subclass that extends it with
        the `is_awesome` Param.
        <pre>
            from my_studio.flow.lib.foo import Foo, FooChild

            class MySuperFooChild(FooChild):
                is_super = flow.BoolParam(True)

            class Project(flow.Object, flow.InjectionProvider):

                foo = flow.Child(Foo)

                def _injection_provider(self, slot_name, default_type):
                    if default_type is FooChild:
                        return MySuperFooChild
        </pre>
        With this set up, your `Project` pipeline flow is using the `foo` lib
        flow with an extended FooChild.
        <b>This rocks !!!</b>
        </p>

        <H2>Demo</H2>
        <p>
        In the "Demo" group above here you can see a couple of Tasks and a 
        Team of Users.<br>
        Each Task can be assigned a User by drag'n'drop.<br>
        </p>
        <p>
        The Task type is defined in a library. It uses a default User type 
        with a 'dept' param with 'Preprod', 'Prod' and 'Edit' multiple choices.
        </p>
        <p>
        We want to use this library but we have more departments for our users,
        and we also have squad and chapters.<br>
        We define a new User class by inheriting the lib's one and extending it
        with more params. This User type in then injected into the lib.<br>
        We also Inject a custom DeptChoiceValue into the lib to have our own
        department choices.
        </p>
        <H2>Notes</H2>
        <p>
        This demo can't showcase it but injections are tied to the current
        flow root so that they can be different per project. This means you
        can use the same flow lib injected differently in several pipelines.<br>
        On the other hand, the injections are resolved only once per pipeline
        and your providers will never be called twice on the same `slot_name`. 
        This means that all instances of a Project will use the same 
        injections. This is a feature and not a restriction: a [work/data]flow 
        must be consistent in all its occurences in order to provide all the
        intended benefits. 
        </p>
        </font>
        </body></html>
   '''
    )
