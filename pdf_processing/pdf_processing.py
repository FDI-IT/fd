"""
Re-usable code with which to get PDFs from templates
"""
from django.template import Context
from django import http
from django.template.loader import get_template
import ho.pisa as pisa
from sx.pisa3 import pisa_pdf
import cStringIO as StringIO
import cgi

def render_sub_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = context_dict
    html  = template.render(context)
    result = StringIO.StringIO()
    sub_pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")))
    if sub_pdf.err:
        raise "PDF ERROR"
    return sub_pdf

def render_pdf(pdf_list):
    pdf = pisa_pdf.pisaPDF()
    for sub_pdf in pdf_list:
        pdf.addDocument(sub_pdf)

    return pdf

def render_to_pdf(template_src, context_dict):
    #print "Starting render"
    template = get_template(template_src)
    context = context_dict
    html  = template.render(context)
    result = StringIO.StringIO()
    #print "Rendering to PDF"
    pdf = pisa.CreatePDF(StringIO.StringIO(html.encode("ISO-8859-1")), 
                         result,
                         path="http://192.168.0.10:8000",
                         link_callback = pisa.pisaLinkLoader("http://192.168.0.10:8000").getFileName
                        )
    if not pdf.err:
        return http.HttpResponse(result.getvalue(), content_type='application/pdf')
    return http.HttpResponse('We had some errors<pre>%s</pre>' % cgi.escape(html))
