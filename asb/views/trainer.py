from pyramid.view import view_config

import asb.models as models

@view_config(route_name='trainer_index', renderer='/indices/trainer.mako')
def TrainerIndex(context, request):
    trainers = (
        models.DBSession.query(models.Trainer)
        .order_by(models.Trainer.id)
        .all()
    )

    return {'trainers': trainers}

@view_config(route_name='trainer', renderer='/trainer.mako')
def Trainer(context, request):
    trainer = (
        models.DBSession.query(models.Trainer)
        .filter_by(id=request.matchdict['id'])
        .one()
    )

    return {'trainer': trainer}
