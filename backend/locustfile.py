from locust import HttpUser, task, between

class ZenJPUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_score_7203(self):
        self.client.get('/api/score/7203')

    @task(2)
    def get_score_6758(self):
        self.client.get('/api/score/6758')

    @task(1)
    def get_score_9984(self):
        self.client.get('/api/score/9984')
