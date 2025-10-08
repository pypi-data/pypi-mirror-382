# -*- coding: utf-8 -*-
{
    'name': "community_maps",

    'summary': """
    Module to create and manage your map visualizations into a  website""",

    'author': "Community Maps",
    'website': "https://gitlab.com/somitcoop/erp-research/community-maps",

    'category': 'community-maps',
    'version': '16.0.2.0.7',

    'depends': [
        'base',
        'base_rest',
        'sale',
        'crm',
        'metadata',
        'queue_job'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/rules.xml',
        'data/collect_place_submission_email_template.xml',
        'data/ir_cron_submission_transfer.xml',
        'views/cm_menu_root.xml',
        'views/cm_menu_root_config.xml',
        'views/cm_button_color_config_id.xml',
        'views/cm_map.xml',
        'views/cm_filter_group.xml',
        'views/cm_map_colorschema.xml',
        'views/cm_place.xml',
        'views/cm_place_presenter_metadata.xml',
        'views/cm_place_category.xml',
        'views/cm_form_model.xml',
        'views/cm_form_submission.xml',
        'views/cm_form_submission_transfer_request.xml',
        'views/cm_presenter_model.xml',
        'views/cm_submission_transfer_page_template.xml',
        'wizards/cm_collectchildplaces_wizard.xml'
    ],
    "external_dependencies": {
        "python" : [
            "python-slugify",
        ]
    }
}
