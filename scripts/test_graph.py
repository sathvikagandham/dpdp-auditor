import sys
import os

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))
from dpdp_auditor.agent.graph import graph

initial_state={
    "claim":"We share data with marketing prtners.",
    "law_chunk":"",
    "finding":None,
    "retries":0
}

print("Starting Agent Graph...")
final_state=graph.invoke(initial_state)

print("\n--Final State---")
print(f"Retries used: {final_state['retries']}")
if final_state["finding"]:
    print(f"Finding: {final_state['finding']}")
else:
    print("No valid finding generated after maximum retries.")
