# Copyright 2016- Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from abc import abstractmethod
from typing import List, Dict

import gs2_cdk.script

def indent(value: str, size: int) -> str:
    return " " * size + value.replace("\n", "\n" + " " * size).strip(" ")


class Variable:

    def __init__(
            self,
            name: str,
    ):
        self.name = name

    @abstractmethod
    def type_name(self) -> str:
        pass

    def gsl(self):
        output = "{type} {name}".format(
            type=self.type_name(),
            name=self.name,
        )
        return output


class String(Variable):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name,
        )

    def type_name(self) -> str:
        return "string"


class Int(Variable):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name,
        )

    def type_name(self) -> str:
        return "int"


class Float(Variable):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name,
        )

    def type_name(self) -> str:
        return "float"


class Bool(Variable):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name,
        )

    def type_name(self) -> str:
        return "bool"


class Array(Variable):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name,
        )

    def type_name(self) -> str:
        return "array"


class Map(Variable):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name,
        )

    def type_name(self) -> str:
        return "map"


class Event:

    from_task_name: str

    def __init__(
            self,
            name: str,
            arguments: List[Variable],
            next_task_name: str,
    ):
        self.name = name
        self.arguments = arguments
        self.from_task_name = None
        self.next_task_name = next_task_name

    def gsl(self):
        output = ""
        output += "Transition {fromTaskName} handling {eventName} -> {nextTaskName};\n".format(
            fromTaskName=self.from_task_name,
            eventName=self.name,
            nextTaskName=self.next_task_name,
        )
        return output


class ErrorEvent(Event):

    def __init__(
            self,
            next_task_name: str,
    ):
        super().__init__(
            name="Error",
            arguments=[
                String(
                    name="reason",
                ),
            ],
            next_task_name=next_task_name
        )


class BaseTask:

    events: List[Event] = []

    def __init__(
            self,
            name: str,
            arguments: List[Variable],
    ):
        self.name = name
        self.arguments = arguments
        self.events = []

    @abstractmethod
    def gsl(self) -> str:
        pass

    @abstractmethod
    def mermaid(self) -> str:
        pass


class Result:

    def __init__(
            self,
            result_name: str,
            emit_event_name: str,
            emit_event_argument_variable_names: Dict[Variable, str],
    ):
        self.result_name = result_name
        self.emit_event_name = emit_event_name
        self.emit_event_argument_variable_names = emit_event_argument_variable_names


class Script:

    def __init__(
            self,
            name: str,
            payload: str,
    ):
        self.name = name
        self.payload = payload


class Task(BaseTask):

    results = []

    def __init__(
            self,
            name: str,
            arguments: List[Variable],
            script: str,
    ):
        super().__init__(
            name=name,
            arguments=arguments,
        )
        self.script = script
        self.results = []

    def transition(
            self,
            event: Event,
    ) -> 'Task':
        event.from_task_name = self.name
        self.events.append(event)
        return self

    def result(
            self,
            result_name: str,
            emit_event_argument_variable_names: Dict[Variable, str],
            next_task_name: str,
    ):
        self.results.append(
            Result(
                result_name=result_name,
                emit_event_name=result_name,
                emit_event_argument_variable_names=emit_event_argument_variable_names,
            )
        )
        self.transition(Event(
            name=result_name,
            arguments=[
                k
                for k, v in emit_event_argument_variable_names.items()
            ],
            next_task_name=next_task_name,
        ))
        return self

    def script_payload(self) -> Script:
        output = self.script
        output += "\n\n"
        for result in self.results:
            output += "if result == '{result_name}' then\n".format(
                result_name=result.result_name,
            )
            output += indent("""result = {{
    event='{emit_event_name}',
    params={{{param_names}}},
    updatedVariables=args.variables
}}
            """, 2).format(
                emit_event_name=result.emit_event_name,
                param_names=", ".join([
                    "{argument_name}={variable_name}".format(
                        argument_name=argument.name,
                        variable_name=variable_name,
                    )
                    for argument, variable_name in result.emit_event_argument_variable_names.items()
                ])
            )
            output += "end\n"
        return Script(
            name=self.name,
            payload=output,
        )

    def gsl(self):
        output = ""
        output += "Task {name}({arguments}) {{\n".format(
            name=self.name,
            arguments=", ".join(
                [
                    argument.gsl()
                    for argument in self.arguments
                ]
            ),
        )

        for event in self.events:
            output += indent("Event {event}({arguments});\n".format(
                event=event.name,
                arguments=", ".join(
                    [
                        argument.gsl()
                        for argument in event.arguments
                    ]
                ),
            ), 2)

        output += indent("Script grn:gs2:{{region}}:{{ownerId}}:script:{{scriptNamespaceName}}:script:{{stateMachineName}}_{taskName}\n".format(
            taskName=self.name,
        ), 2)

        output += "}\n\n"
        return output

    def mermaid(self):
        output = ""
        for event in self.events:
            if event.next_task_name == "Error":
                continue
            output += "{{stateMachineName}}_{from_task_name}[[{from_task_name}]] -->|{event_name}| {{stateMachineName}}_{next_task_name}\n".format(
                from_task_name=event.from_task_name,
                event_name=event.name,
                next_task_name=event.next_task_name,
            )
        return output


