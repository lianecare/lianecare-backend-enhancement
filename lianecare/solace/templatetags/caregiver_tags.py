from django.utils.safestring import mark_safe
from django import template
from django.utils.translation import gettext_lazy as _

# from solace.models.service import Service
register = template.Library()


@register.simple_tag(name='skill_list')
def skill_list(caregiver=None):
    """
    Ritorna una lista di skill con icona e relativo valore True/False.
    """
    if caregiver:
        htmlresult = []
        a = htmlresult.append
        a('<ul class="pro-list nolist">')
        a('<li><i class="fas fa-{0}"></i>{1} {2}</li>'.format('female' if caregiver.is_smoker else 'male',
                                                              caregiver.get_age(), _('anni')))
        if caregiver.nationality:
            a('<li><i class="far fa-flag"></i><span class="nationality">{0}</li>'.format(
                caregiver.nationality))
        if caregiver.is_smoker is not None:
            a('<li class="is_smoker"><i class="fas fa-smoking {0}"></i>{1}</li>'.format(
                'text-danger' if caregiver.is_smoker else 'text-gray',
                _("Fuma") if caregiver.is_smoker else _("Non fuma")))
        if caregiver.driving_license is not None:
            a('<li class="driving_license"><i class="far fa-address-card {0}"></i>{1}</li>'.format(
                'text-primary' if caregiver.driving_license else 'text-gray',
                _("Ha la patente di guida") if caregiver.driving_license else _("Non ha la patente di guida")))
        if caregiver.has_car is not None:
            a('<li class="has_car"><i class="fas fa-car {0}"></i>{1}</li>'.format(
                'text-primary' if caregiver.has_car else 'text-gray',
                _("Ha un mezzo") if caregiver.has_car else _("Non ha un mezzo")))
        a('<h4 class="card-title small mt-4 mb-2">{0}</h4>'.format(_("Formazione")))
        if caregiver.is_graduate:
            a('<li class="is_graduate"><i class="fas fa-user-md text-primary"></i>{0}</li>'.format(
                _("Ha una laurea in ambito sanitario")))
        if caregiver.is_certificated:
            a('<li class="is_certificated"><i class="fas fa-user-nurse text-primary"></i>{0}</li>'.format(
                _("Ha una certificazione")))
        if caregiver.first_aid:
            a('<li class="first_aid"><i class="fas fa-medkit text-primary"></i>{0}</li>'.format(
                _("Attestato di Primo Soccorso")))
        if caregiver.child_trainer:
            a('<li class="child_trainer"><i class="fas fa-chalkboard-teacher text-primary"></i>{0}</li>'.format(
                _("Formatore per l'infanzia")))
        if caregiver.has_basic_course or caregiver.has_pro_course:
            a('<li><i class="fas fa-certificate {1}"></i>{0}</li>'.format(
                _("Corso Avanzato Liane") if caregiver.has_pro_course else _("Corso base Liane"), 'text-orange' if caregiver.has_pro_course else 'text-primary'))

        a('</ul>')
        return mark_safe(''.join(htmlresult))
    else:
        return ''

        # format_html("{} <b>{}</b> {}",
        #             mark_safe(some_html),
        #             some_text,
        #             some_other_text, )


@register.simple_tag(name='availability_grid_mod')
def availability_grid_mod(availability=None):
    if availability:
        htmlresult = []
        time_day = [_('Mattina'), _('Pomeriggio'), _('Sera'), _('Notte')]
        a = htmlresult.append
        a('<table class="table table-sm table-borderless table-responsive table-availability-mod">')
        a(
            '<thead><tr><th scope="col"></th><th scope="col">{0}</th><th scope="col">{1}</th><th scope="col">{2}</th><th scope="col">{3}</th><th scope="col">{4}</th><th scope="col">{5}</th><th scope="col">{6}</th></tr></thead>'.format(
                _('LUN'), _('MAR'), _('MER'), _('GIO'), _('VEN'), _('SAB'), _('DOM')))
        a('<tbody>')
        for i, row in enumerate(availability):
            a('<tr><th scope="row">{0}</th>'.format(time_day[i]))
            for x, col in enumerate(row):
                a(
                    '<td class="slot-time {0}"><label class="switch"><input type="checkbox" name="availability[{1}][{2}]" value="1" data-unchecked-value="0" data-value-type="array" {3}><span class="slider round"></span></label></td>'.format(
                        'active' if col == 1 else '', i, x, 'checked' if col == 1 else ''))
            a('</tr>')
            i += 1
        a('</tbody></table>')
        return mark_safe(''.join(htmlresult))
    else:
        return ''


@register.simple_tag(name='availability_grid')
def availability_grid(availability=None):
    if availability:
        htmlresult = []
        time_day = [_('Mattina'), _('Pomeriggio'), _('Sera'), _('Notte')]
        a = htmlresult.append
        a('<table class="table table-sm table-borderless table-responsive-sm table-availability">')
        a(
            '<thead><tr><th scope="col"></th><th scope="col">{0}</th><th scope="col">{1}</th><th scope="col">{2}</th><th scope="col">{3}</th><th scope="col">{4}</th><th scope="col">{5}</th><th scope="col">{6}</th></tr></thead>'.format(
                _('LUN'), _('MAR'), _('MER'), _('GIO'), _('VEN'), _('SAB'), _('DOM')))
        a('<tbody>')
        for i, row in enumerate(availability):
            a('<tr><th scope="row">{0}</th>'.format(time_day[i]))
            for x, col in enumerate(row):
                a(
                    '<td class="slot-time {0}"><i class="fas {1}"></i></td>'.format(
                        'active' if col == 1 else '', 'fa-check' if col == 1 else 'fa-times'))
            a('</tr>')
            i += 1
        a('</tbody></table>')
        return mark_safe(''.join(htmlresult))
    else:
        return ''


