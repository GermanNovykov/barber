import sqlite3




class Sqlight:

    def __init__(self, database_file):

        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def add_master(self, user_id, name, surname, spec):
        with self.connection:
            self.cursor.execute('INSERT INTO `masterbase` (`user_id`, `name`, `surname`, `spec`) VALUES (?, ?, ?, ?);', (user_id, name, surname, spec))

    def master_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `masterbase` WHERE `user_id` = ?;', (user_id,)).fetchall()
            return list(result)

    def add_klient(self, user_id, name, phone):
        with self.connection:
            self.cursor.execute('INSERT INTO `userbase` (`user_id`, `name`, `phone`) VALUES (?, ?, ?);', (user_id, name, phone))

    def klient_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `userbase` WHERE `user_id` = ?;', (user_id,)).fetchall()
            return bool(len(result))
    def select_all_masters_by_spec(self, spec):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `masterbase` WHERE `spec` = ?;', (spec,))
            return list(result)
    def select_all_masters_by_name(self, name, surname):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `masterbase` WHERE (`name`, `surname`) = (?, ?);', (name, surname))
            return list(result)

    def find_klient_by_id(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `userbase` WHERE `user_id` = ?;', (user_id,))
            return list(result)
    def select_master_by_id_and_spec(self, id, spec):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `masterbase` WHERE (`id`, `spec`) = (?, ?);', (id, spec))
            return result
    def zapis(self, mastername, mastersurname, date, time, username, userphone, procedura):
        with self.connection:
            self.cursor.execute('INSERT INTO `zapisi` (`mastername`, `mastersurname`, `date`, `time`, `username`, `userphone`, `procedura`) VALUES (?, ?, ?, ?, ?, ?, ?);', (mastername, mastersurname, date, time, username, userphone, procedura))

    def check_zapis_time_u_mastera(self, mastername, mastersurname, date, time):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `zapisi` WHERE (`mastername`, `mastersurname`, `date`, `time`) = (?, ?, ?, ?);', (mastername, mastersurname, date, time)).fetchall()
            return bool(len(result))
    def select_all_zapisi_from_master(self, mastername, mastersurname):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `zapisi` WHERE (`mastername`, `mastersurname`) = (?, ?);', (mastername, mastersurname))
            return list(result)
    def select_all_zapisi_from_date_and_master(self, date, mastername, mastersurname):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `zapisi` WHERE (`date`, `mastername`, `mastersurname`) = (?, ?, ?);', (date, mastername, mastersurname))
            return list(result)
    def delte_zapis(self, id):
        with self.connection:
            return self.cursor.execute('DELETE FROM `zapisi` WHERE `id` = ?;', (id,))
    def get_user_id_from_klient(self, name, phone):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `userbase` WHERE (`name`, `phone`)  = (?, ?);', (name, phone))
            return list(result)
    def get_zapis_from_master_and_time(self, mastername, mastersurname, date, time):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `zapisi` WHERE (`mastername`, `mastersurname`, `date`, `time`) = (?, ?, ?, ?);', (mastername, mastersurname, date, time))
            return list(result)
    def select_zapisi_from_klient(self, username, userphone):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `zapisi` WHERE (`username`, `userphone`) = (?, ?) ORDER BY `date` ASC;', (username, userphone))
            return list(result)
    def delete_master_by_userid(self, user_id):
        with self.connection:
            mastername = list(self.cursor.execute('SELECT `name` FROM `masterbase` WHERE `user_id` = ?;', (user_id,)))[0][0]
            self.cursor.execute('DELETE FROM `zapisi` WHERE `mastername` = ?;', (mastername,))
            self.cursor.execute('DELETE FROM `masterbase` WHERE `user_id` = ?;', (user_id,))

    def select_all_zapisi(self):
        with self.connection:
            return list(self.cursor.execute('SELECT * FROM `zapisi`'))
    def select_all_masters(self):
        with self.connection:
            return list(self.cursor.execute('SELECT * FROM `masterbase`;'))
    def select_master_by_id(self, id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `masterbase` WHERE (`id`) = (?);', (id,))
            return list(result)



    def temp_adduser_id(self, user_id):
        with self.connection:
            if not list(self.cursor.execute('SELECT `user_id` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`user_id`) VALUES (?)', (user_id,))
            else:
                return None



    def temp_addmastername(self, user_id, mastername):
        with self.connection:
            if not list(self.cursor.execute('SELECT `mastername` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`mastername`) VALUES (?)', (mastername,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `mastername` = ? WHERE `user_id` = ?;', (mastername, user_id))


    def temp_selectmastername(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `mastername` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_addmastersurname(self, user_id, mastersurname):
        with self.connection:
            if not list(self.cursor.execute('SELECT `mastersurname` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`mastersurname`) VALUES (?)', (mastersurname,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `mastersurname` = ? WHERE `user_id` = ?;', (mastersurname, user_id))
    def temp_selectmastersurname(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `mastersurname` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_addusername(self, user_id, username):
        with self.connection:
            if not list(self.cursor.execute('SELECT `username` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`username`) VALUES (?)', (username,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `username` = ? WHERE `user_id` = ?;', (username, user_id))
    def temp_selectusername(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `username` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_adduserphone(self, user_id, userphone):
        with self.connection:
            if not list(self.cursor.execute('SELECT `userphone` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`userphone`) VALUES (?)', (userphone,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `userphone` = ? WHERE `user_id` = ?;', (userphone, user_id))
    def temp_selectuserphone(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `userphone` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_adddate(self, user_id, date):
        with self.connection:
            if not list(self.cursor.execute('SELECT `date` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`date`) VALUES (?)', (date,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `date` = ? WHERE `user_id` = ?;',
                                           (date, user_id))
    def temp_selectdate(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `date` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_addtime(self, user_id, time):
        with self.connection:
            if not list(self.cursor.execute('SELECT `time` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`time`) VALUES (?)', (time,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `time` = ? WHERE `user_id` = ?;',
                                           (time, user_id))
    def temp_selecttime(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `time` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_addprocedura(self, user_id, procedura):
        with self.connection:
            if not list(self.cursor.execute('SELECT `procedura` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`procedura`) VALUES (?)', (procedura,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `procedura` = ? WHERE `user_id` = ?;',
                                           (procedura, user_id))
    def temp_selectprocedura(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `procedura` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_addspec(self, user_id, spec):
        with self.connection:
            if not list(self.cursor.execute('SELECT `spec` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`spec`) VALUES (?)', (spec,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `spec` = ? WHERE `user_id` = ?;',
                                           (spec, user_id))
    def temp_selectspec(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `spec` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]

    def temp_addtempid(self, user_id, tempid):
        with self.connection:
            if not list(self.cursor.execute('SELECT `tempid` FROM `tempvalues` WHERE `user_id` = ?', (user_id,))):
                return self.cursor.execute('INSERT INTO `tempvalues` (`tempid`) VALUES (?)', (tempid,))
            else:
                return self.cursor.execute('UPDATE `tempvalues` SET `tempid` = ? WHERE `user_id` = ?;',
                                           (tempid, user_id))

    def temp_selecttempid(self, user_id):
        with self.connection:
            return list(self.cursor.execute('SELECT `tempid` FROM `tempvalues` WHERE `user_id` = ?', (user_id,)))[0][0]
    def temp_deleteall(self, user_id):
        with self.connection:
            return self.cursor.execute('DELETE * FROM `tempvalues` WHERE `user_id` = ?;', (user_id,))


