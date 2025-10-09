"""Scada implementation"""

import typing
from typing import Any

from gwproto import HardwareLayout, Message
from gwproto.messages import EventBase
from result import Ok, Result

from gwproactor import App, AppSettings
from gwproactor.actors.actor import PrimeActor
from gwproactor.config import MQTTClient
from gwproactor.config.links import LinkSettings
from gwproactor.config.proactor_config import ProactorName
from gwproactor.message import DBGPayload, MQTTReceiptPayload
from gwproactor.persister import (
    PersisterInterface,
    TimedRollingFilePersister,
)
from gwproactor_test.dummies import DUMMY_CHILD_NAME, DUMMY_PARENT_NAME


class DummyParent(PrimeActor):
    def process_internal_message(self, message: Message[Any]) -> None:
        self.process_message(message)

    def process_message(self, message: Message[Any]) -> Result[bool, Exception]:
        match message.Payload:
            case DBGPayload():
                message.Header.Src = self.services.publication_name
                dst_client = message.Header.Dst
                message.Header.Dst = ""
                self.services.publish_message(dst_client, message)
        return Ok(True)

    def process_mqtt_message(
        self, mqtt_client_message: Message[MQTTReceiptPayload], decoded: Message[Any]
    ) -> None:
        self.services.logger.path(
            f"++{self.name}.process_mqtt_message %s",
            mqtt_client_message.Payload.message.topic,
        )
        path_dbg = 0
        self.services.stats.add_message(decoded)
        match decoded.Payload:
            case EventBase():
                path_dbg |= 0x00000001
                self.services.generate_event(decoded.Payload)
            case _:
                path_dbg |= 0x00000002
        self.services.logger.path(
            f"--{self.name}.process_mqtt_message  path:0x%08X", path_dbg
        )


class DummyParentSettings(AppSettings):
    child: MQTTClient = MQTTClient()


class DummyParentApp(App):
    CHILD_MQTT: str = DUMMY_CHILD_NAME

    @classmethod
    def app_settings_type(cls) -> type[DummyParentSettings]:
        return DummyParentSettings

    @classmethod
    def prime_actor_type(cls) -> type[DummyParent]:
        return DummyParent

    @property
    def prime_actor(self) -> DummyParent:
        return typing.cast(DummyParent, self._prime_actor)

    @classmethod
    def paths_name(cls) -> str:
        return DUMMY_PARENT_NAME

    def _get_name(self, layout: HardwareLayout) -> ProactorName:
        return ProactorName(
            long_name=layout.atn_g_node_alias,
            short_name="a",
        )

    def _get_link_settings(
        self,
        name: ProactorName,  # noqa: ARG002
        layout: HardwareLayout,
        brokers: dict[str, MQTTClient],  # noqa: ARG002
    ) -> dict[str, LinkSettings]:
        return {
            self.CHILD_MQTT: LinkSettings(
                broker_name=self.CHILD_MQTT,
                peer_long_name=layout.scada_g_node_alias,
                peer_short_name="s",
                downstream=True,
            )
        }

    @classmethod
    def _make_persister(cls, settings: AppSettings) -> PersisterInterface:
        return TimedRollingFilePersister(settings.paths.event_dir)
