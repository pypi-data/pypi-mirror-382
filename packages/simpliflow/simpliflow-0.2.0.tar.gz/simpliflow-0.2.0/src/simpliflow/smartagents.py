#!/usr/bin/env python
# coding: utf-8

import requests
import json
import importlib.util
import sys
import func
import os
from litellm import completion


from openai import OpenAI
import anthropic
import cohere

class Agent:
    def __init__(self, name):
        self.messages = []
        self.name = name
        self.approval = "no"
        self.response_feedback = ""

    # Function that takes a user question as input and returns the chatbot's response
    def get_response(self, model, creativity, diversity, max_tokens):
        output = completion(model=model, messages=self.messages , temperature=creativity, max_tokens=max_tokens, top_p= diversity, drop_params=True)['choices'][0]['message']['content']
        return output


def call_agents(agentsfile, dynamic_input, model, creativity, diversity, max_tokens):

    resultofpreviousagent = None
    interactions = []  # Holds all Interactions in the chain.
    original_question= None

    with open(agentsfile) as f:
        data = json.load(f)
        # continue extracting agents from the JSON file until next_agent is not found
        for agent in data["agents"]:

            # head and next is also not used

            # Instantiate the Agent class with the above parameters
            # name not used currently, but just passed to the instance
            agent_instance = Agent(agent["name_of_agent"])

            # if the agent is the first agent in the chain, the question is the input  else the question is the result of the previous agent
            if agent["head"] == "True":
                question = agent["what_should_agent_do"]

                # if dynamic_input is not None, append it to the question, so it is passed to the agent
                if dynamic_input is not None:
                    question = (
                        agent["what_should_agent_do"]
                        + "- The input is : "
                        + dynamic_input
                    )
             
            else:
                question = (
                    agent["what_should_agent_do"]
                    + "---"
                    + str(resultofpreviousagent)
                    + "---"
                )


            # log messages for the agent to agent_instance.messages,  interactions
            agent_instance.messages = [
                {"role": "system", "content": "You are a " + agent["role_of_agent"]}
            ]
            agent_instance.messages.append({"role": "user", "content": question})
        
           
            # make the call
            resultofagent = agent_instance.get_response(model, creativity, diversity, max_tokens)
       
            original_question = question
            # Add HITL to response if specified
            if agent["require_human_approval_of_response"] == "True":

                while agent_instance.approval.lower() != "yes":

                    print("-------- Human-In-The-Loop (HITL) Approval is Required for Agent: ", agent["name_of_agent"],"-------- ")
                    print("Agent's Current Response:\n", str(resultofagent), end="\n\n")

                    agent_instance.approval = input("Do you approve this response? (yes/no): ")
                    
                    if agent_instance.approval.lower() == "yes":
                        print("Response approved. Continuing...\n")
                        break
                    elif agent_instance.approval.lower() == "no":
                        agent_instance.response_feedback = input("What is wrong with the response? ")
                    # incorporate feedback into the refiring of the agent. 
                        question =  question + ". If you respond like this  - ''' "+ str(resultofagent)+ " ''',  Then my feedback would be ''' "+ agent_instance.response_feedback + " ''' "
                        # remove the last user message and add the new one with feedback
                      
                        #agent_instance.messages = agent_instance.messages[:-1]
                        agent_instance.messages.append({"role": "user", "content": question})
                        
                        # refire the agent
                        resultofagent = agent_instance.get_response(model, creativity, diversity, max_tokens)
                        continue
                    elif agent_instance.approval.lower() != "yes":
                        print("Invalid input.\n")
                        continue

  
            # log the approved/finalized responses, results to agent_instance.messages, interactions and resultofpreviousagent
            resultofpreviousagent = resultofagent
            agent_instance.messages.append({"role": "system", "content": resultofagent})

            interactions.append(
                {
                    "entity": "agent",
                    "name": agent["name_of_agent"],
                    "input": original_question,
                    "feedback_augmented_input": question,
                    "output": resultofagent,
                }
            )

            # print messages
            print( "################################# Agent Name:",agent["name_of_agent"],"#################################",)
            print(resultofagent, end="\n\n")
  

            # if postprocessor_function is not None, call the function with the result of the agent
            if agent["postprocessor_function"] != "None":
                postprocessor_function = agent["postprocessor_function"]
                
                r = getattr(func, postprocessor_function)
                resultoffunction = r(resultofpreviousagent)

                # store the modified result in resultofpreviousagent
                resultofpreviousagent = resultoffunction
                print("################################# Postprocessor Function:",postprocessor_function,"#################################")
                print(resultofpreviousagent, end="\n\n")
                
                # also store the result of function in interactions
                interactions.append(
                    {
                        "entity": "function",
                        "name": postprocessor_function,
                        "input": resultofagent,
                        "output": resultoffunction,
                    }
                )

    # Write the interactions to a JSON file. The location of the Interactions file will be inside an Interactions folder. The name of the interactions file will be borrowed from the agentsfile identifier.
    filename = os.path.splitext(os.path.basename(agentsfile))[0] + "_interactions.json"
    filepath = os.path.join("Interactions", filename)

    # If the Interactions folder does not exist, create it
    if not os.path.exists("Interactions"):
        os.makedirs("Interactions")

    with open(filepath, "w") as f:
        json.dump(interactions, f, indent=4)

    return resultofpreviousagent, interactions


