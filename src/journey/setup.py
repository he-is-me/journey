from ast import Tuple
import calendar
from ctypes import ArgumentError
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from logging import root
import math
from textual.app import App, ComposeResult
from datetime import  datetime
from textual import on
from textual.binding import Binding
from textual.color import Color
from textual.containers import Center, Horizontal, Vertical, VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.types import DuplicateID
from textual.validation import Integer, Length, ValidationResult, Validator
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Input , Label,  RadioButton,  Static, TextArea, Tree, Label
from rich.text import Text
from textual.widgets._tree import TreeNode
from typing import Any,Tuple,  Dict, List,  TypedDict

#TODO if i make this node.data accesible in gloabl I need to make sure it changes everywhere else:
# I need to also make sure that if the user decides to update the data it is updated everywhere


class DisplayOption(Enum):
    SHOW = 'block'
    HIDE = 'none'


class MainGoalLayer(TypedDict):
    node: TreeNode

class GoalType(Enum):
    MAIN_GOAL = 'main_goal'
    SUB_GOAL = 'sub_goal'
    TASK_GOAL = 'task'



@dataclass()
class TreeNodeManager():
    last_added_main_node: TreeNode|None=None
    last_added_sub_node: TreeNode|None=None
    last_added_task_node: TreeNode|None=None
    last_added_node: TreeNode|None = None 
    last_added_node_type: GoalType|None=None
    node_dict: Dict[str,MainGoalLayer] = field(default_factory=dict) #keys are goal names: values is data associated to node
    last_added_node_id: int = 0
    main_goal_node_count: int = 0
    sub_goal_node_count: int = 0
    task_node_count: int = 0
    

    def get_last_added_node(self) -> TreeNode:
        """we use GoalType to check for node type because the 
        type of goal is the same as the type of node 
        i.e: main_goal refers to a main_node"""
        #NOTE might need to remove this error throw as it could 
        # cause problems later 
        if self.last_added_node != None:
            return self.last_added_node
        else:
            raise Exception(f"ERROR in ({self.__class__.__qualname__}: No nodes added to dataclass yet !)")

    
    def get_node_dict(self) -> Dict[str,MainGoalLayer]:
        return self.node_dict



    def get_node_by_label(self,main_node_label: str, sub_node_label: str | None=None,
                          task_node_label: str | None=None,) -> TreeNode | None:
        if sub_node_label == None and task_node_label == None:
            a = self.node_dict.get(main_node_label)
            if isinstance(a, dict):
                return a.get("node") 

        elif sub_node_label != None and task_node_label == None:
            a = self.node_dict.get(main_node_label)
            if isinstance(a,dict):
                d = a.get(sub_node_label)
                if isinstance(d,dict):
                    return d.get("node")

        elif sub_node_label != None and task_node_label != None:
            a = self.node_dict[main_node_label].get(sub_node_label)
            if isinstance(a,dict):
                return a.get(task_node_label)



    def insert_new_node(self, main_node_label: str,node_type: GoalType, node: TreeNode,
                    sub_node_label: str|None=None, task_node_label: str|None=None) -> bool:
        """insert a node into the node dict and set last added node and its type"""
        try:
            if node_type == GoalType.MAIN_GOAL:
                self.node_dict[main_node_label] = {"node": node}  
                self.last_added_main_node = node
            elif node_type == GoalType.SUB_GOAL and sub_node_label != None: 
                self.node_dict[main_node_label][sub_node_label] = {"node":node}
                self.last_added_sub_node = node
            elif sub_node_label != None and task_node_label != None:
                self.node_dict[main_node_label][sub_node_label][task_node_label] = {"node":node}
                self.last_added_task_node = node
            self.last_added_node_type = node_type
            self.last_added_node = node
            return True
        except Exception as e:
            #TODO log err
            return False


    def update_node_data(self, node_data: Any, node_type: GoalType, main_node_label: str,
                         new_data: Any, sub_node_label: str|None=None, task_node_label: str|None=None) -> bool:
        node = None
        if self.last_added_node != None and node_type == self.last_added_node_type:
            self.get_last_added_node().data = new_data
        elif sub_node_label == None and task_node_label == None:
            node = self.get_node_by_label(main_node_label)
        elif sub_node_label != None and task_node_label == None:
            node = self.get_node_by_label(main_node_label, sub_node_label)
        elif sub_node_label != None and task_node_label != None:
            node = self.get_node_by_label(main_node_label, sub_node_label,task_node_label)
        if isinstance(node, TreeNode):
            node.data = new_data
            return True
        return False




    def set_last_added_node(self, node: TreeNode, node_type: GoalType, main_node_label: str,
                            sub_node_label: str|None=None, task_node_label: str|None=None) :
        try:
            if sub_node_label is None and task_node_label is None:
                self.insert_new_node(main_node_label=main_node_label, node=node, node_type=node_type)
            elif isinstance(sub_node_label,str):
                self.insert_new_node(main_node_label=main_node_label, sub_node_label=sub_node_label,
                                 node_type=node_type, node=node)
            else:
                self.insert_new_node(main_node_label=main_node_label, sub_node_label=sub_node_label,
                                 task_node_label=task_node_label, node_type=node_type, node=node)
        except Exception as e:
            #TODO log err 
            return False
        self.last_added_node = node
        self.last_added_node_id = node.id
        self.last_added_node_type = node_type
        return True
            




    




class GoalTree(VerticalGroup):
    """The main goals area tree"""
    node_manager = TreeNodeManager()

    initial_tree: Tree[dict] = Tree(Text("Goals",style="bold underline"), id="goal_tree")
    root_node = initial_tree.root
    tree_root: reactive[TreeNode] = reactive(root_node)
    root_node.expand()
    
    def insert_new_branch(self, label: str, node_data: dict) -> bool:
        node = self.root_node.add(label=label, data=node_data)
        check = self.node_manager.insert_new_node(main_node_label=label, node_type=GoalType.MAIN_GOAL,node=node)
        if check:
            self.node_manager.set_last_added_node(node=node,node_type=GoalType.MAIN_GOAL,main_node_label=label)
            return True
        else:
            return False
    
    def insert_on_last_branch(self, sub_node_label: str,node_data: dict, task_node_label: str|None=None) -> bool:
        if task_node_label == None:
            last_goal = self.node_manager.last_added_main_node
            if isinstance(last_goal, TreeNode):
                node = last_goal.add(label=sub_node_label, data=node_data)
                self.node_manager.set_last_added_node(main_node_label=str(last_goal.label),sub_node_label=sub_node_label
                                                      ,node=node,node_type=GoalType.SUB_GOAL)
                return True
        elif task_node_label != None and sub_node_label != None:
            last_goal = self.node_manager.last_added_sub_node
            if isinstance(last_goal,TreeNode):
                node = last_goal.add_leaf(task_node_label,node_data)
                self.node_manager.set_last_added_node(main_node_label=str(last_goal.label), sub_node_label=sub_node_label,
                                                      task_node_label=task_node_label
                                                      ,node=node,node_type=GoalType.TASK_GOAL)
                return True
        return False


    def insert_new_goal(self, tree_root: Tree[str], goal_name: str) -> Tree:
        tree_root.root.add(goal_name)
        return tree_root
        

    def compose(self) -> ComposeResult:
        #TODO make sure that I know this really wants to take args or not !
        yield self.initial_tree

        # yield self.insert_new_goalTree("Sub Goals", "sub_goals")


class NotificationLevel(Enum):
    INFO = "italic white"
    WARNING = "bold yellow"
    ERROR = "bold red underline"

class Notification(VerticalGroup):
    def __init__(self, label_id: str="notification_label", static_id: str="notification_static", content_text: str=""):
        super().__init__()
        self.noti_label: Label = Label(id=label_id)
        self.noti_static: Static = Static(content=content_text,id=static_id) 
        self._notification_que: List[Tuple[Text,str]] = []
        self.current_message: str



    def add_to_que(self, message: Text, level: NotificationLevel):
        """inserts data into the notification que depending on the NotificationLevel given,
        INFO: goes last, regular white text
        WARNING: goes in the middle, italicized yellow text 
        ERROR: goes first, bold red text"""
        match level:
            case NotificationLevel.INFO:
                self._notification_que.append((message,NotificationLevel.INFO.value))
            case NotificationLevel.WARNING:
                que_len = len(self._notification_que)
                if que_len != 0:
                    idx = math.ceil(que_len/2)
                    self._notification_que.insert(idx, (message, NotificationLevel.WARNING.value))
                else:
                    self._notification_que.append((message,NotificationLevel.WARNING.value))
            case NotificationLevel.ERROR:
                self._notification_que.insert(0,(message,NotificationLevel.ERROR.value))
        return 


    
    def display_and_flush_que(self) -> bool:
        """displays a range of differnt notification in their own repective colors
        and then clears out the buffer"""
        if len(self._notification_que) == 0:
            return False
        else:
            notification_messages: List[Text] = []
            for msg,color in self._notification_que:
                msg.stylize(color)
                notification_messages.append(msg)

            messages =  Text("\n").join(notification_messages)
            self.noti_static.update(messages)
            self._notification_que.clear()
            return True
            




    def send_message(self, message: Text, level: NotificationLevel=NotificationLevel.WARNING):
        """send a single notification message with a specific level"""
        message.stylize(level.value)
        self.noti_static.update(message)


    def compose(self) -> ComposeResult:
        yield Center(
                self.noti_static
                )


    def on_mount(self):
        self.add_to_que(Text("This is an info notification"), NotificationLevel.INFO)
        self.add_to_que(Text("uh oh, this is a warning"), NotificationLevel.WARNING)
        self.add_to_que(Text("OH MY FUCKING GOD ! THIS IS A FUCKING EMERGENCY !!!"), NotificationLevel.ERROR)
        self.display_and_flush_que()

