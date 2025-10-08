# -*- coding: utf-8 -*-


class CmUtils(object):
    @staticmethod
    def get_system_crowdfunding_types_selection():
        return [
            ("none", "None"),
            ("invoicing_amount", "Invoicing goal"),
            ("submission_amount", "Submissions goal"),
        ]

    @staticmethod
    def get_create_existing_model(model_env, query, creation_data=False):
        existing_model = model_env.search(query)
        create_model = True
        if existing_model:
            model = existing_model
            create_model = False
        if create_model and creation_data:
            model = model_env.create(creation_data)
        return model

    @staticmethod
    def update_create_existing_model(model_env, query, creation_data):
        existing_model = model_env.search(query)
        if existing_model:
            existing_model.write(creation_data)
            return existing_model
        return model_env.create(creation_data)