@register.simple_tag(name='subcategories_list')
def subCategoriesList(subCategories=None, forJobPost=False, get_selected_sub_category=None):
    # Add Services
    if subCategories and get_selected_sub_category is None:
        htmlresult = []
        a = htmlresult.append
        a('<h6>Seleziona tutti i servizi di cui necessiti.</h6>' if forJobPost else '<h6>Seleziona tutti i servizi che potresti erogare.</h6>')
        a('<div class="subcat-wrapper">')
        for i, sub in enumerate(subCategories, start=0):
            if forJobPost:
                a(
                    '<div class="sub-cat"><div class="checkbox"><label><input type="checkbox"  name="subcategories" id="id_subcategories_{3}" value="{0}"><span class="important">{1}</span></label></div>{2}</div>'.format(
                        sub.id, sub.name, sub.description, i))
            else:
                a(
                    '<div class="sub-cat"><div class="checkbox"><label><input type="checkbox" name="subcategories[]" value="{0}"><span class="important">{1}</span></label></div>{2}</div>'.format(
                        sub.id, sub.name, sub.description))
        a('</div>')
        return mark_safe(''.join(htmlresult))
    #edit service
    elif subCategories and get_selected_sub_category:
        try:
            htmlresult = []
            a = htmlresult.append
            a('<h6>Seleziona tutti i servizi di cui necessiti.</h6>' if forJobPost else '<h6>Seleziona tutti i servizi che potresti erogare.</h6>')
            a('<div class="subcat-wrapper">')
            for i, sub in enumerate(subCategories, start=0):
                if sub.id in get_selected_sub_category:
                    a(
                        '<div class="sub-cat"><div class="checkbox"><label><input type="checkbox" checked name="subcategories[]" id="id_subcategories_{3}" value="{0}"><span class="important">{1}</span></label></div>{2}</div>'.format(
                            sub.id, sub.name, sub.description, i))
                else:
                    a(
                        '<div class="sub-cat"><div class="checkbox"><label><input type="checkbox" name="subcategories[]" id="id_subcategories_{3}" value="{0}"><span class="important">{1}</span></label></div>{2}</div>'.format(
                            sub.id, sub.name, sub.description, i))
            a('</div>')
            return mark_safe(''.join(htmlresult))
        except:
            return ''
    else:
        return ''



@register.simple_tag(name='services_list')
def servicesList(services=None):
    if services:
        htmlresult = []
        a = htmlresult.append
        for idx, service in enumerate(services):
            a('<div class="card service"><div class="card-header" id="service_{{ forloop.counter }}">')
            a('<span class="float-right badge badge-pill {0}">{1}</span>'.format(
                "badge-info" if service.is_active == True else "badge-danger",
                "Attivo" if service.is_active == True else "Sospeso"))
            a(
                '<h5 class="mb-0"><button class="btn btn-link {0}" data-toggle="collapse" data-target="#collapse{1}" aria-expanded="{2}" aria-controls="collapse{1}">{3}</button></h5></div>'.format(
                    'collapsed' if idx == 1 else '', idx, 'true' if idx == 1 else 'false', service.category.name))
            a('<div id="collapse{0}" class="collapse {1}" aria-labelledby="service_{0}" data-parent="#services-list">'.format(idx,'show' if idx == 1 else ''))
            a('<div class="card-body"><h6 class="small text-uppercase text-primary mt-1">{0}</h6>'.format(_('Servizi proposti')))
            a('<ul>')
            for subcat in service.subcategories.all():
                a('<li><b>{0}</b><br>{1}</li>'.format(subcat.name, subcat.description))
            a('</ul>')
            if service.note:
                a('<div class="service-note"><h5 class="small text-uppercase text-primary mb-1">Note</h5>{0}</div>'.format(service.note))
            a('<div class="service-footer mb-1"><div><span class="title">{0}</span><b>{1} {2}</b></div>'.format(_('Esperienza: '), service.experience, _('anni')))
            a('<div><span class="title">{0}</span><i class="fas {1}"></i></div>'.format(_('Referenze: '), 'fa-user-check' if service.has_references else 'fa-times'))
            a('<div><span class="title">{0}</span><b>{1} €/<small>{2}</small></b></div></div>'.format(_('Prezzo: '), service.price, _('ora')))
            a('<div class="edit-service-footer">')
            a('<button class="edit-service-btn btn btn-small btn-outline-primary ml-1" type="button" data-id="{0}" data-container="edit-service-btn" title="{1}"><i class="fa fa-edit"></i></button>'.format(service.pk, _('Modifica il servizio')))
            a('<button class="suspend-service-btn btn btn-small btn-outline-primary ml-1" type="button" title="{2}" onclick="suspendService({0},{1})"><i class="far {4}"></i> {3}</button>'.format(
                    service.pk, 0 if service.is_active else 1, _('Sospendi il servizio'), _('Pausa') if service.is_active else _('Riprendi'), "fa-pause-circle" if service.is_active else "fa-play-circle"))
            a('<button class="remove-service-btn btn btn-small btn-danger ml-1" type="button" title="{1}" onclick="deleteService(this,{0})"><i class="far fa-trash-alt"></i></button>'.format(
                    service.pk, _('Elimina il servizio')))
            a('</div></div></div></div>')
        return mark_safe(''.join(htmlresult))
    else:
        return ''
