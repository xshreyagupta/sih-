from db import query
def get_authority_for_event(defect_type):
    result= query("SELECT id,name FROM authorities WHERE defect_type= %s LIMIT 1",(defect_type,))
    return result[0] if result else None