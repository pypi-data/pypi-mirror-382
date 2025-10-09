import pdfkit

def generate_pdf(template_name, context=None, output_path=None):
    """Genera PDF desde un template Django."""
    if context is None:
        context = {}

    from django.template.loader import render_to_string
    html = render_to_string(f'sistema/{template_name}', context)
    return _generate_pdf_from_html(html, output_path)


def generate_pdf_from_string(html_content, output_path=None):
    """Genera PDF directamente desde un string HTML."""
    return _generate_pdf_from_html(html_content, output_path)


def _generate_pdf_from_html(html, output_path=None):
    """Función interna para generar PDF desde HTML."""
    options = {
        'enable-local-file-access': True,
        'page-size': 'Letter',
        'encoding': 'UTF-8',
        'margin-top': '1.5cm',
        'margin-right': '1cm',
        'margin-left': '1cm',
        'margin-bottom': '15mm',
    }

    try:
        pdf = pdfkit.from_string(html, False, options=options)
    except Exception as e:
        raise RuntimeError(f"Error al generar PDF: {e}")

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf)
        return output_path

    return pdf