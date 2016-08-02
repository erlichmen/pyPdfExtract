# coding=utf-8
import os

import cStringIO

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdftypes import PDFStream, PDFValueError
from pdfminer.psparser import LIT

LITERAL_FILESPEC = LIT('Filespec')
LITERAL_EMBEDDEDFILE = LIT('EmbeddedFile')


def extract_embedded(data, password):
    def extract1(obj):
        filename = os.path.basename(obj.get('UF') or obj.get('F'))
        file_ref = obj['EF']['F']
        file_obj = doc.getobj(file_ref.objid)
        if not isinstance(file_obj, PDFStream):
            raise PDFValueError(
                'unable to process PDF: reference for %r is not a PDFStream' %
                filename)

        if file_obj.get('Type') is not LITERAL_EMBEDDEDFILE:
            raise PDFValueError(
                'unable to process PDF: reference for %r is not an EmbeddedFile' %
                filename)

        return filename, file_obj.get_data()

    parser = PDFParser(cStringIO.StringIO(data))

    files = set()
    doc = PDFDocument(parser, password)
    for xref in doc.xrefs:
        for obj_id in xref.get_objids():
            obj = doc.getobj(obj_id)
            if isinstance(obj, dict) and obj.get('Type') is LITERAL_FILESPEC:
                filename, data = extract1(obj)

                key = "%s-%s" % (filename, len(data))

                if key not in files:
                    files.add(key)
                    yield filename, data

    return
