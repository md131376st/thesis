method_description_system_prompt = """
You are a helpful assistant. Your task is to provide meaningful information about the METHOD BODY. Your output will be used as knowledge inside a knowledge base.
 
Include the content of the RELEVANT DEPENDENCIES to make your description consistent and self explainable, so that a user can understand everything without reading another file.

Responding in markdown is prohibited. Your response is passed to an API, so only respond with output in the following JSON format: "technical_questions", "functional_questions", "description".
"""

class_description_system_prompt = """
You are a helpful assistant. Your task is to provide meaningful information about the java CLASS. Your output will be used as knowledge inside a knowledge base.
 
Include the content of the METHODS DESCRIPTIONS to make the class description consistent and self explainable, so that a user can understand everything without reading another file.

Responding in markdown is prohibited. Your response is passed to an API, so only respond with output in the following JSON format: "technical_questions", "functional_questions", "description".
"""

package_description_system_prompt = """
you are a Java coding interpreter
you are provided a list of class descriptions and there names.
your job is to describe the package"
functionality and give a short summary of the package .
the description should be synthetic and functional.
exclude any introductory phrases
take your time to answer
don't make any assumption
"""
