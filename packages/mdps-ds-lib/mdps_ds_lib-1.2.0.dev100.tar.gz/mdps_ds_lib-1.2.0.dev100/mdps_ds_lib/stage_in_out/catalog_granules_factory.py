from mdps_ds_lib.lib.utils.factory_abstract import FactoryAbstract


class CatalogGranulesFactory(FactoryAbstract):
    UNITY = 'UNITY'
    STAC_FAST_API = 'STAC_FAST_API'

    def get_instance_from_env(self, **kwargs):
        raise NotImplementedError('not a need yet')

    def get_instance(self, class_type, **kwargs):
        if class_type == CatalogGranulesFactory.UNITY:
            from mdps_ds_lib.stage_in_out.catalog_granules_unity import CatalogGranulesUnity
            return CatalogGranulesUnity()
        if class_type == CatalogGranulesFactory.STAC_FAST_API:
            from mdps_ds_lib.stage_in_out.catalog_granules_fast_api import CatalogGranulesFastAPI
            return CatalogGranulesFastAPI()
        raise ValueError(f'unknown search_type: {class_type}')
