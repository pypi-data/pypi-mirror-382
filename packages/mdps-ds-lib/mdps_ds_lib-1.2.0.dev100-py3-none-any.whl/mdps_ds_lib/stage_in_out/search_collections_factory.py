class SearchCollectionsFactory:
    CMR = 'CMR'
    UNITY = 'UNITY'
    def get_class(self, search_type):
        if search_type == SearchCollectionsFactory.CMR:
            from mdps_ds_lib.stage_in_out.search_collections_cmr import SearchCollectionsCmr
            return SearchCollectionsCmr()
        if search_type == SearchCollectionsFactory.UNITY:
            from mdps_ds_lib.stage_in_out.search_collections_unity import SearchCollectionsUnity
            return SearchCollectionsUnity()
        raise ValueError(f'unknown search_type: {search_type}')
