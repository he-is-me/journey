from ast import Tuple
from ctypes import ArgumentError
from dataclasses import dataclass, field
from enum import Enum
from logging import root
import math
from textual.app import App, ComposeResult
from datetime import  datetime
from textual import on
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical, VerticalGroup
from textual.reactive import reactive
from textual.validation import Integer, Length, ValidationResult, Validator
from textual.widget import Widget
from textual.widgets import Footer, Header, Input , Label,  RadioButton,  Static, TextArea, Tree, Label
from rich.text import Text
from textual.widgets._tree import TreeNode
from typing import Any,Tuple,  Dict, List,  TypedDict

#TODO if i make this node.data accesible in gloabl I need to make sure it changes everywhere else:
# I need to also make sure that if the user decides to update the data it is updated everywhere


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
        """insert a node into the node dict"""
        try:
            if node_type == GoalType.MAIN_GOAL:
                    self.node_dict[main_node_label] = {"node": node}  
            elif node_type == GoalType.SUB_GOAL and sub_node_label != None and task_node_label != None:
                    self.node_dict[main_node_label][sub_node_label] = {"node":node}
            elif sub_node_label != None and task_node_label != None:
                    self.node_dict[main_node_label][sub_node_label][task_node_label] = {"node":node}
            self.last_added_node_type = node_type
            self.last_added_node = node
            self.last_added_main_node = node
            return True
        except Exception as e:
            #TODO log err
            return False


    def insert_node_on_last(self, node: TreeNode, node_type: GoalType):
        if node_type == GoalType.SUB_GOAL and (self.last_added_sub_node != None and
                                               self.last_added_main_node != None):
            
            #PROCEED




        
        
         




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
    
    def insert_on_branch(self, sub_goal_label: str,node_data: dict, task_goal_label: str|None=None):
        if task_goal_label == None:
            last_goal = self.node_manager.last_added_node
            if isinstance(last_goal, TreeNode):
                last_goal.add(label=sub_goal_label, data=node_data)

    def get_last_added_node(self):
        return self.node_manager.last_added_node


    def on_tree_node_selected(self, event: Tree.NodeSelected):
        ...


    def update_node_manager(self):
        self.app.query_one("#mg_description", TextArea).text = "RUNNING REACTIVE UPDATE !"
        ...

    

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
        yield Center(Label(Text("",style="bold underline"),id="sg_title_label"))
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
                Binding("ctrl+a", "add_goal_type", "Add Goal", priority=True),
                ("ctrl+f", "testing_shit", "testing shit")] 

    CSS_PATH = "styling.tcss"

    goal_tree_cls = GoalTree()
    main_goal_page = MainGoalCollection(id="main_goal_page")
    sub_goal_page = SubGoalCollection(id="sub_goal_page")
    page_objects = [MainGoalCollection, SubGoalCollection]
    page_instance = [main_goal_page, sub_goal_page]
    page_num = reactive(0)
    current_page_object = MainGoalCollection
    current_page_instance  = main_goal_page


    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
                self.goal_tree_cls,
                self.main_goal_page 
                , id="screen")

        yield Footer()


    
    def watch_page_num(self):
        self.current_page_object = self.page_objects[self.page_num]
        self.current_page_instance = self.page_instance[self.page_num]




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
            


        for i in text_area_data:
            text_area_name = str(i.id).removeprefix(id_prefix)
            if i.text.strip() == "":
                break
            else:
                complete_data[text_area_name] = i.text

        complete_data["tier"] = selected_tier #tier gets input last so it follows DOM order like everything else
        # a shitty way of checking which page is up to insert new branch or on branch need to change later to something more robust
        if "mg" in str(input_data[0].id): 
            self.query_one(GoalTree).insert_new_branch(complete_data['goal_input'], node_data=complete_data)
        elif "sg" in str(input_data[0].id):
            self.query_one(GoalTree).insert_on_branch(complete_data['goal_input'], node_data=complete_data)

        #DEBUG 
        self.app.query_one(f"#{id_prefix}description", TextArea).text = str(self.app.query_one(GoalTree).node_manager.get_node_dict)




    #
    # def add_main_goal_action(self) -> bool:
    #     """controls adding main goal to goal tree"""
    #     # self.add_goal_action()
    #     goal_tree = self.app.query_one("#goal_tree", Tree)
    #     goal_input_data = self.app.query_one("#mg_goal_input", Input)
    #     start_date_input = self.app.query_one("#mg_start_date", Input)
    #     due_date_input = self.app.query_one("#mg_due_date", Input)
    #     difficulty_input = self.app.query_one("#mg_difficulty", Input)
    #     description = self.app.query_one("#mg_description", TextArea)
    #     tiers = [self.app.query_one("#mg_t1", RadioButton),
    #             self.app.query_one("#mg_t2", RadioButton),
    #             self.app.query_one("#mg_t3", RadioButton)]
    #
    #
    #         self.app.query_one("#mg_description", TextArea).text = "VALIDATION HAPPENED BUT FAILED"
    #         return False
    #     self.app.query_one("#mg_description", TextArea).text = "IT VALIDATED"
    #
    #     #This validates the tier rodio buttons and 
    #     #gets the value of the selected one as an int
    #     selected_tier = None
    #     for tier  in tiers:
    #         if tier.value == True:
    #             selected_tier = tier.label
    #             if "1" in str(selected_tier):
    #                 selected_tier = 1
    #             elif "2" in str(selected_tier):
    #                 selected_tier = 2
    #             else:
    #                 selected_tier = 3
    #     if selected_tier == None: 
    #         self.query_one(Notification).send_message(Text("Tier Not Selected !"),level=NotificationLevel.ERROR)
    #         return False
    #
    #     self.app.query_one("#mg_description", TextArea).text = str("FUCK MEEEEE")            
    #     node = goal_tree.root.add(goal_input_data.value, 
    #                                    data={"start_date": start_date_input.value,
    #                                          "due_date": due_date_input.value,
    #                                          "difficulty": difficulty_input.value,
    #                                          "tier": selected_tier,
    #                                          "description": description.text
    #                                          }
    #                                    )
    #
    #     # self.query_one("#mg_description", TextArea).text = str(node.data)
    #     return True
    #
    #     #NOTE could use node var to store in file just in case user exits or wants to finish later
    #     #the whole node tree and ALL data will be saved and can be easily put back in the tree
    #
    #
    def run_validation_check(self):
        ...

    async def action_next_screen(self):
        """moves user to the next phase of the goal inputing phase"""
        self.page_num += 1
        next_page = self.page_instance[self.page_num % len(self.page_instance)]
        await self.app.query(self.page_objects[(self.page_num % len(self.page_instance)) - 1]).remove() #remove current widget 
        await self.app.query_one("#screen").mount(next_page) # add next widget

    async def action_testing_shit(self):
        self.app.query_one("#sg_description_textbox", TextArea).text = str(self.current_page_object) + " " + str(self.page_num)

    async def action_previous_screen(self) -> None:
        if self.page_num >= 1:
            await self.app.query(self.page_objects[(self.page_num % len(self.page_instance))]).remove() #remove current widget
            self.page_num -= 1
            await self.app.query_one("#screen").mount(self.current_page_instance) # add next widget




if __name__ == "__main__":
    app = JourneyApp()
    app.run()


