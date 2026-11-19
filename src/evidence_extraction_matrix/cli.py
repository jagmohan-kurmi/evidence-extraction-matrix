import argparse,csv,json,sys
from pathlib import Path

def validate(schema,records):
    if not isinstance(schema,dict) or not isinstance(schema.get("fields"),list): raise ValueError("schema must contain a fields array")
    names=[]
    for f in schema["fields"]:
        if not isinstance(f,dict) or not isinstance(f.get("name"),str) or not f["name"].strip(): raise ValueError("every schema field needs a non-empty name")
        names.append(f["name"])
    if len(set(names))!=len(names): raise ValueError("schema field names must be unique")
    if not isinstance(records,list): raise ValueError("records must be an array")
    issues=[]
    for i,rec in enumerate(records):
        if not isinstance(rec,dict) or not isinstance(rec.get("study_id"),str) or not rec["study_id"].strip(): issues.append(f"record {i}: missing study_id"); continue
        vals=rec.get("fields",{})
        if not isinstance(vals,dict): issues.append(f"{rec['study_id']}: fields must be an object"); continue
        for spec in schema["fields"]:
            name=spec["name"]; cell=vals.get(name)
            if spec.get("required",False) and (not isinstance(cell,dict) or cell.get("value") is None or str(cell.get("value")).strip()==""):
                issues.append(f"{rec['study_id']}: missing required field {name}"); continue
            if cell is None: continue
            if not isinstance(cell,dict): issues.append(f"{rec['study_id']}.{name}: value must include evidence object"); continue
            if cell.get("value") is not None and str(cell.get("value")).strip():
                for key in ("page","citation","quote"):
                    if not isinstance(cell.get(key),str) or not cell[key].strip(): issues.append(f"{rec['study_id']}.{name}: missing evidence {key}")
    return issues

def flatten(schema,records,issues=()):
    issue_by_record={}
    for issue in issues:
        match=issue.split(":",1)
        if len(match)==2: issue_by_record.setdefault(match[0],[]).append(match[1].strip())
    columns=["study_id"]+[f["name"] for f in schema["fields"]]+[f"{f['name']}_{k}" for f in schema["fields"] for k in ("page","citation","quote")]+["validation_errors"]
    rows=[]
    for index,rec in enumerate(records):
        row={"study_id":rec.get("study_id","")}; vals=rec.get("fields",{})
        for spec in schema["fields"]:
            name=spec["name"]; cell=vals.get(name,{})
            row[name]=cell.get("value","") if isinstance(cell,dict) else ""
            for k in ("page","citation","quote"): row[f"{name}_{k}"]=cell.get(k,"") if isinstance(cell,dict) else ""
        row["validation_errors"]="; ".join(issue_by_record.get(str(rec.get("study_id","")),issue_by_record.get(f"record {index}",[])))
        rows.append(row)
    return columns,rows

def main(argv=None):
    p=argparse.ArgumentParser(description="Validate evidence extraction records against a JSON schema")
    p.add_argument("input",help="JSON object with schema and records"); p.add_argument("--format",choices=("json","csv"),default="json"); p.add_argument("--output")
    a=p.parse_args(argv)
    try:
        data=json.loads(Path(a.input).read_text(encoding="utf-8")); schema=data.get("schema"); records=data.get("records")
        issues=validate(schema,records)
        if a.format=="json": text=json.dumps({"schema":schema,"records":records,"validation_errors":issues},ensure_ascii=False,indent=2)+"\n"
        else:
            from io import StringIO
            cols,rows=flatten(schema,records,issues); out=StringIO(newline=""); w=csv.DictWriter(out,fieldnames=cols); w.writeheader(); w.writerows(rows); text=out.getvalue()
        Path(a.output).write_text(text,encoding="utf-8",newline="\n") if a.output else sys.stdout.write(text)
        return 1 if issues else 0
    except (OSError,json.JSONDecodeError,AttributeError,ValueError) as e: print(f"error: {e}",file=sys.stderr); return 2
if __name__=="__main__":raise SystemExit(main())
