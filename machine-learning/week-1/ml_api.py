from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

model = joblib.load("C:\\Users\\adity\\Desktop\\summer-of-code-2024-mine\\machine-learning\\week-1\\model.pkl")
functions = joblib.load("C:\\Users\\adity\\Desktop\\summer-of-code-2024-mine\\machine-learning\\week-1\\functions.pkl")


class request_body(BaseModel):
    step : float
    type : str
    amount : float
    oldbalanceOrg : float
    newbalanceOrig : float
    nameDest : str
    oldbalanceDest : float
    newbalanceDest : float
    isFlaggedFraud : int


@app.get("/")
def intro():
    return {"Message" : "ML Model"}

@app.post("/predict/")
def prediction(data : request_body):
    x = [[data.step, data.type, data.amount, data.oldbalanceOrg, data.newbalanceOrig, data.nameDest, data.oldbalanceDest, data.newbalanceDest, data.isFlaggedFraud]]
    x[0][1] = functions[0].transform([x[0][1]])[0]
    asd = x[0][5][0]
    str1 = np.array([asd])
    x[0][5] = functions[1].transform(str1)[0]
    x = functions[2].transform(x)
    y = model.predict(x)
    y = np.where(y >=0.5, 'Fraud', 'Not Fraud')
    return {"Prediction" : y[0][0]}


if __name__ == "__main__":
    uvicorn.run(app)