class MainGoalCollection(VerticalGroup):
    """widget for collecting all user goal info"""

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        """when a tier button is selected the others are made unclickable"""
        t1_button = self.query_one("#mg_t1", RadioButton)
        t2_button = self.query_one("#mg_t2", RadioButton)
        t3_button = self.query_one("#mg_t3", RadioButton)
        id = event.radio_button.id
        value = event.radio_button.value

        if id == "mg_t1":
            if value == False:
                t2_button.disabled = False
                t3_button.disabled = False
            else:
                t2_button.disabled = True
                t3_button.disabled = True

        elif id == "mg_t2":
            if value == False:
                t1_button.disabled = False
                t3_button.disabled = False
            else:
                t1_button.disabled = True
                t3_button.disabled = True

        elif id == "mg_t3":
            if value == False:
                t1_button.disabled = False
                t2_button.disabled = False
            else:
                t1_button.disabled = True
                t2_button.disabled = True





    def compose(self) -> ComposeResult:
        """ids prefixed with mg stands for Main Goal"""
        #TODO add tooltips to all of the inputs and description
        yield Center(Label(Text("Main Goal",style="bold underline"),id="mg_title_label"))
        yield Input(placeholder="Goal Name", id="mg_goal_input",
                    validators=[Length(minimum=1, maximum=500, failure_description="Goal too short !")])

        yield Horizontal(Vertical(Input(placeholder="Start Date (optional)", id="mg_start_date",
                                        validate_on=['changed'],
                                        validators=[DateValidator()],valid_empty=True),

                                  Input(placeholder="Due Date (Day/Month/Year or Month/Year )", id="mg_due_date",
                                        validators=[DateValidator(),
                                                    DateRangeValidator()]),

                                  Input(placeholder="Difficulty (1-3) | 1 = Easy, 3 = Hard", id="mg_difficulty", 
                                        type="number", validators=[Integer(minimum=1, maximum=3)]),
                                  id="mg_dates_dif_vertical",),

                         Vertical(RadioButton(label="Tier 1 (Mission critical Goal)", id="mg_t1", disabled=False),
                                  RadioButton(label="Tier 2 (High-Impact Goal)", id="mg_t2", disabled=False),
                                  RadioButton(label="Tier 3 (Growth & Improvement)", id="mg_t3", disabled=False, tooltip="Not so important but good for growth"),
                         id="mg_tier_vertical"),

              id="mg_main_horizontal")

        yield Label(Text("""Beyond just completing this goal, what would achieving it truly mean for you or your life? How would things be different,
                         and what impact would it have on your well-being, growth, or overall aspirations?""",style="bold"), id="mg_description_label")
        yield TextArea(id="mg_description")

        yield Notification()
        # yield Rule(line_style='heavy')




    @staticmethod
    def send_noti(message: str|Text):


        ...


    @on(Input.Changed)
    def validator_fail_notification(self, event: Input.Changed):
        """when input valifator failed tell user why at bottom of screen"""
        #TODO remove later
        if event.validation_result != None:
            notification = self.query_one(Notification)
            if not event.validation_result.is_valid: 
                notification.send_message(Text("\n".join(event.validation_result.failure_descriptions), style=" bold red"),
                                          level=NotificationLevel.ERROR)
            else:
                notification.send_message(Text(""))
        else:
            return


    




class SubGoalCollection(VerticalGroup):
    """collecting sub goals from user which are 2nd on the hierarchy of 
    goals in journey. These goals are the ones that must be complete before
    the maing goal is complete"""
    subgoal_question = "What potential challenges do you foresee for this subgoal, and what's your plan to overcome them ? (optional)"
    def compose(self) -> ComposeResult:
        # yield Center(Label(Text(f"{self.app.query_one(GoalTree).node_manager.last_added_main_node.label}",style="bold underline"),id="sg_title_label"))
        yield Input(placeholder="Goal Name", id="sg_goal_input", valid_empty=False,
                    validate_on=['blur','changed'],
                    validators=[Length(minimum=1, maximum=500, failure_description="Goal too short !")])

        yield Horizontal(Vertical(Input(placeholder="Due Date (Day/Month/Year or Month/Year )", id="sg_due_date",
                                        validate_on=['changed'],
                                        validators=[DateValidator()]),

                                  Input(placeholder="Difficulty (1-3) | 1 = Easy, 3 = Hard", id="sg_difficulty", 
                                        type="number", validators=[Integer(minimum=1, maximum=3)], validate_on=["blur","submitted"]),
                         id="sg_dates_dif_vertical",),

                         Vertical(RadioButton(label="Tier 1 (Mission critical Goal)", id="sg_t1", disabled=False),
                                  RadioButton(label="Tier 2 (High-Impact Goal)", id="sg_t2", disabled=False),
                                  RadioButton(label="Tier 3 (Growth & Improvement)", id="sg_t3", disabled=False),
                         id="sg_tier_vertical"),

              id="sg_main_horizontal")


        yield Horizontal(
                        Vertical(Center(Label(Text(self.subgoal_question,justify='full'),shrink=True, id="sg_question")),
                                 TextArea(id="sg_question_textbox")),
                        #TODO fix these fucking ID's you dumbass !!! why do you make life harder ????
                        Vertical(Center(Label("description (optional)\n", id="sg_description_center_container")),
                                 TextArea(id='sg_description')),
                         id='sg_description_horizontal')

        

        yield Notification(static_id="sg_notification_static")
 

