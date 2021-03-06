from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from spacy import Language
from spacy.tokens import Span

from lib.nlu.intent import ValueType, CalculationType, ValueDomain, MeasurementType
from lib.nlu.intent.intent import Intent, IntentRecognizer
from lib.nlu.slot.slots import Slots, SlotsFiller
from lib.nlu.topic.topic import Topic, TopicRecognizer
from lib.spacy_components.custom_spacy import get_spacy


class MessageValidationCode(Enum):
    """Class representing the result of the validation of a message.
    VALID is for valid messages.
    NO_TIMEFRAME, AMBIGUOUS_TOPIC, UNKNOWN are returned if there is something "wrong" or missing in the user message.
    NO_TOPIC, NO_INTENT, NO_SLOTS, INTENT_MISMATCH, UNSUPPORTED_ACTION are server-side errors.
    """
    # This means that we should be able to query the user intent and return an answer.
    VALID = 1

    # These valication codes will be returned if there are issues or missing information in the user query, but
    # it is not unexpected that it will be returned.
    NO_TIMEFRAME = 3
    AMBIGUOUS_TOPIC = 4
    UNKNOWN = 5

    # These are server-side errors and should in theory never occur.
    NO_TOPIC = 10
    NO_INTENT = 11
    NO_SLOTS = 12
    INTENT_MISMATCH = 13
    UNSUPPORTED_ACTION = 14

    @staticmethod
    def get_valid_codes() -> List[MessageValidationCode]:
        """Returns a list of message validation codes that indicate that the message is valid."""
        return [MessageValidationCode.VALID]

    @staticmethod
    def get_user_query_error_codes() -> List[MessageValidationCode]:
        """Returns a list of message validation codes that indicate that there is an error
        by the user in the query."""
        return [MessageValidationCode.NO_TIMEFRAME, MessageValidationCode.AMBIGUOUS_TOPIC,
                MessageValidationCode.UNKNOWN]

    @staticmethod
    def get_server_side_error_codes() -> List[MessageValidationCode]:
        """Returns a list of message validation codes that indicate that there was a server-side error."""
        return [MessageValidationCode.NO_TOPIC, MessageValidationCode.NO_INTENT,
                MessageValidationCode.NO_SLOTS, MessageValidationCode.INTENT_MISMATCH,
                MessageValidationCode.UNSUPPORTED_ACTION]


