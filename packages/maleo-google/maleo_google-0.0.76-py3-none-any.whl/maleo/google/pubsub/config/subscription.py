from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar


class SubscriptionConfig(BaseModel):
    id: str = Field(..., description="Subscription's ID")
    max_messages: int = Field(10, description="Subscription's Max messages")
    ack_deadline: int = Field(10, description="Subscription's ACK deadline")


class SubscriptionsConfig(BaseModel):
    pass


SubscriptionsConfigT = TypeVar(
    "SubscriptionsConfigT", bound=Optional[SubscriptionsConfig]
)


class SubscriptionsConfigMixin(BaseModel, Generic[SubscriptionsConfigT]):
    subscriptions: SubscriptionsConfigT = Field(..., description="Subscriptions config")