class TaskGoalCollection(VerticalGroup):
    """collect tasks from users which are 3rd and last in the hierarchy
    of goals in Journey."""
    def __init__(self, id: str):
        super().__init__(id=id)
        self.mounted_widget: Widget|None = None


    @lru_cache(maxsize=3) 
    def get_container(self, id: str) -> Vertical:
        if not id.startswith("#"): 
            id = "#" + id
        return self.query_one(id, Vertical)

    async def set_frequency(self, 
                            widget: Widget,
                            height: int,
                            width: int,
                            ):
        container = self.get_container(id="tg_temp_widget_container")
        if self.mounted_widget != None:
            if self.mounted_widget.id == widget.id:
                self.mounted_widget = None
                container.styles.height = 0
                container.styles.width = 0
                return

        assert height <= 100 and height >= 0
        assert width <= 100 and width >= 0

        try:
            await container.mount(widget)
            container.styles.height = str(height) + '%'
            container.styles.width = str(width) + '%' 
        except Exception:
            return

        self.mounted_widget = widget


    @on(Button.Pressed, """#tg_one_time_thing_btn,
                           #tg_daily_btn,
                           #tg_weekly_btn,
                           #tg_monthly_btn,
                           #tg_quaterly_btn""")
    async def pressed_frequency(self, event: Button.Pressed):
        #TODO put all logic under checks in 1 or 2 function calls to clean this shit up !
        event_id = str(event.button.id)
        if self.mounted_widget != None: 
            await self.mounted_widget.remove()

        if "one_time" in event_id:
            if self.mounted_widget != None:
                container = self.query_one("#tg_temp_widget_container", Vertical)
                container.styles.width = "0"
                container.styles.height = "0"

        elif "daily" in event_id:
            if self.mounted_widget != None:
                container = self.query_one("#tg_temp_widget_container", Vertical)
                container.styles.width = "0"
                container.styles.height = "0"


        elif "weekly" in event_id:
            widget = WeeklyDaySelector(id="tg_weekly_widget")
            await self.set_frequency(widget, 15,100)

        elif "monthly" in event_id:
            widget = MonthlyDateSelector(id="tg_monthly_widget")
            await self.set_frequency(widget, 30,100)

        elif "quaterly" in event_id:
            widget = QuarterlyDateSelector(id="tg_quaterly_widget")
            await self.set_frequency(widget, 30,100)
            

    def compose(self) -> ComposeResult:
        yield Center(Label(Text("Put subgoal name here", style="bold red"),id="tg_page_title"))
        yield Vertical(Input(placeholder="Task Name", id="tg_goal_input"),
                       Center(Label(Text("How frequently will you need to complete this task",
                                style="bold red"),id="tg_page_title")),

                       Horizontal(Button("One Time Thing", id="tg_one_time_thing_btn"),
                                  Button("Daily", id="tg_daily_btn"),
                                  Button("Weekly", id="tg_weekly_btn"),
                                  Button("Monthly", id="tg_monthly_btn"),
                                  Button("Quaterly", id="tg_quaterly_btn"),
                                  id="tg_frequency_horizontal_container"),
              Horizontal(
                       Input(placeholder="Difficulty (1-3) | 1 = Easy, 3 = Hard", id="tg_difficulty", 
                             type="number",
                             validators=[Integer(minimum=1, maximum=3)],
                             validate_on=["blur","submitted"]),
                       Input(placeholder="Due Date (Day/Month/Year or Month/Year )", id="tg_due_date",
                             validate_on=['changed'],
                             validators=[DateValidator()]),
                       id="tg_difficulty_date_horizontal"),
        Vertical(id="tg_temp_widget_container"),
        Notification(static_id="tg_notification_static"),
                     id="tg_vertical_container")

class DailyCompletionSelector(Widget):
    def __init__(self, id: str):
        super().__init__(self, id=id)



    def compose(self) -> ComposeResult:
        return super().compose()



