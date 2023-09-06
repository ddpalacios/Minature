import sqlite3
import requests
from Classes.Audio import Audio


class Soundscape:
    def __init__(self, db_name="Soundscape.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def get_all_audio(self):
        self.cursor.execute("SELECT * FROM Flute")
        audio_records = self.cursor.fetchall()
        audio_list = []

        for audio_record in audio_records:
            audio_data = {
                'id': audio_record[0],
                'file_name': audio_record[1],
                'audio_file': audio_record[2],
                'audio_category': audio_record[3],
                'audio_createDate': audio_record[4]
            }
            audio_list.append(audio_data)

        return audio_list

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Flute (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            audio_file BLOB,
            audio_category TEXT,
            audio_createDate TEXT
        )
        """)
        self.conn.commit()

    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE {table_name}")
        self.conn.commit()

    def insert_audio(self, audio):
        self.cursor.execute(
            "INSERT INTO Flute (audio_file, file_name, audio_category, audio_createDate) VALUES (?, ?, ?, ?)",
            (audio.encoded_audio_blob, audio.audio_name, audio.audio_subtype, audio.create_date))
        self.conn.commit()

    def delete_audio(self, audio_id):
        self.cursor.execute("DELETE FROM Flute WHERE id = ?", (audio_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def extract_and_store_new_audio(self):
        self.drop_table("Flute")
        self.create_tables()
        audio_info_url = "https://life-of-sounds.herokuapp.com/audio_info/"
        response_list_of_all_audio = requests.get(audio_info_url)
        response_list_of_all_audio = response_list_of_all_audio.json()
        for audio_info in response_list_of_all_audio['value']:
            audio_id = audio_info['id']
            audio_name = audio_info['audio_name']
            audio_create_date = audio_info['audio_create_date']
            audio_type = audio_info['audio_type']
            audio_subtype = audio_info['audio_subtype']
            audio_type_id = audio_info['audio_type_id']
            audio_subtype_id = audio_info['audio_subtype_id']

            audio_info_url = f"https://life-of-sounds.herokuapp.com/audio_info/{audio_id}?expand=audio_blob"
            response_of_audio_blob = requests.get(audio_info_url)
            encoded_audio_blob_file = response_of_audio_blob.json()['audio_blob']['audio_blob_file']
            new_audio = Audio(audio_name=audio_name,
                              create_date=audio_create_date,
                              encoded_audio_blob=encoded_audio_blob_file,
                              id=audio_id,
                              audio_blob_id=audio_id,
                              audio_type_id=audio_type_id,
                              audio_subtype_id=audio_subtype_id,
                              audio_type=audio_type,
                              audio_subtype=audio_subtype,
                              audio_image_url=None,
                              )

            self.insert_audio(new_audio)
            print("inserted", audio_subtype)




# data_WareHouse =  DataWarehouse()
#
# department = "Base99"
# data_source = "base99-prod-db_2023-02-07T02-00Z"
# data_stage = "bronze"
#
# current_batch = data_WareHouse.get_current_batch(data_stage, department, data_source)
# if current_batch is None:
#     print(f"No Data available in {data_stage} stage for {department}/{data_source}")
# else:
#     data_WareHouse.create_temporary_views_from_current_batch()
#
#
#
#
#
# ticket_transformed_df = spark.sql("""
# SELECT
# BaseTicket.ticketnumber AS ticket_number,
# BaseTicket.id AS ticket_id,
# BaseTicket.priority AS ticket_priority,
# BaseTicket.subject ,
# BaseTicket.descriptionplaintext AS Description,
# BaseTicket.onhold AS OnHold,
# BaseTicket.status AS Status,
# source.name AS Source,
# customer.customername AS Customer,
# customer.customerid AS CustomerID,
# problemcode.name AS Problem,
# resolution_code.name AS Resolution,
# contact.firstname AS Contact_FirstName,
# contact.lastname AS Contact_LastName,
# contact.emailaddress AS Contact_EmailAddress,
# contact.phonenumber AS Contact_PhoneNumber,
# contact.id AS ContactID,
# BaseTicket.internallastupdate AS Ticket_InternalLastUpdate,
# BaseTicket.createdate AS Ticket_createdate,
# BaseTicket.startdate AS Ticket_StartDate,
# BaseTicket.closedate AS Ticket_CloseDate,
#
# BaseTicket.tickettype AS TicketType,
# BaseTicket.budgettotal AS Ticket_Budget,
# BaseTicket.ticketprivacy AS TicketPrivacy,
# BaseTicket.survey_id AS SurveyID,
# BaseTicket.surveyurl AS SurveyURL,
# BaseTicket.laborcounttotal AS Total_Labor_Count,
# BaseTicket.laborhourstotal AS Total_Labor_Hours,
# BaseTicket.archived AS Ticket_Archived,
# BaseTicket.slaicon AS Ticket_SLA_Icon,
# BaseTicket.slalevel AS Ticket_SLA_Level,
# BaseTicket.subticketcount AS Total_Subtickets,
# BaseTicket.islocked AS Ticket_IsLocked,
# BaseTicket.activitycounttotal AS Ticket_ActivityCount
#
#
# FROM ticketdata_baseticket AS BaseTicket
#
# INNER JOIN ticketdata_baseticket_source AS ticket_source
# ON ticket_source.ticketdata_baseticketid =  BaseTicket.id
# INNER JOIN ticketdata_source AS source
# ON  source.id = ticket_source.ticketdata_sourceid
#
#
# INNER JOIN ticketdata_baseticket_customer AS ticket_customer
# ON ticket_customer.ticketdata_baseticketid  = BaseTicket.id
# INNER JOIN customerdata_customer AS customer
# ON customer.id = ticket_customer.customerdata_customerid
#
#
#
# INNER JOIN ticketdata_ticket_resolution_code AS ticket_resolution_code
# ON ticket_resolution_code.ticketdata_baseticketid  = BaseTicket.id
# INNER JOIN erpdata_resolutioncode AS resolution_code
# ON resolution_code.id = ticket_resolution_code.erpdata_resolutioncodeid
#
#
#
# INNER JOIN ticketdata_baseticket_problemcode AS ticket_problemcode
# ON ticket_problemcode.ticketdata_baseticketid  = BaseTicket.id
# INNER JOIN erpdata_problemcode AS problemcode
# ON problemcode.id = ticket_problemcode.erpdata_problemcodeid
#
#
# INNER JOIN ticketdata_baseticket_contact AS ticket_contact
# ON ticket_contact.ticketdata_baseticketid  = BaseTicket.id
# INNER JOIN customerdata_contact AS contact
# ON contact.id = ticket_contact.customerdata_contactid
#
# """)
#
#
# from pyspark.sql.functions import lit
# from datetime import datetime
#
# # Get the current batch date
# current_year = datetime.now().strftime('%Y')
# current_month = datetime.now().strftime('%m')
# current_day = datetime.now().strftime('%d')
#
# ticket_transformed_df = ticket_transformed_df.withColumn('batch_year', lit(current_year))
# ticket_transformed_df = ticket_transformed_df.withColumn('batch_month', lit(current_month))
# ticket_transformed_df = ticket_transformed_df.withColumn('batch_day', lit(current_day))
#
#
# ticket_transformed_df.createOrReplaceTempView("ticketdata_baseticket")
#
#
# data_stage = 'silver'
# data_WareHouse.write_to_container(data_stage, "Base99", "base99-prod-db_2023-02-07T02-00Z", ticket_transformed_df, merge_key_column='ticket_id')
#
#
# data_stage = 'gold'
# data_WareHouse.write_to_container(data_stage, "Base99", "base99-prod-db_2023-02-07T02-00Z", ticket_transformed_df, merge_key_column='ticket_id')
#
#
# gold_ticket = spark.read.format("delta").load('abfss://impact-analytics-gold-data-lake@impactanalyticsdatalake.dfs.core.windows.net/Base99/base99-prod-db_2023-02-07T02-00Z')
# gold_ticket.createOrReplaceTempView("ticket")
