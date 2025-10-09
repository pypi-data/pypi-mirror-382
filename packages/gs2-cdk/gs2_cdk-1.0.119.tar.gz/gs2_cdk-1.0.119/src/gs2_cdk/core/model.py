from __future__ import annotations
from typing import *
from abc import abstractmethod
from typing import List, Dict, Any

from .func import Func


class CdkResource:

    resource_name: str
    depends_on: List[str] = []

    def __init__(
            self,
            resource_name: str,
    ):
        self.depends_on = []
        self.resource_name = resource_name

    def default_resource_name(self):
        service_name = self.__module__.replace('gs2_cdk.', '').replace('.resource', '')
        return service_name[0].upper() + service_name[1:] + "_" + self.__class__.__name__ + "_" + self.alternate_keys()

    def add_depends_on(
            self,
            resource: CdkResource,
    ):
        self.depends_on.append(resource.resource_name)
        return self

    @abstractmethod
    def resource_type(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def properties(self) -> Dict[str, Any]:
        raise NotImplementedError(self)

    @abstractmethod
    def alternate_keys(self) -> str:
        raise NotImplementedError()

    def template(self) -> Dict[str, Any]:
        return {
            "Type": self.resource_type(),
            "Properties": self.properties(),
            "DependsOn": [
                depend
                for depend in self.depends_on
            ]
        }


class Stack:

    resources: List[CdkResource] = []
    outputs: Dict[str, str] = {}

    def __init__(self):
        self.resources = []
        self.outputs = {}

    def add_resource(
            self,
            resource: CdkResource,
    ):
        self.resources.append(resource)

    def output(
            self,
            name: str,
            path: str,
    ):
        self.outputs[name] = path

    def template(self) -> Dict[str, Any]:
        resources = {}
        for resource in self.resources:
            resources[resource.resource_name] = resource.template()
        outputs = {}
        for k, v in self.outputs.items():
            outputs[k] = v
        return {
            "GS2TemplateFormatVersion": "2019-05-01",
            "Resources": resources,
            "Outputs": outputs,
        }

    def yaml(self) -> str:
        import yaml

        def quoted_presenter(dumper, data):
            if len(data) > 0 and data[0] == '!':
                tag = data[:data.find(' ')]
                value = data[data.find(' ')+1:]
                if value[0] == '[':
                    return dumper.represent_sequence(tag, eval(value))
                else:
                    return dumper.represent_scalar(tag, value)
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)

        def represent_str(dumper, instance):
            import re
            if "\n" in instance:
                instance = re.sub(' +\n| +$', '\n', instance)
                return dumper.represent_scalar('tag:yaml.org,2002:str', instance, style='|')
            else:
                return dumper.represent_scalar('tag:yaml.org,2002:str', instance)

        yaml.add_representer(str, quoted_presenter)
        yaml.add_representer(str, represent_str)

        return yaml.dump(self.template(), indent=2)


class TransactionSettingOptions:

    enable_atomic_commit: Optional[bool]
    transaction_use_distributor: Optional[bool]
    acquire_action_use_job_queue: Optional[bool]
    distributor_namespace_id: Optional[str]
    queue_namespace_id: Optional[str]

    def __init__(
            self,
            enable_atomic_commit: Optional[bool] = None,
            transaction_use_distributor: Optional[bool] = None,
            acquire_action_use_job_queue: Optional[bool] = None,
            distributor_namespace_id: Optional[str] = None,
            queue_namespace_id: Optional[str] = None,
    ):
        self.enable_atomic_commit = enable_atomic_commit
        self.transaction_use_distributor = transaction_use_distributor
        self.acquire_action_use_job_queue = acquire_action_use_job_queue
        self.distributor_namespace_id = distributor_namespace_id
        self.queue_namespace_id = queue_namespace_id


