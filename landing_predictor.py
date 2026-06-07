# landing_predictor.py
"""
Lightweight landing success predictor with sklearn fallback.
If sklearn is not installed, uses heuristic.
"""
import numpy as np
try:
    from sklearn.linear_model import LogisticRegression
    SKLEARN = True
except Exception:
    SKLEARN = False

class LandingPredictor:
    def __init__(self):
        self.model = None
        if SKLEARN:
            self.model = LogisticRegression()
            X = np.random.rand(300,5)
            y = (X[:,0]*0.6 + X[:,1]*0.2 + np.random.rand(300)*0.2 > 0.5).astype(int)
            self.model.fit(X,y)

    def predict(self, features: dict) -> float:
        arr = np.array([[features.get("score",50)/100.0, features.get("wind",5)/20.0, features.get("area",5000)/10000.0, features.get("obstacles",0), features.get("visibility",1)]])
        if self.model is not None:
            p = self.model.predict_proba(arr)[:,1][0]
            return float(p)
        # heuristic fallback
        score = features.get("score",50)
        wind = features.get("wind",5)
        area = features.get("area",5000)
        obstacles = features.get("obstacles",0)
        base = (score/100.0)*0.75 + (min(area/15000,1.0))*0.15 + (1.0 - min(wind/25.0,1.0))*0.1
        base -= obstacles*0.2
        return float(max(0.0, min(1.0, base)))