@dataclass
class Message:
    """Class representing a message and providing related helper-methods.
    topic: The topic of the message.
    intent: The intent of the message.
    slots: The slots of the message.
    """
    topic: Topic
    intent: Intent
    slots: Slots

    @staticmethod
    def validate_message(msg: Message) -> MessageValidationCode:
        """Validates a message."""
        single_fields_validation: Optional[MessageValidationCode] = Message._validate_single_fields(msg)
        if single_fields_validation:
            return single_fields_validation

        return Message._validate_intent_with_slots(msg)

    @staticmethod
    def _validate_intent_with_slots(msg: Message) -> MessageValidationCode:
        """Validates the slots in combination with the different attributes of the intent."""
        has_date: bool = msg.slots.date is not None

        if msg.intent.value_type == ValueType.NUMBER:
            if msg.intent.calculation_type == CalculationType.RAW_VALUE:
                # We need a timeframe to return a daily number. If there is no location, we default to
                # the whole world.
                if msg.intent.measurement_type == MeasurementType.DAILY:
                    if not has_date:
                        return MessageValidationCode.NO_TIMEFRAME
                    else:
                        return MessageValidationCode.VALID
                # If the location is None, we default to the whole world.
                # If the timeframe is null, we assume that the user is asking for today.
                elif msg.intent.measurement_type == MeasurementType.CUMULATIVE:
                    return MessageValidationCode.VALID
            elif msg.intent.calculation_type == CalculationType.SUM:
                # We need a timeframe to return a daily number. If there is no location, we default to the whole
                # world.
                if msg.intent.measurement_type == MeasurementType.DAILY:
                    if not has_date:
                        return MessageValidationCode.NO_TIMEFRAME
                    else:
                        return MessageValidationCode.VALID
                # We can't possibly want the sum of a cumulative value.
                elif msg.intent.measurement_type == MeasurementType.CUMULATIVE:
                    return MessageValidationCode.INTENT_MISMATCH
            elif msg.intent.calculation_type in [CalculationType.MAXIMUM, CalculationType.MINIMUM]:
                # We can't possibly want the highest/lowest cumulative value if the value type is a number,
                # if we are looking for the day or the location with the highest/lowest cumulative value.
                if msg.intent.measurement_type == MeasurementType.CUMULATIVE:
                    return MessageValidationCode.INTENT_MISMATCH
                # If the timeframe is None, we assume that we are searching for the all-time value. If the location is
                # None, we default to the whole world.
                elif msg.intent.measurement_type == MeasurementType.DAILY:
                    return MessageValidationCode.VALID
        elif msg.intent.value_type == ValueType.DAY:
            # We can only want the maximum/minimum when searching for a day.
            if msg.intent.calculation_type in [CalculationType.SUM, CalculationType.RAW_VALUE]:
                return MessageValidationCode.INTENT_MISMATCH
            elif msg.intent.calculation_type in [CalculationType.MAXIMUM, CalculationType.MINIMUM]:
                if msg.intent.measurement_type in [MeasurementType.DAILY, MeasurementType.CUMULATIVE]:
                    return MessageValidationCode.VALID
        elif msg.intent.value_type == ValueType.LOCATION:
            # We can only want the maximum/minimum when searching for a location.
            if msg.intent.calculation_type in [CalculationType.SUM, CalculationType.RAW_VALUE]:
                return MessageValidationCode.INTENT_MISMATCH
            elif msg.intent.calculation_type in [CalculationType.MAXIMUM, CalculationType.MINIMUM]:
                # We don't have any mandatory slots in this case.
                if msg.intent.measurement_type in [MeasurementType.DAILY, MeasurementType.CUMULATIVE]:
                    return MessageValidationCode.VALID

        return MessageValidationCode.UNSUPPORTED_ACTION

    @staticmethod
    def _validate_single_fields(msg: Message) -> Optional[MessageValidationCode]:
        """Checks whether the different attributes of the message on their own are valid."""
        if msg.topic is None:
            return MessageValidationCode.NO_TOPIC
        if msg.intent is None:
            return MessageValidationCode.NO_INTENT

        if msg.slots is None:
            return MessageValidationCode.NO_SLOTS

        if msg.topic == Topic.UNKNOWN:
            return MessageValidationCode.UNKNOWN
        if msg.topic == Topic.AMBIGUOUS:
            return MessageValidationCode.AMBIGUOUS_TOPIC

        if msg.intent.value_type == ValueType.UNKNOWN:
            return MessageValidationCode.UNKNOWN
        if msg.intent.calculation_type == CalculationType.UNKNOWN:
            return MessageValidationCode.UNKNOWN
        if msg.intent.value_domain == ValueDomain.UNKNOWN:
            return MessageValidationCode.UNKNOWN
        if msg.intent.measurement_type == MeasurementType.UNKNOWN:
            return MessageValidationCode.UNKNOWN


class MessageBuilder:
    """Class that provides a helper methods to recognize the message from a span."""
    def __init__(self):
        self._topic_recognizer: TopicRecognizer = TopicRecognizer()
        self._intent_recognizer: IntentRecognizer = IntentRecognizer()
        self._slots_filler: SlotsFiller = SlotsFiller()

    def create_message(self, span: Span) -> Message:
        """Builds a message based on a span."""
        topic: Topic = self._topic_recognizer.recognize_topic(span)
        intent: Intent = self._intent_recognizer.recognize_intent(span)
        slots: Slots = self._slots_filler.fill_slots(span)

        return Message(topic, intent, slots)