class WeeklyDaySelector(Widget):
    def __init__(self, id: str):
        super().__init__(id=id)
        self.activated_buttons: list[str] = []


    def on_button_pressed(self, event: Button.Pressed):
        button_name = str(event.button.label)
        if button_name in self.activated_buttons:
            event.button.styles.color = None
            event.button.styles.background = None
            self.activated_buttons.remove(button_name)
            return
        self.activated_buttons.append(str(event.button.label))
        event.button.styles.color = "white"
        event.button.styles.background= 'green'


    def compose(self) -> ComposeResult:
        yield Horizontal(
                Button("Monday", id="wk_monday", classes="auto_size_small_margin"),
                Button("Tuesday", id="wk_tueday", classes="auto_size_small_margin"),
                Button("Wednesday", id="wk_wednesday", classes="auto_size_small_margin"),
                Button("Thursday", id="wk_thursday", classes="auto_size_small_margin"),
                Button("Friday", id="wk_friday", classes="auto_size_small_margin"),
                Button("Saturday", id="wk_saturday", classes="auto_size_small_margin"),
                Button("Sunday", id="wk_sunday", classes="auto_size_small_margin"),
                id="wk_buttons_horizontal")



class DaySelector(Widget):
    displayed: reactive[DisplayOption] = reactive(DisplayOption.SHOW)
    def __init__(self, id: str):
        super().__init__(id=id)
        self.day_buttons: list[Button] = []
        self.selected_days: list[str] = []
        self.container = self.app.query_one("#tg_temp_widget_container", Vertical)
        self.button_states: dict[str,list[str]] = {} 
        self.initial_mount: bool = True
        self.current_day_count: int|None = None
        self.previous_day_count: int|None = None
        self.previous_month: int|None = None
        self.month = 0
        self.int_month = 0
        self.year = datetime.today().year
        self.month_name = str(calendar.month_name[self.int_month])[:3] # pyright: ignore[]
    
    @staticmethod
    def _reset_button_state(func):
        def wrapper(self):
            for button in self.day_buttons:
                self.deactivate_button(button, True)
            result = func(self)
            return result
        return wrapper

    @_reset_button_state
    def _collect_active_buttons(self) -> set[str]:
        active_buttons = [button
                          for button in self.day_buttons 
                          if button.styles.background == Color(0,128,0)]
        return  {str(button.name) for button in active_buttons}
        

    def activate_button(self, button: Button, set_state_only: bool=False):
        button_name = str(button.name)
        button.styles.color = "white"
        button.styles.background = "green"
        if button_name not in self.selected_days:
            self.selected_days.append(button_name)
        if set_state_only:
            return
        if self.month_name not in self.button_states:
            self.button_states[self.month_name] = []
        self.button_states[self.month_name].append(button_name)
 


    def deactivate_button(self, button: Button, full_clear: bool=False):
        button.styles.color = None
        button.styles.background = None
        if full_clear:
            self.selected_days.clear()
        else:
            if str(button.name) in self.selected_days:
                self.selected_days.remove(str(button.name))
            if str(button.name) in self.button_states[self.month_name]:
                self.button_states[self.month_name].remove(str(button.name))

    @_reset_button_state
    def _set_button_states(self):
        """when user goes back to another month where they've 
           already selected days, this sets them back, it turns 
           off button selection from previous month before that 
        """
        set_days = []
        for month in self.button_states:
            if self.month_name == month:
                set_days = self.button_states[month]
        if len(set_days) != 0:
            for button in self.day_buttons:
                for day in set_days:
                    if button.name == day:
                        self.activate_button(button, set_state_only=True)
                    

    def get_last_day_in_month(self) -> int|None:
        try:
            return max(calendar.monthcalendar(datetime.today().year, self.month)[-1])
        except calendar.IllegalMonthError:
            raise ValueError(f"month == {self.month}")
        
    def remove_extra_days(self):
        for button in self.day_buttons:
            try:
                day = int(button.name) #pyright: ignore  
            except ValueError:
                raise Exception("Button Names possibly changed, button names should be string ints so they are transformable")

            if day > self.current_day_count: #pyright: ignore
                button.display = DisplayOption.HIDE.value
 

    def add_missing_days(self):
        for button in self.day_buttons:
            try:
                day = int(button.name) #pyright: ignore  
            except ValueError:
                raise Exception("Button Names possibly changed, button names should be string ints so they are transformable")

            if day <= self.current_day_count: #pyright: ignore
                button.display = DisplayOption.SHOW.value
 




    def watch_displayed(self):
        if self.displayed == DisplayOption.HIDE:
            self.previous_month = self.month
            self.initial_mount = False
            self.display = DisplayOption.HIDE.value
        else:
            self.display = DisplayOption.SHOW.value
            self.month_name = calendar.month_abbr[self.month]
            self.previous_day_count = self.current_day_count
            self.current_day_count = self.get_last_day_in_month()
            if self.current_day_count and self.previous_day_count:
                if self.current_day_count > self.previous_day_count:
                    self.add_missing_days()
                else:
                    self.remove_extra_days()
            self._set_button_states()



    def watch_month(self):
        self.month_name = calendar.month_abbr[self.month]
        self.previous_day_count = self.current_day_count
        self.current_day_count = self.get_last_day_in_month()
        


    def selected_day(self, button: Button, button_name: str):
        if button_name in self.selected_days:
            self.deactivate_button(button)
            return
        self.activate_button(button)



    def set_all_dates(self):
        """sets all dates selected in current month for all other months"""
        #TODO add a check to make sure the month actually contains that day 
        # if we select january 31st febuary 31st should not be added because 
        # it doesnt exist
        for month in calendar.month_abbr:
            if month and month not in self.button_states:
                self.button_states[month] = []
        for selected_month in self.button_states: 
            self.button_states[selected_month] = self.button_states[self.month_name]
        for button in self.day_buttons:
            button_name = str(button.name)
            for selected_month in self.button_states:
                for day in self.button_states[selected_month]:
                    if day == button_name:
                        self.activate_button(button, set_state_only=True)

                
                

    def add_unset_option(self):
        unset_button = Button("unset dates", name="unset", id="day_unset_option")
        self.query_one("#days_options_horizontal", Horizontal).mount(unset_button)


    def on_button_pressed(self, event: Button.Pressed):
        button = event.button
        button_name = str(button.name)
        if "back" in button_name:
            self.displayed = DisplayOption.HIDE
            self.app.query_one(MonthlyDateSelector).displayed = DisplayOption.SHOW

        elif "set_all" in button_name:
            self.set_all_dates()
            self.add_unset_option()


        elif "unset" in button_name:
            for b in self.day_buttons:
                self.deactivate_button(b)
            self.button_states.clear()
            button.remove()
            
            ...

        else:
            self.selected_day(button, button_name)
            ...
        




    def on_mount(self):
        self.container.styles.height = "35%"
        if not self.current_day_count:
            self.current_day_count = self.get_last_day_in_month()
        if self.current_day_count:
            self.app.query_one("#tg_goal_input", Input).value = str(self.current_day_count)
            if self.current_day_count < len(self.day_buttons):
                self.remove_extra_days()




    def spawn_buttons(self):
        """spawns 31 buttons to cover each day an any month 
        if a month like feb needs less buttons they will be 
        removed using a watch func"""

        for num in range(1,32):
            day = str(num)
            self.day_buttons.append(Button(label=day,
                                           name=day,
                                           compact=False,
                                           classes="day_buttons",
                                           id=f"day_button_{day}"
                                           ))

        buttons = Vertical(
                          # Static(self.month_name, classes=""),
                          Horizontal(*self.day_buttons[0:8], classes="center_widget"),
                          Horizontal(*self.day_buttons[8:16], classes="center_widget"),
                          Horizontal(*self.day_buttons[16:24], classes="center_widget"),
                          Horizontal(*self.day_buttons[24:], classes="center_widget"),
                          Horizontal(Button("back", name="days_back_button"),
                                     Button("set date(s) for all months", name="days_set_all_button"),
                                     classes="center_widget", id="days_options_horizontal"), id="days_main_vertical")
        return buttons
        

    def compose(self) -> ComposeResult:
        yield self.spawn_buttons()
        

