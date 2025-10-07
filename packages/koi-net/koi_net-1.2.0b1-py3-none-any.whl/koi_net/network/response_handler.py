import logging
from rid_lib import RID
from rid_lib.types import KoiNetNode
from rid_lib.ext import Manifest, Cache
from rid_lib.ext.bundle import Bundle

from ..protocol.api_models import (
    RidsPayload,
    ManifestsPayload,
    BundlesPayload,
    FetchRids,
    FetchManifests,
    FetchBundles,
)

logger = logging.getLogger(__name__)


class ResponseHandler:
    """Handles generating responses to requests from other KOI nodes."""
    
    cache: Cache
    
    def __init__(
        self, 
        cache: Cache, 
    ):
        self.cache = cache
        
    def fetch_rids(self, req: FetchRids, source: KoiNetNode) -> RidsPayload:
        """Returns response to fetch RIDs request."""
        logger.info(f"Request to fetch rids, allowed types {req.rid_types}")
        rids = self.cache.list_rids(req.rid_types)
        
        return RidsPayload(rids=rids)
        
    def fetch_manifests(self, req: FetchManifests, source: KoiNetNode) -> ManifestsPayload:
        """Returns response to fetch manifests request."""
        logger.info(f"Request to fetch manifests, allowed types {req.rid_types}, rids {req.rids}")
        
        manifests: list[Manifest] = []
        not_found: list[RID] = []
        
        for rid in (req.rids or self.cache.list_rids(req.rid_types)):
            bundle = self.cache.read(rid)
            if bundle:
                manifests.append(bundle.manifest)
            else:
                not_found.append(rid)
        
        return ManifestsPayload(manifests=manifests, not_found=not_found)
        
    def fetch_bundles(self, req: FetchBundles, source: KoiNetNode) -> BundlesPayload:
        """Returns response to fetch bundles request."""
        logger.info(f"Request to fetch bundles, requested rids {req.rids}")
        
        bundles: list[Bundle] = []
        not_found: list[RID] = []

        for rid in req.rids:
            bundle = self.cache.read(rid)
            if bundle:
                bundles.append(bundle)
            else:
                not_found.append(rid)
            
        return BundlesPayload(bundles=bundles, not_found=not_found)