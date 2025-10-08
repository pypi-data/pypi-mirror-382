#!/usr/bin/env python
import json
import sys
import traceback

from .import_module import import_module
from .storage import get_step_to_callable

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("arg file path missing")
    arg_file_path = sys.argv[1]
    
    with open(arg_file_path, "r") as f:
        arg_data = json.load(f)
    
    app_path = arg_data["app_path"]
    step_name = arg_data["step_name"]
    seed = arg_data["seed"]
    output_file = arg_data.get("output_file", None)
    
    
    try:
        import_module(app_path)

        datallog_step_function = get_step_to_callable(step_name)
        if datallog_step_function is None:
            raise Exception(f"Step {step_name} not found")
        
        step_result = datallog_step_function(seed)
        result = {
            "type": "result",
            "step_result": step_result
        }
        
    except Exception as e:
        import traceback
        result = {"type": "error", "message": str(traceback.format_exc())}
        
    with open(output_file, "w") as f:
        json.dump(result, f)
        output_file.flush()
        
    sys.exit(0)