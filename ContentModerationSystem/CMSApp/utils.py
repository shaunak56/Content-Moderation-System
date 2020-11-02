from keras.models import model_from_json
from models import *
import pickle

def moderate():

    json_file = open('static/CMSApp/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("model.h5")
    print("Loaded model from disk")

    # evaluate loaded model on test data
    loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    with open('static/CMSApp/tokenizer.pickle', 'rb') as handle:
        tokenizer = pickle.load(handle)

    print("Loaded tokenizer from disk")

    while 1:
        comments = Content.objects.filter(is_moderated=False)

        for comment in comments:
            moderate_contents(loaded_model,tokenizer,comments)
            comment.is_moderated = True
            comment.save()

            if comment.is_last:
                comment.content_group.report_status = '1'
