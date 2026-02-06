
import sys, os, json, re

def extract_first_json(text: str):
  
    # Remove common code-fence wrappers
    # ```json ... ``` or ``` ... ```
    text = text.strip()
    fence = re.compile(r"^```[a-zA-Z0-9]*\s*([\s\S]*?)\s*```$", re.MULTILINE)
    m = fence.search(text)
    if m:
        text = m.group(1).strip()

    # Try direct parse first
    for candidate in (text, ):
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # If that failed, try to locate the first {...} or [...]
    # simple bracket matcher
    def find_balanced(s, open_char, close_char):
        depth = 0
        start = -1
        for i,c in enumerate(s):
            if c == open_char:
                if depth == 0:
                    start = i
                depth += 1
            elif c == close_char and depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    return s[start:i+1]
        return None

    for opener, closer in (('{','}'), ('[',']')):
        frag = find_balanced(text, opener, closer)
        if frag:
            try:
                return json.loads(frag)
            except Exception:
                pass

    return None

def main():
    if len(sys.argv) != 2:
        print("Usage: repair_raw_json.py <path/to/raw_txt>")
        sys.exit(2)
    raw_txt = sys.argv[1]
    if not os.path.isfile(raw_txt):
        print(f"ERROR: not a file: {raw_txt}")
        sys.exit(2)

    with open(raw_txt, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    obj = extract_first_json(raw)
    out_path = raw_txt.replace(".txt", "__REPAIRED.json")
    if obj is None:
        # If we truly cannot parse, write an error JSON so pipeline won't 0-byte
        obj = {"_error": "could_not_parse_json", "_raw_sample": raw[:2000]}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

    print(f"[repaired] {out_path}")

if __name__ == "__main__":
    main()
