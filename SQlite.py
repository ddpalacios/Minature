import sqlite3
from sqlite3 import Error


class SQLLite:
    def __init__(self):
        self.database = r"C:\sqlite\db\Miniature.db"
        self.conn = None

    def close(self):
        self.conn.close()

    def __create_connection(self):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(self.database)
            self.conn = conn

        except Error as e:
            print(e)

        return self.conn

    def execute_query(self, query):
        if self.conn is None:
            self.conn = self.__create_connection()

        self.conn.row_factory = sqlite3.Row
        c = self.conn.cursor()
        returned_records = c.execute(query)
        self.conn.commit()

        return returned_records

    def create_miniature_environment_tables(self):
        sql_create_environment_table = """ CREATE TABLE IF NOT EXISTS Environment (
                                           id	INTEGER PRIMARY KEY AUTOINCREMENT,
                                           pixelSize	INTEGER,
                                           TotalPopulation	INTEGER,
                                           TotalEnergyBlocks	INTEGER,
                                           TotalSpecies	INTEGER,
                                           frames_per_second	INTEGER,
                                           env_width	INTEGER,
                                           env_height	INTEGER,
                                           AverageSpeciesFitness	INTEGER,
                                           Duration	INTEGER,
                                           StartDateTime	TEXT,
                                           EndDateTime	TEXT,
                                           CreateDateTime	TEXT,
                                           TotalGenerations	INTEGER,
                                           NodeCount	INTEGER,
                                           ConnectionCount	INTEGER,
                                           isRunning	INTEGER

                                           ); """
        sql_create_species_table = """ CREATE TABLE IF NOT EXISTS Species (
                                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                                               EnvID INTEGER,
                                               TotalMemberSize	INTEGER,
                                               AverageFitnessScore	INTEGER,
                                               StartDateTime TEXT,
                                               IsExtinct INTEGER,
                                                FOREIGN KEY (EnvID) REFERENCES Environment (id)
                                               ); """
        sql_create_energy_table = """ CREATE TABLE IF NOT EXISTS Energy (
                                                  id	INTEGER PRIMARY KEY AUTOINCREMENT,
                                                   EnvID	INTEGER,
                                                   PosX	INTEGER,
                                                   PosY	INTEGER,
                                                   StartDateTime	TEXT,
                                                   EndDateTime	TEXT,
                                                   DurationInSec	INTEGER,
                                                    FOREIGN KEY (EnvID) REFERENCES Environment (id)
                                                   ); """
        sql_create_cell_table = """CREATE TABLE IF NOT EXISTS Cell (
                                           id	INTEGER PRIMARY KEY AUTOINCREMENT,
                                           EnvID	INTEGER,
                                           AdjustedFitness	INTEGER,
                                           fitness	INTEGER,
                                           isAlive	INTEGER,
                                           TotalTimeAliveInTicks INTEGER,
                                           TotalEnergyRemaining	INTEGER,
                                           TotalEnergyObtained	INTEGER,
                                           PosX	INTEGER,
                                           PosY	INTEGER,
                                           DirX	INTEGER,
                                           DirY	INTEGER,
                                           UpdateDateTime	TEXT,
                                           CreateDateTime	TEXT,
                                           EndDateTime	TEXT,
                                           GenerationNumber	INTEGER,
                                           TotalNodes	INTEGER,
                                           TotalConnections	INTEGER,
                                           SpeciesID 	INTEGER,
                                           FOREIGN KEY (EnvID) REFERENCES Environment (id),
                                           FOREIGN KEY (SpeciesID) REFERENCES Species (id)
                                       );"""

        self.execute_query(sql_create_environment_table)
        self.execute_query(sql_create_species_table)
        self.execute_query(sql_create_energy_table)
        self.execute_query(sql_create_cell_table)


if __name__ == '__main__':
    sql = SQLLite()
    query = '''DELETE from Cell'''
    sql.execute_query(query)
    query = '''DELETE from Energy'''
    sql.execute_query(query)




