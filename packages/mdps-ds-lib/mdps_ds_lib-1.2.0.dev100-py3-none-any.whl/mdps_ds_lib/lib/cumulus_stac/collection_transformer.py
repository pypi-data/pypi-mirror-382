import json
import logging
from urllib.parse import quote_plus, urlparse, unquote_plus

import pystac
from pystac.utils import datetime_to_str

from pystac import Link, Collection, Extent, SpatialExtent, TemporalExtent, Summaries

from mdps_ds_lib.lib.constants import Constants
from mdps_ds_lib.lib.cumulus_stac.stac_transformer_abstract import StacTransformerAbstract
from mdps_ds_lib.lib.utils.time_utils import TimeUtils

STAC_COLLECTION_SCHEMA = '''{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json#",
    "title": "STAC Collection Specification",
    "description": "This object represents Collections in a SpatioTemporal Asset Catalog.",
    "allOf": [
        {
            "$ref": "#/definitions/collection"
        }
    ],
    "definitions": {
        "collection": {
            "title": "STAC Collection",
            "description": "These are the fields specific to a STAC Collection. All other fields are inherited from STAC Catalog.",
            "type": "object",
            "required": [
                "stac_version",
                "type",
                "id",
                "description",
                "license",
                "extent",
                "links"
            ],
            "properties": {
                "stac_version": {
                    "title": "STAC version",
                    "type": "string",
                    "const": "1.0.0"
                },
                "stac_extensions": {
                    "title": "STAC extensions",
                    "type": "array",
                    "uniqueItems": true,
                    "items": {
                        "title": "Reference to a JSON Schema",
                        "type": "string",
                        "format": "iri"
                    }
                },
                "type": {
                    "title": "Type of STAC entity",
                    "const": "Collection"
                },
                "id": {
                    "title": "Identifier",
                    "type": "string",
                    "minLength": 1
                },
                "title": {
                    "title": "Title",
                    "type": "string"
                },
                "description": {
                    "title": "Description",
                    "type": "string",
                    "minLength": 1
                },
                "keywords": {
                    "title": "Keywords",
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "license": {
                    "title": "Collection License Name",
                    "type": "string",
                    "pattern": "^[\\\\w\\\\-\\\\.\\\\+]+$"
                },
                "providers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": [
                            "name"
                        ],
                        "properties": {
                            "name": {
                                "title": "Organization name",
                                "type": "string"
                            },
                            "description": {
                                "title": "Organization description",
                                "type": "string"
                            },
                            "roles": {
                                "title": "Organization roles",
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "producer",
                                        "licensor",
                                        "processor",
                                        "host"
                                    ]
                                }
                            },
                            "url": {
                                "title": "Organization homepage",
                                "type": "string",
                                "format": "iri"
                            }
                        }
                    }
                },
                "extent": {
                    "title": "Extents",
                    "type": "object",
                    "required": [
                        "spatial",
                        "temporal"
                    ],
                    "properties": {
                        "spatial": {
                            "title": "Spatial extent object",
                            "type": "object",
                            "required": [
                                "bbox"
                            ],
                            "properties": {
                                "bbox": {
                                    "title": "Spatial extents",
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "title": "Spatial extent",
                                        "type": "array",
                                        "oneOf": [
                                            {
                                                "minItems": 4,
                                                "maxItems": 4
                                            },
                                            {
                                                "minItems": 6,
                                                "maxItems": 6
                                            }
                                        ],
                                        "items": {
                                            "type": "number"
                                        }
                                    }
                                }
                            }
                        },
                        "temporal": {
                            "title": "Temporal extent object",
                            "type": "object",
                            "required": [
                                "interval"
                            ],
                            "properties": {
                                "interval": {
                                    "title": "Temporal extents",
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "title": "Temporal extent",
                                        "type": "array",
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "items": {
                                            "type": [
                                                "string",
                                                "null"
                                            ],
                                            "format": "date-time",
                                            "pattern": "(\\\\+00:00|Z)$"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "assets": {
                    "$ref": "../../item-spec/json-schema/item.json#/definitions/assets"
                },
                "links": {
                    "title": "Links",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/link"
                    }
                },
                "summaries": {
                    "$ref": "#/definitions/summaries"
                }
            }
        },
        "link": {
            "type": "object",
            "required": [
                "rel",
                "href"
            ],
            "properties": {
                "href": {
                    "title": "Link reference",
                    "type": "string",
                    "format": "iri-reference",
                    "minLength": 1
                },
                "rel": {
                    "title": "Link relation type",
                    "type": "string",
                    "minLength": 1
                },
                "type": {
                    "title": "Link type",
                    "type": "string"
                },
                "title": {
                    "title": "Link title",
                    "type": "string"
                }
            }
        },
        "summaries": {
            "type": "object",
            "additionalProperties": {
                "anyOf": [
                    {
                        "title": "JSON Schema",
                        "type": "object",
                        "minProperties": 1,
                        "allOf": [
                            {
                                "$ref": "http://json-schema.org/draft-07/schema"
                            }
                        ]
                    },
                    {
                        "title": "Range",
                        "type": "object",
                        "required": [
                            "minimum",
                            "maximum"
                        ],
                        "properties": {
                            "minimum": {
                                "title": "Minimum value",
                                "type": [
                                    "number",
                                    "string"
                                ]
                            },
                            "maximum": {
                                "title": "Maximum value",
                                "type": [
                                    "number",
                                    "string"
                                ]
                            }
                        }
                    },
                    {
                        "title": "Set of values",
                        "type": "array",
                        "minItems": 1
                    }
                ]
            }
        }
    }
}'''
# The following lines are a part of summaries > additionalProperties > oneOf > [last item].
# But including that will not make it a valid schema.
# excluding it for now
# "items": {
#     "description": "For each field only the original data type of the property can occur (except for arrays), but we can't validate that in JSON Schema yet. See the sumamry description in the STAC specification for details."
# }
LOGGER = logging.getLogger(__name__)


