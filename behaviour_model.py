from sklearn.ensemble import IsolationForest


class BehaviourAnomalyModel:

    def __init__(self):

        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.10,
            random_state=42
        )

    def train(self, X):

        self.model.fit(X)

    def predict(self, X):

        predictions = self.model.predict(X)

        anomaly_scores = (
            self.model
            .decision_function(X)
        )

        results = []

        for prediction, score in zip(
            predictions,
            anomaly_scores
        ):

            if prediction == -1:
                label = "ANOMALOUS"
            else:
                label = "NORMAL"

            results.append({
                "label": label,
                "score": float(score)
            })

        return results