# Copyright 2016 Game Server Services, Inc. or its affiliates. All Rights
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

from __future__ import annotations

import re
from typing import *
from gs2 import core


class TransactionSetting(core.Gs2Model):
    enable_auto_run: bool = None
    enable_atomic_commit: bool = None
    transaction_use_distributor: bool = None
    commit_script_result_in_use_distributor: bool = None
    acquire_action_use_job_queue: bool = None
    distributor_namespace_id: str = None
    key_id: str = None
    queue_namespace_id: str = None

    def with_enable_auto_run(self, enable_auto_run: bool) -> TransactionSetting:
        self.enable_auto_run = enable_auto_run
        return self

    def with_enable_atomic_commit(self, enable_atomic_commit: bool) -> TransactionSetting:
        self.enable_atomic_commit = enable_atomic_commit
        return self

    def with_transaction_use_distributor(self, transaction_use_distributor: bool) -> TransactionSetting:
        self.transaction_use_distributor = transaction_use_distributor
        return self

    def with_commit_script_result_in_use_distributor(self, commit_script_result_in_use_distributor: bool) -> TransactionSetting:
        self.commit_script_result_in_use_distributor = commit_script_result_in_use_distributor
        return self

    def with_acquire_action_use_job_queue(self, acquire_action_use_job_queue: bool) -> TransactionSetting:
        self.acquire_action_use_job_queue = acquire_action_use_job_queue
        return self

    def with_distributor_namespace_id(self, distributor_namespace_id: str) -> TransactionSetting:
        self.distributor_namespace_id = distributor_namespace_id
        return self

    def with_key_id(self, key_id: str) -> TransactionSetting:
        self.key_id = key_id
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> TransactionSetting:
        self.queue_namespace_id = queue_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TransactionSetting]:
        if data is None:
            return None
        return TransactionSetting()\
            .with_enable_auto_run(data.get('enableAutoRun'))\
            .with_enable_atomic_commit(data.get('enableAtomicCommit'))\
            .with_transaction_use_distributor(data.get('transactionUseDistributor'))\
            .with_commit_script_result_in_use_distributor(data.get('commitScriptResultInUseDistributor'))\
            .with_acquire_action_use_job_queue(data.get('acquireActionUseJobQueue'))\
            .with_distributor_namespace_id(data.get('distributorNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enableAutoRun": self.enable_auto_run,
            "enableAtomicCommit": self.enable_atomic_commit,
            "transactionUseDistributor": self.transaction_use_distributor,
            "commitScriptResultInUseDistributor": self.commit_script_result_in_use_distributor,
            "acquireActionUseJobQueue": self.acquire_action_use_job_queue,
            "distributorNamespaceId": self.distributor_namespace_id,
            "keyId": self.key_id,
            "queueNamespaceId": self.queue_namespace_id,
        }


class LogSetting(core.Gs2Model):
    logging_namespace_id: str = None

    def with_logging_namespace_id(self, logging_namespace_id: str) -> LogSetting:
        self.logging_namespace_id = logging_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[LogSetting]:
        if data is None:
            return None
        return LogSetting()\
            .with_logging_namespace_id(data.get('loggingNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loggingNamespaceId": self.logging_namespace_id,
        }


class DataObjectHistory(core.Gs2Model):
    data_object_history_id: str = None
    data_object_name: str = None
    generation: str = None
    content_length: int = None
    created_at: int = None
    revision: int = None

    def with_data_object_history_id(self, data_object_history_id: str) -> DataObjectHistory:
        self.data_object_history_id = data_object_history_id
        return self

    def with_data_object_name(self, data_object_name: str) -> DataObjectHistory:
        self.data_object_name = data_object_name
        return self

    def with_generation(self, generation: str) -> DataObjectHistory:
        self.generation = generation
        return self

    def with_content_length(self, content_length: int) -> DataObjectHistory:
        self.content_length = content_length
        return self

    def with_created_at(self, created_at: int) -> DataObjectHistory:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> DataObjectHistory:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        data_object_name,
        generation,
    ):
        return 'grn:gs2:{region}:{ownerId}:datastore:{namespaceName}:user:{userId}:data:{dataObjectName}:history:{generation}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            dataObjectName=data_object_name,
            generation=generation,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+):history:(?P<generation>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+):history:(?P<generation>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+):history:(?P<generation>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+):history:(?P<generation>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_data_object_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+):history:(?P<generation>.+)', grn)
        if match is None:
            return None
        return match.group('data_object_name')

    @classmethod
    def get_generation_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+):history:(?P<generation>.+)', grn)
        if match is None:
            return None
        return match.group('generation')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DataObjectHistory]:
        if data is None:
            return None
        return DataObjectHistory()\
            .with_data_object_history_id(data.get('dataObjectHistoryId'))\
            .with_data_object_name(data.get('dataObjectName'))\
            .with_generation(data.get('generation'))\
            .with_content_length(data.get('contentLength'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataObjectHistoryId": self.data_object_history_id,
            "dataObjectName": self.data_object_name,
            "generation": self.generation,
            "contentLength": self.content_length,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class DataObject(core.Gs2Model):
    data_object_id: str = None
    name: str = None
    user_id: str = None
    scope: str = None
    allow_user_ids: List[str] = None
    status: str = None
    generation: str = None
    previous_generation: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_data_object_id(self, data_object_id: str) -> DataObject:
        self.data_object_id = data_object_id
        return self

    def with_name(self, name: str) -> DataObject:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> DataObject:
        self.user_id = user_id
        return self

    def with_scope(self, scope: str) -> DataObject:
        self.scope = scope
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> DataObject:
        self.allow_user_ids = allow_user_ids
        return self

    def with_status(self, status: str) -> DataObject:
        self.status = status
        return self

    def with_generation(self, generation: str) -> DataObject:
        self.generation = generation
        return self

    def with_previous_generation(self, previous_generation: str) -> DataObject:
        self.previous_generation = previous_generation
        return self

    def with_created_at(self, created_at: int) -> DataObject:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> DataObject:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> DataObject:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        data_object_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:datastore:{namespaceName}:user:{userId}:data:{dataObjectName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            dataObjectName=data_object_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_data_object_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+):user:(?P<userId>.+):data:(?P<dataObjectName>.+)', grn)
        if match is None:
            return None
        return match.group('data_object_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DataObject]:
        if data is None:
            return None
        return DataObject()\
            .with_data_object_id(data.get('dataObjectId'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_scope(data.get('scope'))\
            .with_allow_user_ids(None if data.get('allowUserIds') is None else [
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')))
            ])\
            .with_status(data.get('status'))\
            .with_generation(data.get('generation'))\
            .with_previous_generation(data.get('previousGeneration'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataObjectId": self.data_object_id,
            "name": self.name,
            "userId": self.user_id,
            "scope": self.scope,
            "allowUserIds": None if self.allow_user_ids is None else [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids))
            ],
            "status": self.status,
            "generation": self.generation,
            "previousGeneration": self.previous_generation,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class ScriptSetting(core.Gs2Model):
    trigger_script_id: str = None
    done_trigger_target_type: str = None
    done_trigger_script_id: str = None
    done_trigger_queue_namespace_id: str = None

    def with_trigger_script_id(self, trigger_script_id: str) -> ScriptSetting:
        self.trigger_script_id = trigger_script_id
        return self

    def with_done_trigger_target_type(self, done_trigger_target_type: str) -> ScriptSetting:
        self.done_trigger_target_type = done_trigger_target_type
        return self

    def with_done_trigger_script_id(self, done_trigger_script_id: str) -> ScriptSetting:
        self.done_trigger_script_id = done_trigger_script_id
        return self

    def with_done_trigger_queue_namespace_id(self, done_trigger_queue_namespace_id: str) -> ScriptSetting:
        self.done_trigger_queue_namespace_id = done_trigger_queue_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ScriptSetting]:
        if data is None:
            return None
        return ScriptSetting()\
            .with_trigger_script_id(data.get('triggerScriptId'))\
            .with_done_trigger_target_type(data.get('doneTriggerTargetType'))\
            .with_done_trigger_script_id(data.get('doneTriggerScriptId'))\
            .with_done_trigger_queue_namespace_id(data.get('doneTriggerQueueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggerScriptId": self.trigger_script_id,
            "doneTriggerTargetType": self.done_trigger_target_type,
            "doneTriggerScriptId": self.done_trigger_script_id,
            "doneTriggerQueueNamespaceId": self.done_trigger_queue_namespace_id,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    done_upload_script: ScriptSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_done_upload_script(self, done_upload_script: ScriptSetting) -> Namespace:
        self.done_upload_script = done_upload_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> Namespace:
        self.log_setting = log_setting
        return self

    def with_created_at(self, created_at: int) -> Namespace:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Namespace:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Namespace:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:datastore:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):datastore:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Namespace]:
        if data is None:
            return None
        return Namespace()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_done_upload_script(ScriptSetting.from_dict(data.get('doneUploadScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "doneUploadScript": self.done_upload_script.to_dict() if self.done_upload_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }