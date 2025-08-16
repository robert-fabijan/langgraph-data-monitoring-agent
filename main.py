from agent.entry import build_agent
import json
# from IPython.display import Image, display
# if __name__ == "__main__":
    # Build the agent graph
graph = build_agent().compile()

    # # Display the graph structure
    
    # img = graph.get_graph(xray=1).draw_mermaid_png()
    # with open("graph.png", "wb") as f:
    #     f.write(img)
    # import os
    # os.system("open graph.png")  # macOS: opens the image in Preview

    # Example raw logs to invoke the agent
# raw_data = None
# with open("data.json", "r") açs f:
#     raw_data = json.load(f)
# result = graph.invoke({
#     "raw_data": raw_data
# })
# print(result["summary"])