class InParam:
    def __init__(
            self,
            current_state_machine_variable: Variable,
            sub_state_machine_variable: Variable,
    ):
        self.current_state_machine_variable = current_state_machine_variable
        self.sub_state_machine_variable = sub_state_machine_variable


class OutParam:
    def __init__(
            self,
            sub_state_machine_variable: Variable,
            current_state_machine_variable: Variable,
    ):
        self.sub_state_machine_variable = sub_state_machine_variable
        self.current_state_machine_variable = current_state_machine_variable


class SubStateMachineTask(BaseTask):

    def __init__(
            self,
            name: str,
            sub_state_machine_name: str,
            in_params: List[InParam],
            out_params: List[OutParam],
    ):
        super().__init__(
            name=name,
            arguments=[],
        )
        self.sub_state_machine_name = sub_state_machine_name
        self.in_params = in_params
        self.out_params = out_params

    def transition(
            self,
            event: Event,
    ) -> 'SubStateMachineTask':
        event.from_task_name = self.name
        self.events.append(event)
        return self

    def gsl(self):
        output = ""
        output += "SubStateMachineTask {name} {{\n".format(
            name=self.name,
        )

        output += indent("using {subStateMachineName};\n".format(
            subStateMachineName=self.name,
        ), 2)

        output += indent("in (" + ", ".join([
            in_param.sub_state_machine_variable.name + " <- " + in_param.current_state_machine_variable.name
            for in_param in self.in_params
        ]) + ");\n", 2)

        output += indent("out (" + ", ".join([
            out_param.sub_state_machine_variable.name + " -> " + out_param.current_state_machine_variable.name
            for out_param in self.out_params
        ]) + ");\n", 2)

        output += "}\n\n"
        return output

    def mermaid(self):
        output = ""
        output += "{{stateMachineName}}_{name}[/{name}/]\n".format(
            name=self.name,
        )
        return output


class WaitTask(BaseTask):

    results = []

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name=name,
            arguments=[],
        )

    def transition(
            self,
            event: Event,
    ) -> 'WaitTask':
        event.from_task_name = self.name
        self.events.append(event)
        return self

    def result(
            self,
            result_name: str,
            emit_event_argument_variable_names: Dict[Variable, str],
            next_task_name: str,
    ):
        self.results.append(
            Result(
                result_name=result_name,
                emit_event_name=result_name,
                emit_event_argument_variable_names=emit_event_argument_variable_names,
            )
        )
        self.transition(Event(
            name=result_name,
            arguments=[
                k
                for k, v in emit_event_argument_variable_names.items()
            ],
            next_task_name=next_task_name,
        ))
        return self

    def gsl(self):
        output = ""
        output += "WaitTask {name} {{\n".format(
            name=self.name,
        )

        for event in self.events:
            output += indent("Event {event}({arguments});\n".format(
                event=event.name,
                arguments=", ".join(
                    [
                        argument.gsl()
                        for argument in event.arguments
                    ]
                ),
                next=event.next_task_name,
            ), 2)

        output += "}\n\n"
        return output

    def mermaid(self):
        output = ""
        for event in self.events:
            if event.next_task_name == "Error":
                continue
            output += "{{stateMachineName}}_{from_task_name}([{from_task_name}]) -->|{event_name}| {{stateMachineName}}_{next_task_name}\n".format(
                from_task_name=event.from_task_name,
                event_name=event.name,
                next_task_name=event.next_task_name,
            )
        return output


