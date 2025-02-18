# NOTE:
# - This script uses a **mocked Asana API**.
# - Disclaimer: I am not entirely sure how the actual Asana API looks or functions. The implementation here is purely fictional and created as an example.

import sqlite3
from typing import Any, Self
import uuid
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AsanaProject:
    id: str
    name: str
    link: str

@dataclass
class AsanaTask:
    id: str
    project_id: str
    name: str
    due_date: str
    status: str
    link: str

@dataclass
class AsanaProjectUpdate:
    name: str

@dataclass
class AsanaTaskUpdate:
    name: str
    due_date: str
    status: str
    
class SqlLiteClient:
    def __init__(self, dbName: str):
        self.__conn = sqlite3.connect(dbName)
        self.__conn.row_factory = sqlite3.Row
        self.__cursor = self.__conn.cursor()        
        
    def execute(self, sql: str,  parameters = (), /) -> Self:
        self.__cursor.execute(sql, parameters)
        
    def fetchone(self) -> Any:
        return self.__cursor.fetchone()
    
    def fetchall(self) -> list[Any]:
        return self.__cursor.fetchall()    

    def commit(self):
        self.__conn.commit()
        
    def close(self):
        self.__conn.close()
        

class Asana_Api:
    def __init__(self):
        self.__create_tables()
    
    def __create_tables(self):
        client = SqlLiteClient("asana.db")
        try:
            client.execute("""
            CREATE TABLE IF NOT EXISTS Project (
                Id TEXT COLLATE NOCASE PRIMARY KEY,
                Name TEXT COLLATE NOCASE NOT NULL
            )
            """)        

            # Create the Task table
            client.execute("""
            CREATE TABLE IF NOT EXISTS Task (
                Id TEXT COLLATE NOCASE PRIMARY KEY,
                ProjectId TEXT NOT NULL,
                Name TEXT COLLATE NOCASE NOT NULL,
                DueDate TEXT,
                Status TEXT,
                FOREIGN KEY (ProjectId) REFERENCES Project (Id)
            )
            """)

            client.commit()
        finally:
            client.close()

    def purge_all_data(self):
        client = SqlLiteClient("asana.db")
        try:            
            client.execute("DROP TABLE IF EXISTS Task")
            client.execute("DROP TABLE IF EXISTS Project")        
            client.commit()
        finally:
            client.close()
        
        self.__create_tables()

    #----------------------#
    #      PROJECTS        #
    #----------------------#
    def create_project(self, project_name: str) -> AsanaProject:
        project_id = str(uuid.uuid4())
        client = SqlLiteClient("asana.db")
        try:
            client.execute("INSERT INTO Project (Id, Name) VALUES (?, ?)", (project_id, project_name))
            client.commit()
            return AsanaProject(
                project_id, 
                project_name,
                f"https://example.com/projects/{project_id}"
            )            
        finally:
            client.close()            

    def get_project_id(self, project_name: str) -> str:
        client = SqlLiteClient("asana.db")
        try:
            client.execute("SELECT Id FROM Project WHERE Name = ?", (project_name,))
            result = client.fetchone()
            return result[0] if result else None
        finally:
            client.close()


    def get_project_by_id(self, project_id: str) -> AsanaProject:
        client = SqlLiteClient("asana.db")
        try:
            client.execute("SELECT Id, Name FROM Project WHERE Id = ?", (project_id,))
            entity = client.fetchone()
            return self.__map_project__(entity) if entity else None
        finally:
            client.close()
    
    def get_project_by_name(self, project_name: str) -> AsanaProject:
        client = SqlLiteClient("asana.db")
        try:
            client.execute("SELECT Id, Name FROM Project WHERE Name = ?", (project_name,))
            entity = client.fetchone()
            return self.__map_project__(entity) if entity else None
        finally:
            client.close()
    

    def update_project(self, project_id: str, model: AsanaProjectUpdate) -> AsanaProject:
        entity = self.get_project_by_id(project_id)
        client = SqlLiteClient("asana.db")
        try:
            if not entity:
                return None

            client.execute("UPDATE Project SET Name = ? WHERE Id = ? ", (model.name, project_id))
            client.commit()

            entity.name = model.name
            return entity
        finally:
            client.close()
    

    def get_projects(self) -> list[AsanaProject]:
        client = SqlLiteClient("asana.db")
        try:
            client.execute("SELECT Id, Name FROM Project")
            entities = client.fetchall()
            return [self.__map_project__(entity) for entity in entities]
        finally:
            client.close()
    

    def delete_project_by_id(self, project_id: str) -> bool:
        client = SqlLiteClient("asana.db")
        try:
            if project_id:
                client.execute("DELETE FROM Task WHERE ProjectId = ?", (project_id,))
                client.execute("DELETE FROM Project WHERE Id = ?", (project_id,))
                client.commit()
                return True

            return False
        finally:
            client.close()
    

    def delete_project(self, project_name: str) -> bool:
        project_id = self.get_project_id(project_name)
        return self.delete_project_by_id(project_id)

    #----------------------#
    #         TASKS        #
    #----------------------#
    def create_task(self, project_id: str, task_name: str, due_date: str = None, status: str = "Not Started") -> AsanaTask:
        task_id = str(uuid.uuid4())

        if not due_date or due_date == "today":
            due_date = str(datetime.now().date())

        client = SqlLiteClient("asana.db")
        try:
            client.execute("INSERT INTO Task (Id, ProjectId, Name, DueDate, Status) VALUES (?, ?, ?, ?,?)", (task_id, project_id, task_name, due_date, status))
            client.commit()
            return AsanaTask(
                id=task_id,
                project_id=project_id,
                name=task_name,
                due_date=due_date,
                status=status,
                link=f"https://example.com/tasks/{task_id}")
        finally:
            client.close()
            

    def get_task_by_id(self, task_id: str) -> AsanaTask:
        client = SqlLiteClient("asana.db")
        try:        
            client.execute("SELECT Id, ProjectId, Name, DueDate, Status FROM Task WHERE Id = ?", (task_id,))
            entity = client.fetchone()
            return None if not entity else self.__map_task__(entity)
        finally:
            client.close()
    

    def get_task_by_name(self, project_name: str, name: str) -> AsanaTask:
        project = self.get_project_by_name(project_name)
        if not project:
            return None
        
        client = SqlLiteClient("asana.db")
        try:        
            client.execute("SELECT Id, ProjectId, Name, DueDate, Status FROM Task WHERE ProjectId = ? AND Name = ?", (project.id, name))
            entity = client.fetchone()
            return None if not entity else self.__map_task__(entity)
        finally:
            client.close()
    

    def get_tasks_by_project_id(self, project_id: str) -> list[AsanaTask]:
        client = SqlLiteClient("asana.db")
        try:                
            client.execute("SELECT Id, ProjectId, Name, DueDate, Status FROM Task WHERE ProjectId = ?", (project_id, ))
            entities = client.fetchall()
            return [self.__map_task__(entity) for entity in entities]
        finally:
            client.close()
        

    def get_tasks_by_project_name(self, project_name: str) -> list[AsanaTask]:
        sql = (
            "SELECT t.Id, t.ProjectId, t.Name, t.DueDate, t.Status "
            "FROM Task AS t "
            "JOIN Project AS p ON t.ProjectId = p.Id "            
            "WHERE p.Name = ? "            
        )
        
        client = SqlLiteClient("asana.db")
        try:                
            client.execute(sql, (project_name, ))
            entities = client.fetchall()
            return [self.__map_task__(entity) for entity in entities]
        finally:
            client.close()


    def update_task_status(self, task_id: str, status: str) -> bool:
        if task_id and status:
            client = SqlLiteClient("asana.db")
            try:                            
                client.execute("UPDATE Task SET Status = ? WHERE Id = ?", (status, task_id,))
                client.commit()
                return True
            finally:
                client.close()

        return False

    def update_task(self, task_id: str, model: AsanaTaskUpdate) -> AsanaTask:
        entity = self.get_task_by_id(task_id)
        if not entity:
            return None

        sql = (
            "UPDATE Task "
            "SET Name = ?, DueDate = ?, Status = ? "
            "WHERE Id = ?"
        )

        client = SqlLiteClient("asana.db")
        try:                            
            client.execute(sql, (model.name, model.due_date, model.status, task_id))
            client.commit()
        finally:
            client.close()        

        entity.name = model.name
        entity.due_date = model.due_date
        entity.status = model.due_date

        return entity

    def delete_task_by_id(self, task_id: str) -> bool:
        if task_id:
            client = SqlLiteClient("asana.db")
            try:                                        
                client.execute("DELETE FROM Task WHERE Id = ?", (task_id,))
                client.commit()
                return True
            finally:
                client.close()        

        return False

    def delete_task_by_name(self, project_name: str, name: str) -> bool:
        project = self.get_project_by_name(project_name)
        if not project:
            return False

        if name:
            client = SqlLiteClient("asana.db")
            try:                                                    
                client.execute("DELETE FROM Task WHERE ProjectId = ? AND Name = ?", (project.id, name))
                client.commit()
                return True
            finally:
                client.close()        

        return False

    def __map_task__(self, entity: sqlite3.Row) -> AsanaTask:
        return AsanaTask(
            id=entity["Id"],
            project_id=entity["ProjectId"],
            name=entity["Name"],
            due_date=entity["DueDate"],
            status=entity["Status"],
            link=f"https://example.com/tasks/{entity["Id"]}")

    def __map_project__(self, entity: sqlite3.Row) -> AsanaProject:
        return AsanaProject(
            id=entity["Id"],
            name=entity["Name"],
            link=f"https://example.com/projects/{entity["Id"]}")
