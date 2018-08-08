
#encoding: utf-8

# In[74]:


#####################################################################
#                       Libraries:                                  #
#####################################################################
#!/usr/bin/python
#import pandas as pd
import numpy as np
import matplotlib as plt
# dealing with operations systems like reading a file
import sys, os
import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join
import glob,re


# In[75]:


## Rechieve all scene's ID in text to process -- their type is 'H'
global relative_Pronouns
relative_Pronouns = ["which","whom","whose","that"] # words that we would remove and their type is 'F'

def Get_Scene_ID(layer, Elaborator_ID):
    List_ID = []
    for element in layer:
        if element.tag == 'node':
            for child_node in element:
                if child_node.tag == 'edge' and child_node.attrib["type"] == 'H':
                    List_ID.append(child_node.attrib["toID"])
                    Following_Node = Get_Node_By_ID(layer,child_node.attrib["toID"])
                    List1 = Create_Intermidiate_Scene(layer1,layer2, Following_Node, Elaborator_ID)
                    List_ID.extend(List1)
    return List_ID, Elaborator_ID
#####################################################################
# get the ListID of elaborator scene include into other scene
def Create_Intermidiate_Scene(layer1,layer2, Scene_Node, Elaborator_ID):
    ListID = []
    if Is_Node_Terminal(Scene_Node):
        return []
    else:
        for child_node in Scene_Node:
            if child_node.tag == 'edge' and child_node.attrib["type"] == 'E':
                Next_nd = Get_Node_By_ID(layer2, child_node.attrib["toID"])
                if Is_Node_Terminal(Next_nd) == 0 and Next_nd.attrib["ID"] not in ListID:
                    for fils in Next_nd:
                        if fils.tag == 'edge' and fils.attrib["type"] == 'F':                                                     
                            ListID.append(Next_nd.attrib["ID"])
                            Elaborator_ID.append(Next_nd.attrib["ID"]) 
                            break
            elif child_node.tag == 'edge' and child_node.attrib["type"] != 'E':
                Next_nd = Get_Node_By_ID(layer2, child_node.attrib["toID"])
                List1 = Create_Intermidiate_Scene(layer1,layer2, Next_nd, Elaborator_ID)
                ListID.extend(List1)
        return ListID
#####################################################################
# Get the related node to an edge (by attribut 'toID')
def Get_Node_By_ID(layer,ID):
    for node in layer:
        if node.tag == 'node' and node.attrib["ID"] == ID:
            return node
#####################################################################
# Check if all edges of a node are Terminals, or not
def Is_Node_Terminal(node):
    for child in node:
        if child.tag == 'edge' and child.attrib["type"] != "Terminal":
            return 0
    return 1
#####################################################################
# if it's Temrial or A or P .. check all different types in paper
def Get_Type_Edge(edge):
    if edge.tag == 'edge':
        return edge.attrib["type"]
#####################################################################
# Get word related to an edge from layer 1.
def Get_Word(layer, ID) :
    for node in layer:
        if node.tag == 'node' and node.attrib["ID"] == ID:
            for child_node in node:
                if child_node.attrib["text"] not in relative_Pronouns:
                    return child_node.attrib["text"]
                else:
                    if ELABORATOR_PROCESS == 0:                        
                        return child_node.attrib["text"]
                    elif ELABORATOR_PROCESS == 1:                       
                        if child_node.attrib["text"] == "whose":
                            return "'s"
                        else:
                            return ""
#####################################################################
# Get the original sentence we have as Input; just to make a visual comparaison
def Get_Original(layer):
    original = ""
    for node in layer:
        if node.tag == 'node':
            for child_node in node:
                if node.attrib["type"] == 'Punctuation':
                    original = original[:len(original)-1] + child_node.attrib["text"] + " "
                else:
                    original += child_node.attrib["text"] + " "
    return original
#####################################################################
# Get all edge's ID of a specific Node
def Get_All_Edge_ID(layer, NodeID):
    List = []
    for node in layer:
        if node.tag == "node" and node.attrib["ID"] == NodeID:
            for child in node:
                if child.tag == 'edge':
                    List.append(child.attrib["toID"])
    return List
#####################################################################
# if a node is Terminal, means all its edges are Terminals so we rechieve the text presented by it
def Get_Text_From_Terminal_Node(layer1, layer2, terminal_Nd):
    Text = ""
    if Is_Node_Terminal(terminal_Nd):
        for edgeID in Get_All_Edge_ID(layer2, terminal_Nd.attrib["ID"]):
            if Get_Word(layer1, edgeID) != "":
                if Get_Word(layer1, edgeID) == "'s":
                    Text = Text[:len(Text)-2] + Get_Word(layer1, edgeID) + " "
                else:
                    Text += Get_Word(layer1, edgeID) + " "
    return Text
