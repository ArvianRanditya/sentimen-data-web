import joblib

rf = joblib.load("models/rf_model.pkl")
tfidf = joblib.load("models/tfidf_sentiment.pkl")

print("Jumlah Tree :", len(rf.estimators_))
print("Jumlah Feature :", len(tfidf.vocabulary_))
print("Classes :", rf.classes_)
print("Feature pertama :", list(tfidf.vocabulary_.keys())[:20])