class TransactionSetting:

    enable_atomic_commit: bool
    transaction_use_distributor: bool
    acquire_action_use_job_queue: bool
    distributor_namespace_id: str
    queue_namespace_id: str

    def __init__(
            self,
            options: Optional[TransactionSettingOptions] = TransactionSettingOptions(),
    ):
        self.enable_atomic_commit = options.enable_atomic_commit if options.enable_atomic_commit else False
        self.transaction_use_distributor = options.transaction_use_distributor if options.transaction_use_distributor else False
        self.acquire_action_use_job_queue = options.acquire_action_use_job_queue if options.acquire_action_use_job_queue else False
        self.distributor_namespace_id = options.distributor_namespace_id if options.distributor_namespace_id else None
        self.queue_namespace_id = options.queue_namespace_id if options.queue_namespace_id else None

    def properties(self) -> Dict[str, Any]:
        return {
            "EnableAutoRun": True,
            "EnableAtomicCommit": self.enable_atomic_commit,
            "TransactionUseDistributor": self.transaction_use_distributor,
            "AcquireActionUseJobQueue": self.acquire_action_use_job_queue,
            "DistributorNamespaceId": self.distributor_namespace_id,
            "QueueNamespaceId": self.queue_namespace_id,
        }


class ScriptSetting:

    trigger_script_id: str
    done_trigger_target_type: str
    done_trigger_script_id: str
    done_trigger_queue_namespace_id: str

    def __init__(
            self,
            trigger_script_id: str = None,
            done_trigger_target_type: str = 'none',
            done_trigger_script_id: str = None,
            done_trigger_queue_namespace_id: str = None,
    ):
        self.trigger_script_id = trigger_script_id
        self.done_trigger_target_type = done_trigger_target_type
        self.done_trigger_script_id = done_trigger_script_id
        self.done_trigger_queue_namespace_id = done_trigger_queue_namespace_id

    def properties(self) -> Dict[str, Any]:
        return {
            "TriggerScriptId": self.trigger_script_id,
            "DoneTriggerTargetType": self.done_trigger_target_type,
            "DoneTriggerScriptId": self.done_trigger_script_id,
            "DoneTriggerQueueNamespaceId": self.done_trigger_queue_namespace_id,
        }

class NotificationSettingOptions:

    gateway_namespace_id: Optional[str]
    enable_transfer_mobile_notification: Optional[bool]
    sound: Optional[str]

    def __init__(
            self,
            gateway_namespace_id: Optional[str] = None,
            enable_transfer_mobile_notification: Optional[bool] = False,
            sound: Optional[str] = None,
    ):
        self.gateway_namespace_id = gateway_namespace_id
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        self.sound = sound


class NotificationSetting:

    gateway_namespace_id: str
    enable_transfer_mobile_notification: bool
    sound: str

    def __init__(
            self,
            options: Optional[NotificationSettingOptions] = NotificationSettingOptions(),
    ):
        self.gateway_namespace_id = options.gateway_namespace_id if options.gateway_namespace_id else None
        self.enable_transfer_mobile_notification = options.enable_transfer_mobile_notification if options.enable_transfer_mobile_notification else False
        self.sound = options.sound if options.sound else None

    def properties(self) -> Dict[str, Any]:
        return {
            "GatewayNamespaceId": self.gateway_namespace_id,
            "EnableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "Sound": self.sound,
        }


class LogSetting:

    logging_namespace_id: str

    def __init__(
            self,
            logging_namespace_id: str,
    ):
        self.logging_namespace_id = logging_namespace_id

    def properties(self) -> Dict[str, Any]:
        return {
            "LoggingNamespaceId": self.logging_namespace_id,
        }


class Config:

    key: str
    value: str

    def __init__(
            self,
            key: str,
            value: str,
    ):
        self.key = key
        self.value = value

    def properties(self) -> Dict[str, Any]:
        return {
            "Key": self.key,
            "Value": self.value,
        }


class AcquireAction:

    action: str
    request: Dict[str, Any]

    def __init__(
            self,
            action: str,
            request: Dict[str, Any],
    ):
        self.action = action
        self.request = request

    def properties(self) -> Dict[str, Any]:
        properties = {}
        for k, v in self.request.items():
            properties[k] = v
        return {
            "action": self.action,
            "request": properties,
        }


class ConsumeAction:

    action: str
    request: Dict[str, Any]

    def __init__(
            self,
            action: str,
            request: Dict[str, Any],
    ):
        self.action = action
        self.request = request

    def properties(self) -> Dict[str, Any]:
        properties = {}
        for k, v in self.request.items():
            properties[k] = v
        return {
            "action": self.action,
            "request": properties,
        }


class VerifyAction(ConsumeAction):

    def __init__(
            self,
            action: str,
            request: Dict[str, Any],
    ):
        super().__init__(action, request)
