from dataclasses import dataclass
from rid_lib.ext import Cache
from koi_net.behaviors import Behaviors
from koi_net.config import NodeConfig
from koi_net.context import ActionContext, HandlerContext
from koi_net.effector import Effector
from koi_net.handshaker import Handshaker
from koi_net.identity import NodeIdentity
from koi_net.kobj_worker import KnowledgeProcessingWorker
from koi_net.lifecycle import NodeLifecycle
from koi_net.network.error_handler import ErrorHandler
from koi_net.network.event_queue import EventQueue
from koi_net.network.graph import NetworkGraph
from koi_net.network.request_handler import RequestHandler
from koi_net.network.resolver import NetworkResolver
from koi_net.network.response_handler import ResponseHandler
from koi_net.poll_event_buffer import PollEventBuffer
from koi_net.poller import NodePoller
from koi_net.processor.default_handlers import (
    basic_manifest_handler, 
    basic_network_output_filter, 
    basic_rid_handler, 
    node_contact_handler, 
    edge_negotiation_handler, 
    forget_edge_on_node_deletion, 
    secure_profile_handler
)
from koi_net.processor.event_worker import EventProcessingWorker
from koi_net.processor.knowledge_pipeline import KnowledgePipeline
from koi_net.processor.kobj_queue import KobjQueue
from koi_net.secure import Secure
from koi_net.server import NodeServer


@dataclass
class NodeContainer:
    poll_event_buf: PollEventBuffer
    kobj_queue: KobjQueue
    event_queue: EventQueue
    config: NodeConfig
    cache: Cache
    identity: NodeIdentity
    graph: NetworkGraph
    secure: Secure
    request_handler: RequestHandler
    response_handler: ResponseHandler
    resolver: NetworkResolver
    handler_context: HandlerContext
    behaviors: Behaviors
    pipeline: KnowledgePipeline
    kobj_worker: KnowledgeProcessingWorker
    event_worker: EventProcessingWorker
    error_handler: ErrorHandler
    lifecycle: NodeLifecycle
    server: NodeServer
    poller: NodePoller
    

class NodeAssembler:
    poll_event_buf = PollEventBuffer
    kobj_queue = KobjQueue
    event_queue = EventQueue
    config = NodeConfig
    cache = Cache
    identity = NodeIdentity
    graph = NetworkGraph
    secure = Secure
    handshaker = Handshaker
    request_handler = RequestHandler
    response_handler = ResponseHandler
    resolver = NetworkResolver
    knowledge_handlers = [
        basic_rid_handler,
        basic_manifest_handler,
        secure_profile_handler,
        edge_negotiation_handler,
        node_contact_handler,
        basic_network_output_filter,
        forget_edge_on_node_deletion
    ]
    handler_context = HandlerContext
    action_context = ActionContext
    effector = Effector
    behaviors = Behaviors
    pipeline = KnowledgePipeline
    kobj_worker = KnowledgeProcessingWorker
    event_worker = EventProcessingWorker
    error_handler = ErrorHandler
    lifecycle = NodeLifecycle
    server = NodeServer
    poller = NodePoller
    
    @classmethod
    def create(cls) -> NodeContainer:
        poll_event_buffer = cls.poll_event_buf()
        kobj_queue = cls.kobj_queue()
        event_queue = cls.event_queue()
        config = cls.config.load_from_yaml()
        cache = cls.cache(
            directory_path=config.koi_net.cache_directory_path
        )
        identity = cls.identity(
            config=config
        )
        graph = cls.graph(
            cache=cache,
            identity=identity
        )
        secure = cls.secure(
            identity=identity,
            cache=cache,
            config=config
        )
        handshaker = cls.handshaker(
            cache=cache,
            identity=identity,
            event_queue=event_queue
        )
        error_handler = cls.error_handler(
            kobj_queue=kobj_queue,
            handshaker=handshaker
        )
        request_handler = cls.request_handler(
            cache=cache,
            identity=identity,
            secure=secure,
            error_handler=error_handler
        )
        response_handler = cls.response_handler(
            cache=cache
        )
        resolver = cls.resolver(
            config=config,
            cache=cache,
            identity=identity,
            graph=graph,
            request_handler=request_handler
        )
        handler_context = cls.handler_context(
            identity=identity,
            config=config,
            cache=cache,
            event_queue=event_queue,
            kobj_queue=kobj_queue,
            graph=graph,
            request_handler=request_handler,
            resolver=resolver
        )
        action_context = cls.action_context(
            identity=identity
        )
        effector = cls.effector(
            cache=cache,
            resolver=resolver,
            kobj_queue=kobj_queue,
            action_context=action_context
        )
        behaviors = cls.behaviors(
            cache=cache,
            identity=identity,
            event_queue=event_queue,
            resolver=resolver,
            request_handler=request_handler,
            kobj_queue=kobj_queue
        )
        pipeline = cls.pipeline(
            handler_context=handler_context,
            cache=cache,
            request_handler=request_handler,
            event_queue=event_queue,
            graph=graph,
            knowledge_handlers=cls.knowledge_handlers
        )
        kobj_worker = cls.kobj_worker(
            kobj_queue=kobj_queue,
            pipeline=pipeline
        )
        event_worker = cls.event_worker(
            config=config,
            cache=cache,
            event_queue=event_queue,
            request_handler=request_handler,
            poll_event_buf=poll_event_buffer
        )
        lifecycle = cls.lifecycle(
            config=config,
            identity=identity,
            graph=graph,
            kobj_queue=kobj_queue,
            kobj_worker=kobj_worker,
            event_queue=event_queue,
            event_worker=event_worker,
            cache=cache,
            handshaker=handshaker,
            behaviors=behaviors
        )
        server = cls.server(
            config=config,
            lifecycle=lifecycle,
            secure=secure,
            kobj_queue=kobj_queue,
            response_handler=response_handler,
            poll_event_buf=poll_event_buffer
        )
        poller = cls.poller(
            kobj_queue=kobj_queue,
            lifecycle=lifecycle,
            resolver=resolver,
            config=config
        )
        
        return NodeContainer(
            poll_event_buf=poll_event_buffer,
            kobj_queue=kobj_queue,
            event_queue=event_queue,
            config=config,
            cache=cache,
            identity=identity,
            graph=graph,
            secure=secure,
            request_handler=request_handler,
            response_handler=response_handler,
            resolver=resolver,
            handler_context=handler_context,
            behaviors=behaviors,
            pipeline=pipeline,
            kobj_worker=kobj_worker,
            event_worker=event_worker,
            error_handler=error_handler,
            lifecycle=lifecycle,
            server=server,
            poller=poller
        )