import sqlite3
conn = sqlite3.connect('report_data.db')
c = conn.cursor()

c.execute('''
            CREATE TABLE IF NOT EXISTS report_data(
            report_id TEXT PRIMARY KEY ,
            status TEXT  default 'running')
        ''')
conn.commit()
conn.close()

class ReportDB: 
    @staticmethod
    def insert_report(report_id):
        conn = sqlite3.connect('report_data.db')
        c = conn.cursor()
        c.execute('''
                INSERT INTO report_data(report_id , status) VALUES(? , 'running')
                ''', (report_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_report(report_id):
        conn = sqlite3.connect('report_data.db')
        c = conn.cursor()
        c.execute('''
                SELECT * FROM report_data WHERE report_id=?
                ''', (report_id,))
        report = c.fetchone()
        conn.close()
        return report
    
    @staticmethod
    def update_report_status_to_finished(report_id):
        conn = sqlite3.connect('report_data.db')
        c = conn.cursor()
        c.execute('''
                UPDATE report_data 
                SET status = 'finished'
                where report_id = ?
                ''', (report_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def getStatusOf(report_id):
        report = ReportDB.get_report(report_id )
        if report == None:
            return "not_found"
        return report[1]

