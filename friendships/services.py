from friendships.models import Friendship


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # 错误的写法一
        # 这种写法会导致 N + 1 Queries 的问题
        # 即，filter 出所有 friendships 耗费了一次 Query
        # 而 for 循环每个 friendship 取 from_user 又耗费了 N 次 Queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # 错误的写法二
        # 这种写法是使用了 JOIN 操作，让 friendship table 和 user table 在 from_user
        # 这个属性上 join 了起来。join 操作在大规模用户的 web 场景下是禁用的，因为非常慢。
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # 虽然下面这句.from_user不需要再Query，但是前面JOIN了，非常慢
        # return [friendship.from_user for friendship in friendships]

        # 正确的写法一，自己手动 filter id，使用 IN Query 查询
        # 1，3各一个Query,第二句.from_user_id在friendships里面可以直接查到，不需要Query
        # get_followers这个方法也可以只得到from_user_id，不需要得到from_user的list，这样的话就只需要1，2
        # friendships = Friendship.objects.filter(to_user=user)  1
        # follower_ids = [friendship.from_user_id for friendship in friendships]  2
        # followers = User.objects.filter(id__in=follower_ids)  3

        # 正确的写法二，使用 prefetch_related，会自动执行成两条语句，用 In Query 查询
        # 实际执行的 SQL 查询和上面是一样的，一共两条 SQL Queries
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]