class MonthlyDateSelector(Widget):
    displayed: reactive[DisplayOption] = reactive(DisplayOption.SHOW)
    def __init__(self,id: str):
        super().__init__(id=id)
        self.month_buttons: list[Button] = []
        self.container = self.app.query_one("#tg_temp_widget_container", Vertical)
        self.day_selector_widget = DaySelector(id="day_selector_widget")
    

    def watch_displayed(self):
        if self.displayed == DisplayOption.HIDE:
            self.display = DisplayOption.HIDE.value
        else:
            self.display  = DisplayOption.SHOW.value



    def on_button_pressed(self, event: Button.Pressed):
        button = event.button
        assert type(int(button.name)) == int # pyright: ignore[]  
        month = int(button.name) #the name arg for each monb_name] # pyright: ignore[]
        self.day_selector_widget.month = month 
        if (not self.day_selector_widget.is_mounted and 
            self.day_selector_widget.id not in self.children):
            try:
                self.container.mount(self.day_selector_widget)
                self.displayed = DisplayOption.HIDE
                return
            except Exception:
                pass
        self.displayed = DisplayOption.HIDE
        self.day_selector_widget.displayed = DisplayOption.SHOW
        

            

    def monthly_widget(self):
        for idx,month in enumerate(calendar.month_name):
            if month.strip() != "":
                self.month_buttons.append(Button(month[:3], id=f"month_{str(month[:3]).lower()}",
                                                 name=str(idx)))

        return Horizontal(Vertical(*self.month_buttons[0:3],
						 id=f"month_jan_to_mar"), 
                        Vertical(*self.month_buttons[3:6],
						id=f"month_apr_to_jun"),
                        Vertical(*self.month_buttons[6:9],
						id=f"month_jul_to_sep"),
                        Vertical(*self.month_buttons[9:12],
						id=f"month_oct_to_dec"),
                        id="month_buttons_horizontal")
            

    
    def compose(self) -> ComposeResult:
        yield self.monthly_widget()