class PassTask(BaseTask):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name=name,
            arguments=[],
        )

    def gsl(self):
        return "PassTask Pass;\n\n"

    def mermaid(self):
        output = ""
        output += "{{stateMachineName}}_{name}[\\{name}/]\n".format(
            name=self.name,
        )
        return output


class ErrorTask(BaseTask):

    def __init__(
            self,
            name: str,
    ):
        super().__init__(
            name=name,
            arguments=[
                String(
                    name="reason",
                ),
            ],
        )

    def gsl(self):
        return "ErrorTask {name}(string reason);\n\n".format(name=self.name)

    def mermaid(self):
        return ""


class StateMachine:

    def __init__(
            self,
            state_machine_definition: 'StateMachineDefinition',
            name: str,
            variables: List[Variable],
    ):
        self.name = name
        self.variables = variables
        self.tasks = []
        self.entry_point_value = None
        state_machine_definition.add(self)

    def task(
            self,
            *args,
    ) -> 'StateMachine':
        if isinstance(args, list) or isinstance(args, tuple):
            self.tasks.extend(list(args))
        else:
            self.tasks.append(args)
        return self

    def entry_point(
            self,
            task_name: str,
    ) -> 'StateMachine':
        self.entry_point_value = task_name
        return self

    def scripts(self):
        scripts = []
        for task in self.tasks:
            if isinstance(task, Task):
                script = task.script_payload()
                script.name = self.name + "_" + script.name
                scripts.append(script)
        return scripts

    def gsl(self):
        output = "StateMachine {name} {{\n".format(name=self.name)

        variables = ""
        if self.variables:
            variables += "Variables {\n"
        for variable in self.variables:
            variables += indent(variable.gsl() + ";\n", 2)
        if self.variables:
            variables += "}\n\n"

        output += indent(variables, 2)

        if self.entry_point_value:
            output += "  EntryPoint {entry_point};\n\n".format(
                entry_point=self.entry_point_value,
            )

        for task in self.tasks:
            output += indent(task.gsl(), 2)

        for task in self.tasks:
            for event in task.events:
                output += indent(event.gsl(), 2)

        output += "}\n"

        output = output.replace("{stateMachineName}", self.name)

        return output

    def mermaid(self):
        output = "subgraph {name}\n".format(name=self.name)
        for task in self.tasks:
            output += indent(task.mermaid(), 2)
            output += "\n"
        output += "end\n"

        for task in self.tasks:
            if isinstance(task, SubStateMachineTask):
                output += "\n"
                output += "{{stateMachineName}}_{taskName} --> {subStateMachineName}_{{{subStateMachineName}_entryPoint}}\n".format(
                    taskName=task.name,
                    subStateMachineName=task.sub_state_machine_name,
                )
                output += "{subStateMachineName}_Pass -->|Pass| {{stateMachineName}}_{nextTaskName}\n".format(
                    subStateMachineName=task.sub_state_machine_name,
                    nextTaskName=task.events[0].next_task_name,
                )
            if isinstance(task, WaitTask):
                output += "\n"
                output += "Player ----->|Interaction| {{stateMachineName}}_{taskName}\n".format(
                    taskName=task.name,
                )

        output = output.replace("{stateMachineName}", self.name)

        return output


