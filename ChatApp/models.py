import pymysql
from util.DB import DB
from util.TYPE import TYPE


class dbConnect:
    """
    ユーザー
    """

    def createUser(user_id, user_name, email, password):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "INSERT INTO users (id, user_name, email, password) VALUES (%s, %s, %s, %s);"
            cursor.execute(sql, (user_id, user_name, email, password))
            connection.commit()
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    # getUser -> getUserById, getUserByEmail に拡張
    def getUserById(user_id):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "SELECT * FROM users WHERE id=%s;"
            cursor.execute(sql, (user_id))
            user = cursor.fetchone()
            return user
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    def getUserByEmail(email):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "SELECT * FROM users WHERE email=%s;"
            cursor.execute(sql, (email))
            user = cursor.fetchone()
            return user
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    """
    フレンド
    """

    def createFriendRequest(sender_id, receiver_id):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()

            # 既に申請済みかどうかをチェックするクエリ
            sql = "SELECT * FROM friend_requests WHERE sender_id = %s AND receiver_id = %s"
            cursor.execute(sql, (sender_id, receiver_id))
            existing_request = cursor.fetchone()

            # 既に申請済みの場合は'duplicate'を返す
            if existing_request:
                return "duplicate"

            # 申請が重複していない場合、新しいフレンド申請を作成する
            sql = "INSERT INTO friend_requests(sender_id, receiver_id) VALUES(%s, %s)"
            cursor.execute(sql, (sender_id, receiver_id))
            connection.commit()

            # 成功した場合は'success'を返す
            return "success"

        except Exception as err:
            print(err, "が発生しています")
            # エラーが発生した場合は'error'を返す
            return "error"
        finally:
            cursor.close()

    # 友達申請一覧を取得する
    def getFriendReqList(receiver_id):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()

            # 友達申請一覧を取得するクエリ
            sql = "SELECT fr.sender_id,u1.user_name as sender_name,fr.created_at \
                FROM friend_requests fr INNER JOIN users u1 on sender_id = u1.id \
                WHERE fr.receiver_id=%s;"

            cur.execute(sql, (receiver_id))
            friend_requests = cur.fetchall()

            return friend_requests

        except Exception as e:
            print(e + "が発生しています")
            abort(500)
        finally:
            cur.close()

    # 友達追加処理
    # def addFriend(receiver_id, sender_id):
    #     try:
    #         connection = DB.getConnection()
    #         cursor = connection.cursor()

    #         sql = "INSERT INTO friends (user_id,friends_id) VALUES (%s, %s);"

    #         cursor.execute(sql, (receiver_id, sender_id))
    #         connection.commit()

    #     except Exception as e:
    #         print(e + "が発生しています")
    #         abort(500)
    #     finally:
    #         cursor.close()
    def addFriendAndChannel(
        sender_id, receiver_id, channel_name, channel_description, channel_type, role
    ):
        try:
            connection = DB.getConnection()

            # トランザクションの開始
            with connection.cursor() as cursor:
                # フレンド追加
                sql_add_friend = (
                    "INSERT INTO friends (user_id, friend_id) VALUES (%s, %s);"
                )
                cursor.execute(sql_add_friend, (sender_id, receiver_id))

                # チャンネル追加
                sql_add_channel = "INSERT INTO channels (channel_name, abstract, type) VALUES (%s, %s, %s);"
                cursor.execute(
                    sql_add_channel, (channel_name,
                                      channel_description, channel_type)
                )

                # フレンド追加
                sql_get_channel_id = "SELECT LAST_INSERT_ID() as current_id;"
                cursor.execute(sql_get_channel_id)
                channel_id = cursor.fetchone()['current_id']
                sql_add_channel_user = (
                    "INSERT INTO channel_users (channel_id, user_id, role) VALUES (%s, %s, %s);"
                )
                cursor.execute(sql_add_channel_user,
                               (channel_id, sender_id, role))
                cursor.execute(sql_add_channel_user,
                               (channel_id, receiver_id, role))

                connection.commit()

            return "success"

        except Exception as e:
            print(e + "が発生しています")
            # ロールバック処理
            connection.rollback()
            return "error"

    def deleteFriendRequest(sender_id, receiver_id):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "DELETE FROM friend_requests WHERE (sender_id = %s AND receiver_id = %s)\
                OR (sender_id = %s AND receiver_id = %s);"
            cursor.execute(
                sql, (sender_id, receiver_id, receiver_id, sender_id))
            connection.commit()
        except Exception as err:
            print(err + "が発生しました")
            abort(500)
        finally:
            cursor.close()

    def checkFriend(user_id1, user_id2):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = """
                SELECT CASE WHEN EXISTS (
                SELECT * FROM friends
                WHERE (user_id = %s AND friend_id = %s)
                OR (user_id = %s AND friend_id = %s)
                ) THEN 'Yes'
                ELSE 'No'
                END AS is_friend;
                """
            cursor.execute(sql, (user_id1, user_id2, user_id2, user_id1))
            result = cursor.fetchone()
            return result
        except Exception as err:
            print(err + "が発生しました")
            abort(500)
        finally:
            cursor.close()

    """
    チャンネル
    """

    def getChannelAll():
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "SELECT * FROM channels;"
            cursor.execute(sql)
            channels = cursor.fetchall()
            return channels
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    def getChannelById(channel_id):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "SELECT * FROM channels WHERE id=%s;"
            cursor.execute(sql, (channel_id))
            channel = cursor.fetchone()
            return channel
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    def getChannelByName(channel_name):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "SELECT * FROM channels WHERE channel_name=%s;"
            cursor.execute(sql, (channel_name))
            channel = cursor.fetchone()
            return channel
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    def getChannels(user_id, channel_type):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()

            # publicチャットの時は、where句でuser_idを指定しない
            if channel_type == TYPE.PUBLIC_CHAT:
                sql = "SELECT c.*,cu.user_id FROM channels as c INNER JOIN channel_users as cu ON c.id = cu.channel_id\
                WHERE c.type = %s ORDER BY c.updated_at DESC;"
                cursor.execute(sql, (channel_type))
            else:
                sql = "SELECT c.*,cu.user_id FROM channels as c INNER JOIN channel_users as cu ON c.id = cu.channel_id\
                WHERE cu.user_id = %s AND c.type = %s ORDER BY c.updated_at DESC;"
                cursor.execute(sql, (user_id, channel_type))

            channel = cursor.fetchall()
            return channel
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    # channelsテーブルにレコードを挿入し、挿入したchannel_idを取得する
    def addChannelGetId(newChannelName, newChannelDescription, channelType):
        try:
            connection = DB.getConnection()
            # チャンネル情報をchannelsテーブルに挿入
            cursor = connection.cursor()
            sql = "INSERT INTO channels (channel_name, abstract, type) VALUES (%s, %s, %s);"
            cursor.execute(
                sql, (newChannelName, newChannelDescription, channelType))
            connection.commit()

            # 挿入したチャンネル情報のidを取得
            cursor2 = connection.cursor()
            sql2 = "SELECT LAST_INSERT_ID() as current_id;"
            cursor2.execute(sql2)
            id = cursor2.fetchall()
            return id

        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    # channel_usersテーブルにレコードを挿入
    def addChannelUser(channel_id, user_id, role):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "INSERT INTO channel_users (channel_id, user_id, role) VALUES (%s, %s, %s);"
            cursor.execute(sql, (channel_id, user_id, role))
            connection.commit()
        except Exception as err:
            print(err + "が発生しました")
            abort(500)
        finally:
            cursor.close

    def updateChannel(newChannelName, newChannelDescription, channel_id):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "UPDATE channels SET channel_name=%s, abstract=%s WHERE id=%s;"
            cursor.execute(
                sql, (newChannelName, newChannelDescription, channel_id))
            connection.commit()
        except Exception as err:
            print(err + "が発生しました")
            abort(500)
        finally:
            cursor.close()

    # グループのチャンネルの削除

    def deleteChannel_group(channel_id):
        try:
            connection = DB.getConnection()
            cursor1 = connection.cursor()
            sql1 = "DELETE me from messages me where me.channel_id=%s;"
            cursor1.execute(sql1, (channel_id))

            cursor2 = connection.cursor()
            sql2 = "DELETE cu from channel_users cu where cu.channel_id=%s;"
            cursor2.execute(sql2, (channel_id))

            cursor3 = connection.cursor()
            sql3 = "DELETE c from channels c where c.id=%s"
            cursor3.execute(sql3, (channel_id))
            connection.commit()
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor1.close()
            cursor2.close()
            cursor3.close()

    # パブリックのチャンネルの削除
    def deleteChannel_public(channel_id):
        try:
            connection = DB.getConnection()
            cursor1 = connection.cursor()
            sql1 = "DELETE me from messages me where me.channel_id=%s;"
            cursor1.execute(sql1, (channel_id))

            cursor2 = connection.cursor()
            sql2 = "DELETE cu from channel_users cu where cu.channel_id=%s;"
            cursor2.execute(sql2, (channel_id))

            cursor3 = connection.cursor()
            sql3 = "DELETE c from channels c where c.id=%s"
            cursor3.execute(sql3, (channel_id))
            connection.commit()
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor1.close()
            cursor2.close()
            cursor3.close()

    """
    グループ
    """

    def getFriendsList(user_id, user_id2):
        try:
            conn = DB.getConnection()
            cur = conn.cursor()
            sql = "SELECT fr1.friend_id as id,u1.user_name as name\
                    FROM friends fr1 INNER JOIN users u1 on friend_id = u1.id \
                    WHERE fr1.user_id=%s \
                    UNION SELECT fr1.user_id as id,u1.user_name as name \
                    FROM friends fr1 INNER JOIN users u1 on user_id = u1.id \
                    WHERE fr1.friend_id=%s;"
            cur.execute(sql, (user_id, user_id2))
            friends = cur.fetchall()
            return friends
        except Exception as e:
            print(e + "が発生しています")
            abort(500)
        finally:
            cur.close()

    """
    メッセージ
    """

    def getMessageAll(channel_id, type):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "SELECT m.id,u.id as user_id,u.user_name,m.content ,m.type FROM messages m INNER JOIN users u ON m.user_id = u.id WHERE channel_id=%s AND type=%s;"
            cursor.execute(sql, (channel_id, type))
            messages = cursor.fetchall()
            return messages
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    def createMessage(channel_id, user_id, message, type):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "INSERT INTO messages(channel_id, user_id, content, type) VALUES(%s, %s, %s, %s)"
            cursor.execute(sql, (channel_id, user_id, message, type))
            connection.commit()
        except Exception as err:
            print(str(err) + "が発生しています")
            abort(500)
        finally:
            cursor.close()

    def copyMessage(channel_id, user_id, message):
        try:
            connection = DB.getConnection()

            with connection.cursor() as cursor:
                sql = "INSERT INTO messages(channel_id, user_id, content, type) VALUES(%s, %s, %s, %s)"
                cursor.execute(sql, (channel_id, user_id,
                               message, TYPE.CHAT_MESSAGE))
                cursor.execute(sql, (channel_id, user_id,
                               message, TYPE.NOTE_MESSAGE))

                connection.commit()
        except Exception as err:
            print(err + "が発生しています")
            connection.rollback()
            abort(500)

    def deleteMessage(message_id):
        try:
            connection = DB.getConnection()
            cursor = connection.cursor()
            sql = "DELETE FROM messages WHERE id=%s;"
            cursor.execute(sql, (message_id))
            connection.commit()
        except Exception as err:
            print(err + "が発生しています")
            abort(500)
        finally:
            cursor.close()