class QuarterlyDateSelector(Widget):
    def __init__(self, id: str):
        super().__init__(id=id)
        self.month_buttons: list[Button] = []
        self.buttons: list[Button] = []
        self.selected_buttons: list[str] = []
        self.container = self.app.query_one("#tg_temp_widget_container", Vertical)



    def row_selection(self, quarter_button: Button, quarter_button_name: str):
        button_container = quarter_button.parent
        if button_container != None:
            self.app.query_one("#tg_goal_input", Input).value = str(button_container.children)
            for month_button in button_container.children:
                month_name = str(month_button.name)
                if month_name != quarter_button_name and month_name not in self.selected_buttons:
                    quarter_button.styles.background = "green"
                    quarter_button.styles.color = "white"
                    month_button.styles.background = "green"
                    month_button.styles.color = "white"
                    self.selected_buttons.append(month_name)
                elif month_name in self.selected_buttons:
                    quarter_button.styles.background = "transparent"
                    quarter_button.styles.color = None
                    month_button.styles.background = None
                    month_button.styles.color = None
                    self.selected_buttons.remove(month_name)



    @on(Button.Pressed, " #Q1, #Q2, #Q3, #Q4 ")
    def whole_quarter_button_pressed(self, event: Button.Pressed):
        button_name = str(event.button.name)
        self.row_selection(event.button, button_name)
        return

    @on(Button.Pressed, """#qmonth_jan,#qmonth_feb,#qmonth_mar,#qmonth_apr,
                           #qmonth_may,#qmonth_jun,#qmonth_jul,#qmonth_aug,
                           #qmonth_sep,#qmonth_oct,#qmonth_nov,#qmonth_dec""")
    def month_button_pressed(self, event: Button.Pressed):
        button_name = str(event.button.name)
        button = event.button
        if button_name in self.selected_buttons:
            button.styles.background = None
            button.styles.color = None
            self.selected_buttons.remove(button_name)
            return
        button.styles.background = "green"
        button.styles.color = "white"
        self.selected_buttons.append(button_name)
        

    def spawn_widget(self):
        for month_num, month in enumerate(calendar.month_abbr):
            if month_num == 0:
                continue
            self.month_buttons.append(Button(month, 
                                                       id=f"qmonth_{str(month).lower()}", 
                                                       name=str(month_num)))

        return Horizontal(Vertical(Button("Q1",classes="center_align",compact=True,name="Q1", id="Q1"),
						*self.month_buttons[0:3],
                        id=f"month_jan_to_mar"), 
                        Vertical(Button("Q2", classes="center_align",compact=True,name="Q2", id="Q2"),
						*self.month_buttons[3:6],
						id=f"month_apr_to_jun"),
                        Vertical(Button("Q3", classes="center_align",compact=True,name="Q3", id="Q3"),
						*self.month_buttons[6:9],
						id=f"month_jul_to_sep"),
                        Vertical(Button("Q4", classes="center_align",compact=True,name="Q4", id="Q4"),
						*self.month_buttons[9:12],
						id=f"month_oct_to_dec"),
                        id="month_buttons_horizontal")
            

    def compose(self) -> ComposeResult:
        yield self.spawn_widget()
        
            


class DateValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if self.check_date(value):
            return self.success()
        return self.failure("Invalid Date")


    @staticmethod
    def check_date(value: str, get_date: bool=False) -> bool|datetime:
        format_opt = "%m/%d/%y"
        try:
            converted_date = datetime.strptime(value,format_opt)
            if get_date:
                return converted_date
            return True
        except Exception as e:
            #TODO log this
            return False



class DateRangeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        start_date = app.query_one("#mg_start_date", Input).value
        if start_date.strip() == "":
            return self.success()
        if self.check_range(value):
            return self.success()
        return self.failure("Invalid date range, start date > due date !")



    @staticmethod
    def check_range(value) -> bool:
        """checks that start date is less than or equal to due date"""
        start_date = app.query_one("#mg_start_date", Input).value
        try:
            start = DateValidator.check_date(start_date, get_date=True)
            end = DateValidator.check_date(value, get_date=True)
        except Exception as e:
            return False
        else:
            if isinstance(start,datetime) and isinstance(end,datetime):
                return start <= end
            return False