class StateMachineDefinition:

    state_machine_name: str = ""
    state_machines: List[StateMachine] = []

    def add(
            self,
            state_machine: StateMachine,
    ):
        self.state_machines.append(state_machine)

    def entry_point_state_machine_name(
            self,
            state_machine_name: str,
    ):
        self.state_machine_name = state_machine_name

    def state_machine(
            self,
            name: str,
            variables: List[Variable],
    ) -> StateMachine:
        return StateMachine(
            state_machine_definition=self,
            name=name,
            variables=variables,
        )

    def script_task(
            self,
            name: str,
            arguments: List[Variable],
            script: str,
    ) -> Task:
        return Task(
            name=name,
            arguments=arguments,
            script=script,
        )

    def sub_state_machine_task(
            self,
            name: str,
            sub_state_machine_name: str,
            in_params: List[InParam],
            out_params: List[OutParam],
            next_task_name: str,
    ) -> SubStateMachineTask:
        return SubStateMachineTask(
            name=sub_state_machine_name,
            sub_state_machine_name=sub_state_machine_name,
            in_params=in_params,
            out_params=out_params,
        ).transition(
            Event(
                name="Pass",
                arguments=[
                    out_param.sub_state_machine_variable
                    for out_param in out_params
                ],
                next_task_name=next_task_name,
            )
        )

    def in_param(
            self,
            current_state_machine_variable: Variable,
            sub_state_machine_variable: Variable,
    ) -> InParam:
        return InParam(
            current_state_machine_variable,
            sub_state_machine_variable,
        )

    def out_param(
            self,
            sub_state_machine_variable: Variable,
            current_state_machine_variable: Variable,
    ) -> OutParam:
        return OutParam(
            sub_state_machine_variable,
            current_state_machine_variable,
        )

    def wait_task(
            self,
            name: str,
    ) -> WaitTask:
        return WaitTask(
            name=name,
        )

    def pass_task(
            self,
            name: str,
    ) -> PassTask:
        return PassTask(
            name=name,
        )

    def error_task(
            self,
            name: str,
    ) -> ErrorTask:
        return ErrorTask(
            name=name,
        )

    def result(
            self,
            name: str,
            event_name: str,
            event_argument_variable_names: Dict[Variable, str],
    ) -> Result:
        return Result(
            result_name=name,
            emit_event_name=event_name,
            emit_event_argument_variable_names=event_argument_variable_names,
        )

    def string_type(
            self,
            name: str,
    ) -> String:
        return String(
            name=name,
        )

    def int_type(
            self,
            name: str,
    ) -> Int:
        return Int(
            name=name,
        )

    def float_type(
            self,
            name: str,
    ) -> Float:
        return Float(
            name=name,
        )

    def bool_type(
            self,
            name: str,
    ) -> Bool:
        return Bool(
            name=name,
        )

    def array_type(
            self,
            name: str,
    ) -> Array:
        return Array(
            name=name,
        )

    def map_type(
            self,
            name: str,
    ) -> Map:
        return Map(
            name=name,
        )

    def append_scripts(
            self,
            stack: "gs2_cdk.Stack",
            script_namespace: gs2_cdk.script.Namespace,
    ) -> List["gs2_cdk.script.Script"]:
        scripts = []
        for state_machines in self.state_machines:
            for script in state_machines.scripts():
                deploy_script = gs2_cdk.script.Script(
                    stack=stack,
                    namespace_name=script_namespace.name,
                    name=script.name,
                    script=script.payload.strip(),
                )
                deploy_script.add_depends_on(script_namespace)
                scripts.append(deploy_script)
        return scripts

    def gsl(self):
        output = ""
        for state_machine in self.state_machines:
            output += state_machine.gsl()
            output += "\n"
        return output

    def mermaid(self):
        output = "flowchart TD\n"

        output += indent("Start ----> {stateMachineName}_{entryPoint}\n".format(
            stateMachineName=self.state_machines[0].name,
            entryPoint=self.state_machines[0].entry_point_value,
        ), 2)

        output += indent("{stateMachineName}_Pass ----> Exit\n".format(
            stateMachineName=self.state_machines[0].name,
        ), 2)

        for state_machine in self.state_machines:
            output += indent(state_machine.mermaid(), 2)
            output += "\n"

        for state_machine in self.state_machines:
            output = output.replace("{" + state_machine.name + "_entryPoint}", state_machine.entry_point_value)
        return output
