from testing.testcases import TestCase


# 先测试Model,再migrate

class CommentModelTests(TestCase):

    def test_comment(self):
        user = self.create_user('linghu')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertNotEqual(comment.__str__(), None)
