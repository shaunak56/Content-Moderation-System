from .models import Content, ContentGroup, User, Report
from .constants import target_classes

from django.core.exceptions import ObjectDoesNotExist

from keras.models import model_from_json
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
import pandas as pd
import numpy as np
import json
import sys, traceback


def error():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("\nLINE = :", exc_traceback.tb_lineno)
    formatted_lines = traceback.format_exc().splitlines()
    print("ERROR = ", formatted_lines[-1], end="\n")


def PredictToxicity(model, tokenizer, content_obj):

    report_json = {"Error"}

    try:
        report_obj = Report.objects.get(content=content_obj)
    except:
        report_obj = Report.objects.create(content=content_obj)
    try:
        content_text = content_obj.text
        tokenized_text = tokenizer.texts_to_sequences([content_text])
        padded_seq = pad_sequences(tokenized_text, maxlen=400)
        y_hat_test_proba_lst_deep = model.predict(padded_seq)
        report_json = {}
        for i in range(len(target_classes)):
            report_json[target_classes[i]] = round(y_hat_test_proba_lst_deep[0], 0)
        return True
    except Exception as e:
        error()
        print("ERROR IN UsageAnalysisAPI", str(e))
        report_obj.report = json.dumps(report_json)
        report_obj.save()
        return False
