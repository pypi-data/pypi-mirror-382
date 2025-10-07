ALLOW_CERTIFICATE_PUSHING = False
MORANGO_SERIALIZE_BEFORE_QUEUING = True
MORANGO_DESERIALIZE_AFTER_DEQUEUING = True
MORANGO_DISALLOW_ASYNC_OPERATIONS = False
MORANGO_DISABLE_FSIC_V2_FORMAT = False
MORANGO_DISABLE_FSIC_REDUCTION = False
MORANGO_INSTANCE_INFO = {}
MORANGO_INITIALIZE_OPERATIONS = (
    "morango.sync.operations:InitializeOperation",
    "morango.sync.operations:LegacyNetworkInitializeOperation",
    "morango.sync.operations:NetworkInitializeOperation",
)
MORANGO_SERIALIZE_OPERATIONS = (
    "morango.sync.operations:SerializeOperation",
    "morango.sync.operations:LegacyNetworkSerializeOperation",
    "morango.sync.operations:NetworkSerializeOperation",
)
MORANGO_QUEUE_OPERATIONS = (
    "morango.sync.operations:ProducerQueueOperation",
    "morango.sync.operations:ReceiverQueueOperation",
    "morango.sync.operations:LegacyNetworkQueueOperation",
    "morango.sync.operations:NetworkQueueOperation",
)
MORANGO_TRANSFERRING_OPERATIONS = (
    "morango.sync.operations:PullProducerOperation",
    "morango.sync.operations:PushProducerOperation",
    "morango.sync.operations:PushReceiverOperation",
    "morango.sync.operations:PullReceiverOperation",
    "morango.sync.operations:NetworkPushTransferOperation",
    "morango.sync.operations:NetworkPullTransferOperation",
)
MORANGO_DEQUEUE_OPERATIONS = (
    "morango.sync.operations:ProducerDequeueOperation",
    "morango.sync.operations:ReceiverDequeueOperation",
    "morango.sync.operations:LegacyNetworkDequeueOperation",
    "morango.sync.operations:NetworkDequeueOperation",
)
MORANGO_DESERIALIZE_OPERATIONS = (
    "morango.sync.operations:ProducerDeserializeOperation",
    "morango.sync.operations:ReceiverDeserializeOperation",
    "morango.sync.operations:LegacyNetworkDeserializeOperation",
    "morango.sync.operations:NetworkDeserializeOperation",
)
MORANGO_CLEANUP_OPERATIONS = (
    "morango.sync.operations:CleanupOperation",
    "morango.sync.operations:NetworkCleanupOperation",
)
MORANGO_TEST_POSTGRESQL = False
