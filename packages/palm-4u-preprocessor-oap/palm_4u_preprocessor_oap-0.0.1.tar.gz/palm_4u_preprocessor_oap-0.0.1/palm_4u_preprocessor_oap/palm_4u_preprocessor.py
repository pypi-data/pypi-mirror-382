import logging
from .process_mock import mock_process
from pygeoapi.process.base import BaseProcessor

LOGGER = logging.getLogger(__name__)

PROCESS_METADATA = {
    'version': '0.0.1',
    'id': 'palm4u_preprocessor',
    'title': {
        'en': 'Palm4U Preprocessor',
    },
    'description': {
        'en': 'Palm4U Preprocessor',
    },
    'jobControlOptions': ['sync-execute'],
    'keywords': ['palm4u'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'geometry': {
            'title': 'Input Polygon',
            'description': 'The input polygon as a GeoJSON polygon geometry (type "Polygon").',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/geo+json'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'keywords': ['geometry']
        },
        'model_id': {
            'title': 'Model ID',
            'description': 'The ID of the Palm4U model to use.',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'keywords': ['model']
        }
    },
    'outputs': {
        'resultZip': {
            'title': 'Result ZIP',
            'description': 'A ZIP file containing all output files.',
            'schema': {
                'type': 'string',
                'contentMediaType': 'application/zip'
            },
        },
    },
    'example': {
        'inputs': {
            'geometry': {
                'coordinates': [
                    [
                        [
                            9.353911531282023,
                            51.29092919045166
                        ],
                        [
                            9.361424455458916,
                            51.28654387412095
                        ],
                        [
                            9.37331991873944,
                            51.28936305412219
                        ],
                        [
                            9.362676609487806,
                            51.29695831662494
                        ],
                        [
                            9.353911531282023,
                            51.29092919045166
                        ]
                    ]
                ],
                'type': 'Polygon'
            },
            'model_id': 'example_model_id'
        }
    }
}

class Palm4UPreprocessor(BaseProcessor):
    """Palm4U Preprocessor"""

    def __init__(self, processor_def, outputs=None):
        super().__init__(processor_def, PROCESS_METADATA)

    def execute(self, data, outputs=None):
        """
        :param data: JSON input data that includes geometry.
        :returns: Tuple (mimetype, produced_outputs)
        """
        mime_type = 'application/zip'
        produced_outputs = mock_process(data.get('geometry'), data.get('model_id'))

        return mime_type, produced_outputs

    def __repr__(self):
        return f'<Palm4UPreprocessor> {self.name}'