class JourneyApp(App): 
    """A comprehensive neovim terminal application"""

    BINDINGS = [("ctrl+n", "next_screen", "Go next " ),
                ("ctrl+b", "previous_screen", "Go back"),
                Binding("ctrl+a", "add_goal_type", "Add Goal", priority=True)
                ]

    CSS_PATH = "styling.tcss"

    goal_tree_cls = GoalTree()
    main_goal_page = MainGoalCollection(id="main_goal_page")
    sub_goal_page = SubGoalCollection(id="sub_goal_page")
    task_goal_page = TaskGoalCollection(id='task_goal_page')
    page_objects = [MainGoalCollection, SubGoalCollection, TaskGoalCollection]
    page_instance = [main_goal_page, sub_goal_page, task_goal_page]
    page_num = reactive(0)
    current_page_object = MainGoalCollection
    current_page_instance  = main_goal_page


    def on_mount(self):
        self.theme = "catppuccin-mocha"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                self.goal_tree_cls,
                self.main_goal_page 
                , id="screen")

        yield Footer()


    
    def watch_page_num(self):
        try:
            self.current_page_object = self.page_objects[self.page_num]
            self.current_page_instance = self.page_instance[self.page_num]
        except Exception:
            self.app.query_one("#tg_input", Input).placeholder =  str(len(self.page_objects))


    def action_add_goal_type(self):
        """this is only for adding main goals, sub goals and task
        are added throguh selected events handling"""
        self.add_goal_action()


    def final_input_validation(self, input_widgets: list[Input]) -> bool:
        notification_box = self.query_one(Notification)
        for widget in input_widgets:
            widget.validate(widget.value)
            if not widget.is_valid:
                widget.focus()
                notification_box.send_message(Text("Invalid input !"), level=NotificationLevel.ERROR)
                return False
                
        return True

    
    def fetch_inputs(self, widgets: Widget) -> list[Input]:
        """Gives back user data of Input widgets by default or whole input objects, WARNING 
           (you need to explicitly set user data to Flase IF you set whole_object to True
           or else this function will raise an exception)"""
        input_widgets = widgets.query(Input)
        return [x for x in input_widgets]



    def fetch_tiers(self, widgets: Widget) -> list[RadioButton]:
        """Gives back user data of Radio Button widgets by default or whole input objects, 
           WARNING (you need to explicitly set user data to Flase IF you set whole_object 
           to True or else this function will raise an exception)"""
        radio_button_widgets = widgets.query(RadioButton)
        return [x for x in radio_button_widgets if x.value == True] # only return the tier radio button that is selected


    def fetch_text_area(self, widgets: Widget) ->  list[TextArea]:
        """Gives back user data of Text Area widgets by default or whole input objects, 
           WARNING (you need to explicitly set user data to Flase IF you set whole_object 
           to True or else this function will raise an exception)"""
        text_area_widgets = widgets.query(TextArea)
        return [x for x in text_area_widgets]


    

    def add_goal_action(self):
        all_child_widgets = self.app.query_one(self.current_page_object)# gets all of the widgets from current page 
        input_data = self.fetch_inputs(all_child_widgets)
        tier_data = self.fetch_tiers(all_child_widgets)
        text_area_data = self.fetch_text_area(all_child_widgets)
        if self.current_page_object== MainGoalCollection:
            id_prefix = "mg_"
        elif self.current_page_object == SubGoalCollection:
            id_prefix = "sg_"
        else:
            id_prefix = "tg_"

        complete_data = {}
        if not self.final_input_validation(input_data): #make sure inputs are valid
            return False

        selected_tier = None
        for tier  in tier_data:
            if tier.value == True:
                selected_tier = tier.label
                if "1" in str(selected_tier):
                    selected_tier = 1
                elif "2" in str(selected_tier):
                    selected_tier = 2
                else:
                    selected_tier = 3
        if selected_tier == None: 
            self.query_one(Notification).send_message(Text("Tier Not Selected !"),level=NotificationLevel.ERROR)
            return False

        for i in input_data:
            input_name = str(i.id).removeprefix(id_prefix)
            complete_data[input_name] = i.value
            

        complete_data["tier"] = selected_tier #tier gets added after input so it follows DOM order like everything else

        for i in text_area_data:
            text_area_name = str(i.id).removeprefix(id_prefix)
            if i.text.strip() == "":
                break
            else:
                complete_data[text_area_name] = i.text

        # a shitty way of checking which page is up to insert new branch or on branch need to change later to something more robust
        if "mg" in str(input_data[0].id): 
            self.query_one(GoalTree).insert_new_branch(complete_data['goal_input'], node_data=complete_data)
        #DEBUG
            # self.app.query_one(f"#{id_prefix}description", TextArea).text = str(self.app.query_one(GoalTree).node_manager.last_added_node)
        elif "sg" in str(input_data[0].id):
            self.query_one(GoalTree).insert_on_last_branch(complete_data['goal_input'], node_data=complete_data)
        #DEBUG
            # self.app.query_one(f"#{id_prefix}description", TextArea).text = str(self.app.query_one(GoalTree).node_manager.last_added_sub_node)


    async def action_next_screen(self):
        """moves user to the next phase of the goal inputing phase"""
        if self.page_num < len(self.page_instance) - 1: 
            self.page_num += 1
        else:
            self.page_num = 0
        next_page = self.page_instance[self.page_num % len(self.page_instance)]
        await self.app.query(self.page_objects[(self.page_num % len(self.page_instance)) - 1]).remove() #remove current widget 
        await self.app.query_one("#screen").mount(next_page) # add next widget



    async def action_previous_screen(self) -> None:
        if self.page_num >= 1:
            await self.app.query(self.page_objects[(self.page_num % len(self.page_instance))]).remove() #remove current widget
            self.page_num -= 1
            await self.app.query_one("#screen").mount(self.current_page_instance) # add next widget




if __name__ == "__main__":
    app = JourneyApp()
    app.run()