#####################################################################
# Tree iteration , with deep course -- return the text
def recursive(layer1, layer2, Node,All_sceneID, Elaborator_ID):
    Text = ""
    if Is_Node_Terminal(Node):
        Text += Get_Text_From_Terminal_Node(layer1, layer2, Node)
        return Text
    else:
        List_child = Get_Child_List(Node) # all Node's child in a list
        for i in range(len(List_child)):
            if List_child[i].attrib["toID"] not in All_sceneID:
                Order_Child(i,List_child)  # Reorder child in case we have: ['A','F','A','P']
                if Get_Type_Edge(List_child[i]) == "Terminal":
                    if Get_Word(layer1, List_child[i].attrib['toID']) != "":
                        if Get_Word(layer1, List_child[i].attrib['toID']) == "'s":
                            print(Get_Word(layer1, List_child[i].attrib['toID'])+'0')
                            Text = Text[:len(Text)-2] + Get_Word(layer1, List_child[i].attrib['toID']) + " "
                        else:
                            Text += Get_Word(layer1, List_child[i].attrib['toID']) + " "
                else:
                    Next_nd = Get_Node_By_ID(layer2, List_child[i].attrib['toID'])
                    Text += recursive(layer1, layer2, Next_nd, All_sceneID, Elaborator_ID)
    return Text
#####################################################################
# Combine all scenes in one sentence simple as output
def Get_Simple(Lists_Scene):
    simple = ''
    for scene in Lists_Scene:
        simple += scene[0].upper() + scene[1: len(scene)-1] + '. '
    return simple
#####################################################################
# The main function returns the entire simple sentence and also list of scene independently, the return is a list of two lists
def Main(layer1, layer2):   
    global ELABORATOR_PROCESS
    Lists_Scene, Elaborator_ID, Lists_Scene = ([] for i in range(3)) # initialize 3 empty list at same time
    All_sceneID, Elaborator_ID = Get_Scene_ID(layer2, Elaborator_ID) # this fucntion return two list     
    # loop on differents scene and get scene per scene
    for sceneID in All_sceneID:
        if sceneID in Elaborator_ID:            
            ELABORATOR_PROCESS = 1
        else:      
            ELABORATOR_PROCESS = 0        
        result = ""
        Node_Scene = Get_Node_By_ID(layer2, sceneID) # get the first Node the scene started with
        result = recursive(layer1, layer2, Node_Scene, All_sceneID, Elaborator_ID) # recursive to get text by initial Node_scene
        Lists_Scene.append(result) # append final result which contain the text represented by te Node_Scene
    simple = Get_Simple(Lists_Scene)
    return simple, Lists_Scene # this list contains all scene
#####################################################################
def Get_Child_List(Node):
    List = []
    for child in Node:
        if child.tag == "edge":
            List.append(child)
    return List
#####################################################################
# Reorder child in case we have: ['A','F','A','P']
def Order_Child(Current_child_Index,List_child):
    i = Current_child_Index
    if set([i,i+1,i+2,i+3]).issubset(range(len(List_child))) and List_child[i].attrib["type"] == 'A' and List_child[i+1].attrib["type"] == 'F' and List_child[i+2].attrib["type"] == 'A' and List_child[i+3].attrib["type"] == 'P':
        if Get_Text_From_Terminal_Node(layer1, layer2, Get_Node_By_ID(layer2, List_child[i+1].attrib[("toID")])) != "'s ": # yes I compare to ''s' cause orignally it's whose
            temp0 = List_child[i]
            temp3 = List_child[i+3]
            List_child[i] = List_child[i+2]
            List_child[i+3] = List_child[i+1]
            List_child[i+2] = temp0
            List_child[i+1] = temp3
#####################################################################
# this function reorder the XML files extracted by name
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)    
    parts[1::2] = map(int, parts[1::2])    
    return parts            
#####################################################################
def Get_XML_files(mypath):
    onlyXML = []
    for infile in sorted(glob.glob(mypath + '/*.xml'), key=numericalSort):
        onlyXML.append(infile.split("/")[-1])     
    return onlyXML
#####################################################################


# In[76]:


##################################################################### 
#                     Load data & Variables:                       #
#####################################################################
#Global variables:       
# mypath directory xml fiels
mypath = sys.argv[1]
onlyXML = Get_XML_files(mypath) # get all XML file that outcome from parser part
layers = []
for fileXML in onlyXML:
    file_path = mypath + "/" + fileXML
    tree = ET.parse(file_path)
    root = tree.getroot()
    List1 = []
    for child in root: # retrive the two layers we have on the tree
        if child.tag == 'layer':
            List1.append(child)
    List1.append(fileXML.split('_')[1]) # the 3rd element indicate the number of paragraph ex 'test_NPara_NLine'
    List1.append(fileXML.split('_')[2])
    layers.append(List1)

# In[77]:


#####################################################################
#                              Main Operations:                     #
#####################################################################
layer = layers[0]
layer1, layer2 = layer[0], layer[1]
simple, Lists_Scene = Main(layer1, layer2) # Main function,  see details above

# This method is used to avoid problems with unicode characters encountered with print fucntion
sys.stdout.buffer.write ((simple + " \n").encode ('utf-8'))

for i in range(1,len(layers)):
    layer = layers[i]    
    layer1, layer2 = layer[0], layer[1]
    simple, Lists_Scene = Main(layer1, layer2) # Main function,  see details above
    if layer[2] == layers[i-1][2]:
        sys.stdout.buffer.write ((simple + " \n").encode ('utf-8'))
    elif layer[2] != layers[i-1][2]:
        sys.stdout.buffer.write (("\n" + simple + " \n").encode ('utf-8'))
        
#print("Original: ", Get_Original(layer1))   
            