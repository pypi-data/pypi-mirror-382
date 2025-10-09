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


class SendNotificationEntry(core.Gs2Model):
    user_id: str = None
    issuer: str = None
    subject: str = None
    payload: str = None
    enable_transfer_mobile_notification: bool = None
    sound: str = None

    def with_user_id(self, user_id: str) -> SendNotificationEntry:
        self.user_id = user_id
        return self

    def with_issuer(self, issuer: str) -> SendNotificationEntry:
        self.issuer = issuer
        return self

    def with_subject(self, subject: str) -> SendNotificationEntry:
        self.subject = subject
        return self

    def with_payload(self, payload: str) -> SendNotificationEntry:
        self.payload = payload
        return self

    def with_enable_transfer_mobile_notification(self, enable_transfer_mobile_notification: bool) -> SendNotificationEntry:
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        return self

    def with_sound(self, sound: str) -> SendNotificationEntry:
        self.sound = sound
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
    ) -> Optional[SendNotificationEntry]:
        if data is None:
            return None
        return SendNotificationEntry()\
            .with_user_id(data.get('userId'))\
            .with_issuer(data.get('issuer'))\
            .with_subject(data.get('subject'))\
            .with_payload(data.get('payload'))\
            .with_enable_transfer_mobile_notification(data.get('enableTransferMobileNotification'))\
            .with_sound(data.get('sound'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "issuer": self.issuer,
            "subject": self.subject,
            "payload": self.payload,
            "enableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "sound": self.sound,
        }


class FirebaseToken(core.Gs2Model):
    firebase_token_id: str = None
    user_id: str = None
    token: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_firebase_token_id(self, firebase_token_id: str) -> FirebaseToken:
        self.firebase_token_id = firebase_token_id
        return self

    def with_user_id(self, user_id: str) -> FirebaseToken:
        self.user_id = user_id
        return self

    def with_token(self, token: str) -> FirebaseToken:
        self.token = token
        return self

    def with_created_at(self, created_at: int) -> FirebaseToken:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> FirebaseToken:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> FirebaseToken:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:gateway:{namespaceName}:user:{userId}:firebase:token'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('user_id')

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
    ) -> Optional[FirebaseToken]:
        if data is None:
            return None
        return FirebaseToken()\
            .with_firebase_token_id(data.get('firebaseTokenId'))\
            .with_user_id(data.get('userId'))\
            .with_token(data.get('token'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "firebaseTokenId": self.firebase_token_id,
            "userId": self.user_id,
            "token": self.token,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class WebSocketSession(core.Gs2Model):
    web_socket_session_id: str = None
    connection_id: str = None
    namespace_name: str = None
    user_id: str = None
    session_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_web_socket_session_id(self, web_socket_session_id: str) -> WebSocketSession:
        self.web_socket_session_id = web_socket_session_id
        return self

    def with_connection_id(self, connection_id: str) -> WebSocketSession:
        self.connection_id = connection_id
        return self

    def with_namespace_name(self, namespace_name: str) -> WebSocketSession:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> WebSocketSession:
        self.user_id = user_id
        return self

    def with_session_id(self, session_id: str) -> WebSocketSession:
        self.session_id = session_id
        return self

    def with_created_at(self, created_at: int) -> WebSocketSession:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> WebSocketSession:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> WebSocketSession:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        connection_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:gateway:{namespaceName}:user:{userId}:session:{connectionId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            connectionId=connection_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_connection_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('connection_id')

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
    ) -> Optional[WebSocketSession]:
        if data is None:
            return None
        return WebSocketSession()\
            .with_web_socket_session_id(data.get('webSocketSessionId'))\
            .with_connection_id(data.get('connectionId'))\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_session_id(data.get('sessionId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "webSocketSessionId": self.web_socket_session_id,
            "connectionId": self.connection_id,
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "sessionId": self.session_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    firebase_secret: str = None
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

    def with_firebase_secret(self, firebase_secret: str) -> Namespace:
        self.firebase_secret = firebase_secret
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
        return 'grn:gs2:{region}:{ownerId}:gateway:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+)', grn)
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
            .with_firebase_secret(data.get('firebaseSecret'))\
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
            "firebaseSecret": self.firebase_secret,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }