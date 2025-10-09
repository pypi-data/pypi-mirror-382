from datetime import datetime

import json

from .app_model import DataModel
from .app_reporter import Reporter
from .report_builder import ReportBuilder


class ResearchBuilder:

    def __init__(self, kawa_client, name, unique_tag=None):
        self._k = kawa_client
        self._tag = unique_tag or f'#{name}'
        self._name = name
        self._reporter = Reporter(name=name)
        self._models = []
        self._results = []
        self._report = None

    def publish_models(self):
        for model in self._models:
            model.sync()

    def publish_results(self):
        created_views = []
        relationships = []
        for model in self._models:
            view_ids = model.create_views()
            created_views.append({
                'sheetId': str(model.sheet_id),
                'viewIds': view_ids
            })
            # Each model of the research can be linked to multiple models
            relationships.append({
                'sheetName': model.name,
                'asciiRepresentations': [rel.ascii() for rel in model.relationships],
            })

        result = {
            'views': created_views,
            'data': self._results,
            'relationships': relationships,
        }

        return json.dumps(result)

    def register_result(self, description, df):
        self._results.append({
            'description': description,
            'df': df.to_csv(),
        })

    def register_model(self, model_id):
        sheet = self._k.entities.sheets().get_entity_by_id(model_id)
        if not sheet:
            raise Exception(f'Sheet with id={model_id} not found')
        model = DataModel(
            kawa=self._k,
            reporter=self._reporter,
            name=sheet['displayInformation']['displayName'],
            sheet=sheet
        )
        self._models.append(model)
        return model

    def report(self):
        self._report = ReportBuilder(
            kawa_client=self._k,
            name=self._name,
            unique_tag=self._tag,
        )
        return self._report

    def _sync(self):
        for model in self._models:
            model.sync()