class CollectionTransformer(StacTransformerAbstract):
    def __init__(self, report_to_ems:bool = True, include_date_range=False, items_base_url=''):
        super().__init__()
        self.__stac_collection_schema = json.loads(STAC_COLLECTION_SCHEMA)
        self.__cumulus_collection_schema = {}
        self.__report_to_ems = report_to_ems
        self.__include_date_range = include_date_range

        self.__output_provider = None
        self.__output_cumulus_collection = None
        self.__input_dapa_collection: Collection = None
        self.__items_base_url = items_base_url

    def get_collection_id(self):
        if self.__input_dapa_collection is None:
            raise ValueError(f'pls load and parse __input_dapa_collection via from_stac')
        return self.__input_dapa_collection.id

    def get_collection_bbox(self):
        if self.__input_dapa_collection is None:
            raise ValueError(f'pls load and parse __input_dapa_collection via from_stac')
        return self.__input_dapa_collection.extent.spatial.bboxes[0]

    def get_collection_time_range(self):
        if self.__input_dapa_collection is None:
            raise ValueError(f'pls load and parse __input_dapa_collection via from_stac')
        return self.__input_dapa_collection.extent.temporal.intervals

    @property
    def output_provider(self):
        return self.__output_provider

    def generate_target_link_url(self, regex: str = None, bucket: str = None):
        href_link = ['unknown_bucket', 'unknown_regex']
        if regex is not None and regex != '':
            href_link[1] = regex
        if bucket is not None and bucket != '':
            href_link[0] = bucket
        return f"./collection.json?bucket={href_link[0]}&regex={quote_plus(href_link[1])}"

    def __convert_to_stac_link_obj(self, collection_file_obj: dict, rel_type: str = 'item'):
        """
        expected output
        {
          "title": "<sampleFileName>",
          "href": "<bucket>___<regex>"
          "type": "<type>",
          "rel": "item"
        }

        Sample input:
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS",
                    "type": "data",
                    "reportToEms": True
                }
        TODO: missing reportToEms
        :param collection_file_obj:
        :return: dict
        """
        temp_link = Link(target=self.generate_target_link_url(
                collection_file_obj['regex'] if 'regex' in collection_file_obj else None,
                collection_file_obj['bucket'] if 'bucket' in collection_file_obj else None,
            ),
            rel=rel_type
            )
        if 'type' in collection_file_obj:
            temp_link.media_type = collection_file_obj['type']
        if 'sampleFileName' in collection_file_obj:
            temp_link.title = collection_file_obj['sampleFileName']
        return temp_link

    def to_stac(self, source: dict) -> dict:
        source_sample = {
            "createdAt": 1647992847582,
            "granuleId": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0$",
            "process": "modis",
            "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
            "name": "ATMS_SCIENCE_Group",
            "files": [
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS",
                    "type": "data",
                    "reportToEms": True
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}01\\.PDS\\.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000001.PDS.xml",
                    "reportToEms": True,
                    "type": "metadata"
                },
                {
                    "bucket": "internal",
                    "regex": "^P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}00.PDS.cmr.xml$",
                    "sampleFileName": "P1570515ATMSSCIENCEAXT11344000000000.PDS.cmr.xml",
                    "reportToEms": True,
                    "type": "metadata"
                }
            ],
            "granuleIdExtraction": "(P[0-9]{3}[0-9]{4}[A-Z]{13}T[0-9]{12}0).+",
            "reportToEms": True,
            "version": "001",
            "duplicateHandling": "replace",
            "updatedAt": 1647992847582,
            "url_path": "{cmrMetadata.Granule.Collection.ShortName}___{cmrMetadata.Granule.Collection.VersionId}",
            "timestamp": 1647992849273
        }
        collection_id = f"{source['name']}___{source['version']}"
        temporal_extent = []
        if 'dateFrom' in source:
            temporal_extent.append(self.get_time_obj(source['dateFrom']))
        if 'dateTo' in source:
            temporal_extent.append(self.get_time_obj(source['dateTo']))
        stac_collection = Collection(
            id=collection_id,
            # href=f"https://ideas-api-to-be-hosted/slcp/collections/{input_collection['ShortName']}::{input_collection['VersionId']}",
            description="TODO",
            extent=Extent(
                SpatialExtent([[0.0, 0.0, 0.0, 0.0]]),
                TemporalExtent([temporal_extent])
            ),
            license="proprietary",
            providers=[],
            # title=input_collection['LongName'],
            # keywords=[input_collection['SpatialKeywords']['Keyword']],
            summaries=Summaries({
                "updated": [datetime_to_str(TimeUtils().parse_from_unix(source['updatedAt'], True).get_datetime_obj())],
                "granuleId": [source['granuleId'] if 'granuleId' in source else ''],
                "granuleIdExtraction": [source['granuleIdExtraction'] if 'granuleIdExtraction' in source else ''],
                "process": [source['process'] if 'process' in source else ''],
                "totalGranules": [source['total_size'] if 'total_size' in source else -1],
            }),
            # assets={}
        )
        stac_collection.links = [self.__convert_to_stac_link_obj({
            "regex": source['url_path'] if 'url_path' in source else './collection.json',
            "sampleFileName": source['sampleFileName'],
            "type": "application/json",

        }, 'root')] + \
                                [self.__convert_to_stac_link_obj(k) for k in source['files']] + \
                                [Link(rel='parent', target=f'{self.__items_base_url}/{Constants.CATALOG}', media_type='application/json', title=f"UDS Catalog"),
                                 Link(rel='items', target=f'{self.__items_base_url}/{Constants.COLLECTIONS}/{collection_id}/items', media_type='application/json', title=f"{collection_id} Granules")]
        return stac_collection.to_dict(include_self_link=False, transform_hrefs=False)

    def get_href(self, input_href: str):
        parse_result = urlparse(input_href)
        if parse_result.query == '':
            return ''
        query_dict = [k.split('=') for k in parse_result.query.split('&')]
        query_dict = {k[0]: unquote_plus(k[1]) for k in query_dict}
        return query_dict

    def __convert_from_stac_links(self, link_obj: dict):
        output_file_object = {
            'reportToEms': self.__report_to_ems
        }
        if 'type' in link_obj:
            output_file_object['type'] = link_obj['type']
        if 'title' in link_obj:
            output_file_object['sampleFileName'] = link_obj['title']
        if 'href' in link_obj:
            href_dict = self.get_href(link_obj['href'])
            if 'bucket' in href_dict:
                output_file_object['bucket'] = href_dict['bucket']
            if 'regex' in href_dict:
                output_file_object['regex'] = href_dict['regex']
        return output_file_object

    def from_stac(self, source: dict) -> dict:
        self.__input_dapa_collection = pystac.Collection.from_dict(source)
        if not self.__input_dapa_collection.validate():
            raise ValueError(f'invalid source dapa: {self.__input_dapa_collection}')
        output_collection_cumulus = {
            # "createdAt": 1647992847582,
            "reportToEms": self.__report_to_ems,
            "duplicateHandling": "skip",
            # "updatedAt": 1647992847582,
            # "timestamp": 1647992849273
        }
        summaries = self.__input_dapa_collection.summaries.lists
        if 'granuleId' in summaries:
            output_collection_cumulus['granuleId'] = summaries['granuleId'][0]
        if 'granuleIdExtraction' in summaries:
            output_collection_cumulus['granuleIdExtraction'] = summaries['granuleIdExtraction'][0]
        if 'process' in summaries:
            output_collection_cumulus['process'] = summaries['process'][0]
        name_version = self.__input_dapa_collection.id.split('___')
        output_collection_cumulus['name'] = name_version[0]
        output_collection_cumulus['version'] = name_version[1]
        output_files = []
        for each_link_obj in self.__input_dapa_collection.links:
            each_link_obj: Link = each_link_obj
            each_file_obj = self.__convert_from_stac_links(each_link_obj.to_dict())
            if each_link_obj.rel == 'root':
                if 'regex' in each_file_obj:
                    output_collection_cumulus['url_path'] = each_file_obj['regex']
                if 'sampleFileName' in each_file_obj:
                    output_collection_cumulus['sampleFileName'] = each_file_obj['sampleFileName']
            else:
                output_files.append(each_file_obj)
        output_collection_cumulus['files'] = output_files
        if len(self.__input_dapa_collection.extent.temporal.intervals) > 0:
            date_interval = self.__input_dapa_collection.extent.temporal.intervals[0]
            if len(date_interval) == 2 and self.__include_date_range is True:
                if date_interval[0] is not None:
                    output_collection_cumulus['dateFrom'] = date_interval[0].strftime(TimeUtils.MMDD_FORMAT)
                if date_interval[1] is not None:
                    output_collection_cumulus['dateTo'] = date_interval[1].strftime(TimeUtils.MMDD_FORMAT)
        LOGGER.debug(f'self.__input_dapa_collection.providers: {self.__input_dapa_collection.providers}')
        self.__output_provider = None if self.__input_dapa_collection.providers is None or len(self.__input_dapa_collection.providers) < 1 else self.__input_dapa_collection.providers[0].name
        self.__output_cumulus_collection = output_collection_cumulus
        return output_collection_cumulus
