# NOTE:
# - This section defines the Asana tools to be utilized by the agent.
# - Pydantic AI tools offer multiple flavors for defining tools: `plan` (decorator), `context` (decorator), and `tool definition`. See the documentation: https://ai.pydantic.dev/tools/
# - For this example, I opted for the `tool definition` flavor because it is loosely coupled to the agent until runtime.
#   This approach ensures flexibility, allowing the tools to be reused by various Asana agents (e.g., Console, Streamlit, etc.).

import json
from typing import List
from pydantic_ai.tools import Tool
from asana_api import Asana_Api, AsanaProject, AsanaTask, AsanaTaskUpdate

class AsanaTools:
    def __init__(self):
        self.__asana__ = Asana_Api()
        self.__tools__ : List[Tool] = []

         # project related tools
        self.__tools__.append(Tool(name = "create_project", function = self.create_project, description="Creates a project by name"))
        self.__tools__.append(Tool(name = "get_project_id", function = self.get_project_id, description="Gets a project id by project name"))
        self.__tools__.append(Tool(name = "get_project_by_id", function = self.get_project_by_id, description="Gets a project object by project id"))
        self.__tools__.append(Tool(name = "get_project_by_name", function = self.get_project_by_name, description="Gets a project object by project name"))
        self.__tools__.append(Tool(name = "get_projects", function = self.get_projects, description="Gets all existing project objects. Takes no arguments."))
        self.__tools__.append(Tool(name = "update_project", function = self.update_project, description="Updates an existing project object for a given project id"))
        self.__tools__.append(Tool(name = "delete_project_by_id", function = self.delete_project_by_id, description="Deletes an existing project object by project id"))
        self.__tools__.append(Tool(name = "delete_project", function = self.delete_project, description="Deletes an existing project object by project name"))

        # task related tools
        self.__tools__.append(Tool(name = "create_task", function = self.create_task, description="Creates a task by name for a given project id"))
        self.__tools__.append(Tool(name = "get_task_by_id", function = self.get_task_by_id, description="Gets a task by task id"))
        self.__tools__.append(Tool(name = "get_task_by_name", function = self.get_task_by_name, description="Gets a task for a given project using the project name and task name"))
        self.__tools__.append(Tool(name = "get_tasks_by_project_id", function = self.get_tasks_by_project_id, description="Gets all existing task objects for a given project id"))
        self.__tools__.append(Tool(name = "get_tasks_by_project_name", function = self.get_tasks_by_project_name, description="Gets all existing task objects for a given project name"))
        self.__tools__.append(Tool(name = "update_task_status", function = self.update_task_status, description="Updates an existing task object's status for a given task id"))
        self.__tools__.append(Tool(name = "update_task", function = self.update_task, description="Updates an existing task object for a given task id"))
        self.__tools__.append(Tool(name = "delete_task_by_id", function = self.delete_task_by_id, description="Deletes an existing task object by task id"))
        self.__tools__.append(Tool(name = "delete_task_by_name", function = self.delete_task_by_name, description="Deletes an existing task object for a given project name and for a given task name"))   

    #----------------------#
    #      PROJECTS        #
    #----------------------#

    def create_project(self, project_name: str) -> AsanaProject:
        """
        Creates a project by name.

        Example call: create_project("Test Project")
        
        Args:
            project_name (str): The name of the project to create.
        Returns:
            AsanaProject: A project object that was created or an error message if the API call threw an error.
        """

        return self.__asana__.create_project(project_name)

    def get_project_id(self, project_name: str) -> str:
        """
        Gets a project id by project name.

        Example call: get_project_id("Test Project")
        
        Args:
            project_name (str): The name of the project to get the project id.
        Returns:
            str: A project id if it exists, else None if not found, or an error message if the API call threw an error.            
        """

        project_id = self.__asana__.get_project_id(project_name)
        return project_id

    def get_project_by_id(self, project_id: str) -> AsanaProject:
        """
        Gets a project object by project id.

        Example call: get_project_by_id("Project Id")
        
        Args:
            project_id (str): The the project id to get the project object.
        Returns:
            AsanaProject: A project object if it exists, else None if not found, or an error message if the API call threw an error. 
        """

        project = self.__asana__.get_project_by_id(project_id)
        return project

    def get_project_by_name(self, project_name: str) -> AsanaProject:
        """
        Gets a project object by project name.

        Example call: get_project_by_name("Project name")
        
        Args:
            project_name (str): The the project name to get the project object.
        Returns:
            AsanaProject: A project object if it exists, else None if not found, or an error message if the API call threw an error.             
        """

        project = self.__asana__.get_project_by_name(project_name)
        return project

    def get_projects(self) -> List[AsanaProject]:
        """
        Gets all existing project objects.

        Example call: get_projects()            
        
        Returns:
            List[AsanaProject]: A list of project objects if any, or an error message if the API call threw an error. 
        """

        projects = self.__asana__.get_projects()        
        return projects

    def update_project(self, project_id: str, model: AsanaProject) -> AsanaProject:
        """
        Updates an existing project object for a given project id.

        Example call: update_project("Project Id", model)
        
        Args:
            project_id (str): The project id to update the project object.
            model (AsanaProject): A json representation of a model with the following properties:
                {
                    "name": "(str) The name of the project to update"
                }
        Returns:
            AsanaProject: Updated project object if successful, else None if not found, or an error message if the API call threw an error.
        """
        project = self.__asana__.update_project(project_id, model)
        return project

    def delete_project_by_id(self, project_id: str) -> bool:
        """
        Deletes an existing project object by project id.

        Example call: delete_project_by_id("Project Id")
        
        Args:
            project_id (str): The project id to delete an existing project object.
        Returns:
            bool: True if deleted, else false not found, or an error message if the API call threw an error. 
        """

        result = self.__asana__.delete_project_by_id(project_id)
        return result

    def delete_project(self, project_name: str) -> bool:
        """
        Deletes an existing project object by project name.

        Example call: delete_project("Project Name")
        
        Args:
            project_name (str): The project name to delete the project object.
        Returns:
            bool: True if deleted, else false not found, or an error message if the API call threw an error. 
        """

        result = self.__asana__.delete_project(project_name)
        return result

    #----------------------#
    #         TASKS        #
    #----------------------#

    def create_task(self, project_id: str, task_name: str, due_date: str = None, status: str = "Not Started") -> AsanaTask:
        """
        Creates a task by name for a given project id.

        Example call: create_task("Project Id", "Test Task", "2021-12-31", "Not Started")
        
        Args:
            task_name (str): The task name to create.
            project_id (str): The project id to create the task under.
            due_date (str): The date the task is due in the format YYYY-MM-DD. If not given, the current day is used.
            status (str): The status of the task. Possible values: ['Not Started', 'In Progress', 'Completed']. Default is 'Not Started'. 
        Returns:
            AsanaTask: created task object if successful, or an error message if the API call threw an error.
        """

        task = self.__asana__.create_task(project_id, task_name, due_date, status)        
        return task

    def get_task_by_id(self, task_id: str) -> AsanaTask:
        """
        Gets a task by task id.

        Example call: get_task_by_id("Task Id")
        
        Args:
            task_id (str): The task id to get the task object.
        Returns:
            AsanaTask: task object if it exists, else None if not found, or an error message if the API call threw an error.            
        """

        task = self.__asana__.get_task_by_id(task_id)
        return task

    def get_task_by_name(self, project_name: str, name: str) -> AsanaTask:
        """
        Gets a task for a given project using the project name and task name.

        Example call: get_task_by_name("Project Name", "Task Name")
        
        Args:
            project_name (str): The project name where the task belongs too.
            name (str): The task name get to get the task object.
        Returns:
            AsanaTask: task object if it exists, else None if not found, or an error message if the API call threw an error.
        """

        task = self.__asana__.get_task_by_name(project_name, name)
        return task

    def get_tasks_by_project_id(self, project_id: str) -> List[AsanaTask]:
        """
        Gets all existing task objects for a given project id.

        Example call: get_tasks_by_project_id("Project Id")
        
        Args:
            project_id (str): The project id where to get task objects.
        Returns:
            list(AsanaTask): A list of tasks objects if any, or an error message if the API call threw an error. 
        """

        tasks = self.__asana__.get_tasks_by_project_id(project_id)        
        return tasks

    def get_tasks_by_project_name(self, project_name: str) -> List[AsanaTask]:
        """
        Gets all existing task objects for a given project name.

        Example call: get_tasks_by_project_name("Project Name")
        
        Args:
            project_name (str): The project name where to get task objects.
        Returns:
            list(AsanaTask): A list of tasks objects if any, or an error message if the API call threw an error. 
        """

        tasks = self.__asana__.get_tasks_by_project_name(project_name)        
        return tasks

    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Updates an existing task object's status for a given task id.

        Example call: update_task_status("Task Id", "Completed")
        
        Args:
            task_id (str): The task id to update the task object's status.
            status (str): The status to update the task status. Possible values: ['Not Started', 'In Progress, 'Completed'].
        Returns:
            bool: Updated of true else false if not found, or an error message if the API call threw an error. 
        """

        result = self.__asana__.update_task_status(task_id, status)
        return result

    def update_task(self, task_id: str, model: str) -> AsanaTask:
        """
        Updates an existing task object for a given task id.

        Example call: update_task("Task Id", model)
        
        Args:
            task_id (str): The task id used to update the task object.
            model (str): A json representation of a model with the following properties:
                {
                    "name": "(str) The name of the task to update.",
                    "due_date": "(str) The due_date of the task to update.",
                    "status": "(str) The status of the task to update. Valid Status: ['Not Started', 'In Progress', 'Completed']",
                }
        Returns:
            AsanaTask: Updated task object if successful, else None if not found, or an error message if the API call threw an error.
        """

        data_model = json.loads(model)
        update_model = AsanaTaskUpdate(**data_model)

        project = self.__asana__.update_task(task_id, update_model)
        return project

    def delete_task_by_id(self, task_id: str) -> bool:
        """
        Deletes an existing task object by task id.

        Example call: delete_task_by_id("Task Id")
        
        Args:
            task_id (str): The task id to delete an existing task object.
        Returns:
            bool: True if deleted, else False if not found, or an error message if the API call threw an error.              
        """

        result = self.__asana__.delete_task_by_id(task_id)
        return result

    def delete_task_by_name(self, project_name: str, name: str) -> bool:
        """
        Deletes an existing task object for a given project name and for a given task name.

        Example call: delete_task_by_name("Project Name", "Task Id")
        
        Args:
            project_name (str): The project name where the task belongs too.
            name (str): The task name used to delete an existing task object.
        Returns:
            bool: True if deleted, else False if not found, or an error message if the API call threw an error. 
        """

        result = self.__asana__.delete_task_by_name(project_name, name)
        return result

    def get_tools(self) -> List[Tool]:
        return self.__tools__
