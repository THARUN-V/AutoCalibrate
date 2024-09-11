from ParseParams import *
import json

if __name__ == "__main__":
    
    params = ParseParams()
    
    print(params.args.json_path)
    
    with open(params.args.json_path,"r") as json_file:
        f = json.load(json_file)
        
    # f["test_val"] = 15975345685
    # del f["new_val"]
    
    # with open(params.args.json_path,"w") as json_file:
    #     json.dump(f,json_file)
    
    print(json.dumps(f,indent = 4))