import logging
import os
from collections import defaultdict

from pystac import Catalog, Item, Asset, Link

from mdps_ds_lib.lib.utils.file_utils import FileUtils
LOGGER = logging.getLogger(__name__)


class GranulesCatalog:

    @staticmethod
    def standardize_stage_out_collection_id_format(current_collection_id: str):
        collection_identifier_parts = current_collection_id.split(':')
        if len(collection_identifier_parts) < 6:
            raise ValueError(
                f'invalid collection ID. Need to be in <URN>:<ORG>:<Project>:<Tenant>:<Venue>:<Collection ID> but it is {current_collection_id}')
        for i in range(5):
            collection_identifier_parts[i] = collection_identifier_parts[i].upper()
        current_collection_id = ':'.join(collection_identifier_parts)
        current_collection_id = f'{current_collection_id}___001' if '___' not in current_collection_id else current_collection_id
        return current_collection_id

    @staticmethod
    def get_unity_formatted_collection_id(current_collection_id: str, project_venue_set: tuple):
        if current_collection_id == '' or current_collection_id is None:
            raise ValueError(f'NULL or EMPTY collection_id: {current_collection_id}')
        collection_identifier_parts = current_collection_id.split(':')
        if len(collection_identifier_parts) >= 6:
            LOGGER.debug(f'current_collection_id is assumed to be in UNITY format: {current_collection_id}')
            return GranulesCatalog.standardize_stage_out_collection_id_format(current_collection_id)
        LOGGER.info(f'current_collection_id is not UNITY formatted ID: {current_collection_id}')
        if project_venue_set[0] is None or project_venue_set[1] is None:
            raise ValueError(f'missing project or venue in ENV which is needed due to current_collection_id not UNITY format: {project_venue_set}')
        new_collection = f'URN:NASA:UNITY:{project_venue_set[0].upper()}:{project_venue_set[1].upper()}:{current_collection_id}'
        new_collection = f'{new_collection}___001' if '___' not in new_collection else new_collection
        LOGGER.info(f'UNITY formatted ID: {new_collection}')
        return new_collection
    
    def update_catalog(self, catalog_file_path: str, file_paths: list, rel_name: str = 'item'):
        if not FileUtils.file_exist(catalog_file_path):
            raise ValueError(f'missing file: {catalog_file_path}')
        catalog = FileUtils.read_json(catalog_file_path)
        catalog = Catalog.from_dict(catalog)
        catalog.clear_links(rel_name)
        for each_path in file_paths:
            catalog.add_link(Link('item', each_path, 'application/json'))
        return catalog.to_dict(False, False)

    def get_child_link_hrefs(self, catalog_file_path: str, rel_name: str = 'item'):
        if not FileUtils.file_exist(catalog_file_path):
            raise ValueError(f'missing file: {catalog_file_path}')
        catalog = FileUtils.read_json(catalog_file_path)
        catalog = Catalog.from_dict(catalog)
        child_links = [k.href for k in catalog.get_links(rel=rel_name)]
        catalog_dir = os.path.dirname(catalog_file_path)
        new_child_links = []
        for each_link in child_links:
            if not FileUtils.is_relative_path(each_link):
                new_child_links.append(each_link)
                continue
            new_child_links.append(os.path.join(catalog_dir, each_link))
        return new_child_links

    @staticmethod
    def is_bbox_valid(bbox_array):
        if len(bbox_array) != 4:
            return False
        lon_a, lat_a, lon_b, lat_b = bbox_array
        if lon_a == lon_b or lat_a == lat_b:
            return False
        return True

    def get_granules_item(self, granule_stac_json) -> Item:
        if not FileUtils.file_exist(granule_stac_json):
            raise ValueError(f'missing file: {granule_stac_json}')
        granules_stac = FileUtils.read_json(granule_stac_json)
        granules_stac = Item.from_dict(granules_stac)
        if granules_stac.bbox is not None and not self.is_bbox_valid(granules_stac.bbox):
            raise ValueError(f'invalid BBOX. It may be a point or a line: {granules_stac.bbox}')
        return granules_stac

    def extract_assets_href(self, granules_stac: Item, dir_name: str = '') -> dict:
        try:
            self_dir = os.path.dirname(granules_stac.self_href)
        except:
            self_dir = None
        assets = defaultdict(dict)
        for k, v in granules_stac.get_assets().items():
            href = v.href
            if v.roles is None or len(v.roles) < 1:
                LOGGER.warning(f'asset do not have roles: {v}')
                continue
            role_key = v.roles[0]
            if not FileUtils.is_relative_path(href):
                assets[role_key][k] = href
                continue
            if dir_name is not None and len(dir_name) > 0:
                assets[role_key][k] = os.path.join(dir_name, href)
                continue
            if self_dir is not None and len(self_dir) > 0:
                assets[role_key][k] = os.path.join(self_dir, href)
                continue
            assets[role_key][k] = href
        return assets

    def update_assets_href(self, granules_stac: Item,  new_assets: dict):
        for k, v in new_assets.items():
            if k in granules_stac.assets:
                existing_asset = granules_stac.assets.get(k)
                existing_asset.href = v
            else:
                existing_asset = Asset(v, k)
            granules_stac.add_asset(k, existing_asset)
        return self
