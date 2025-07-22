from dataclasses import dataclass, field
from enum import Enum
import math
from platform import libc_ver
from typing import List, Tuple
from fileinput import filename
from tokenize import Number
from textual.app import App, ComposeResult
from pathlib import Path
from datetime import date, datetime
from textual import on
from textual.binding import Binding
from textual.containers import Center, Horizontal, HorizontalGroup, HorizontalScroll, Vertical, VerticalGroup, VerticalScroll
from textual.css.types import TextAlign
from textual.reactive import reactive
from textual.events import Focus
from textual.validation import Integer, Length, ValidationResult, Validator
from textual.widget import Widget
from textual.widgets import Button, Digits, Footer, Header, Input , Label, MarkdownViewer, Pretty, RadioButton, Rule, Static, TextArea, Tree, Label
from textual import log 
from rich.text import Text

#TODO if i make this node.data accesible in gloabl I need to make sure it changes everywhere else:
# I need to also make sure that if the user decides to update the data it is updated everywhere


class GoalType(Enum):
    MAIN_GOAL = 'main_goal'
    SUB_GOAL = 'sub_goal'
    TASK_GOAL = 'task'

@dataclass()
class TreeNodeManager():
    main_goal_nodes: dict[GoalType,dict] = field(default_factory=dict)
    sub_goal_nodes: dict[GoalType,dict] = field(default_factory=dict)
    task_nodes: dict[GoalType,dict] = field(default_factory=dict)
    last_accessed_node: str = ""
    last_accessed_node_id: int = 0





class GoalMenu(VerticalGroup):
    """The main goals area tree"""
    node_manager = TreeNodeManager()

    def insert_root_node(self, tree_root: str, tree_id: str):
        tree: Tree[str] = Tree(Text(tree_root,style="bold underline"), id=tree_id)
        tree.root.expand()
        return tree

    
    def add_node_data(self, node: dict[str,int|str], goal_type: str, goal_name: str):
        try:
            self.node_manager.main_goal_nodes[GoalType.MAIN_GOAL][goal_name] = node
        except Exception as e:
            return False
        else:
            return True



    def on_tree_node_selected(self, event: Tree.NodeSelected):
        ...



    

    def insert_new_goal(self, tree_root: Tree[str], goal_name: str) -> Tree:
        tree_root.root.add(goal_name)
        return tree_root
        

    def compose(self) -> ComposeResult:
        #TODO make sure that I know this really wants to take args or not !
        yield self.insert_root_node("Goals", "goals_tree")

        # yield self.insert_new_goalTree("Sub Goals", "sub_goals")


class NotificationLevel(Enum):
    INFO = "italic white"
    WARNING = "bold yellow"
    ERROR = "bold red underline"

class Notification(Widget):
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
        yield Input(placeholder="Goal Name", id="mg_goal_input", valid_empty=False,
                    validate_on=['blur','changed'],
                    validators=[Length(minimum=1, maximum=500, failure_description="Goal too short !")])

        yield Horizontal(Vertical(Input(placeholder="Start Date (optional)", id="mg_start_date",
                                        validate_on=['changed'],
                                        validators=[DateValidator()],valid_empty=True),

                                  Input(placeholder="Due Date (Day/Month/Year or Month/Year )", id="mg_due_date",
                                        validate_on=['changed'],
                                        validators=[DateValidator(),
                                                    DateRangeValidator()]),

                                  Input(placeholder="Difficulty (1-3) | 1 = Easy, 3 = Hard", id="mg_difficulty", 
                                        type="number", validators=[Integer(minimum=1, maximum=3)], validate_on=["blur","submitted"]),
                         id="mg_dates_dif_vertical",),

                         Vertical(RadioButton(label="Tier 1 (Mission critical Goal)", id="mg_t1", disabled=False),
                                  RadioButton(label="Tier 2 (High-Impact Goal)", id="mg_t2", disabled=False),
                                  RadioButton(label="Tier 3 (Growth & Improvement)", id="mg_t3", disabled=False),
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
                        Vertical(Center(Label("description (optional)\n", id="sg_description")),
                                 TextArea(id='sg_description_textbox')),
                         id='sg_description_horizontal')

        

        yield Notification(static_id="sg_notification_static")
 


    




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
                Binding("ctrl+a", "add_goal_type", "Add Goal", priority=True)] 

    CSS_PATH = "styling.tcss"

    page_num = 0
    page_ids = ["MainGoalCollection", "SubGoalCollection"]
    main_goal_page = MainGoalCollection(id="main_goal_page")
    sub_goal_page = SubGoalCollection(id="sub_goal_page")
    pages = [main_goal_page, sub_goal_page]


    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                GoalMenu(),
                MainGoalCollection()
                , id="screen")

        yield Footer()




    def action_add_goal_type(self):
        """this is only for adding main goals, sub goals and task
        are added throguh selected events handling"""
        if self.page_num == 0:
            self.add_main_goal_action()







    def final_input_validation(self, input_widgets: Tuple[Input,...]) -> bool:
        notification_box = self.query_one(Notification)
        for widget in input_widgets:
            if not widget.is_valid:
                widget.focus
                notification_box.send_message(Text("Invalid input !"), level=NotificationLevel.ERROR)
                return False
                
        return True


        



    def add_main_goal_action(self) -> bool:
        """controls adding main goal to goal tree"""
        main_goal_tree = self.app.query_one("#goals_tree", Tree)
        goal_input_data = self.app.query_one("#mg_goal_input", Input)
        start_date_input = self.app.query_one("#mg_start_date", Input)
        due_date_input = self.app.query_one("#mg_due_date", Input)
        difficulty_input = self.app.query_one("#mg_difficulty", Input)
        description = self.app.query_one("#mg_description", TextArea)
        tiers = [self.app.query_one("#mg_t1", RadioButton),
                self.app.query_one("#mg_t2", RadioButton),
                self.app.query_one("#mg_t3", RadioButton)]

        unvalidated_input: Tuple[Input,...] = (goal_input_data, start_date_input, due_date_input,difficulty_input) 
        if not self.final_input_validation(unvalidated_input):
            return False

        #This validates the tier rodio buttons and 
        #gets the value of the selected one as an int
        selected_tier = None
        for tier  in tiers:
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
                
        node = main_goal_tree.root.add(goal_input_data.value, 
                                       data={"start_date": start_date_input.value,
                                             "due_date": due_date_input.value,
                                             "difficulty": difficulty_input.value,
                                             "tier": selected_tier,
                                             "description": description.text},
                                       )
        self.query_one("#mg_description", TextArea).text = str(node.data)
        return True

        #NOTE could use node var to store in file just in case user exits or wants to finish later
        #the whole node tree and ALL data will be saved and can be easily put back in the tree


    def run_validation_check(self):
        ...

    async def action_next_screen(self):
        """moves user to the next phase of the goal inputing phase"""
        self.page_num += 1
        next_page = self.pages[self.page_num % len(self.pages)]
        await self.app.query(self.page_ids[(self.page_num % len(self.pages)) - 1]).remove() #remove current widget 
        await self.app.query_one("#screen").mount(next_page) # add next widget


    async def action_previous_screen(self) -> None:
        if self.page_num >= 1:
            next_page = self.pages[(self.page_num % len(self.pages)) - 1]
            await self.app.query(self.page_ids[(self.page_num % len(self.pages))]).remove() #remove main_goal_vert
            self.page_num -= 1
            await self.app.query_one("#screen").mount(next_page) # add sub_goal




if __name__ == "__main__":
    app = JourneyApp()
    app.run()


