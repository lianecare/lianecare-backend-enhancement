import csv
import datetime

from allauth.account.models import EmailAddress
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from lianecare.courses.models import Course, Enrollment
from lianecare.solace.models import CaregiverProMore, Service, SubCategory, JobPost, Proposal
from django.db import connection

def text_mapper(val: str)-> str:
    return str(val).replace("\n","").replace("\r","").replace("\t","")

def date_mapper(val: datetime.datetime)-> str:
    return val.strftime("%Y-%m-%d")

def nbool_mapper(val: bool)-> str:
    if val is None:
        return ""
    if val:
        return "Si"
    return "No"

def enrollment_status_mapper(val: int)-> str:

    for t in Enrollment.TIPO_STATO:
        if t[0] == val:
            return t[1]

    return Enrollment.TIPO_STATO[0][1]

@login_required
def \
    caregiverpro_export_view(request):
    filename = "CaregiversPRO_%s.csv" % datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    response = HttpResponse(
        content_type='text/csv'
    )
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    subquery_jobposts_count = "(SELECT COUNT(*) FROM solace_jobpost JP WHERE EXISTS(select 0 from solace_jobpost_subcategories JPSC where JPSC.jobpost_id = JP.id and JPSC.subcategory_id = subcat.id)) as jobposts_count"
    subquery_proposals_count = "(SELECT COUNT(*) FROM solace_proposal P INNER JOIN solace_jobpost PJP on PJP.id = P.jobpost_id WHERE P.caregiverpro_id = u.id AND EXISTS(select 0 from solace_jobpost_subcategories PJPSC where PJPSC.jobpost_id = PJP.id and PJPSC.subcategory_id = subcat.id)) as proposals_count"
    fields = [
        ("u.username", "User Name", text_mapper),
        ("u.first_name", "Cognome", text_mapper),
        ("u.last_name", "Nome", text_mapper),
        ("u.email", "Email", text_mapper),
        ("cg.identity_checked", "Identità verificata", text_mapper),
        ("cg.phone", "Telefono", text_mapper),
        ("cg.gender", "Sesso",  text_mapper),
        ("cg.birthday", "Data Nascita", date_mapper),
        ("cg.nationality", "Nazionalita", text_mapper ),
        ("cg.city", "Citta", text_mapper),
        ("cg.postcode", "CAP", text_mapper),
        ("cg.region", "Regione", text_mapper),
        ("u.date_joined", "Data Registrazione", date_mapper),
        ("cg.how_know_us", "Come ci hai conosciutoq", text_mapper),
        #TODO profilo completo
        ("cg.is_graduate", "Laurea ambito sanitario", nbool_mapper),
        ("cg.is_certificated", "Certificazione ambito sanitario", nbool_mapper),
        ("cg.first_aid", "Attestato primo soccorso", nbool_mapper),
        ("cg.child_trainer", "Formatore ufficiale infanzia", nbool_mapper),
        ("cg.driving_license", "Patente", nbool_mapper),
        ("cg.has_car", "Automunito", nbool_mapper),
        ("cat.name", "Categoria", text_mapper),
        ("subcat.name", "Sottocategoria", text_mapper),
        ("svc.experience", "Esperienza (anni)", text_mapper),
        ("svc.has_references", "Ha Referenze", nbool_mapper),
        ("svc.price", "Prezzo", text_mapper),
        ("svc.note", "Note", text_mapper),
        (subquery_jobposts_count, "Pubblicazione Job Post", text_mapper),
        (subquery_proposals_count, "Match Job Post", text_mapper),
    ]
    all_courses = Course.objects.all()
    for c in all_courses:
        q = "(SELECT e.status from courses_enrollment e WHERE e.user_id = u.id AND e.course_id = " + str(c.id) + " )"
        fields.append(
            (q, c.title, enrollment_status_mapper)
        )
    fields_str = ", ".join(map(lambda x: x[0], fields))

    query = "SELECT " + fields_str + \
            " FROM public.solace_caregiverpromore cg" \
            " INNER JOIN users_user u ON cg.user_id = U.id" \
            " LEFT JOIN solace_service svc ON svc.caregiver_id = u.id" \
            " LEFT JOIN solace_category cat ON svc.category_id = cat.id" \
            " LEFT JOIN solace_service_subcategories ssc ON ssc.service_id = svc.id" \
            " LEFT JOIN solace_subcategory subcat ON ssc.subcategory_id = subcat.id" \
            " ORDER BY u.date_joined"

    print(query)
    writer = csv.writer(response, delimiter=";")
    header_row = []
    for f in fields:
        header_row.append(f[1])

    writer.writerow(header_row)

    with connection.cursor() as cursor:
        cursor.execute(query)

        for cursor_row in cursor.fetchall():
            res_row = []

            i = 0
            for cursor_col in cursor_row:
                res_row.append(
                    fields[i][2](cursor_col)
                )
                i = i + 1

            writer.writerow(res_row)

    return response
