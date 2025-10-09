FRAMEWORK_TO_EVALUATION = {
    'digital-outcomes-and-specialists-7': {
        'digital-capability-and-delivery-partner': 'Lot 2 - Digital Capability and Delivery Partners'
    },
    'g-cloud-15': {
        'iaas-and-paas': 'Lot 1a - Infrastructure as a Service (IaaS) and Platform as a Service (PaaS)',
        'iaas-and-paas-above-official':
        'Lot 1b - Infrastructure as a Service (IaaS) and Platform as a Service (PaaS) above OFFICIAL',
        'cloud-software':
        'Lot 2a - Infrastructure Software as a Service (iSaaS) and/or Lot 2b - Software as a Service (SaaS)',
        'cloud-support': 'Lot 3 - Cloud Support'
    }
}

FRAMEWORK_TO_LOT_PRICING = {
    'g-cloud-15': {
        'iaas-and-paas': 'Lot 1a - Infrastructure as a Service (IaaS) and Platform as a Service (PaaS)',
        'iaas-and-paas-above-official':
        'Lot 1b - Infrastructure as a Service (IaaS) and Platform as a Service (PaaS) above OFFICIAL',
        'cloud-software':
        'Lot 2a - Infrastructure Software as a Service (iSaaS) and/or Lot 2b - Software as a Service (SaaS)',
        'cloud-support': 'Lot 3 - Cloud Support'
    }
}


def get_evaluation_title_mapping(framework):
    return FRAMEWORK_TO_EVALUATION[framework['slug']]


def get_evaluation_title(evaluation):
    return FRAMEWORK_TO_EVALUATION[evaluation['frameworkSlug']][evaluation['route']]


def get_technical_ability_certificate_title_mapping(framework):
    return {
        framework["technicalAbilityCertificateSettings"]["lotToRoute"][lot['slug']]:
        f"Lot {lot['number']} - {lot['name']}"
        for lot in framework['lots']
        if lot['slug'] in framework["technicalAbilityCertificateSettings"]["lotToRoute"]
    }


def get_technical_ability_certificate_title(technical_ability_certificate, framework):
    lot_slug = next(
        (
            lot_slug
            for lot_slug, route in framework["technicalAbilityCertificateSettings"]["lotToRoute"].items()
            if route == technical_ability_certificate["route"]
        ),
        None
    )

    lot = next(
        (
            lot
            for lot in framework["lots"]
            if lot["slug"] == lot_slug
        ),
        None
    )

    return f"Lot {lot['number']} - {lot['name']}"


def get_lot_pricing_title_mapping(framework):
    return FRAMEWORK_TO_LOT_PRICING[framework['slug']]


def get_lot_pricing_title(lot_pricing):
    return FRAMEWORK_TO_LOT_PRICING[lot_pricing['frameworkSlug']][lot_pricing['route']]
