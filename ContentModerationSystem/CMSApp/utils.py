from .constants import target_classes
from .models import *
from ContentModerationSystem import settings

from django.core.exceptions import ObjectDoesNotExist

from keras.models import model_from_json
from keras.models import model_from_json
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
import pandas as pd
import numpy as np
import json
import sys, traceback
import pickle


def error():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("\nLINE = :", exc_traceback.tb_lineno)
    formatted_lines = traceback.format_exc().splitlines()
    print("ERROR = ", formatted_lines[-1], end="\n")


def PredictToxicity(model, tokenizer, content_obj):

    try:
        report_obj = Report.objects.get(content=content_obj)
    except:
        report_obj = Report.objects.create(content=content_obj)
    try:
        content_text = content_obj.text
        tokenized_text = tokenizer.texts_to_sequences([content_text])
        padded_seq = pad_sequences(tokenized_text, maxlen=400)
        y_hat_test_proba_lst_deep = model.predict(padded_seq)[0]
        report_json = {"Status": "Success", "text_id": content_obj.text_id}
        for i in range(len(target_classes)):
            report_json[target_classes[i]] = str(int(round(y_hat_test_proba_lst_deep[i], 0)))
        report_obj.report = json.dumps(report_json)
        report_obj.save()
    except Exception as e:
        error()
        print("ERROR ", str(e))
        report_json = {"Status": "Error", "text_id": content_obj.text_id}
        report_obj.report = json.dumps(report_json)
        report_obj.save()


def moderate():
    json_file = open(settings.BASE_DIR + '/CMSApp/static/CMSApp/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(settings.BASE_DIR + "/CMSApp/static/CMSApp/model.h5")
    print("Loaded model from disk")

    # evaluate loaded model on test data
    loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    with open(settings.BASE_DIR + '/CMSApp/static/CMSApp/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    print("Loaded tokenizer from disk")

    while 1:
        comments = Content.objects.filter(is_moderated=False)

        for comment in comments:
            PredictToxicity(loaded_model, tokenizer, comment)
            comment.is_moderated = True
            comment.save()

            if comment.is_last:
                comment.content_group.report_status = '1'
                comment.content_group.save()
        break