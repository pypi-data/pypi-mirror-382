class SearchGranulesFactory:
    CMR = 'CMR'
    UNITY = 'UNITY'
    def get_class(self, search_type):
        if search_type == SearchGranulesFactory.CMR:
            from mdps_ds_lib.stage_in_out.search_granules_cmr import SearchGranulesCmr
            return SearchGranulesCmr()
        if search_type == SearchGranulesFactory.UNITY:
            from mdps_ds_lib.stage_in_out.search_granules_unity import SearchGranulesUnity
            return SearchGranulesUnity()
        raise ValueError(f'unknown search_type: {search_type}')
