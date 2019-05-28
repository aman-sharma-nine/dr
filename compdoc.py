import pandas as pd
import datarobot as dr


# Downloading default compliance doc

def download_compliance_doc(project_id, model_id, filepath):
    '''
        returns docx file of model documentation
        project_id : projects id
        model_id  :  chosen models id
        filepath : file location where documentation will be saved

    '''
    doc = dr.models.ComplianceDocumentation(project_id, model_id)
    doc.generate().wait_for_completion()
    doc.download(filepath)


download_compliance_doc(project_id= project.id, model_id= model.id,
                        filepath= '../../../example.docx')

#Creating a new compliance doc template
#A compliance documentation template. Templates are used to customize contents of Compliance Documentation
#Please refer : https://datarobot-public-api-client.readthedocs-hosted.com/en/v2.16.0/autodoc/api_reference.html
#datarobot.models.compliance_doc_template.ComplianceDocTemplate

#### Create a template with the specified name and sections
mytemplate = dr.models.ComplianceDocTemplate.create(name ='My custom Template',
                                                    sections= [{'title' :'My Template - Datarobot',
                                                              'type': 'user',
                                                            "highlightedText": "Testing the highlightedText",
                                                            "regularText" : " Testing the compliance doc \n This is where you will enter the text",
                                                            "sections" :[]}])
#Download custom compliance doc template

mytemplateid = mytemplate.id
download_compliance_doc(project.id, model.id, mytemplateid)


#Adding a custom section to the compliance documentation

default_template = dr.ComplianceDocTemplate.get_default()
default_template.sections_to_json_file('path/to/example.json')
# Add custom sections to the json file in your preferable text editor
my_template = ComplianceDocTemplate.create_from_json_file(
    name='my template',
    path='path/to/example.json'
)
